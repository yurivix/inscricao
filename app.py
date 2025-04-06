import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from fpdf import FPDF

app = Flask(__name__)

# Configurações
UPLOAD_FOLDER = 'uploads'
DOCUMENTOS = [
    "Documento de Identidade",
    "CPF",
    "Título de Eleitor",
    "Comprovante de Residência",
    "Diploma de Graduação",
    "Certidão de Quitação Eleitoral",
    "Foto 3x4",
    "Comprovante de Pagamento",
    "Certidão de Antecedentes Criminais"
]

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html", documentos=DOCUMENTOS)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['arquivo']
    index = int(request.form['index'])
    filename = secure_filename(f"{index:02d}_{DOCUMENTOS[index].replace(' ', '_')}{os.path.splitext(file.filename)[1]}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return redirect(url_for('index'))

@app.route('/gerar-pdf')
def gerar_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    arquivos = sorted(os.listdir(UPLOAD_FOLDER))
    for arquivo in arquivos:
        filepath = os.path.join(UPLOAD_FOLDER, arquivo)
        ext = os.path.splitext(filepath)[1].lower()

        if ext in ['.jpg', '.jpeg', '.png']:
            pdf.add_page()
            pdf.image(filepath, x=10, y=20, w=190)
        elif ext == '.pdf':
            # Ignorar PDFs dentro de PDFs para manter a simplicidade
            continue
        else:
            continue

    output_path = os.path.join(UPLOAD_FOLDER, "documentos_final.pdf")
    pdf.output(output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
