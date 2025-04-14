import re

from nltk import sent_tokenize, download, tokenize


def preserve_markdown_code_excerpts(content, n=2000, overlap=None):
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
    download('punkt')

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


def naive_overlap_excerpts(content, n=2000, overlap=200):
    excerpts = []
    step = n - overlap
    for i in range(0, len(content), step):
        excerpts.append(content[i:i + n])
    return excerpts


def word_boundary_overlap_excerpts(content, n=2000, overlap=200):
    """
    Break content into excerpts of ~n characters with overlap, making sure not to split words.

    Parameters:
        content (str): The complete text.
        n (int): Approximate target length for each excerpt.
        overlap (int): Number of overlapping characters between consecutive excerpts.

    Returns:
        list of str: Excerpts that do not split words.
    """
    tokenizer = tokenize.TreebankWordTokenizer()
    token_spans = list(tokenizer.span_tokenize(content))

    excerpts = []
    text_length = len(content)
    start = 0

    while start < text_length:
        target_end = start + n
        if target_end >= text_length:
            excerpts.append(content[start:])
            break

        boundary = None
        for span in token_spans:
            if span[0] < start:
                continue
            if span[1] <= target_end:
                boundary = span[1]
            else:
                break

        if boundary is None:
            boundary = target_end

        excerpts.append(content[start:boundary])

        new_start = boundary - overlap

        if new_start <= start:
            new_start = boundary

        start = new_start

    return excerpts