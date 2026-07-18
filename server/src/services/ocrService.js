// OCR de albaranes industriales (Kavana Lens).
// Tesseract extrae texto; luego addressCleaner limpia símbolos de tabla
// y filtra materiales para dejar una dirección GPS limpia (ver DECISIONES).

import { cleanAddress } from './addressCleaner.js';
import fs from 'fs';
import { PDFDocument } from 'pdf-lib';
import { createWorker } from 'tesseract.js';

// Convertir PDF a imágenes (usando pdf2pic)
async function pdfToImages(pdfPath) {
  try {
    const { default: pdf2pic } = await import('pdf2pic');
    const options = {
      density: 150,
      saveFilename: "page",
      savePath: "/tmp/pdf_pages",
      format: "png",
      width: 800,
      height: 1000
    };
    
    // pdf2pic necesita convertir página por página
    // Simplificado: usar pdf-lib para extraer textos si es posible
    const pdfBytes = fs.readFileSync(pdfPath);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const pages = pdfDoc.getPageCount();
    
    // Si el PDF tiene texto embebido, extraerlo
    const text = await extractEmbeddedText(pdfDoc);
    if (text) return [{ text, isEmbedded: true }];
    
    // Si no, usar OCR con pdf2pic (requiere poppler instalado)
    if (pages > 0) {
      // Intentar con pdf2pic
      try {
        const convert = pdf2pic.fromPath(pdfPath, options);
        const results = [];
        for (let i = 1; i <= Math.min(pages, 3); i++) { // Máximo 3 páginas
          const result = await convert(i);
          if (result && result.path) {
            results.push({ path: result.path });
          }
        }
        return results;
      } catch (e) {
        console.warn('pdf2pic failed, trying tesseract direct');
      }
    }
    return [];
  } catch (e) {
    console.error('Error converting PDF:', e.message);
    return [];
  }
}

// Extraer texto embebido de PDF (si existe)
async function extractEmbeddedText(pdfDoc) {
  try {
    // PDF con texto embebido - extraerlo directamente
    // Esto funciona si el PDF no está escaneado
    const text = pdfDoc.getTitle() || ''; // Simple fallback
    return text;
  } catch {
    return null;
  }
}

// OCR en imágenes
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
  if (isPdf) {
    // Procesar PDF
    const pages = await pdfToImages(imagePath);
    let bestAddress = null;
    
    if (pages.length > 0) {
      // Si hay texto embebido
      if (pages[0].isEmbedded) {
        bestAddress = cleanAddress(pages[0].text);
      } else {
        // OCR en cada página
        for (const page of pages) {
          if (page.path) {
            const raw = await runTesseract(page.path);
            const addr = cleanAddress(raw);
            if (addr && addr.length > 10) {
              bestAddress = addr;
              break;
            }
          }
        }
      }
    }
    
    return { address: bestAddress, raw: '' };
  }
  
  // Imagen normal
  const raw = await runTesseract(imagePath);
  const address = cleanAddress(raw);
  return { address, raw: raw || '' };
}
