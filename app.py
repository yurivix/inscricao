from flask import Flask, render_template_string, request, send_file
import os
import io
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from fpdf import FPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    return render_template_string(open('templates/index.html').read(), documentos=DOCUMENTOS)

@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    nome = request.form.get("nome")
    reservista_nao_possui = request.form.get("nao_possui_reservista") == "on"

    documentos = {}
    for doc in DOCUMENTOS:
        documentos[doc] = {
            "file": request.files.get(doc),
            "nao_possui": doc == "Certificado de Reservista (para homens)" and reservista_nao_possui
        }

    merger = PdfMerger()

    # Capa com nome
    capa = FPDF()
    capa.add_page()
    capa.set_font("Arial", "B", 24)
    capa.cell(0, 10, f"Documentação de {nome}", ln=True, align="C")
    capa_output = capa.output(dest='S').encode('latin1')
    capa_stream = io.BytesIO(capa_output)
    merger.append(capa_stream)

    for doc_nome, info in documentos.items():
        if doc_nome == "Certificado de Reservista (para homens)" and info["nao_possui"]:
            pdf_info = FPDF()
            pdf_info.add_page()
            pdf_info.set_font("Arial", "", 14)
            pdf_info.multi_cell(0, 10, f"""{doc_nome}:

O candidato declarou que não possui este documento.""")
            info_output = pdf_info.output(dest='S').encode('latin1')
            info_stream = io.BytesIO(info_output)
            merger.append(info_stream)
            continue

        file = info["file"]
        if file and file.filename.lower().endswith(".pdf") and file.mimetype == "application/pdf":
            try:
                file.stream.seek(0)

                # Página com o nome do documento
                nome_pdf = FPDF()
                nome_pdf.add_page()
                nome_pdf.set_font("Arial", "B", 16)
                nome_pdf.multi_cell(0, 10, doc_nome)
                nome_output = nome_pdf.output(dest='S').encode('latin1')
                nome_stream = io.BytesIO(nome_output)
                merger.append(nome_stream)

                # Documento em si
                merger.append(file.stream)
            except Exception:
                erro_pdf = FPDF()
                erro_pdf.add_page()
                erro_pdf.set_font("Arial", "", 14)
                erro_pdf.multi_cell(0, 10, f"""{doc_nome}:

Erro ao processar o arquivo. Verifique se ele está corrompido ou é um PDF válido.""")
                erro_output = erro_pdf.output(dest='S').encode('latin1')
                erro_stream = io.BytesIO(erro_output)
                merger.append(erro_stream)
        elif doc_nome != "Certificado de Reservista (para homens)":
            aviso_pdf = FPDF()
            aviso_pdf.add_page()
            aviso_pdf.set_font("Arial", "", 14)
            aviso_pdf.multi_cell(0, 10, f"""{doc_nome}:

Arquivo não enviado ou formato inválido. Somente arquivos PDF são aceitos.""")
            aviso_output = aviso_pdf.output(dest='S').encode('latin1')
            aviso_stream = io.BytesIO(aviso_output)
            merger.append(aviso_stream)

    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    return send_file(output, as_attachment=True, download_name=f"documentos_{nome}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
