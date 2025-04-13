import inspect
import os
import re
import time

import networkx as nx
import numpy as np

from nltk import sent_tokenize

from app.kv_store import JsonKvStore
from app.openai_llm import OpenAiLlm
from app.logger import logger, set_logger

from app.definitions import INPUT_DOCS_DIR, SOURCE_TO_DOC_ID_KV_PATH, DOC_ID_TO_SOURCE_KV_PATH, EMBEDDINGS_DB, \
    EXCERPT_KV_PATH, DOC_ID_TO_EXCERPT_KV_PATH, KG_DB, ENTITIES_DB, RELATIONSHIPS_DB, KG_SEP, TUPLE_SEP, REC_SEP, \
    COMPLETE_TAG, DATA_DIR, LOG_DIR, COMPLETION_MODEL, EMBEDDING_MODEL
from app.prompts import get_query_system_prompt, excerpt_summary_prompt, get_extract_entities_prompt, \
    get_high_low_level_keywords_prompt, get_kg_query_system_prompt, get_mix_system_prompt

from app.utilities import get_json, read_file, get_docs, make_hash, split_string_by_multi_markers, clean_str, \
    extract_json_from_text, is_float_regex, truncate_list_by_token_size, \
    list_of_list_to_csv, delete_all_files

import nltk

from app.vector_store import NanoVectorStore


