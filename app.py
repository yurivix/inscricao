from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from fpdf import FPDF
import os
import io

app = Flask(__name__)

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

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gerar_pdf", methods=["POST"])
def gerar_pdf():
    arquivos = request.files.getlist("arquivos")
    nao_possui_reservista = request.form.get("nao_possui_reservista") == "true"

    uploads_dict = {int(f.filename.split("_")[0]): f for f in arquivos}

    # Valida todos os documentos, exceto o de reservista se a caixa estiver marcada
    for i in range(len(DOCUMENTOS)):
        if i == 16 and nao_possui_reservista:
            continue
        if i not in uploads_dict:
            return f"Documento obrigatório não enviado: {DOCUMENTOS[i]}", 400

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Gera o PDF com os títulos dos documentos
    for i in range(len(DOCUMENTOS)):
        if i == 16 and nao_possui_reservista:
            continue

        file = uploads_dict[i]
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)

        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{i+1}. {DOCUMENTOS[i]}", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Arquivo enviado: {filename}", ln=True)

    # Adiciona declaração se não tiver certificado de reservista
    if nao_possui_reservista:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Declaração", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, "O candidato declarou, sob responsabilidade, que não possui Certificado de Reservista.")

    # Retorna o PDF como download
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name="Inscricao_OAB_ES.pdf")

if __name__ == "__main__":
    app.run(debug=True)
