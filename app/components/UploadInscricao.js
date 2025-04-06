import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { PDFDocument } from "pdf-lib";

const documentos = [
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
];

export default function UploadInscricao() {
  const [arquivos, setArquivos] = useState({});
  const [concluidos, setConcluidos] = useState({});
  const [progresso, setProgresso] = useState(0);
  const [gerando, setGerando] = useState(false);
  const [mensagem, setMensagem] = useState("");

  const handleChange = async (e, index) => {
    const file = e.target.files[0];
    if (!file) return;

    const newFiles = { ...arquivos, [index]: file };
    const novosConcluidos = { ...concluidos, [index]: true };

    setArquivos(newFiles);
    setConcluidos(novosConcluidos);

    const total = documentos.length;
    const feitos = Object.keys(novosConcluidos).length;
    setProgresso((feitos / total) * 100);

    if (feitos === total) {
      await handleSubmit(newFiles);
    }
  };

  const handleSubmit = async (arquivosParaGerar) => {
    setGerando(true);
    const pdfDoc = await PDFDocument.create();

    for (let i = 0; i < documentos.length; i++) {
      const file = arquivosParaGerar[i];
      if (!file) continue;

      if (file.type === "application/pdf") {
        const bytes = await file.arrayBuffer();
        const donorPdfDoc = await PDFDocument.load(bytes);
        const copiedPages = await pdfDoc.copyPages(
          donorPdfDoc,
          donorPdfDoc.getPageIndices()
        );
        copiedPages.forEach((page) => pdfDoc.addPage(page));
      } else if (file.type.startsWith("image/")) {
        const imageBytes = await file.arrayBuffer();
        let image;
        if (file.type === "image/jpeg") {
          image = await pdfDoc.embedJpg(imageBytes);
        } else if (file.type === "image/png") {
          image = await pdfDoc.embedPng(imageBytes);
        }
        if (image) {
          const page = pdfDoc.addPage([image.width, image.height]);
          page.drawImage(image, {
            x: 0,
            y: 0,
            width: image.width,
            height: image.height,
          });
        }
      }
    }

    const pdfBytes = await pdfDoc.save();
    const blob = new Blob([pdfBytes], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'Inscricao_OAB_ES.pdf';
    link.click();
    URL.revokeObjectURL(url);
    setMensagem("PDF gerado com sucesso!");
    setGerando(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold mb-4">Inscrição OAB-ES</h1>
      {documentos.map((doc, i) => (
        <Card key={i}>
          <CardContent className="p-4 space-y-2">
            <label className="block font-semibold">{i + 1}. {doc}</label>
            <Input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => handleChange(e, i)} />
          </CardContent>
        </Card>
      ))}

      <div className="w-full bg-gray-200 h-4 rounded-full overflow-hidden mt-4">
        <div
          className="h-full bg-blue-500 transition-all"
          style={{ width: `${progresso}%` }}
        ></div>
      </div>

      {gerando && (
        <p className="text-center text-sm text-gray-600">Gerando PDF...</p>
      )}

      {mensagem && (
        <div className="text-center mt-4 text-green-600 font-semibold">
          {mensagem}
        </div>
      )}

      <Button
        onClick={() => {
          setArquivos({});
          setConcluidos({});
          setProgresso(0);
          setMensagem("");
          setGerando(false);
        }}
        variant="outline"
        className="mt-4 w-full"
      >
        Limpar todos os arquivos
      </Button>
    </div>
  );
}
