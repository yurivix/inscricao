from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from fpdf import FPDF
import os
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

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

@app.route('/')
def index():
    return render_template('index.html')  # se quiser usar template HTML

@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    arquivos = request.files.getlist('arquivos')
    nao_possui_reservista = request.form.get('nao_possui_reservista') == 'true'

    arquivos_ordenados = sorted(
        arquivos, key=lambda f: int(f.filename.split('_')[0])
    )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for arquivo in arquivos_ordenados:
        indice = int(arquivo.filename.split('_')[0])
        if indice == 16 and nao_possui_reservista:
            continue

        filename = secure_filename(arquivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        arquivo.save(filepath)

        # Inserir nome do documento como título
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"{indice + 1}. {documentos[indice]}")

        # Adiciona o arquivo como imagem se for imagem
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            pdf.image(filepath, x=10, y=30, w=180)
        else:
            pdf.multi_cell(0, 10, f"Arquivo anexado: {filename} (PDF não embutido neste modelo)")

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Inscricao_OAB_ES.pdf')
    pdf.output(output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
