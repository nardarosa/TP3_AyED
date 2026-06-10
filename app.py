import heapq
import re
import csv
import math
from math import radians, sin, cos, sqrt, atan2
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# ============================================================
#  CLASE GRAFO
# ============================================================
class Graph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, nodo1, nodo2, peso, tipo='walk', color=None):
        if nodo1 not in self.graph: self.graph[nodo1] = {}
        if nodo2 not in self.graph: self.graph[nodo2] = {}
        self.graph[nodo1][nodo2] = {'peso': peso, 'tipo': tipo, 'color': color}

    def distancia_minima(self, origen: str):
        distancia = {node: float("inf") for node in self.graph}
        previo = {node: None for node in self.graph}
        
        distancia[origen] = 0
        pq = [(0, origen)]
        heapq.heapify(pq)
        visitados = set()

        while pq:
            distancia_actual, nodo_actual = heapq.heappop(pq)
            if distancia_actual > distancia[nodo_actual]:
                continue
            if nodo_actual not in visitados:
                visitados.add(nodo_actual)
                for vecino, data in self.graph.get(nodo_actual, {}).items():
                    peso = data['peso']
                    distancia_tentativa = distancia_actual + peso
                    if distancia_tentativa < distancia[vecino]:
                        distancia[vecino] = distancia_tentativa
                        previo[vecino] = nodo_actual
                        heapq.heappush(pq, (distancia_tentativa, vecino))
        return distancia, previo

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def tiempo_caminata(km, velocidad_kmh=5):
    return max(1, round(km / velocidad_kmh * 60))

# ============================================================
#  DATOS
# ============================================================
ATRACCIONES = {
    "A_Obelisco":    ("Obelisco", -34.6037, -58.3816, 15),
    "A_Colon":       ("Teatro Colón", -34.5982, -58.3827, 60),
    "A_Rosada":      ("Casa Rosada", -34.6090, -58.3729, 45),
    "A_Cabildo":     ("Cabildo", -34.6083, -58.3712, 40),
    "A_Congreso":    ("Congreso", -34.6090, -58.3888, 45),
    "A_GalPacifico": ("Galerías Pacífico", -34.5988, -58.3780, 45),
    "A_PlzSanMartin":("Plaza San Martín", -34.5952, -58.3788, 30),
    "A_Ateneo":      ("El Ateneo", -34.5979, -58.3929, 30),
    "A_CCK":         ("Centro Cultural Kirchner", -34.6054, -58.3632, 60),
    "A_PteMujer":    ("Puente de la Mujer", -34.6078, -58.3631, 20),
    "A_Reserva":     ("Reserva Ecológica", -34.6163, -58.3570, 90),
    "A_SanTelmo":    ("Plaza Dorrego", -34.6219, -58.3705, 60),
    "A_MAMBA":       ("MAMBA", -34.6171, -58.3706, 60),
    "A_Bombonera":   ("La Bombonera", -34.6364, -58.3642, 60),
    "A_Caminito":    ("Caminito", -34.6412, -58.3606, 60),
    "A_Cementerio":  ("Cementerio Recoleta", -34.5877, -58.3906, 60),
    "A_BellasArtes": ("Bellas Artes", -34.5817, -58.3958, 75),
    "A_Floralis":    ("Floralis Genérica", -34.5812, -58.3931, 20),
    "A_MALBA":       ("MALBA", -34.5768, -58.4043, 90),
    "A_Japones":     ("Jardín Japonés", -34.5756, -58.4142, 60),
    "A_Rosedal":     ("Rosedal", -34.5716, -58.4228, 45),
    "A_Planetario":  ("Planetario", -34.5705, -58.4111, 45),
    "A_PlzSerrano":  ("Plaza Serrano", -34.5881, -58.4289, 45),
    "A_River":       ("Estadio River Plate", -34.5468, -58.4491, 90),
    "A_BChino":      ("Barrio Chino", -34.5596, -58.4490, 60)
}

