import os
import shutil
import subprocess
import tempfile

from flask import (Flask, after_this_request, jsonify, request, send_file,
                   send_from_directory)
from pdf2docx import Converter

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024


@app.get("/")
def home():
    return send_from_directory("static", "index.html")


@app.errorhandler(413)
def too_big(_):
    return jsonify(error="الملف أكبر من 30 ميجا"), 413


@app.post("/convert")
def convert():
    f = request.files.get("file")
    if not f or not f.filename.lower().endswith(".pdf"):
        return jsonify(error="ارفع ملف PDF"), 400

    work = tempfile.mkdtemp()

    @after_this_request
    def cleanup(resp):
        shutil.rmtree(work, ignore_errors=True)
        return resp

    src = os.path.join(work, "in.pdf")
    out = os.path.join(work, "out.docx")
    f.save(src)

    try:
        if request.form.get("ocr") == "1":
            ocr_pdf = os.path.join(work, "ocr.pdf")
            subprocess.run(
                ["ocrmypdf", "--skip-text", "-l", "ara+eng", src, ocr_pdf],
                check=True, timeout=280, capture_output=True)
            src = ocr_pdf
        cv = Converter(src)
        cv.convert(out)
        cv.close()
    except subprocess.TimeoutExpired:
        return jsonify(error="العملية أخذت وقت طويل. جرّب ملف أصغر"), 504
    except Exception as e:
        return jsonify(error=f"فشل التحويل: {e}"), 500

    name = os.path.splitext(os.path.basename(f.filename))[0] + ".docx"
    return send_file(out, as_attachment=True, download_name=name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
