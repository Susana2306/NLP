import re

from transformers import pipeline

_ner = pipeline(
    "ner",
    model="mrm8488/bert-spanish-cased-finetuned-ner",
    aggregation_strategy="simple",
)

_summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
)

_LABEL_ES = {
    "PER":  "Persona",
    "ORG":  "Organización",
    "LOC":  "Lugar",
}

_DATE_RE = re.compile(
    r"\b\d{1,2}\s+de\s+\w+|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    re.IGNORECASE,
)
_TIME_RE = re.compile(
    r"\b\d{1,2}:\d{2}(?:\s*[ap]\.?m\.?)?|\b\d{1,2}\s*[ap]\.?m\.",
    re.IGNORECASE,
)


_NER_MAX_WORDS   = 400

_SUMM_MAX_WORDS  = 700

_SUMM_MIN_WORDS  = 40


def extract_entities(text: str) -> dict[str, list[str]]:

    words = text.split()
    chunk = " ".join(words[:_NER_MAX_WORDS]) if len(words) > _NER_MAX_WORDS else text

    entities: dict[str, list[str]] = {}

    for ent in _ner(chunk):
        label = _LABEL_ES.get(ent["entity_group"])
        word  = ent["word"].replace("##", "").strip()
        if label and word:
            entities.setdefault(label, []).append(word)

    for match in _DATE_RE.findall(text):
        entities.setdefault("Fecha", []).append(match)
    for match in _TIME_RE.findall(text):
        entities.setdefault("Hora", []).append(match)

    return {k: list(dict.fromkeys(v)) for k, v in entities.items()}


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