HOTELES = {
    "H_Alvear":          ("Alvear Palace Hotel", -34.5877, -58.3890, 0),
    "H_Hilton":          ("Hilton Buenos Aires", -34.6054, -58.3637, 0),
    "H_Sheraton":        ("Sheraton Buenos Aires", -34.5932, -58.3735, 0),
    "H_NH9deJulio":      ("NH 9 de Julio", -34.6067, -58.3821, 0),
    "H_Abasto":          ("Abasto Hotel", -34.6041, -58.4102, 0),
}

RESTAURANTES = {
    "R_AlCarbon":    ("Al Carbón", -34.5967, -58.3729, 60),
    "R_Estancia":    ("La Estancia", -34.5987, -58.3738, 60),
    "R_Aldo":        ("Aldo's Restorán", -34.6116, -58.3778, 60),
    "R_Desnivel":    ("El Desnivel", -34.6167, -58.3722, 60),
    "R_Cabrera":     ("La Cabrera", -34.5895, -58.4307, 60),
}

NOMBRES = {}
NOMBRES.update({k: v[0] for k, v in ATRACCIONES.items()})
NOMBRES.update({k: v[0] for k, v in HOTELES.items()})
NOMBRES.update({k: v[0] for k, v in RESTAURANTES.items()})

def parse_bus_stops():
    bus_stops = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'bus_turistico_paradas.csv')
    
    if not os.path.exists(csv_path): return bus_stops

    with open(csv_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            geom = row.get('geometry', '')
            match = re.search(r'POINT \(([-\d\.]+) ([-\d\.]+)\)', geom)
            if match:
                lon, lat = float(match.group(1)), float(match.group(2))
                bid = f"B_{row['id']}"
                recorrido = row['recorrido']
                color = 'Amarillo' if 'Amarillo' in recorrido else 'Rojo'
                bus_stops[bid] = {
                    'id': bid,
                    'nombre': row['nombre'],
                    'color': color,
                    'lat': lat,
                    'lon': lon,
                    'tVisita': 0
                }
                NOMBRES[bid] = row['nombre']
    return bus_stops

def construir_grafo():
    G = Graph()
    
    todos_nodos = {}
    for k, v in ATRACCIONES.items(): todos_nodos[k] = (v[1], v[2])
    for k, v in HOTELES.items(): todos_nodos[k] = (v[1], v[2])
    for k, v in RESTAURANTES.items(): todos_nodos[k] = (v[1], v[2])
    
    bus_stops = parse_bus_stops()
    
    # Caminata POI <-> Parada
    for poi_id, (lat1, lon1) in todos_nodos.items():
        distancias = []
        for bid, bdata in bus_stops.items():
            km = haversine_km(lat1, lon1, bdata['lat'], bdata['lon'])
            distancias.append((km, bid))
        distancias.sort()
        
        for km, bid in distancias[:3]:
            mins = tiempo_caminata(km)
            G.add_edge(poi_id, bid, mins, 'walk')
            G.add_edge(bid, poi_id, mins, 'walk')
            
        # Caminata POI <-> POI
        d_pois = []
        for p2, (lat2, lon2) in todos_nodos.items():
            if poi_id == p2: continue
            km = haversine_km(lat1, lon1, lat2, lon2)
            if km < 2.0: d_pois.append((km, p2))
        d_pois.sort()
        for km, p2 in d_pois[:5]:
            mins = tiempo_caminata(km)
            G.add_edge(poi_id, p2, mins, 'walk')
            
    # Viaje Bus <-> Bus
    rojo = [b for b in bus_stops.values() if b['color'] == 'Rojo']
    amarillo = [b for b in bus_stops.values() if b['color'] == 'Amarillo']
    
    def connect_bus_line(line_stops, color):
        line_stops.sort(key=lambda x: x['nombre'])
        for i in range(len(line_stops)):
            n1 = line_stops[i]['id']
            n2 = line_stops[(i+1) % len(line_stops)]['id']
            # Viaje entre paradas (ej. 4 mins)
            G.add_edge(n1, n2, 4, 'bus', color)
            G.add_edge(n2, n1, 4, 'bus', color)
            
    connect_bus_line(rojo, 'Rojo')
    connect_bus_line(amarillo, 'Amarillo')
    
    return G, bus_stops

GRAFO_COMPLETO, BUS_STOPS_DATA = construir_grafo()

def _coords(nid):
    if nid in ATRACCIONES: return ATRACCIONES[nid][1], ATRACCIONES[nid][2]
    if nid in HOTELES: return HOTELES[nid][1], HOTELES[nid][2]
    if nid in RESTAURANTES: return RESTAURANTES[nid][1], RESTAURANTES[nid][2]
    if nid in BUS_STOPS_DATA: return BUS_STOPS_DATA[nid]['lat'], BUS_STOPS_DATA[nid]['lon']
    return None, None

def _buscar_gastro(nodo_act, visitados):
    lat_a, lon_a = _coords(nodo_act)
    cands = []
    for r_id, d in RESTAURANTES.items():
        if r_id in visitados: continue
        km = haversine_km(lat_a, lon_a, d[1], d[2])
        mins = tiempo_caminata(km)
        cands.append((mins, r_id, d[0], d[3]))
    if cands:
        cands.sort()
        return cands[0]
    return None

def reconstruct_path(previos, start, end):
    path = []
    curr = end
    while curr:
        path.append(curr)
        if curr == start: break
        curr = previos[curr]
    path.reverse()
    
    steps = []
    for i in range(len(path) - 1):
        n1 = path[i]
        n2 = path[i+1]
        edge = GRAFO_COMPLETO.graph[n1][n2]
        steps.append({
            'desde': n1,
            'hacia': n2,
            'peso': edge['peso'],
            'tipo': edge['tipo'],
            'color': edge.get('color')
        })
    return steps

def agrupar_pasos(steps):
    grouped = []
    current_bus = None
    
    for s in steps:
        if s['tipo'] == 'bus':
            if current_bus is None or current_bus['color'] != s['color']:
                if current_bus: grouped.append(current_bus)
                current_bus = {
                    'tipo': 'bus',
                    'color': s['color'],
                    'desde': s['desde'],
                    'hacia': s['hacia'],
                    'peso': s['peso'],
                    'paradas_count': 1
                }
            else:
                current_bus['hacia'] = s['hacia']
                current_bus['peso'] += s['peso']
                current_bus['paradas_count'] += 1
        else:
            if current_bus:
                grouped.append(current_bus)
                current_bus = None
            grouped.append(s)
            
    if current_bus: grouped.append(current_bus)
    return grouped

def calcular_itinerario(hotel, horas, dias, usar_gastro):
    TIEMPO_MAX = int(horas * 60)
    itinerarios = {}
    visitados = {hotel}
    
    for dia in range(1, dias + 1):
        actual = hotel
        t_acum = 0
        
        # Iniciar lista de items visuales con el Hotel
        dia_items = []
        dia_items.append({
            'tipo_nodo': 'hotel',
            'nombre': HOTELES[hotel][0],
            'tVisita': 0,
            'lat': HOTELES[hotel][1],
            'lon': HOTELES[hotel][2]
        })
        
        almuerzo = not usar_gastro
        
        while True:
            # Check Almuerzo
            if not almuerzo and t_acum >= TIEMPO_MAX * 0.4:
                rest = _buscar_gastro(actual, visitados)
                if rest:
                    r_viaje, r_id, r_nom, r_dur = rest
                    # Agregamos la caminata al item anterior
                    dia_items[-1]['traslado'] = f"Caminar hacia restaurante ({r_viaje} min)"
                    dia_items.append({
                        'tipo_nodo': 'gastro',
                        'nombre': r_nom,
                        'tVisita': r_dur,
                        'lat': RESTAURANTES[r_id][1],
                        'lon': RESTAURANTES[r_id][2]
                    })
                    t_acum += r_viaje + r_dur
                    actual = r_id
                    visitados.add(r_id)
                    almuerzo = True
                    continue
            
            dist, prevs = GRAFO_COMPLETO.distancia_minima(actual)
            
            mejor_dest = None
            menor_v = float('inf')
            
            for d, t in dist.items():
                if d not in visitados and d.startswith("A_") and t < menor_v:
                    menor_v = t
                    mejor_dest = d
                    
            if not mejor_dest: break
            
            t_vis = ATRACCIONES[mejor_dest][3]
            costo = menor_v + t_vis
            
            km_v = haversine_km(ATRACCIONES[mejor_dest][1], ATRACCIONES[mejor_dest][2], HOTELES[hotel][1], HOTELES[hotel][2])
            t_vuelta = tiempo_caminata(km_v)
            
            if t_acum + costo + t_vuelta > TIEMPO_MAX: break
            
            raw = reconstruct_path(prevs, actual, mejor_dest)
            grp = agrupar_pasos(raw)
            
            # Anexar pasos intermedios (paradas de bus)
            for st in grp:
                hacia = st['hacia']
                # texto de traslado para el nodo anterior
                if st['tipo'] == 'walk':
                    dia_items[-1]['traslado'] = f"Caminar a la siguiente parada ({st['peso']} min)"
                else:
                    dia_items[-1]['traslado'] = f"Tomar bus {st['color']} por {st['paradas_count']} paradas ({st['peso']} min)"
                
                # nodo actual en el paso
                if hacia == mejor_dest:
                    dia_items.append({
                        'tipo_nodo': 'atrac',
                        'nombre': ATRACCIONES[hacia][0],
                        'tVisita': t_vis,
                        'lat': ATRACCIONES[hacia][1],
                        'lon': ATRACCIONES[hacia][2]
                    })
                else:
                    dia_items.append({
                        'tipo_nodo': 'parada',
                        'nombre': BUS_STOPS_DATA[hacia]['nombre'],
                        'tVisita': 0,
                        'lat': BUS_STOPS_DATA[hacia]['lat'],
                        'lon': BUS_STOPS_DATA[hacia]['lon']
                    })
            
            t_acum += costo
            visitados.add(mejor_dest)
            actual = mejor_dest

        # Volver al hotel
        df, pf = GRAFO_COMPLETO.distancia_minima(actual)
        t_v = df.get(hotel, 20)
        raw = reconstruct_path(pf, actual, hotel)
        grp = agrupar_pasos(raw)
        
        for st in grp:
            hacia = st['hacia']
            if st['tipo'] == 'walk':
                dia_items[-1]['traslado'] = f"Caminar hacia tu destino ({st['peso']} min)"
            else:
                dia_items[-1]['traslado'] = f"Tomar bus {st['color']} por {st['paradas_count']} paradas ({st['peso']} min)"
            
            if hacia == hotel:
                dia_items.append({
                    'tipo_nodo': 'hotel',
                    'nombre': HOTELES[hotel][0],
                    'tVisita': 0,
                    'lat': HOTELES[hotel][1],
                    'lon': HOTELES[hotel][2]
                })
            else:
                dia_items.append({
                    'tipo_nodo': 'parada',
                    'nombre': BUS_STOPS_DATA[hacia]['nombre'],
                    'tVisita': 0,
                    'lat': BUS_STOPS_DATA[hacia]['lat'],
                    'lon': BUS_STOPS_DATA[hacia]['lon']
                })
        
        t_acum += t_v
        itinerarios[dia] = {
            'items': dia_items,
            'tiempo': t_acum
        }
    
    return itinerarios

# ============================================================
#  FLASK ROUTES
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():
    itinerarios = None
    if request.method == "POST":
        h = request.form.get("hotel")
        hs = float(request.form.get("horas", 8))
        d = int(request.form.get("dias", 4))
        r = request.form.get("restaurante") == "on"
        if h in HOTELES:
            itinerarios = calcular_itinerario(h, hs, d, r)
            
    return render_template("index.html", hoteles=HOTELES, itinerarios=itinerarios)

if __name__ == "__main__":
    print("=" * 50)
    print("  App Itinerarios (Monolito SSR)  -  Running")
    print("==================================================")
    app.run(debug=True, port=5000)