class SmolRag:
    def __init__(
            self,
            llm=None,
            embeddings_db=None,
            entities_db=None,
            relationships_db=None,
            source_to_doc_kv=None,
            doc_to_source_kv=None,
            doc_to_excerpt_kv=None,
            excerpt_kv=None,
            query_cache_kv=None,
            embedding_cache_kv=None
    ):
        set_logger("main.log")
        nltk.download('punkt')

        self.llm = llm or OpenAiLlm(
            COMPLETION_MODEL,
            EMBEDDING_MODEL,
            query_cache_kv=query_cache_kv,
            embedding_cache_kv=embedding_cache_kv
        )

        self.dimensions = 1536
        self.embeddings_db = embeddings_db or NanoVectorStore(EMBEDDINGS_DB, self.dimensions)
        self.entities_db = entities_db or NanoVectorStore(ENTITIES_DB, self.dimensions)
        self.relationships_db = relationships_db or NanoVectorStore(RELATIONSHIPS_DB, self.dimensions)

        self.source_to_doc_kv = source_to_doc_kv or JsonKvStore(SOURCE_TO_DOC_ID_KV_PATH)
        self.doc_to_source_kv = doc_to_source_kv or JsonKvStore(DOC_ID_TO_SOURCE_KV_PATH)
        self.doc_to_excerpt_kv = doc_to_excerpt_kv or JsonKvStore(DOC_ID_TO_EXCERPT_KV_PATH)
        self.excerpt_kv = excerpt_kv or JsonKvStore(EXCERPT_KV_PATH)

        if os.path.exists(KG_DB):
            try:
                self.graph = nx.read_graphml(KG_DB)
                logger.info(f"Knowledge graph loaded from {KG_DB}")
            except Exception as e:
                logger.error(f"Error loading knowledge graph from {KG_DB}: {e}")
                self.graph = nx.Graph()
        else:
            self.graph = nx.Graph()
            logger.info("No existing knowledge graph found; creating a new one.")

    def remove_document_by_id(self, doc_id):
        if self.doc_to_source_kv.has(doc_id):
            source = self.doc_to_source_kv.get_by_key(doc_id)
            self.doc_to_source_kv.remove(doc_id)
            self.source_to_doc_kv.remove(source)
            self.doc_to_source_kv.save()
            self.source_to_doc_kv.save()
        if self.doc_to_excerpt_kv.has(doc_id):
            excerpt_ids = self.doc_to_excerpt_kv.get_by_key(doc_id)
            for excerpt_id in excerpt_ids:
                self.excerpt_kv.remove(excerpt_id)
            self.doc_to_excerpt_kv.remove(doc_id)
            self.excerpt_kv.save()
            self.doc_to_excerpt_kv.save()
            self.embeddings_db.delete(excerpt_ids)
            self.embeddings_db.save()

    def import_documents(self):
        sources = get_docs(INPUT_DOCS_DIR)
        for source in sources:
            content = read_file(source)
            doc_id = make_hash(content, "doc_")

            if not self.source_to_doc_kv.has(source):
                logger.info(f"Importing new document: {source} (ID: {doc_id})")
                self._add_document_maps(source, content)
                self._embed_document(content, doc_id)
                self._extract_entities(content, doc_id)
            elif not self.source_to_doc_kv.equal(source, doc_id):
                logger.info(f"Updating document: {source} (New ID: {doc_id})")
                old_doc_id = self.source_to_doc_kv.get_by_key(source)
                self.remove_document_by_id(old_doc_id)
                self._add_document_maps(source, content)
                self._embed_document(content, doc_id)
                self._extract_entities(content, doc_id)
            else:
                logger.debug(f"No changes detected for document: {source} (ID: {doc_id})")

    def _add_document_maps(self, source, content):
        doc_id = make_hash(content, "doc_")
        self.source_to_doc_kv.add(source, doc_id)
        self.doc_to_source_kv.add(doc_id, source)
        self.source_to_doc_kv.save()
        self.doc_to_source_kv.save()

    def _embed_document(self, content, doc_id):
        start_time = time.time()
        excerpts = self._get_excerpts(content)
        excerpt_ids = []
        for i, excerpt in enumerate(excerpts):
            excerpt_id = make_hash(excerpt, "excerpt_id_")
            excerpt_ids.append(excerpt_id)
            summary = self._get_excerpt_summary(content, excerpt)
            embedding_content = f"{excerpt}\n\n{summary}"
            embedding_result = self.llm.get_embedding(embedding_content)
            vector = np.array(embedding_result, dtype=np.float32)
            self.embeddings_db.upsert([
                {"__id__": excerpt_id, "__vector__": vector, "__doc_id__": doc_id, "__inserted_at__": time.time()}
            ])
            self.excerpt_kv.add(excerpt_id, {
                "doc_id": doc_id,
                "doc_order_index": i,
                "excerpt": excerpt,
                "summary": summary,
                "indexed_at": time.time()
            })
            logger.info(f"Created embedding for excerpt {excerpt_id} associated with document {doc_id}")

        self.excerpt_kv.save()
        self.embeddings_db.save()
        self.doc_to_excerpt_kv.add(doc_id, excerpt_ids)
        self.doc_to_excerpt_kv.save()
        elapsed = time.time() - start_time
        logger.info(f"Document {doc_id} processed with {len(excerpts)} excerpts in {elapsed:.2f} seconds.")

    def _get_excerpts(self, content, n=2000):
        """
        Split `content` into code/text chunks up to `n` characters.

        The function processes the content as follows:
          1) Code blocks (denoted by triple backticks) remain whole, but the triple backticks
             are removed from the output.
          2) Regular text is split into paragraphs (using one or more newlines).
          3) Paragraphs longer than `n` characters are further split into sentences using NLTK.
          4) Any sentence that exceeds `n` characters is stored on its own.

        All text excerpts stripped of leading and trailing whitespace.
        """
        parts = re.split(r'(```.*?```)', content, flags=re.DOTALL)
        excerpts = []

        for part in parts:
            part_stripped = part.strip()
            if part_stripped.startswith('```') and part_stripped.endswith('```'):
                code_content = part_stripped[3:-3].strip()
                excerpts.append(code_content)
                continue

            if len(part) <= n:
                excerpts.append(part.strip())
                continue

            paragraphs = re.split(r'\n\n+', part)
            current_excerpt = ""
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue

                if len(paragraph) <= n:
                    if current_excerpt:
                        proposed_excerpt = current_excerpt + "\n\n" + paragraph
                    else:
                        proposed_excerpt = paragraph

                    if len(proposed_excerpt) <= n:
                        current_excerpt = proposed_excerpt
                    else:
                        if current_excerpt:
                            excerpts.append(current_excerpt.strip())
                        current_excerpt = paragraph
                else:
                    if current_excerpt:
                        excerpts.append(current_excerpt.strip())
                        current_excerpt = ""
                    sentences = sent_tokenize(paragraph)
                    sentence_excerpt = ""
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) > n:
                            if sentence_excerpt:
                                excerpts.append(sentence_excerpt.strip())
                                sentence_excerpt = ""
                            excerpts.append(sentence.strip())
                            continue
                        if sentence_excerpt:
                            proposed_sentence_excerpt = sentence_excerpt + " " + sentence
                        else:
                            proposed_sentence_excerpt = sentence
                        if len(proposed_sentence_excerpt) <= n:
                            sentence_excerpt = proposed_sentence_excerpt
                        else:
                            excerpts.append(sentence_excerpt.strip())
                            sentence_excerpt = sentence
                    if sentence_excerpt:
                        excerpts.append(sentence_excerpt.strip())
            if current_excerpt:
                excerpts.append(current_excerpt.strip())

        return excerpts

    def _get_excerpt_summary(self, full_doc, excerpt):
        prompt = excerpt_summary_prompt(full_doc, excerpt)
        try:
            summary = self.llm.get_completion(prompt)
        except Exception as e:
            logger.error(f"LLM call in _get_excerpt_summary failed: {e}")
            summary = "Summary unavailable."
        return summary

    def _extract_entities(self, content, doc_id):
        start_time = time.time()
        total_entities = 0
        total_relationships = 0
        excerpts = self._get_excerpts(content)

        for excerpt in excerpts:
            excerpt_id = make_hash(excerpt, "excerpt_id_")
            try:
                result = self.llm.get_completion(get_extract_entities_prompt(excerpt))
            except Exception as e:
                logger.error(f"LLM call for entity extraction failed for excerpt {excerpt_id}: {e}")
                continue

            data_str = result.replace(COMPLETE_TAG, '').strip()
            records = split_string_by_multi_markers(data_str, [REC_SEP])
            clean_records = []
            for record in records:
                if record.startswith('(') and record.endswith(')'):
                    record = record[1:-1]
                clean_records.append(clean_str(record))
            records = clean_records

            for record in records:
                fields = split_string_by_multi_markers(record, [TUPLE_SEP])
                if not fields:
                    continue
                fields = [field[1:-1] if field.startswith('"') and field.endswith('"') else field for field in fields]
                record_type = fields[0].lower()

                if record_type == 'entity':
                    if len(fields) >= 4:
                        _, name, category, description = fields[:4]
                        existing_node = self.graph.nodes.get(name)
                        if existing_node:
                            existing_descriptions = split_string_by_multi_markers(existing_node["description"], KG_SEP)
                            descriptions = KG_SEP.join(set(list(existing_descriptions) + [description]))
                            existing_categories = split_string_by_multi_markers(existing_node["category"], KG_SEP)
                            categories = KG_SEP.join(set(list(existing_categories) + [category]))
                            existing_excerpt_ids = split_string_by_multi_markers(existing_node["excerpt_id"], KG_SEP)
                            excerpt_ids = KG_SEP.join(set(list(existing_excerpt_ids) + [excerpt_id]))
                            # Todo: summarise descriptions with LLM query if they get too long
                            self.graph.add_node(
                                name,
                                category=categories,
                                description=descriptions,
                                excerpt_id=excerpt_ids
                            )
                        else:
                            self.graph.add_node(name, category=category, description=description, excerpt_id=excerpt_id)
                        total_entities += 1
                        entity_id = make_hash(name, prefix="ent-")
                        embedding_content = f"{name} {description}"
                        embedding_result = self.llm.get_embedding(embedding_content)
                        vector = np.array(embedding_result, dtype=np.float32)
                        self.entities_db.upsert([
                            {
                                "__id__": entity_id,
                                "__vector__": vector,
                                "__entity_name__": name,
                                "__inserted_at__": time.time(),
                            }
                        ])
                elif record_type == 'relationship':
                    if len(fields) >= 6:
                        _, source, target, description, keywords, weight = fields[:6]
                        source, target = sorted([source, target])
                        # Todo: summarise descriptions with LLM query if they get too long
                        existing_edge = self.graph.edges.get((source, target))
                        weight = float(weight) if is_float_regex(weight) else 1.0
                        if existing_edge:
                            existing_descriptions = split_string_by_multi_markers(existing_edge["description"], KG_SEP)
                            descriptions = KG_SEP.join(set(list(existing_descriptions) + [description]))
                            existing_keywords = split_string_by_multi_markers(existing_edge["keywords"], KG_SEP)
                            keywords = KG_SEP.join(set(list(existing_keywords) + [keywords]))
                            existing_excerpt_ids = split_string_by_multi_markers(existing_edge["excerpt_id"], KG_SEP)
                            excerpt_ids = KG_SEP.join(set(list(existing_excerpt_ids) + [excerpt_id]))
                            weight = sum([weight, existing_edge["weight"]])
                            self.graph.add_edge(source, target, description=descriptions, keywords=keywords,
                                                weight=weight,
                                                excerpt_id=excerpt_ids)
                        else:
                            self.graph.add_edge(source, target, description=description, keywords=keywords,
                                                weight=weight,
                                                excerpt_id=excerpt_id)
                        total_relationships += 1

                        relationship_id = make_hash(f"{source}_{target}", prefix="ent-")
                        embedding_content = f"{keywords} {source} {target} {description}"
                        embedding_result = self.llm.get_embedding(embedding_content)
                        vector = np.array(embedding_result, dtype=np.float32)
                        self.relationships_db.upsert([
                            {
                                "__id__": relationship_id,
                                "__vector__": vector,
                                "__source__": source,
                                "__target__": target,
                                "__inserted_at__": time.time(),
                            }
                        ])
                elif record_type == 'content_keywords':
                    if len(fields) >= 2:
                        self.graph.graph['content_keywords'] = fields[1]

        self.entities_db.save()
        self.relationships_db.save()

        nx.write_graphml(self.graph, KG_DB)
        elapsed = time.time() - start_time
        logger.info(f"Extracted {total_entities} entities and {total_relationships} relationships "
                    f"from document {doc_id} in {elapsed:.2f} seconds.")

    def query(self, text):
        logger.info(f"Received query: {text}")
        excerpts = self._get_query_excerpts(text)
        logger.info(f"Retrieved {len(excerpts)} excerpts for the query.")
        excerpt_context = self._get_excerpt_context(excerpts)
        system_prompt = get_query_system_prompt(excerpt_context)

        return self.llm.get_completion(text, context=system_prompt.strip(), use_cache=False)

    def _get_excerpt_context(self, excerpts):
        context = ""
        for excerpt in excerpts:
            context += inspect.cleandoc(f"""
                ## Excerpt
    
                {excerpt["excerpt"]}
    
                ## Summary
    
                {excerpt["summary"]} 
            """)
            context += "\n\n"

        return context

    def _get_query_excerpts(self, text):
        embedding = self.llm.get_embedding(text)
        embedding_array = np.array(embedding)
        results = self.embeddings_db.query(query=embedding_array, top_k=5, better_than_threshold=0.02)
        excerpts = [self.excerpt_kv.get_by_key(result["__id__"]) for result in results]
        excerpts = truncate_list_by_token_size(excerpts, get_text_for_row=lambda x: x["excerpt"], max_token_size=4000)
        return excerpts

    def hybrid_kg_query(self, text):
        prompt = get_high_low_level_keywords_prompt(text)
        result = self.llm.get_completion(prompt)
        keyword_data = extract_json_from_text(result)
        logger.info("Processed high/low level keywords for hybrid KG query.")

        ll_dataset, ll_entity_excerpts, ll_relations = self._get_low_level_dataset(keyword_data)
        hl_dataset, hl_entities, hl_entity_excerpts = self._get_high_level_dataset(keyword_data)

        entities = ll_dataset + hl_entities
        relations = ll_relations + hl_dataset
        excerpts = ll_entity_excerpts + hl_entity_excerpts
        context = self._get_kg_query_context(entities, excerpts, relations)
        system_prompt = get_kg_query_system_prompt(context)
        return self.llm.get_completion(text, context=system_prompt.strip(), use_cache=False)

    def local_kg_query(self, text):
        prompt = get_high_low_level_keywords_prompt(text)
        result = self.llm.get_completion(prompt)
        keyword_data = extract_json_from_text(result)
        logger.info("Processed high/low level keywords for local KG query.")

        ll_dataset, ll_entity_excerpts, ll_relations = self._get_low_level_dataset(keyword_data)
        entities = ll_dataset
        relations = ll_relations
        excerpts = ll_entity_excerpts
        context = self._get_kg_query_context(entities, excerpts, relations)
        system_prompt = get_kg_query_system_prompt(context)
        return self.llm.get_completion(text, context=system_prompt.strip(), use_cache=False)

    def global_kg_query(self, text):
        prompt = get_high_low_level_keywords_prompt(text)
        result = self.llm.get_completion(prompt)
        keyword_data = extract_json_from_text(result)
        logger.info("Processed high/low level keywords for global KG query.")

        hl_dataset, hl_entities, hl_entity_excerpts = self._get_high_level_dataset(keyword_data)
        entities = hl_entities
        relations = hl_dataset
        excerpts = hl_entity_excerpts
        context = self._get_kg_query_context(entities, excerpts, relations)
        system_prompt = get_kg_query_system_prompt(context)
        return self.llm.get_completion(text, context=system_prompt.strip(), use_cache=False)

    def mix_query(self, text):
        prompt = get_high_low_level_keywords_prompt(text)
        result = self.llm.get_completion(prompt)
        keyword_data = extract_json_from_text(result)
        logger.info("Processed high/low level keywords for mixed KG query.")

        ll_dataset, ll_entity_excerpts, ll_relations = self._get_low_level_dataset(keyword_data)
        hl_dataset, hl_entities, hl_entity_excerpts = self._get_high_level_dataset(keyword_data)

        kg_entities = ll_dataset + hl_entities
        kg_relations = ll_relations + hl_dataset
        kg_excerpts = ll_entity_excerpts + hl_entity_excerpts
        query_excerpts = self._get_query_excerpts(text)
        kg_context = self._get_kg_query_context(kg_entities, kg_excerpts, kg_relations)
        excerpt_context = self._get_excerpt_context(query_excerpts)
        system_prompt = get_mix_system_prompt(excerpt_context, kg_context)
        return self.llm.get_completion(text, context=system_prompt.strip(), use_cache=False)

    def _get_kg_query_context(self, entities, excerpts, relations):
        entity_csv = [["entity", "type", "description", "rank"]]
        for entity in entities:
            entity_csv.append([
                    entity["entity_name"],
                    entity.get("category", "UNKNOWN"),
                    entity.get("description", "UNKNOWN"),
                    entity["rank"],
                ])
        entity_context = list_of_list_to_csv(entity_csv)
        relation_csv = [["source", "target", "description", "keywords", "weight", "rank"]]
        for relation in relations:
            relation_csv.append([
                    relation["src_tgt"][0],
                    relation["src_tgt"][1],
                    relation["description"],
                    relation["keywords"],
                    relation["weight"],
                    relation["rank"],
                ])
        relations_context = list_of_list_to_csv(relation_csv)
        excerpt_csv = [["excerpt"]]
        for excerpt in excerpts:
            excerpt_csv.append([excerpt["excerpt"]])
        excerpt_context = list_of_list_to_csv(excerpt_csv)
        context = inspect.cleandoc(f"""
            -----Entities-----
            ```csv
            {entity_context}
            ```
            -----Relationships-----
            ```csv
            {relations_context}
            ```
            -----Excerpts-----
            ```csv
            {excerpt_context}
            ```
        """)
        logger.info(f"KG query context built with {len(entities)} entities, {len(relations)} relationships, "
                    f"and {len(excerpts)} excerpts.")
        return context

    def _get_high_level_dataset(self, keyword_data):
        hl_keywords = keyword_data.get("high_level_keywords", [])
        logger.info(f"Found {len(hl_keywords)} high-level keywords.")
        if len(hl_keywords):
            hl_embedding = self.llm.get_embedding(hl_keywords)
            hl_embedding_array = np.array(hl_embedding)
            hl_results = self.relationships_db.query(query=hl_embedding_array, top_k=25, better_than_threshold=0.02)
        hl_data = [self.graph.edges.get((r["__source__"], r["__target__"])) for r in hl_results]
        hl_degrees = [self.graph.degree(r["__source__"]) + self.graph.degree(r["__target__"]) for r in hl_results]
        hl_dataset = []
        for k, n, d in zip(hl_results, hl_data, hl_degrees):
            hl_dataset.append({"src_tgt": (k["__source__"], k["__target__"]), "rank": d, **n, })
        hl_dataset = sorted(hl_dataset, key=lambda x: (x["rank"], x["weight"]), reverse=True)
        hl_dataset = truncate_list_by_token_size(
            hl_dataset,
            get_text_for_row=lambda x: x["description"],
            max_token_size=4000,
        )
        hl_entity_excerpts = self._get_excerpts_for_relationships(hl_dataset)
        hl_entities = self._get_entities_from_relationships(hl_dataset)
        logger.info(f"High-level dataset: {len(hl_dataset)} relationships, {len(hl_entities)} entities extracted.")
        return hl_dataset, hl_entities, hl_entity_excerpts

    def _get_low_level_dataset(self, keyword_data):
        ll_keywords = keyword_data.get("low_level_keywords", [])
        logger.info(f"Found {len(ll_keywords)} low-level keywords.")
        if len(ll_keywords):
            ll_embedding = self.llm.get_embedding(ll_keywords)
            ll_embedding_array = np.array(ll_embedding)
            ll_results = self.entities_db.query(query=ll_embedding_array, top_k=25, better_than_threshold=0.02)
        ll_data = [self.graph.nodes.get(r["__entity_name__"]) for r in ll_results]
        ll_degrees = [self.graph.degree(r["__entity_name__"]) for r in ll_results]
        ll_dataset = [
            {**n, "entity_name": k["__entity_name__"], "rank": d}
            for k, n, d in zip(ll_results, ll_data, ll_degrees)
        ]
        ll_entity_excerpts = self._get_excerpts_for_entities(ll_dataset)
        ll_relations = self._get_relationships_from_entities(ll_dataset)
        logger.info(f"Low-level dataset: {len(ll_dataset)} entities, {len(ll_relations)} relationships extracted.")
        return ll_dataset, ll_entity_excerpts, ll_relations

    def _get_excerpts_for_entities(self, kg_dataset):
        excerpt_ids = [split_string_by_multi_markers(row["excerpt_id"], KG_SEP) for row in kg_dataset]
        all_edges = [self.graph.edges(row["entity_name"]) for row in kg_dataset]
        sibling_names = set()
        for edge in all_edges:
            if not edge:
                continue
            sibling_names.update([e[1] for e in edge])
        sibling_nodes = [self.graph.nodes.get(name) for name in list(sibling_names)]
        sibling_excerpt_lookup = {
            k: set(split_string_by_multi_markers(v["excerpt_id"], [KG_SEP]))
            for k, v in zip(sibling_names, sibling_nodes)
            if v is not None and "excerpt_id" in v
        }
        all_excerpt_data_lookup = {}
        for index, (excerpt_ids, edges) in enumerate(zip(excerpt_ids, all_edges)):
            for excerpt_id in excerpt_ids:
                if excerpt_id in all_excerpt_data_lookup:
                    continue
                relation_counts = 0
                if edges:
                    for edge in edges:
                        sibling_name = edge[1]
                        if sibling_name in sibling_excerpt_lookup and excerpt_id in sibling_excerpt_lookup[
                            sibling_name]:
                            relation_counts += 1
                excerpt_data = self.excerpt_kv.get_by_key(excerpt_id)
                if excerpt_data is not None and "excerpt" in excerpt_data:
                    all_excerpt_data_lookup[excerpt_id] = {
                        "data": excerpt_data,
                        "order": index,
                        "relation_counts": relation_counts,
                    }

        all_excerpts = [
            {"id": k, **v}
            for k, v in all_excerpt_data_lookup.items()
            if v is not None and v.get("data") is not None and "excerpt" in v["data"]
        ]

        if not all_excerpts:
            logger.warning("No valid excerpts found for low-level entities.")
            return []

        all_excerpts = sorted(all_excerpts, key=lambda x: (x["order"], -x["relation_counts"]))
        all_excerpts = [t["data"] for t in all_excerpts]

        all_excerpts = truncate_list_by_token_size(
            all_excerpts,
            get_text_for_row=lambda x: x["excerpt"],
            max_token_size=4000,
        )
        logger.info(f"Extracted {len(all_excerpts)} excerpts for low-level entities.")
        return all_excerpts

    def _get_relationships_from_entities(self, kg_dataset):
        node_edges_list = [self.graph.edges(row["entity_name"]) for row in kg_dataset]

        edges = []
        seen = set()

        for node_edges in node_edges_list:
            for edge in node_edges:
                sorted_edge = tuple(sorted(edge))
                if sorted_edge not in seen:
                    seen.add(sorted_edge)
                    edges.append(sorted_edge)

        edges_pack = [self.graph.edges.get((e[0], e[1])) for e in edges]
        edges_degree = [self.graph.degree(e[0]) + self.graph.degree(e[1]) for e in edges]

        edges_data = [
            {"src_tgt": k, "rank": d, **v}
            for k, v, d in zip(edges, edges_pack, edges_degree)
            if v is not None
        ]
        edges_data = sorted(edges_data, key=lambda x: (x["rank"], x["weight"]), reverse=True)
        edges_data = truncate_list_by_token_size(
            edges_data,
            get_text_for_row=lambda x: x["description"],
            max_token_size=1000,
        )
        logger.info(f"Extracted {len(edges_data)} relationships from low-level entities.")
        return edges_data

    def _get_excerpts_for_relationships(self, kg_dataset):
        excerpt_ids = [
            split_string_by_multi_markers(dp["excerpt_id"], [KG_SEP])
            for dp in kg_dataset
        ]

        all_excerpts_lookup = {}

        for index, excerpt_ids in enumerate(excerpt_ids):
            for excerpt_id in excerpt_ids:
                if excerpt_id not in all_excerpts_lookup:
                    all_excerpts_lookup[excerpt_id] = {
                        "data": self.excerpt_kv.get_by_key(excerpt_id),
                        "order": index,
                    }

        if any([v is None for v in all_excerpts_lookup.values()]):
            logger.warning("Text chunks are missing, maybe the storage is damaged")
        all_excerpts = [
            {"id": k, **v} for k, v in all_excerpts_lookup.items() if v is not None
        ]
        all_excerpts = sorted(all_excerpts, key=lambda x: x["order"])
        all_excerpts = [t["data"] for t in all_excerpts]

        all_excerpts = truncate_list_by_token_size(
            all_excerpts,
            get_text_for_row=lambda x: x["excerpt"],
            max_token_size=4000,
        )

        return all_excerpts

    def _get_entities_from_relationships(self, kg_dataset):
        entity_names = []
        seen = set()

        for e in kg_dataset:
            if e["src_tgt"][0] not in seen:
                entity_names.append(e["src_tgt"][0])
                seen.add(e["src_tgt"][0])
            if e["src_tgt"][1] not in seen:
                entity_names.append(e["src_tgt"][1])
                seen.add(e["src_tgt"][1])

        data = [self.graph.nodes.get(entity_name) for entity_name in entity_names]
        degrees = [self.graph.degree(entity_name) for entity_name in entity_names]

        # Todo: we need to filter out missing node data (ie no description) in case the node was added as an edge only
        data = [
            {**n, "entity_name": k, "rank": d}
            for k, n, d in zip(entity_names, data, degrees) if 'description' in n
        ]

        # Todo: figure out how we hit a bug here with missing description
        data = truncate_list_by_token_size(
            data,
            get_text_for_row=lambda x: x["description"],
            max_token_size=4000,
        )
        logger.info(f"Extracted {len(data)} entities from relationships.")
        return data


