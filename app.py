from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from fpdf import FPDF
import os
import io

app = Flask(__name__)

DOCUMENTOS = [
    "Requerimento de inscrição da OAB-ES",
    "Requerimento de inscrição no Conselho Federal da OAB",
    "Histórico Escolar com diploma ou colação de grau (autenticado)",
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

@app.route('/')
def index():
    return render_template('index.html', documentos=list(enumerate(DOCUMENTOS)))

@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    nome_completo = request.form.get('nome_completo', '').strip()
    nao_possui_reservista = 'nao_possui_reservista' in request.form

    arquivos = []
    for i, doc in enumerate(DOCUMENTOS):
        file = request.files.get(f'arquivo_{i}')
        if doc == "Certificado de Reservista (para homens)":
            if file and file.filename:
                arquivos.append((doc, file))
            elif nao_possui_reservista:
                arquivos.append((doc, None))
            else:
                return f'O documento "{doc}" é obrigatório, ou marque "Não possuo".'
        else:
            arquivos.append((doc, file if file and file.filename else None))

    merger = PdfMerger()

    # Capa
    capa_pdf = FPDF()
    capa_pdf.add_page()
    capa_pdf.set_font("Arial", size=24)
    capa_pdf.cell(0, 20, "Inscrição na OAB/ES", ln=True, align="C")
    capa_pdf.set_font("Arial", size=16)
    capa_pdf.cell(0, 10, f"Candidato: {nome_completo}", ln=True, align="C")
    capa_stream = io.BytesIO()
    capa_pdf.output(capa_stream)
    capa_stream.seek(0)
    merger.append(capa_stream)

    # Inserir documentos
    for doc_nome, file in arquivos:
        # Página de título
        titulo_pdf = FPDF()
        titulo_pdf.add_page()
        titulo_pdf.set_font("Arial", "B", 18)
        titulo_pdf.cell(0, 100, doc_nome, ln=True, align="C")
        titulo_stream = io.BytesIO()
        titulo_pdf.output(titulo_stream)
        titulo_stream.seek(0)
        merger.append(titulo_stream)

        if file:
            file.stream.seek(0)
            merger.append(file.stream)
        elif doc_nome == "Certificado de Reservista (para homens)" and nao_possui_reservista:
            aviso_pdf = FPDF()
            aviso_pdf.add_page()
            aviso_pdf.set_font("Arial", "", 14)
            aviso_pdf.multi_cell(0, 10, "Declaro que não possuo Certificado de Reservista.")
            aviso_stream = io.BytesIO()
            aviso_pdf.output(aviso_stream)
            aviso_stream.seek(0)
            merger.append(aviso_stream)

    resultado_pdf = io.BytesIO()
    merger.write(resultado_pdf)
    merger.close()
    resultado_pdf.seek(0)

    return send_file(resultado_pdf, download_name='inscricao_oab_es.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
