import base64

from flask import Flask, jsonify, render_template, request
from PIL import Image

from modules.nlp_processor import extract_entities, summarize, translate
from modules.ocr import clean_text, extract_text, extract_text_from_pdf
from modules.tts import text_to_audio

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB


def _audio_b64(text: str) -> str:
    buf = text_to_audio(text)
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


if __name__ == "__main__":
    app.run(debug=True)
