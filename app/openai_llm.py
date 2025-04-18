import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.definitions import QUERY_CACHE_KV_PATH, EMBEDDING_CACHE_KV_PATH, COMPLETION_MODEL, EMBEDDING_MODEL, \
    OPENAI_API_KEY
from app.kv_store import JsonKvStore
from app.logger import logger
from app.utilities import make_hash

load_dotenv()


class OpenAiLlm:
    def __init__(self, completion_model=None, embedding_model=None, query_cache_kv=None, embedding_cache_kv=None, openai_api_key=None) -> None:
        """
        Initializes the OpenAiLlm instance with specified models and caches.
        """
        self.client = openai_api_key or OpenAI(api_key=OPENAI_API_KEY)
        self.query_cache_kv = query_cache_kv or JsonKvStore(QUERY_CACHE_KV_PATH)
        self.embedding_cache_kv = embedding_cache_kv or JsonKvStore(EMBEDDING_CACHE_KV_PATH)
        self.completion_model = completion_model or COMPLETION_MODEL
        self.embedding_model = embedding_model or EMBEDDING_MODEL

    def get_completion(self, query: str, model: Optional[str] = None, context: str = "", use_cache: bool = True) -> str:
        """
        Gets a completion from the API with optional caching.

        :param query: User's query string.
        :param model: The model to use; if None, use self.completion_model.
        :param context: Optional context or instructions.
        :param use_cache: Whether to use the cached results.
        :return: The completion result.
        """
        model = model or self.completion_model
        query_hash = make_hash(query, 'qry-')
        if use_cache and self.query_cache_kv.has(query_hash):
            logger.info("Query cache hit")
            return self.query_cache_kv.get_by_key(query_hash)["result"]

        logger.info("New query")
        system_message = [{"role": "system", "content": context}] if context else []
        messages: List[Dict[str, str]] = [{"role": "user", "content": query}]

        try:
            response = self.client.chat.completions.create(
                model=model,
                store=True,
                messages=system_message + messages
            )
            result = response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting completion: {e}")
            raise

        self.query_cache_kv.add(query_hash, {"query": query, "result": result})
        self.query_cache_kv.save()

        return result

    # Todo: add caching for chat completion
    def get_chat_completion(self, query: str, model: Optional[str] = None, context: str = "",
                            chat_history: List[Dict[str, str]] = []) -> List[Dict[str, str]]:
        """
        Gets a chat completion by providing the chat history and query.

        :param query: New query to send.
        :param model: The model to use; if None, use self.completion_model.
        :param context: Optional system context instructions.
        :param chat_history: List of previous chat messages.
        :return: Updated chat history including the assistant's response.
        """
        model = model or self.completion_model
        system_message = [{"role": "system", "content": context}] if context else []
        messages = chat_history + [{"role": "user", "content": query}]

        try:
            response = self.client.chat.completions.create(
                model=model,
                store=True,
                messages=system_message + messages
            )
            assistant_reply = response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise

        messages.append({"role": "assistant", "content": assistant_reply})
        return messages

    def get_embedding(self, content: Any, model: Optional[str] = None) -> List[float]:
        """
        Gets the embedding for the provided content using the specified model.

        :param content: The text or data to be embedded.
        :param model: The model to use; if None, use self.embedding_model.
        :return: The embedding vector.
        """
        model = model or self.embedding_model
        content_hash = make_hash(str(content), 'emb-')

        if self.embedding_cache_kv.has(content_hash):
            logger.info("Embedding cache hit")
            embedding = self.embedding_cache_kv.get_by_key(content_hash)
        else:
            logger.info("New embedding")
            try:
                response = self.client.embeddings.create(
                    model=model,
                    input=content,
                )
                embedding = response.data[0].embedding
            except Exception as e:
                logger.error(f"Error getting embedding: {e}")
                raise
            self.embedding_cache_kv.add(content_hash, embedding)
            self.embedding_cache_kv.save()

        return embedding
