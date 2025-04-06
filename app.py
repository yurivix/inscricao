from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from fpdf import FPDF
import os
from datetime import datetime
from PyPDF2 import PdfMerger

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", documentos=list(enumerate(DOCUMENTOS)))

@app.route("/gerar_pdf", methods=["POST"])
def gerar_pdf():
    nome_completo = request.form.get("nome_completo", "Nome não informado")
    nao_possui_reservista = request.form.get("nao_possui_reservista") == "true"

    arquivos = []
    for i, doc in enumerate(DOCUMENTOS):
        file = request.files.get(f"arquivo_{i}")
        if file and file.filename:
            filename = secure_filename(f"{i}_{file.filename}")
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            arquivos.append((doc, path))
        else:
            return f"Faltando documento obrigatório: {doc}", 400

    # Cria capa
    capa = FPDF()
    capa.add_page()
    capa.set_font("Arial", "B", 18)
    capa.set_text_color(0, 40, 104)
    capa.cell(0, 10, "Ordem dos Advogados do Brasil", ln=True, align="C")
    capa.cell(0, 10, "Seccional do Espírito Santo", ln=True, align="C")
    capa.ln(10)
    capa.set_font("Arial", "B", 16)
    capa.set_text_color(0, 0, 0)
    capa.cell(0, 10, "Inscrição na OAB/ES", ln=True, align="C")
    capa.ln(20)
    capa.set_font("Arial", size=14)
    capa.cell(0, 10, f"Nome completo: {nome_completo}", ln=True, align="C")
    capa.ln(10)
    capa.set_font("Arial", size=12)
    capa.cell(0, 10, f"Data: {datetime.today().strftime('%d/%m/%Y')}", ln=True, align="C")

    if nao_possui_reservista:
        capa.ln(10)
        capa.set_text_color(200, 0, 0)
        capa.set_font("Arial", "B", 12)
        capa.multi_cell(0, 10, "Declaração: O candidato declarou que NÃO possui o Certificado de Reservista.", align="C")
        capa.set_text_color(0, 0, 0)

    # Cria índice
    capa.add_page()
    capa.set_font("Arial", "B", 14)
    capa.cell(0, 10, "Índice dos Documentos", ln=True, align="C")
    capa.ln(5)
    capa.set_font("Arial", size=12)
    for i, (doc, path) in enumerate(arquivos):
        capa.cell(0, 10, f"{i+1}. {doc}", ln=True)

    capa_path = os.path.join(app.config['UPLOAD_FOLDER'], "00_capa.pdf")
    capa.output(capa_path)

    # Merge all
