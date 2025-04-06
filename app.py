from flask import Flask, request, send_file
from flask_cors import CORS
from PyPDF2 import PdfMerger
from PIL import Image
import io

app = Flask(__name__)
CORS(app)  # permite requisições do frontend React

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

@app.route("/gerar_pdf", methods=["POST"])
def gerar_pdf():
    arquivos = request.files.getlist("arquivos")
    nao_possui_reservista = request.form.get("nao_possui_reservista") == "true"

    arquivos_ordenados = [None] * len(documentos)

    # Atribui arquivos à posição correta baseado no nome enviado (index_nome)
    for arquivo in arquivos:
        filename = arquivo.filename
        if "_" in filename:
            index_str, _ = filename.split("_", 1)
            try:
                index = int(index_str)
                arquivos_ordenados[index] = arquivo
            except ValueError:
                continue

    # Se o candidato marcou "Não possuo", pulamos o arquivo 16 (reservista)
    if nao_possui_reservista:
        arquivos_ordenados[16] = None

    merger = PdfMerger()

    for arquivo in arquivos_ordenados:
        if not arquivo:
            continue

        filename = arquivo.filename.lower()

        if filename.endswith((".jpg", ".jpeg", ".png")):
            img = Image.open(arquivo.stream).convert("RGB")
            img_io = io.BytesIO()
            img.save(img_io, format="PDF")
            img_io.seek(0)
            merger.append(img_io)
        elif filename.endswith(".pdf"):
            merger.append(arquivo.stream)

    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Inscricao_OAB_ES.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)
