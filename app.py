from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from io import BytesIO
from PyPDF2 import PdfMerger
from PIL import Image
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
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
    return render_template("index.html", documentos=documentos)

@app.route("/gerar_pdf", methods=["POST"])
def gerar_pdf():
    arquivos = request.files.getlist("arquivos")
    nomes = request.form.getlist("nomes[]")

    if not arquivos or len(arquivos) != len(nomes):
        return "Por favor, envie todos os documentos obrigatórios.", 400

    merger = PdfMerger()

    for file, nome in zip(arquivos, nomes):
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext == ".pdf":
            merger.append(file)
        elif file_ext in [".jpg", ".jpeg", ".png"]:
            image = Image.open(file.stream).convert("RGB")
            temp_pdf = BytesIO()
            image.save(temp_pdf, format="PDF")
            temp_pdf.seek(0)
            merger.append(temp_pdf)
        else:
            return f"Formato de arquivo não suportado: {filename}", 400

    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Inscricao_OAB_ES.pdf",
        mimetype="application/pdf"
    )
