import os
import json
import httpx
import base64
import re
from typing import List
from models import Stop

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "google/gemini-flash-1.5"

PROMPT_BASE = """
Extrae la lista de paradas de entrega del contenido proporcionado.
Cada parada debe tener de forma obligatoria:
- cliente (string)
- direccion (string)
- horario_limite (string en formato HH:MM de 24h, o null si no se especifica)

Devuelve ÚNICAMENTE un array JSON estructurado de la siguiente forma, sin bloques de código markdown:
[
  {"cliente": "Nombre", "direccion": "Calle Falsa 123", "horario_limite": "14:30"}
]
"""

def _preprocess_lines(text: str) -> List[str]:
    """Join lines that are likely continuations of the same entry.
    Heuristic: if a line does not contain a time pattern (HH:MM) at the end,
    and the next line does not start with a capital letter (likely a continuation),
    we merge them.
    """
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    i = 0
    result = []
    while i < len(lines):
        current = lines[i]
        # Look ahead to see if we need to merge
        while i + 1 < len(lines):
            # Check if current line ends with time pattern
            if re.search(r'\d{2}:\d{2}\s*$', current):
                break
            # If next line starts with a lowercase letter or a digit (time likely on next line)
            next_line = lines[i + 1]
            # If next line starts with a digit (maybe time) or lowercase, likely continuation
            if next_line and (next_line[0].isdigit() or next_line[0].islower()):
                current += ' ' + next_line.lstrip()
                i += 1
                continue
            # Otherwise break
            break
        result.append(current)
        i += 1
    return result

def _simple_parse(text: str) -> List[Stop]:
    """Parser de respaldo por líneas: formato 'Cliente, Dirección, HH:MM' (dirección puede contener comas)"""
    stops = []
    for line in _preprocess_lines(text):
        if not line.strip() or line.startswith('#'):
            continue
        # Find time pattern HH:MM at end of line
        time_match = re.search(r'(\d{2}:\d{2})\s*$', line)
        if time_match:
            time_str = time_match.group(1)
            # Remove the time part from line
            line_without_time = line[:time_match.start()].rstrip()
            # Split by comma, first part is client, rest is address (may contain commas)
            parts = [p.strip() for p in line_without_time.split(',')]
            if len(parts) >= 2:
                cliente = parts[0]
                # Join remaining parts as address (excluding possible empty)
                direccion = ','.join(parts[1:]).strip()
                # Remove trailing commas and spaces
                direccion = direccion.rstrip(',').strip()
                stops.append(Stop(
                    cliente=cliente,
                    direccion=direccion,
                    horario_limite=time_str
                ))
                continue
        # Fallback: try to split by commas assuming no commas in address
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 2:
            # Assume last part is time if it matches HH:MM, otherwise ignore time
            posible_time = parts[-1]
            if re.fullmatch(r'\d{2}:\d{2}', posible_time):
                time_str = posible_time
                addr_parts = parts[:-1]
            else:
                time_str = None
                addr_parts = parts
            if len(addr_parts) >= 2:
                cliente = addr_parts[0]
                direccion = ','.join(addr_parts[1:]).strip()
                # Remove trailing commas and spaces
                direccion = direccion.rstrip(',').strip()
                stops.append(Stop(
                    cliente=cliente,
                    direccion=direccion,
                    horario_limite=time_str
                ))
    return stops

def _clean_and_parse_json(content: str) -> List[Stop]:
    """Limpia la respuesta del LLM y la convierte en objetos Stop"""
    try:
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        json_str = json_match.group(0) if json_match else content
        stops_data = json.loads(json_str)
        return [Stop(**item) for item in stops_data]
    except Exception:
        return []

async def extract_stops_from_text(text: str) -> List[Stop]:
    """Usa un LLM vía OpenRouter para extraer datos estructurados de paradas desde texto libre.
    Si no hay API key o la llamada falla, recurre de forma segura al parser por líneas.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return _simple_parse(text)

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "Eres un asistente experto en logística industrial que extrae datos estructurados."},
            {"role": "user", "content": f"{PROMPT_BASE}\n\nTexto a analizar:\n{text}"}
        ],
        "temperature": 0.0
    }
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            stops = _clean_and_parse_json(content)
            return stops if stops else _simple_parse(text)
        except Exception:
            return _simple_parse(text)

async def extract_stops_from_image(image_bytes: bytes, mime_type: str) -> List[Stop]:
    """Envía la imagen codificada en Base64 a OpenRouter para análisis multimodal"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return []

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT_BASE},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.0
    }
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return _clean_and_parse_json(content)
        except Exception:
            return []