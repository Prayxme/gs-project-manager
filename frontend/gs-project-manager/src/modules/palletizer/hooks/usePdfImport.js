import { useState } from "react";
import { parsePdfTicket } from "../services/palletApi";

// Lectura del Pick Ticket en PDF y ventana de revisión antes de pasarlo al formulario.
export function usePdfImport(t) {
  const [pdfLoading, setPdfLoading] = useState(false);
  const [showPdfModal, setShowPdfModal] = useState(false);
  const [pdfParsedData, setPdfParsedData] = useState(null);

  const leerPdf = async (file) => {
    setPdfLoading(true);
    try {
      setPdfParsedData(await parsePdfTicket(file));
      setShowPdfModal(true);
    } catch (error) {
      alert(`${t.pdfError} ${error.message}`);
    } finally {
      setPdfLoading(false);
    }
  };

  return {
    pdfLoading, showPdfModal, pdfParsedData, setPdfParsedData, leerPdf,
    cerrarModal: () => setShowPdfModal(false),
  };
}
