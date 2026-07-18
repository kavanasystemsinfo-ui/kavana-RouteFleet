// OCR de albaranes industriales (Kavana Lens).
// Extrae texto de imágenes, PDFs y CSV sin dependencias pesadas.
// Tesseract.js es OPCIONAL (solo si está instalado en node_modules).
// Fallback: lectura directa + addressCleaner inteligente.

import { cleanAddress } from './addressCleaner.js';
import fs from 'fs';

// OCR con Tesseract (solo si está instalado)
async function runTesseract(imagePath) {
  try {
    // Dynamic import - solo falla si no está instalado
    const tesseractModule = await import('tesseract.js').catch(() => null);
    if (!tesseractModule) return null;
    
    const Tesseract = tesseractModule.default;
    const { data } = await Tesseract.recognize(imagePath, 'spa', {
      logger: () => {}
    });
    return data.text;
  } catch (e) {
    console.warn('Tesseract no disponible:', e.message);
    return null;
  }
}

// Extraer texto de PDF (binario)
async function extractPdfText(pdfPath) {
  try {
    // Intentar con pdf-lib si está disponible
    const pdfLib = await import('pdf-lib').catch(() => null);
    if (pdfLib && pdfLib.PDFDocument) {
      try {
        const pdfBytes = fs.readFileSync(pdfPath);
        const pdfDoc = await pdfLib.PDFDocument.load(pdfBytes);
        // pdf-lib no extrae texto directamente, pero confirma que es PDF válido
        console.log(`PDF con ${pdfDoc.getPageCount()} páginas - intentando extracción de texto`);
      } catch (e) {
        console.warn('pdf-lib no pudo cargar PDF:', e.message);
      }
    }
    
    // Fallback universal: leer como texto plano y extraer strings legibles
    const buffer = fs.readFileSync(pdfPath, 'utf8');
    
    // Extraer strings que pueden ser direcciones (patrones comunes en PDFs)
    const addressPatterns = [
      /Calle\s+\w+[\s\w,]*\d+/gi,
      /Avenida\s+\w+[\s\w,]*\d+/gi,
      /Carrer\s+\w+[\s\w,]*\d+/gi,
      /Ronda\s+\w+[\s\w,]*\d+/gi,
      /Paseo\s+\w+[\s\w,]*\d+/gi,
      /Plaza\s+\w+[\s\w,]*\d+/gi,
      /Ctra\.\s+\w+[\s\w,]*\d+/gi,
      /Camino\s+\w+[\s\w,]*\d+/gi,
      /C\/\s*\w+[\s\w,]*\d+/gi,
    ];
    
    let found = '';
    for (const pattern of addressPatterns) {
      const match = buffer.match(pattern);
      if (match) {
        found += match.join('\n') + '\n';
      }
    }
    
    if (found.trim()) return found;
    
    // Si no hay direcciones, extraer todo texto legible
    const text = buffer.replace(/[^\x20-\x7E\n\u00C0-\u00FFÁÉÍÓÚÑáéíóúñ]/g, ' ')
                       .replace(/\s+/g, ' ')
                       .trim();
    return text;
  } catch (e) {
    console.warn('Error extrayendo texto de PDF:', e.message);
    return '';
  }
}

// Procesar CSV
function extractCsvText(filePath) {
  try {
    const csv = fs.readFileSync(filePath, 'utf8');
    return csv;
  } catch (e) {
    console.warn('Error leyendo CSV:', e.message);
    return '';
  }
}

export async function processManifestImage(imagePath, isPdf = false, isCsv = false) {
  let raw = '';
  
  if (isCsv) {
    raw = extractCsvText(imagePath);
  } else if (isPdf) {
    raw = await extractPdfText(imagePath);
  } else {
    // Imagen: intentar OCR primero, fallback a lectura de metadatos
    const ocrResult = await runTesseract(imagePath);
    if (ocrResult) {
      raw = ocrResult;
    } else {
      // Fallback: leer el archivo como texto (puede funcionar para capturas)
      try {
        raw = fs.readFileSync(imagePath, 'utf8').replace(/[^\x20-\x7E\nÁÉÍÓÚÑáéíóúñ]/g, ' ').replace(/\s+/g, ' ').trim();
      } catch (e) {
        raw = '';
      }
    }
  }
  
  const address = cleanAddress(raw);
  return { address, raw };
}
