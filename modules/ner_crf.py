import re
from pathlib import Path

import pycrfsuite

MODEL_PATH = Path(__file__).parent / "ner_crf_model.crfsuite"

_LABEL_ES = {
    "PER": "Persona",
    "ORG": "Organización",
    "LOC": "Lugar",
}

_SENT_RE = re.compile(r'(?<=[.!?])\s+')


def tokenize(text: str) -> list[list[str]]:
    sentences = _SENT_RE.split(text.strip())
    return [s.split() for s in sentences if s.strip()]


def _word_features(sentence: list[str], i: int) -> list[str]:
    w = sentence[i]
    feats = [
        "bias",
        f"word.lower={w.lower()}",
        f"word[-3:]={w[-3:]}",
        f"word[-2:]={w[-2:]}",
        f"word[:3]={w[:3]}",
        f"word[:2]={w[:2]}",
        f"word.isupper={w.isupper()}",
        f"word.istitle={w.istitle()}",
        f"word.isdigit={w.isdigit()}",
        f"word.has_hyphen={'-' in w}",
        f"word.has_dot={'.' in w}",
    ]
    if i > 0:
        p1 = sentence[i - 1]
        feats += [
            f"-1:word.lower={p1.lower()}",
            f"-1:word.istitle={p1.istitle()}",
            f"-1:word.isupper={p1.isupper()}",
            f"-1:word[-2:]={p1[-2:]}",
        ]
        if i > 1:
            p2 = sentence[i - 2]
            feats += [
                f"-2:word.lower={p2.lower()}",
                f"-2:word.istitle={p2.istitle()}",
            ]
    else:
        feats.append("BOS")

    if i < len(sentence) - 1:
        n1 = sentence[i + 1]
        feats += [
            f"+1:word.lower={n1.lower()}",
            f"+1:word.istitle={n1.istitle()}",
            f"+1:word.isupper={n1.isupper()}",
            f"+1:word[-2:]={n1[-2:]}",
        ]
        if i < len(sentence) - 2:
            n2 = sentence[i + 2]
            feats += [
                f"+2:word.lower={n2.lower()}",
                f"+2:word.istitle={n2.istitle()}",
            ]
    else:
        feats.append("EOS")

    return feats


def _sentence_features(sentence: list[str]) -> list[list[str]]:
    return [_word_features(sentence, i) for i in range(len(sentence))]


_MAX_SPAN = 5
_STOP_CHARS = re.compile(r'[.,;:()\[\]!?]')
_STOPWORDS = {
    'de', 'del', 'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'con', 'en', 'por', 'para', 'que', 'y', 'o', 'a', 'se', 'no', 'al',
    'lo', 'le', 'les', 'su', 'sus', 'este', 'esta', 'estos', 'estas',
    'es', 'son', 'fue', 'era', 'hay', 'como', 'más', 'mas', 'si',
}

_ENTITY_BLOCKLIST = {
    'tarjeta', 'cédula', 'cedula', 'número', 'numero', 'documento',
    'identificacion', 'identificación', 'identidad', 'no', 'nro',
    'expedido', 'expide', 'dado', 'certifica', 'certific',
    'realizo', 'realizó', 'aprobo', 'aprobó', 'con', 'una', 'el', 'la',
}


def _is_proper(word: str) -> bool:
    return word.istitle() or word.isupper()


def _clean_span(words: list[str]) -> list[str]:
    while words and words[-1].lower() in _STOPWORDS:
        words = words[:-1]
    while words and words[0].lower() in _STOPWORDS:
        words = words[1:]
    if not words:
        return []
    if words[0].lower() in _ENTITY_BLOCKLIST:
        return []
    proper = sum(1 for w in words if _is_proper(w))
    if proper / len(words) < 0.5:
        return []
    return words


def _flush(entities: dict, current_type: str | None, current_words: list[str]) -> None:
    if current_words and current_type:
        label = _LABEL_ES.get(current_type)
        cleaned = _clean_span(list(current_words))
        if label and cleaned:
            entities.setdefault(label, []).append(" ".join(cleaned))


def _bio_to_entities(tokens: list[str], tags: list[str]) -> dict[str, list[str]]:
    entities: dict[str, list[str]] = {}
    current_type: str | None = None
    current_words: list[str] = []

    for token, tag in zip(tokens, tags):
        if _STOP_CHARS.search(token):
            _flush(entities, current_type, current_words)
            current_type = None
            current_words = []
            continue

        if tag.startswith("B-"):
            _flush(entities, current_type, current_words)
            current_type = tag[2:]
            current_words = [token]
        elif tag.startswith("I-") and current_type == tag[2:]:
            current_words.append(token)
            if len(current_words) >= _MAX_SPAN:
                _flush(entities, current_type, current_words)
                current_type = None
                current_words = []
        else:
            _flush(entities, current_type, current_words)
            current_type = None
            current_words = []

    _flush(entities, current_type, current_words)
    return entities


def train_and_save() -> None:
    import random
    from datasets import load_dataset
    from modules.cert_data_generator import generate as gen_cert

    trainer = pycrfsuite.Trainer()
    trainer.set_params({
        "c1": 0.05,
        "c2": 0.05,
        "max_iterations": 150,
        "feature.possible_transitions": True,
    })


    print("Generando datos sintéticos de certificados…")
    cert_data = gen_cert(1200)
    for tokens, labels in cert_data:
        trainer.append(_sentence_features(tokens), labels)


    print("Cargando WikiANN (español)…")
    ds = load_dataset("wikiann", "es")
    tag_names = ds["train"].features["ner_tags"].feature.names
    wikiann = list(ds["train"])
    random.seed(0)
    random.shuffle(wikiann)
    print("Añadiendo 5 000 ejemplos de WikiANN…")
    for ex in wikiann[:5000]:
        tokens = ex["tokens"]
        labels = [tag_names[t] for t in ex["ner_tags"]]
        trainer.append(_sentence_features(tokens), labels)

    print("Entrenando CRF…")
    trainer.train(str(MODEL_PATH))
    print(f"Modelo guardado en {MODEL_PATH}")


_tagger: pycrfsuite.Tagger | None = None


def _get_tagger() -> pycrfsuite.Tagger:
    global _tagger
    if _tagger is None:
        if not MODEL_PATH.exists():
            train_and_save()
        _tagger = pycrfsuite.Tagger()
        _tagger.open(str(MODEL_PATH))
    return _tagger


def extract_entities_crf(text: str) -> dict[str, list[str]]:
    tagger = _get_tagger()
    combined: dict[str, list[str]] = {}

    for sentence in tokenize(text):
        if not sentence:
            continue
        tags = tagger.tag(_sentence_features(sentence))
        for label, words in _bio_to_entities(sentence, tags).items():
            combined.setdefault(label, []).extend(words)

    return {k: list(dict.fromkeys(v)) for k, v in combined.items()}
