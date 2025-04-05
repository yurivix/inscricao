from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfMerger
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

documentos = [
    "requerimento_oab_es", "requerimento_cf", "historico", "certidao_federal",
    "cert_aprovacao", "cert_crime", "cert_civel", "cert_familia",
    "cert_crime_fed2", "cert_civel_fed2", "declaracao_atividade",
    "declaracao_pj", "certidao_eleitoral", "rg", "cpf", "titulo",
    "reservista", "residencia", "responsabilidade"
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        merger = PdfMerger()
        for doc in documentos:
            file = request.files.get(doc)
            if file:
                path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                file.save(path)
                merger.append(path)
        output = os.path.join(UPLOAD_FOLDER, "inscricao_ordenada.pdf")
        merger.write(output)
        merger.close()
        return send_file(output, as_attachment=True)
    return render_template("index.html", documentos=documentos)
