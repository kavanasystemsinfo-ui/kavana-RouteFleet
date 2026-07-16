import os
import math
import asyncio
import httpx
import subprocess
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from typing import List, Optional, Dict, Tuple

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from models import Stop, RouteRequest, RouteResponse
from extract import extract_stops_from_text, extract_stops_from_image
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pathlib

# --- Configuración de entorno ---
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")
# En producción desactivamos /docs, /redoc y /openapi.json para no exponer el schema
ENABLE_DOCS = DEBUG

app = FastAPI(
    title="Kavana Logistic",
    description="Optimización de rutas de reparto con ventanas de tiempo",
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None,
)

# --- CORS: solo orígenes explícitos desde env (CORS_ORIGIN, separado por comas) ---
_cors_origin = os.getenv("CORS_ORIGIN", "")
allowed_origins = [o.strip() for o in _cors_origin.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# --- Rate limiting (protege contra abuso de OpenRouter/Nominatim) ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Constantes de seguridad
MAX_UPLOAD_MB = 15
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".csv", ".xlsx", ".xls", ".pdf", ".docx", ".png", ".jpg", ".jpeg"}


# Serve frontend
frontend_path = pathlib.Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/app")
async def serve_frontend():
    index = frontend_path / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"error": "Frontend not found"}

# Simple in-memory cache for geocoding results
_geocode_cache: Dict[str, Optional[Tuple[float, float]]] = {}

def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en kilómetros entre dos puntos en la Tierra."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

async def geocode_address(address: str, client: httpx.AsyncClient) -> Optional[tuple]:
    """Obtiene latitud y longitud mediante Nominatim con caching y rate limiting."""
    key = address.lower().strip()
    if key in _geocode_cache:
        return _geocode_cache[key]
    
    # Rate limit: wait at least 1 second between requests to be nice to Nominatim
    await asyncio.sleep(1.0)
    try:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1},
            headers={"User-Agent": "KavanaLogistic/1.0 (+https://kavana.dev)"},
            timeout=10.0
        )
        if resp.status_code == 200:
            data = resp.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                _geocode_cache[key] = (lat, lon)
                return (lat, lon)
            else:
                _geocode_cache[key] = None
                return None
        elif resp.status_code == 429:
            # If rate limited, wait a bit longer and retry once
            await asyncio.sleep(2.0)
            resp2 = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": address, "format": "json", "limit": 1},
                headers={"User-Agent": "KavanaLogistic/1.0 (+https://kavana.dev)"},
                timeout=10.0
            )
            if resp2.status_code == 200:
                data = resp2.json()
                if data:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    _geocode_cache[key] = (lat, lon)
                    return (lat, lon)
            _geocode_cache[key] = None
            return None
        else:
            _geocode_cache[key] = None
            return None
    except Exception:
        _geocode_cache[key] = None
        return None

async def geocode_addresses(addresses: List[str], client: httpx.AsyncClient) -> List[Optional[tuple]]:
    """Geocode a list of addresses sequentially, respecting rate limits."""
    results = []
    for addr in addresses:
        results.append(await geocode_address(addr, client))
    return results

def resolver_vrp(paradas_list: List[Stop], depot_geocode: tuple, coords: List[tuple], vehicle_count: int):
    """Motor OR‑Tools centralizado usado por ambos endpoints."""
    all_coords = [depot_geocode] + coords
    n_locations = len(all_coords)

    # Matrices de distancia (metros) y tiempo (segundos a 40 km/h)
    distance_matrix = [[0]*n_locations for _ in range(n_locations)]
    time_matrix = [[0]*n_locations for _ in range(n_locations)]
    avg_speed_kmh = 40.0

    for i in range(n_locations):
        for j in range(n_locations):
            if i == j:
                distance_matrix[i][j] = 0
                time_matrix[i][j] = 0
            else:
                dist = haversine(all_coords[i][0], all_coords[i][1],
                                 all_coords[j][0], all_coords[j][1])
                distance_matrix[i][j] = int(dist * 1000)               # metros
                time_matrix[i][j] = int((dist / avg_speed_kmh) * 3600)  # segundos

    manager = pywrapcp.RoutingIndexManager(n_locations, vehicle_count, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    def time_callback(from_index, to_index):
        return time_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_distance_index = routing.RegisterTransitCallback(distance_callback)
    transit_time_index = routing.RegisterTransitCallback(time_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_distance_index)

    # Dimensión de Tiempo para las Ventanas de Trabajo
    routing.AddDimension(transit_time_index, 30 * 60, 24 * 3600, False, "Time")
    time_dimension = routing.GetDimensionOrDie("Time")

    # Ventana del depósito (todo el día)
    time_dimension.CumulVar(manager.NodeToIndex(0)).SetRange(0, 24 * 3600)

    for i, stop in enumerate(paradas_list):
        node_idx = manager.NodeToIndex(i + 1)
        if stop.horario_limite:
            try:
                h, m = map(int, stop.horario_limite.split(":"))
                limite_segundos = h * 3600 + m * 60
                time_dimension.CumulVar(node_idx).SetRange(0, limite_segundos)
            except Exception:
                time_dimension.CumulVar(node_idx).SetRange(0, 24 * 3600)
        else:
            time_dimension.CumulVar(node_idx).SetRange(0, 24 * 3600)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        raise HTTPException(status_code=400, detail="OR-Tools no pudo encontrar una ruta óptima viable con las restricciones dadas.")

    orden_optimizado = []
    detalles = []
    distancia_total = 0
    tiempo_total = 0

    for vehicle_id in range(vehicle_count):
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:  # omitir el depósito en la lista de paradas a visitar
                orden_optimizado.append(node - 1)  # índice original de la parada
                time_var = time_dimension.CumulVar(index)
                arrival_min = solution.Min(time_var) // 60
                detalles.append({
                    "cliente": paradas_list[node - 1].cliente,
                    "direccion": paradas_list[node - 1].direccion,
                    "hora_llegada_estimada": f"{int(arrival_min // 60):02d}:{int(arrival_min % 60):02d}"
                })
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            distancia_total += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

    tiempo_total = distancia_total / 1000 / avg_speed_kmh  # horas

    return {
        "orden_optimizado": orden_optimizado,
        "distancia_total_km": round(distancia_total / 1000, 2),
        "tiempo_total_horas": round(tiempo_total, 2),
        "detalles": detalles
    }

@app.get("/")
async def read_index():
    """Sirve el frontend estático."""
    if os.path.exists('frontend/index.html'):
        return FileResponse('frontend/index.html')
    return {"message": "Servidor Kavana Logistic Activo. Endpoint de API listo."}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

# Handler global para errores 500 (no exponer tracebacks en producción)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if DEBUG:
        raise exc
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno del servidor. Inténtalo de nuevo."}
    )

