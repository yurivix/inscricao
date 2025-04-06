from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Lista atualizada dos documentos exigidos pela OAB-ES
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

# Apenas este documento é opcional
documentos_opcionais = ["Certificado de Reservista (para homens)"]

@app.route("/")
def index():
    return render_template("index.html",
                           documentos=enumerate(documentos),
                           documentos_opcionais=documentos_opcionais)

@app.route("/gerar_pdf", methods=["POST"])
def gerar_pdf():
    nome_completo = request.form.get("nome_completo", "Candidato")
    nao_possui_reservista = request.form.get("nao_possui_reservista")

    arquivos_final = []

    # Adiciona capa personalizada
    capa_path = os.path.join(UPLOAD_FOLDER, "capa.pdf")
    gerar_capa_pdf(nome_completo, capa_path)
    arquivos_final.append(capa_path)

    for i, nome_doc in enumerate(documentos):
        file = request.files.get(f"arquivo_{i}")
        if file and file.filename:
            filename = secure_filename(f"{i}_{file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            titulo_pdf_path = os.path.join(UPLOAD_FOLDER, f"titulo_{i}.pdf")
            gerar_titulo_pdf(nome_doc, titulo_pdf_path)

            arquivos_final.append(titulo_pdf_path)
            arquivos_final.append(filepath)

        elif nome_doc == "Certificado de Reservista (para homens)" and nao_possui_reservista:
            aviso_path = os.path.join(UPLOAD_FOLDER, f"aviso_reservista.pdf")
            gerar_aviso_reservista(aviso_path)

            titulo_pdf_path = os.path.join(UPLOAD_FOLDER, f"titulo_{i}.pdf")
            gerar_titulo_pdf(nome_doc, titulo_pdf_path)

            arquivos_final.append(titulo_pdf_path)
            arquivos_final.append(aviso_path)

        elif nome_doc not in documentos_opcionais:
            return f"Documento obrigatório faltando: {nome_doc}", 400

    # Junta os PDFs
    pdf_saida = os.path.join(UPLOAD_FOLDER, f"{nome_completo}_inscricao.pdf")
    unir_pdfs(arquivos_final, pdf_saida)

    return send_file(pdf_saida, as_attachment=True)

# Funções auxiliares

def gerar_titulo_pdf(texto, path):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 100, texto)
    c.showPage()
    c.save()

def gerar_aviso_reservista(path):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 14)
    aviso = "O candidato declarou que não possui Certificado de Reservista."
    c.drawCentredString(width / 2, height - 100, aviso)
    c.showPage()
    c.save()

def gerar_capa_pdf(nome_candidato, path):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 150, "Inscrição - OAB/ES")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 200, f"Nome do Candidato: {nome_candidato}")
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width / 2, height - 240, "Documentação anexa conforme exigido no edital.")
    c.showPage()
    c.save()

def unir_pdfs(lista_paths, output_path):
    merger = PdfMerger()
    for path in lista_paths:
        merger.append(path)
    merger.write(output_path)
    merger.close()

if __name__ == "__main__":
    app.run(debug=True)
