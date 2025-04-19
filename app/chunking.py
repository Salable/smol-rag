from nltk import tokenize
from nltk import sent_tokenize, download
import re

# download('punkt')

import re
from typing import List, Optional
from nltk.tokenize import sent_tokenize


def preserve_markdown_code_excerpts(
    content: str,
    n: int = 2000,
    overlap: Optional[int] = None,
) -> List[str]:
    """Split *content* into excerpts of at most *n* characters without breaking
    fenced code blocks (``` … ```).

    The algorithm keeps entire code blocks intact. If a code block plus its
    neighbouring paragraph both fit within *n*, they are merged so readers see
    the context together.

    Plain‑text paragraphs that still exceed *n* are further split into
    sentences using *nltk.sent_tokenize*.

    Parameters
    ----------
    content:
        The complete Markdown document.
    n:
        Maximum length of a single excerpt (characters). Default is ``2000``.
    overlap:
        If given (>0), the last *overlap* characters of each excerpt are
        prepended to the next excerpt. Use this to maintain context across
        boundaries. ``None`` → no overlap.

    Returns
    -------
    list[str]
        Ordered list of excerpts.
    """

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _flush(buf: list[str]) -> None:
        """Append the current buffer to *excerpts* if it contains anything."""
        if buf:
            txt = "\n\n".join(buf).strip()
            if txt:
                excerpts.append(txt)
            buf.clear()

    def _append_text(chunk: str) -> None:
        """Append normal Markdown *chunk* into *buffer*, respecting *n*."""
        paragraphs = re.split(r"\n{2,}", chunk.strip())
        for para in paragraphs:
            if not para:
                continue

            # If paragraph fits into the current buffer, add it whole
            if buffer and len("\n\n".join(buffer) + "\n\n" + para) <= n:
                buffer.append(para)
                continue

            # Otherwise, flush the current buffer and handle the paragraph alone
            if buffer:
                _flush(buffer)

            if len(para) <= n:
                buffer.append(para)
                continue

            # Paragraph still too big — split by sentences
            for sentence in sent_tokenize(para):
                sentence = sentence.strip()
                if not sentence:
                    continue

                # Extremely long sentences are hard‑split at *n*
                if len(sentence) > n:
                    for i in range(0, len(sentence), n):
                        excerpts.append(sentence[i : i + n])
                    continue

                if buffer and len("\n\n".join(buffer) + " " + sentence) > n:
                    _flush(buffer)
                buffer.append(sentence)

    # ---------------------------------------------------------------------
    # Main processing loop
    # ---------------------------------------------------------------------
    code_pattern = re.compile(r"(```.*?```)", re.DOTALL)
    parts = code_pattern.split(content)

    excerpts: list[str] = []
    buffer: list[str] = []

    for part in parts:
        if not part.strip():
            continue

        # --- Code block ---------------------------------------------------
        if part.startswith("```") and part.endswith("```"):
            code_block = part.strip()

            # Attempt to keep code with the current buffer
            if buffer and len("\n\n".join(buffer) + "\n\n" + code_block) <= n:
                buffer.append(code_block)
            else:
                _flush(buffer)

                # Code block longer than *n* → hard split
                if len(code_block) > n:
                    for i in range(0, len(code_block), n):
                        excerpts.append(code_block[i : i + n])
                else:
                    excerpts.append(code_block)
            continue

        # --- Regular Markdown text ---------------------------------------
        _append_text(part)

    _flush(buffer)

    # ---------------------------------------------------------------------
    # Optional overlap handling
    # ---------------------------------------------------------------------
    if overlap and overlap > 0 and len(excerpts) > 1:
        overlapped: list[str] = []
        for i, ex in enumerate(excerpts):
            if i > 0:
                ex = excerpts[i - 1][-overlap:] + ex
            overlapped.append(ex)
        return overlapped

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
