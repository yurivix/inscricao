from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from PIL import Image
import os
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

documentos = [
    "Requerimento de inscrição da OAB-ES",
    "Requerimento de inscrição no Conselho Federal da OAB",
    "Histórico Escolar com diploma ou colação de grau (autenticado)",
    "Certidão Negativa Cartório Distribuidor Justiça Federal",
    "Certificado de Aprovação em Exame de Ordem",
    "Certidão Negativa - Cartório Distribuidor do Crime",
    "Certidão Negativa - Cartório Distribuidor do Cível",
    "Certidão Negativa - Cartório Distribuidor da Família",
    "Certidão Negativa - Cartório Distribuidor do Crime Federal 2ª Região",
    "Certidão Negativa - Cartório Distribuidor Cível Federal 2ª Região",
    "Declaração de atividade, função ou cargo (com ou sem atividade)",
    "Declaração de atividade da pessoa jurídica vinculada",
    "Certidão de quitação eleitoral",
    "RG",
    "CPF",
    "Título de Eleitor (frente/verso)",
    "Certificado de Reservista (para homens)",
    "Comprovante de residência atualizado",
    "Declaração de responsabilidade das informações"
]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", documentos=documentos)

@app.route("/gerar_pdf", methods=["POST"])
def gerar_pdf():
    merger = PdfMerger()
    for i, doc_nome in enumerate(documentos):
        # Pular Certificado de Reservista se marcado como "não possui"
        if i == 16 and request.form.get("nao_possui_reservista") == "true":
            continue

        file = request.files.get(f"arquivo{i}")
        if not file:
            continue

        filename = secure_filename(f"{i:02d}_{doc_nome}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file.stream).convert("RGB")
            image.save(filepath, "PDF")
        elif file.filename.lower().endswith(".pdf"):
            file.save(filepath)
        else:
            continue

        merger.append(filepath)

    output_pdf = os.path.join(UPLOAD_FOLDER, "Inscricao_OAB_ES_Final.pdf")
    merger.write(output_pdf)
    merger.close()

    return send_file(output_pdf, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
