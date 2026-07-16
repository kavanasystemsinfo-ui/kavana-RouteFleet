from pydantic import BaseModel, Field
from typing import List, Optional

class Stop(BaseModel):
    cliente: str
    direccion: str
    horario_limite: Optional[str] = Field(None, description="Formato HH:MM o None")

class RouteRequest(BaseModel):
    paradas: Optional[List[Stop]] = None
    document_text: Optional[str] = None
    depot: Optional[str] = None
    vehicle_count: int = Field(1, ge=1, le=50, description="Número de vehículos (máx 50 para evitar DoS en OR-Tools)")

class RouteResponse(BaseModel):
    orden_optimizado: List[int]
    distancia_total_km: float
    tiempo_total_horas: float
    detalles: List[dict]