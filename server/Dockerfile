# Servidor KAVANA RouteFleet API (Node + better-sqlite3)
FROM node:20-bookworm-slim

WORKDIR /app

# Dependencias del sistema para compilar better-sqlite3
RUN apt-get update && apt-get install -y --no-install-recommends python3 make g++ \
    && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json* ./
RUN npm install --omit=dev

COPY . .

# better-sqlite3 necesita build nativo; se reinstala en el sitio por si acaso
RUN npm rebuild better-sqlite3 2>/dev/null || true

ENV PORT=5001
EXPOSE 5001

CMD ["node", "src/index.js"]
