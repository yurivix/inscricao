from flask import Flask, render_template, request, redirect, send_file, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from PIL import Image
import os
import io

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
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

@app.route("/")
def index():
    arquivos = os.listdir(UPLOAD_FOLDER)
    arquivos_enviados = [nome for nome in arquivos if nome.split("_")[0].isdigit()]
    return render_template("index.html", documentos=documentos, arquivos=arquivos_enviados)

@app.route("/upload", methods=["POST"])
def upload():
    index = request.form.get("index")
    file = request.files.get("arquivo")
    if not index:
        return redirect(url_for("index"))

    # Se não enviou arquivo e marcou "não possuo"
    if not file or file.filename == "":
        if request.form.get("nao_possui") == "on":
            placeholder_path = os.path.join(UPLOAD_FOLDER, f"{index}_nao_possui.txt")
            with open(placeholder_path, "w") as f:
                f.write("Documento não apresentado.")
        return redirect(url_for("index"))

    filename = f"{index}_" + secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    return redirect(url_for("index"))

@app.route("/gerar_pdf", methods=["POST"])
def gerar_pdf():
    arquivos = sorted(os.listdir(UPLOAD_FOLDER), key=lambda x: int(x.split("_")[0]))
    merger = PdfMerger()

    for nome in arquivos:
        path = os.path.join(UPLOAD_FOLDER, nome)
        if nome.endswith(".pdf"):
            merger.append(path)
        elif nome.lower().endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(path).convert("RGB")
            temp_pdf = io.BytesIO()
            image.save(temp_pdf, format="PDF")
            temp_pdf.seek(0)
            merger.append(temp_pdf)
        else:
            continue  # ignora arquivos não suportados

    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return send_file(output, download_name="Inscricao_OAB_ES.pdf", as_attachment=True)

@app.route("/limpar", methods=["POST"])
def limpar():
    for f in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, f))
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
