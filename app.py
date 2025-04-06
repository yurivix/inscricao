from flask import Flask, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from io import BytesIO
from PyPDF2 import PdfMerger
from PIL import Image
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DOCUMENTOS = [
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

    merger = PdfMerger()

    for file in arquivos:
        filename = secure_filename(file.filename)

        # Extrai o índice do nome do arquivo (esperado: "16_Nome do Documento.pdf")
        try:
            index = int(filename.split("_")[0])
        except:
            continue

        # Pula o reservista se o candidato marcou como "não possuo"
        if index == 16 and nao_possui_reservista:
            continue

        # Salva temporariamente
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Converte imagem para PDF se necessário
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(file_path).convert("RGB")
            image_pdf_path = file_path + ".pdf"
            image.save(image_pdf_path)
            merger.append(image_pdf_path)
            os.remove(image_pdf_path)
        else:
            merger.append(file_path)

        os.remove(file_path)

    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="Inscricao_OAB_ES.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
