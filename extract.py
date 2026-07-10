import os, json, httpx, base64, re
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

Devuelve UNICAMENTE un array JSON estructurado de la siguiente forma, sin bloques de codigo markdown:
[
  {"cliente": "Nombre", "direccion": "Calle Falsa 123", "horario_limite": "14:30"}
]
"""

def _simple_parse(text: str) -> List[Stop]:
    """Parser inteligente que detecta automaticamente el formato de entrada."""
    # Format 1: "NN. HH:MM - Cliente - Direccion" (PDF/Report)
    report_pattern = re.findall(
        r'(\d{2}:\d{2})\s*[-–—]\s*(.+?)\s*[-–—]\s*(.+?)(?:\s*,\s*\d+\.|\s*\d+\.|\s*$)',
        text, re.MULTILINE
    )
    if report_pattern:
        stops = []
        for time_str, cliente, direccion in report_pattern:
            c = cliente.strip().rstrip(' ,')
            d = direccion.strip().rstrip(' ,')
            stops.append(Stop(cliente=c, direccion=d, horario_limite=time_str.strip()))
        if stops:
            return stops

    # Format 2: single line items with optional number prefix
    stops = []
    # Skip common header/footer words
    skip_words = ['albaran', 'ruta', 'paradas:', 'deposito:', 'total:', 'vehiculos', 'optimizado', 'kavana', 'pagina']
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Skip header lines
        if any(line.lower().startswith(w) for w in skip_words):
            continue
        # Strip leading number/dot/bullet
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        if len(line) < 5:
            continue
        # Look for HH:MM
        tm = re.search(r'(\d{2}:\d{2})\s*$', line)
        if tm:
            time_str = tm.group(1)
            rest = line[:tm.start()].rstrip()
            # Split by first comma or dash
            sep = re.split(r'\s*[-–—,]\s*', rest, maxsplit=1)
            if len(sep) >= 2:
                stops.append(Stop(cliente=sep[0], direccion=sep[1], horario_limite=time_str))
            else:
                stops.append(Stop(cliente=f"P{len(stops)+1}", direccion=rest, horario_limite=time_str))
            continue
        # Address only
        if len(line) > 5 and any(c.isalpha() for c in line):
            stops.append(Stop(cliente=f"Parada {len(stops)+1}", direccion=line))

    # Format 3: comma separated with "Cliente, Dir, HH:MM"
    if not stops:
        for line in text.splitlines():
            line = line.strip().lstrip('0123456789.-–—*•\t ')
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                stops.append(Stop(cliente=parts[0], direccion=','.join(parts[1:])))
    return stops

def _clean_and_parse_json(content: str) -> List[Stop]:
    try:
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        json_str = json_match.group(0) if json_match else content
        stops_data = json.loads(json_str)
        return [Stop(**item) for item in stops_data]
    except Exception:
        return []

async def extract_stops_from_text(text: str) -> List[Stop]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return _simple_parse(text)
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "Eres un asistente experto en logistica industrial que extrae datos estructurados."},
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
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return []
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT_BASE},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
            ]
        }],
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