if __name__ == '__main__':
    delete_all_files(DATA_DIR)
    delete_all_files(LOG_DIR)

    smol_rag = SmolRag()

    smol_rag.import_documents()

    print(smol_rag.query("what do rabbits eat?"))  # Should answer
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.query("what do cats eat?"))  # Should reject
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.query("What's the subject matter we can discuss?"))  # Should answer

    print(smol_rag.hybrid_kg_query("what do rabbits eat?"))  # Should answer
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.hybrid_kg_query("what do cows eat?"))  # Should reject
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.hybrid_kg_query("What's the subject matter we can discuss?"))

    print(smol_rag.local_kg_query("what do rabbits eat?"))  # Should answer
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.local_kg_query("what do cows eat?"))  # Should reject
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.local_kg_query("What's the subject matter we can discuss?"))

    print(smol_rag.global_kg_query("what do rabbits eat?"))  # Should answer
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.global_kg_query("what do cows eat?"))  # Should reject
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.global_kg_query("What's the subject matter we can discuss?"))

    print(smol_rag.mix_query("what do rabbits eat?"))  # Should answer
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.mix_query("what do cows eat?"))  # Should reject
    print("=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print(smol_rag.mix_query("What's the subject matter we can discuss?"))

    # smol_rag.remove_document_by_id("doc_4c3f8100da0b90c1a44c94e6b4ffa041")

    # Todo: Use Jaal graph visualisation to inspect knowledge graph
