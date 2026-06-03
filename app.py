import base64

from flask import Flask, jsonify, render_template, request
from PIL import Image

from modules.generator import PoetryGenerator
from modules.nlp_processor import extract_entities, summarize, translate
from modules.ocr import clean_text, extract_text, extract_text_from_pdf
from modules.tts import text_to_audio

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024 

_gen = PoetryGenerator()
_load_error: str = ""
try:
    _gen.load()
    print(f"[generator] Model loaded — {len(_gen.list_authors())} authors available.")
except Exception as e:
    import traceback
    _load_error = traceback.format_exc()
    print(f"[generator] Failed to load model:\n{_load_error}")


def _audio_b64(text: str, lang: str = "es") -> str:
    buf = text_to_audio(text, lang=lang)
    return base64.b64encode(buf.read()).decode("utf-8")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No se recibió ningún archivo."}), 400

    lang = request.form.get("lang", "spa")
    num_sentences = int(request.form.get("num_sentences", 3))
    do_translate = request.form.get("translate") == "1"
    is_pdf = file.filename.lower().endswith(".pdf")

    try:
        if is_pdf:
            raw_text, total_pages = extract_text_from_pdf(file.read(), lang=lang)
            source_info = f"PDF · {total_pages} página(s)"
        else:
            image = Image.open(file)
            raw_text = extract_text(image, lang=lang)
            source_info = "Imagen"
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500

    cleaned = clean_text(raw_text)
    if not cleaned:
        return jsonify({"error": "No se detectó texto legible. Prueba con un archivo más claro."}), 400

    entities = extract_entities(cleaned)
    summary = summarize(cleaned, num_sentences=num_sentences)
    translated_text = translate(cleaned) if do_translate else ""

    narration = ""
    if entities:
        narration = "Información encontrada. " + ". ".join(
            f"{cat}: {', '.join(items)}" for cat, items in entities.items()
        )

    try:
        audio_text = _audio_b64(cleaned)
        audio_entities = _audio_b64(narration) if narration else ""
        audio_summary = _audio_b64(summary)
    except Exception as exc:
        return jsonify({"error": f"Error al generar audio: {exc}"}), 500

    return jsonify({
        "source_info": source_info,
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "entities": entities,
        "summary": summary,
        "translated_text": translated_text,
        "audio_text": audio_text,
        "audio_entities": audio_entities,
        "audio_summary": audio_summary,
    })


@app.route("/authors")
def get_authors():
    return jsonify({
        "authors": _gen.list_authors() if _gen.is_ready else [],
        "ready": _gen.is_ready,
        "load_error": _load_error,
    })


@app.route("/generate", methods=["POST"])
def generate():
    if not _gen.is_ready:
        return jsonify({
            "error": "El modelo no está disponible. Ejecuta `python train.py` y reinicia la app."
        }), 503

    data = request.get_json(force=True, silent=True) or {}
    speech = data.get("speech", "")
    author = data.get("author") or _gen.find_author(speech)

    if not author:
        sample = ", ".join(_gen.list_authors()[:5])
        return jsonify({
            "error": f"No se encontró el autor en tu solicitud. Ejemplos: {sample}…"
        }), 400

    try:
        temperature = max(0.05, min(float(data.get("temperature", 0.5)), 0.8))
        poem = _gen.generate_poem(author=author, num_chars=300, temperature=temperature)
    except Exception as exc:
        import traceback; traceback.print_exc()
        return jsonify({"error": f"Error al generar poema: {exc}"}), 500

    try:
        audio = _audio_b64(poem)
    except Exception as exc:
        import traceback; traceback.print_exc()
        return jsonify({"author": author, "poem": poem, "audio": ""})

    return jsonify({"author": author, "poem": poem, "audio": audio})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