@app.post("/api/optimizar-ruta", response_model=RouteResponse)
@limiter.limit("20/minute")
async def optimizar_ruta(request: Request, req: RouteRequest):
    """Endpoint para entrada manual (texto libre o lista de paradas)."""
    if req.paradas is None and req.document_text is not None:
        paradas_list = await extract_stops_from_text(req.document_text)
    elif req.paradas is not None:
        paradas_list = req.paradas
    else:
        raise HTTPException(status_code=400, detail="Faltan las paradas o el texto.")

    if not paradas_list:
        raise HTTPException(status_code=400, detail="No se detectaron paradas válidas.")

    direcciones = [p.direccion for p in paradas_list]
    depot_addr = req.depot if req.depot else direcciones[0]

    async with httpx.AsyncClient() as client:
        # Geocode directions sequentially
        geocoding_results = await geocode_addresses(direcciones, client)
        depot_geocode = await geocode_address(depot_addr, client)

    coords = [geo for geo in geocoding_results if geo is not None]
    if len(coords) != len(paradas_list) or not depot_geocode:
        failed_indices = [i for i, g in enumerate(geocoding_results) if g is None]
        failed_addresses = [direcciones[i] for i in failed_indices]
        detail = f"Error en la geocodificación de las direcciones: {failed_addresses}"
        if not depot_geocode:
            detail += f"; Dirección del depósito falló: {depot_addr}"
        raise HTTPException(status_code=422, detail=detail)

    return resolver_vrp(paradas_list, depot_geocode, coords, req.vehicle_count)

@app.post("/api/optimizar-archivo", response_model=RouteResponse)
@limiter.limit("10/minute")
async def optimizar_archivo(
    request: Request,
    file: UploadFile = File(...),
    depot: Optional[str] = Form(None),
    vehicle_count: int = Form(1)
):
    """Endpoint para subir archivos (TXT, CSV, Excel, PDF, DOCX, PNG/JPG)."""
    # R1: límite de tamaño (DoS)
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Archivo demasiado grande. Máximo {MAX_UPLOAD_MB} MB."
        )

    # R6/R7: validación de extensión permitida
    filename = (file.filename or "").lower()
    ext = os.path.splitext(filename)[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {ext}. Permitidos: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    paradas_list = []

    try:
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            mime_type = "image/png" if filename.endswith('.png') else "image/jpeg"
            paradas_list = await extract_stops_from_image(content, mime_type)
        else:
            # Procesar formatos de texto/documento
            if filename.endswith('.txt'):
                text = content.decode('utf-8', errors='ignore')
            elif filename.endswith('.csv'):
                import pandas as pd
                import io
                df = pd.read_csv(io.BytesIO(content))
                text = df.to_string(index=False)
            elif filename.endswith(('.xlsx', '.xls')):
                import pandas as pd
                import io
                df = pd.read_excel(io.BytesIO(content))
                text = df.to_string(index=False)
            elif filename.endswith('.pdf'):
                # Use pdftotext via subprocess
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                try:
                    result = subprocess.run(['pdftotext', tmp_path, '-'], capture_output=True, text=True, timeout=10)
                    if result.returncode != 0:
                        raise HTTPException(status_code=500, detail=f"pdftotext failed: {result.stderr}")
                    text = result.stdout
                finally:
                    os.unlink(tmp_path)
            elif filename.endswith('.docx'):
                import docx
                import io
                doc = docx.Document(io.BytesIO(content))
                text = "\n".join([p.text for p in doc.paragraphs])
            else:
                text = content.decode('utf-8', errors='ignore')
            
            paradas_list = await extract_stops_from_text(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando el archivo: {str(e)}")

    if not paradas_list:
        raise HTTPException(status_code=400, detail="No se pudieron extraer paradas del archivo.")

    direcciones = [p.direccion for p in paradas_list]
    depot_addr = depot if depot else direcciones[0]

    async with httpx.AsyncClient() as client:
        # Geocode directions sequentially
        geocoding_results = await geocode_addresses(direcciones, client)
        depot_geocode = await geocode_address(depot_addr, client)

    coords = [geo for geo in geocoding_results if geo is not None]
    if len(coords) != len(paradas_list) or not depot_geocode:
        failed_indices = [i for i, g in enumerate(geocoding_results) if g is None]
        failed_addresses = [direcciones[i] for i in failed_indices]
        detail = f"Error en la geocodificación de las direcciones: {failed_addresses}"
        if not depot_geocode:
            detail += f"; Dirección del depósito falló: {depot_addr}"
        raise HTTPException(status_code=422, detail=detail)

    return resolver_vrp(paradas_list, depot_geocode, coords, vehicle_count)