from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PyPDF2 import PdfMerger
from werkzeug.utils import secure_filename
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return "Servidor está rodando. Use o frontend React para enviar os arquivos."

@app.route("/gerar_pdf", methods=["POST"])
def gerar_pdf():
    arquivos = request.files.getlist("arquivos")
    nao_possui_reservista = request.form.get("nao_possui_reservista") == "true"

    if not arquivos and not nao_possui_reservista:
        return jsonify({"erro": "Nenhum arquivo enviado"}), 400

    arquivos_ordenados = sorted(arquivos, key=lambda f: int(f.filename.split("_")[0]))

    merger = PdfMerger()

    for arquivo in arquivos_ordenados:
        filename = secure_filename(arquivo.filename)
        caminho = os.path.join(UPLOAD_FOLDER, filename)
        arquivo.save(caminho)
        merger.append(caminho)

    buffer = BytesIO()
    merger.write(buffer)
    merger.close()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Inscricao_OAB_ES.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)
