// Servidor Express KAVANA RouteFleet.
import express from 'express';
import dbModule from './db.js';
import apiRouter from './routes/api.js';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PODS_DIR = path.join(__dirname, '../../pods');

export function createServer(db) {
  const app = express();
  app.use(express.json());
  app.use('/api', apiRouter(db));
  // Sirve los PODs generados como descarga directa.
  if (fs.existsSync(PODS_DIR)) app.use('/pods', express.static(PODS_DIR));
  else fs.mkdirSync(PODS_DIR, { recursive: true });
  app.use('/pods', express.static(PODS_DIR));
  return app;
}

// Arranque solo si se ejecuta directamente.
if (import.meta.url === `file://${process.argv[1]}`) {
  const db = dbModule.initDb();
  const app = createServer(db);
  const PORT = process.env.PORT || 5001;
  app.listen(PORT, () => console.log(`KAVANA RouteFleet API en puerto ${PORT}`));
}
