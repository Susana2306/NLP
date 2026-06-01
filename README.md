# Asistente Visual — NLP para Accesibilidad

Asistente que ayuda a personas con discapacidad visual a leer documentos mediante OCR, NLP y síntesis de voz.

**Flujo:** `Imagen → OCR → Limpieza → NLP (NER + Resumen) → Voz`

---

## Estructura del proyecto

```
NLP/
├── app.py                  # Interfaz Streamlit (punto de entrada)
├── requirements.txt
├── modules/
│   ├── ocr.py              # Extracción de texto con Tesseract
│   ├── nlp_processor.py    # NER + resumen extractivo (spaCy)
│   └── tts.py              # Texto a voz (gTTS)
└── README.md
```

---

## Instalación

### 1. Tesseract OCR (requerido)

Descarga e instala desde:  
<https://github.com/UB-Mannheim/tesseract/wiki>

Durante la instalación, marca **Spanish** en los paquetes de idioma.

Ruta de instalación por defecto en Windows:  
`C:\Program Files\Tesseract-OCR\tesseract.exe`

Si instalas en otra ruta, edita la línea en [modules/ocr.py](modules/ocr.py):
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\ruta\a\tesseract.exe"
```

### 2. Dependencias Python

```bash
pip install -r requirements.txt
```

### 3. Modelo de spaCy en español

```bash
python -m spacy download es_core_news_sm
```

---

## Ejecución

```bash
streamlit run app.py
```

Abre el navegador en `http://localhost:8501`.

---

## Funcionalidades NLP

| Técnica | Módulo | Descripción |
|---|---|---|
| Limpieza de texto | `ocr.py` | Normalización de espacios y caracteres |
| NER (Reconocimiento de Entidades) | `nlp_processor.py` | Detecta personas, lugares, organizaciones |
| Detección de fechas/horas | `nlp_processor.py` | Regex + spaCy para horarios y fechas |
| Resumen extractivo | `nlp_processor.py` | Frecuencia TF para seleccionar oraciones clave |
| Síntesis de voz | `tts.py` | Convierte cualquier resultado a audio MP3 |

---

## Notas

- `gTTS` requiere conexión a internet para generar el audio.
- El modelo `es_core_news_sm` pesa ~12 MB y se descarga una sola vez.
- Para imágenes con texto pequeño o borroso, mejores resultados con imágenes de alta resolución.
