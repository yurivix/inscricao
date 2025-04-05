from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

documentos = [
    "requerimento_oab_es",
    "requerimento_cf",
    "historico",
    "certidao_federal",
    "cert_aprovacao",
    "cert_crime",
    "cert_civel",
    "cert_familia",
    "cert_crime_fed2",
    "cert_civel_fed2",
    "declaracao_atividade",
    "declaracao_pj",
    "certidao_eleitoral",
    "rg",
    "cpf",
    "titulo",
    "reservista",
    "residencia",
    "responsabilidade"
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            merger = PdfMerger()
            for doc in documentos:
                file = request.files.get(doc)
                if file and file.filename.endswith(".pdf"):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    merger.append(filepath)
            output_path = os.path.join(UPLOAD_FOLDER, "inscricao_final.pdf")
            merger.write(output_path)
            merger.close()
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"Erro ao processar: {str(e)}", 500
    return render_template("index.html", documentos=documentos)

if __name__ == "__main__":
    app.run(debug=True)
