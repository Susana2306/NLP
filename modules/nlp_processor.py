import re

from transformers import pipeline

from modules.ner_crf import extract_entities_crf

_summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
)

_translator = None

def _get_translator():
    global _translator
    if _translator is None:
        _translator = pipeline(
            "translation",
            model="Helsinki-NLP/opus-mt-es-en",
        )
    return _translator

_DATE_RE = re.compile(
    r"\b\d{1,2}\s+de\s+\w+|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    re.IGNORECASE,
)
_TIME_RE = re.compile(
    r"\b\d{1,2}:\d{2}(?:\s*[ap]\.?m\.?)?|\b\d{1,2}\s*[ap]\.?m\.",
    re.IGNORECASE,
)

_SUMM_MAX_WORDS  = 700
_SUMM_MIN_WORDS  = 40


def extract_entities(text: str) -> dict[str, list[str]]:
    entities = extract_entities_crf(text)

    for match in _DATE_RE.findall(text):
        entities.setdefault("Fecha", []).append(match)
    for match in _TIME_RE.findall(text):
        entities.setdefault("Hora", []).append(match)

    return {k: list(dict.fromkeys(v)) for k, v in entities.items()}


_TRANS_MAX_WORDS = 400


def translate(text: str) -> str:
    translator = _get_translator()
    words = text.split()

    if not words:
        return text

    chunks = [
        " ".join(words[i : i + _TRANS_MAX_WORDS])
        for i in range(0, len(words), _TRANS_MAX_WORDS)
    ]

    translated_chunks = []
    for chunk in chunks:
        try:
            result = translator(chunk, max_length=512)
            translated_chunks.append(result[0]["translation_text"])
        except Exception:
            translated_chunks.append(chunk)

    return " ".join(translated_chunks)


def summarize(text: str, num_sentences: int = 3) -> str:

    words = text.split()

    if len(words) < _SUMM_MIN_WORDS:
        return text

    chunk = " ".join(words[:_SUMM_MAX_WORDS]) if len(words) > _SUMM_MAX_WORDS else text

    max_out = max(60, num_sentences * 50)
    min_out = max(20, num_sentences * 20)

    try:
        result = _summarizer(
            chunk,
            max_length=max_out,
            min_length=min_out,
            do_sample=False,
        )
        return result[0]["summary_text"]
    except Exception:
        return text
