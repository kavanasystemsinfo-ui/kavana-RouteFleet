// OCR de albaranes industriales (Kavana Lens).
// Soporte PDF inteligente: texto embebido si existe, o imágenes con OCR.

import { cleanAddress } from './addressCleaner.js';
import fs from 'fs';
import { PDFDocument } from 'pdf-lib';

// Extraer texto de PDF (si está disponible)
async function extractPdfText(pdfPath) {
  try {
    const pdfBytes = fs.readFileSync(pdfPath);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    
    // Intentar extraer texto embebido
    // pdf-lib no extrae texto directamente, usar método alternativo
    // Si PDF viene de Google Sheets/Excel, tiene texto
    
    // Fallback: leer como texto plano (PDF con texto)
    const raw = fs.readFileSync(pdfPath, 'utf8');
    // Filtrar solo texto legible (eliminar códigos binarios)
    const text = raw.replace(/[^\x20-\x7E\nÑñÁÉÍÓÚáéíóú]/g, ' ')
                   .replace(/\s+/g, ' ')
                   .trim();
    
    return text;
  } catch (e) {
    return '';
  }
}

// OCR en imágenes (Tesseract online)
async function runTesseract(imagePath) {
  try {
    const Tesseract = (await import('tesseract.js')).default;
    const { data } = await Tesseract.recognize(imagePath, 'spa', { 
      logger: () => {},
      tesseractPath: 'https://unpkg.com/tesseract.js@5.1.0/dist/worker.min.js'
    });
    return data.text;
  } catch (e) {
    console.error('OCR error:', e.message);
    return '';
  }
}

export async function processManifestImage(imagePath, isPdf = false) {
  let raw = '';
  
  if (isPdf) {
    // Intentar extraer texto del PDF primero
    raw = await extractPdfText(imagePath) || '';
    
    // Si no hay texto, usar OCR (requiere poppler en servidor)
    if (!raw.trim()) {
      // Fallback: no se puede OCR sin poppler en Render free
      return { address: null, raw: '', note: 'PDF requiere poppler - use JPG/PNG o instale poppler' };
    }
  } else {
    // Imagen -> OCR
    raw = await runTesseract(imagePath);
  }
  
  const address = cleanAddress(raw);
  return { address, raw };
}
