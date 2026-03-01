# nic_touring_leon.py
# Guía turística de León, Nicaragua con mapa interactivo realista

import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
from dataclasses import dataclass
from typing import List, Dict, Tuple
import math
import json

# Configuración de página
st.set_page_config(
    page_title="Nic Touring - León, Nicaragua",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ESTILOS CSS ====================

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1e3a5f;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1e3a5f;
    }
    .route-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ESTRUCTURA DE DATOS ====================

@dataclass
class Lugar:
    id: int
    nombre: str
    categoria: str
    subcategoria: str
    descripcion: str
    historia: str
    horario: str
    lat: float
    lon: float
    direccion: str
    telefono: str
    precio: str
    icono: str
    color: str

# ==================== BASE DE DATOS COMPLETA DE LEÓN ====================

LUGARES = [
    # MUSEOS
    Lugar(1, "Catedral de León", "Museos", "Religioso",
        "La catedral más grande de Centroamérica, Patrimonio de la Humanidad por la UNESCO.",
        "Construida entre 1747 y 1814 por el obispo Isidro Marín. Estilo barroco y neoclásico. Sus túneles subterráneos conectan la catedral con otros templos.",
        "Lunes-Sábado: 8:00-16:00, Domingo: 9:00-14:00",
        12.4350, -86.8784, "Calle Real, frente al Parque Central", "2311-1185",
        "Entrada: $3, Subir a techos: $5", "⛪", "#8B4513"),
    
    Lugar(2, "Museo de Arte Fundación Ortiz-Gurdián", "Museos", "Arte",
        "Una de las colecciones de arte más importantes de Centroamérica.",
        "Fundado por el matrimonio Ortiz-Gurdián. Dos sedes: Casa de los Páez (arte colonial) y Casa de los Guardiola (arte contemporáneo).",
        "Martes-Domingo: 10:00-18:00",
        12.4321, -86.8815, "Calle Real, una cuadra al oeste de la Catedral", "2311-2114",
        "$5 extranjeros, $2 nacionales", "🎨", "#9932CC"),
    
    Lugar(3, "Museo de Leyendas y Tradiciones", "Museos", "Folclore",
        "Museo al aire libre con figuras gigantes de personajes del folclore nicaragüense.",
        "Creado por el maestro César Caracas. Muestra personajes como La Llorona, La Carretanagua, El Cadejo y otros.",
        "Lunes-Domingo: 9:00-17:00",
        12.4389, -86.8823, "Contiguo al Cementerio Municipal", "2311-7580",
        "$2", "👹", "#FF6347"),
    
    Lugar(4, "Museo de la Revolución", "Museos", "Histórico",
        "Museo dedicado a la Revolución Sandinista de 1979.",
        "Ubicado en la casa familiar de la poetisa Claribel Alegría. Contiene fotografías, armas y documentos históricos.",
        "Lunes-Viernes: 9:00-17:00, Sábados: 9:00-13:00",
        12.4335, -86.8802, "Calle de Rubén Darío, frente al Parque Rubén Darío", "2311-7742",
        "Donación voluntaria", "⭐", "#DC143C"),
    
    Lugar(5, "Museo Archivo Rubén Darío", "Museos", "Literario",
        "Casa natal del poeta Rubén Darío, padre del Modernismo literario.",
        "Conserva manuscritos originales, muebles personales y objetos del poeta.",
        "Lunes-Viernes: 8:00-17:00, Sábados: 8:00-12:00",
        12.4338, -86.8805, "Calle Real, esquina con Calle Rubén Darío", "2311-1243",
        "$2", "📚", "#4682B4"),
    
    Lugar(6, "Museo Adiact", "Museos", "Arte Contemporáneo",
        "Museo de arte contemporáneo y diseño.",
        "Espacio para exposiciones temporales de artistas nacionales e internacionales.",
        "Martes-Sábado: 10:00-18:00",
        12.4367, -86.8798, "Del Banco de la Producción, 2 cuadras al norte", "2311-4567",
        "Gratis", "🖼️", "#FF69B4"),
    
    # IGLESIAS
    Lugar(7, "Iglesia La Merced", "Iglesias", "Colonial",
        "Una de las iglesias más antiguas de León, con hermoso patio interior.",
        "Construida en el siglo XVIII. Destaca por su arquitectura barroca y su campanario.",
        "Diario: 6:00-18:00",
        12.4345, -86.8778, "Calle Real, frente al Parque Rubén Darío", "Sin teléfono",
        "Gratis", "⛪", "#DAA520"),
    
    Lugar(8, "Iglesia San Francisco", "Iglesias", "Colonial",
        "Iglesia y convento franciscano del siglo XVII.",
        "Fundada en 1639. Alberga el Museo de Tradiciones y Leyendas en su patio.",
        "Diario: 6:00-18:00",
        12.4367, -86.8823, "Del Cementerio, 1 cuadra al sur", "2311-2234",
        "Gratis", "⛪", "#B8860B"),
    
    Lugar(9, "Iglesia La Recolección", "Iglesias", "Barroco",
        "Hermosa iglesia barroca del siglo XVIII.",
        "Destaca por su fachada elaborada y su interior sencillo pero elegante.",
        "Diario: 6:00-18:00",
        12.4312, -86.8765, "Calle La Recolección, 3 cuadras al sur del Parque Central", "Sin teléfono",
        "Gratis", "⛪", "#CD853F"),
    
    Lugar(10, "Iglesia El Calvario", "Iglesias", "Colonial",
        "Iglesia ubicada en el barrio El Calvario.",
        "Conocida por su procesión durante Semana Santa.",
        "Diario: 6:00-18:00",
        12.4289, -86.8756, "Barrio El Calvario", "Sin teléfono",
        "Gratis", "⛪", "#D2691E"),
    
    Lugar(11, "Iglesia Zaragoza", "Iglesias", "Neoclásico",
        "Iglesia del barrio Zaragoza.",
        "Construida a finales del siglo XIX. Arquitectura sencilla pero imponente.",
        "Diario: 6:00-18:00",
        12.4401, -86.8834, "Barrio Zaragoza", "Sin teléfono",
        "Gratis", "⛪", "#8B4513"),
    
    # PARQUES
    Lugar(12, "Parque Central Juan José Quezada", "Parques", "Urbano",
        "Parque principal de León, corazón de la ciudad.",
        "Centro histórico desde la época colonial. Rodeado de la Catedral y edificios históricos.",
        "Abierto 24 horas",
        12.4344, -86.8790, "Centro de León, frente a la Catedral", "Sin teléfono",
        "Gratis", "🌳", "#228B22"),
    
    Lugar(13, "Parque Rubén Darío", "Parques", "Cultural",
        "Parque dedicado al poeta Rubén Darío.",
        "Contiene un monumento al poeta y es lugar de eventos culturales.",
        "Abierto 24 horas",
        12.4335, -86.8802, "Calle Rubén Darío, entre Real y Central", "Sin teléfono",
        "Gratis", "🌳", "#32CD32"),
    
    # CULTURA Y NATURALEZA
    Lugar(14, "Barrio Indígena de Sutiaba", "Cultura", "Patrimonio",
        "Barrio indígena con raíces prehispánicas.",
        "Fundado por indígenas en el siglo XVI. Conserva tradiciones, danzas y artesanías.",
        "Acceso libre",
        12.4256, -86.8923, "Oeste de León, 2 km del centro", "Sin teléfono",
        "Gratis", "🏘️", "#8B008B"),
    
    Lugar(15, "Teatro José de la Cruz Mena", "Cultura", "Teatro",
        "Teatro histórico de León.",
        "Inaugurado en 1884. Escenario de importantes eventos culturales.",
        "Según programación",
        12.4345, -86.8801, "Calle Real, frente al Parque Rubén Darío", "2311-2345",
        "Varía según evento", "🎭", "#4B0082"),
    
    Lugar(16, "Ruinas de León Viejo", "Naturaleza", "Arqueológico",
        "Primer asentamiento español en Nicaragua, Patrimonio de la Humanidad.",
        "Fundada en 1524 por Francisco Hernández de Córdoba. Destruida por el Volcán Momotombo en 1610.",
        "Lunes-Domingo: 8:00-17:00",
        12.3978, -86.6175, "Puerto Momotombo, 30 km de León", "Sin teléfono",
        "$5 extranjeros, $1 nacionales", "🏺", "#A0522D"),
    
    Lugar(17, "Hervideros de San Jacinto", "Naturaleza", "Geotermal",
        "Fumarolas y aguas termales activas.",
        "Manifestación de actividad volcánica. Pozas de barro hirviendo.",
        "Lunes-Domingo: 8:00-17:00",
        12.5967, -86.8967, "San Jacinto, 24 km de León", "Sin teléfono",
        "$2", "♨️", "#FF4500"),
    
    # VOLCANES
    Lugar(18, "Volcán Cerro Negro", "Volcanes", "Activo",
        "Volcán activo famoso por el sandboarding.",
        "Última erupción en 1999. Altura: 728 msnm. Ideal para sandboarding y trekking.",
        "Tours diarios: 6:00-18:00",
        12.5083, -86.7022, "25 km noreste de León", "Sin teléfono",
        "Tour: $30-50", "🌋", "#2F4F4F"),
    
    Lugar(19, "Volcán Telica", "Volcanes", "Activo",
        "Volcán activo con cráter fumante visible.",
        "Altura: 1,061 msnm. Uno de los volcanes más activos de Nicaragua.",
        "Tours diarios",
        12.6021, -86.8453, "30 km de León", "Sin teléfono",
        "Tour: $35-60", "🌋", "#696969"),
    
    Lugar(20, "Volcán San Cristóbal", "Volcanes", "Activo",
        "El volcán más alto de Nicaragua.",
        "Altura: 1,745 msnm. Requiere buena condición física para ascender.",
        "Tours con reservación",
        12.7023, -87.0045, "70 km de León", "Sin teléfono",
        "Tour: $80-120", "🌋", "#000000"),
    
    # PLAYAS
    Lugar(21, "Playa Las Peñitas", "Playas", "Tranquila",
        "Playa tranquila ideal para relajarse y ver tortugas.",
        "Santuario de tortugas marinas (julio-diciembre). Olas suaves para nadar.",
        "Acceso libre 24 horas",
        12.3417, -87.0256, "18 km al oeste de León", "Sin teléfono",
        "Gratis", "🏖️", "#1E90FF"),
    
    Lugar(22, "Playa Poneloya", "Playas", "Surf",
        "Playa popular para surfistas.",
        "Olas fuertes ideales para surf. Atardeceres espectaculares.",
        "Acceso libre 24 horas",
        12.3756, -87.0214, "20 km al oeste de León", "Sin teléfono",
        "Gratis", "🏄", "#00BFFF"),
    
    Lugar(23, "Reserva Natural Isla Juan Venado", "Playas", "Reserva",
        "Reserva de manglares y hábitat de tortugas.",
        "Estuario con manglares, aves y tortugas. Recorridos en lancha.",
        "Lunes-Domingo: 6:00-18:00",
        12.3301, -86.9856, "Entre Las Peñitas y Poneloya", "Sin teléfono",
        "Tour: $25-40", "🐢", "#20B2AA"),
    
    # RESTAURANTES
    Lugar(24, "El Bodegón", "Restaurantes", "Gourmet",
        "Restaurante de alta cocina nicaragüense.",
        "Ambiente elegente en una casona colonial. Especialidad en carnes y mariscos.",
        "Martes-Domingo: 12:00-22:00",
        12.4334, -86.8803, "Calle Rubén Darío, frente al Parque Rubén Darío", "2311-4567",
        "$$$", "🍽️", "#8B0000"),
    
    Lugar(25, "El Sesteo", "Restaurantes", "Tradicional",
        "Restaurante histórico de León.",
        "Funciona desde 1972. Comida típica nicaragüense en ambiente colonial.",
        "Lunes-Domingo: 11:00-22:00",
        12.4342, -86.8795, "Calle Real, esquina con Calle Central", "2311-2341",
        "$$", "🍲", "#B22222"),
    
    Lugar(26, "Tacubaya", "Restaurantes", "Mexicano-Nica",
        "Fusión de cocina mexicana y nicaragüense.",
        "Conocido por sus tacos y ambiente bohemio.",
        "Martes-Domingo: 13:00-23:00",
        12.4356, -86.8789, "Calle Real, cerca de la Catedral", "2311-7890",
        "$$", "🌮", "#D2691E"),
    
    Lugar(27, "Coco Calala", "Restaurantes", "Mariscos",
        "Especializado en mariscos frescos.",
        "Ambiente playero en medio de la ciudad. Ceviches y pescados destacados.",
        "Miércoles-Lunes: 12:00-21:00",
        12.4321, -86.8812, "Calle Central, 2 cuadras al sur", "2311-3456",
        "$$", "🦐", "#FF7F50"),
    
    Lugar(28, "Pan & Paz Bakery", "Restaurantes", "Café",
        "Panadería francesa artesanal.",
        "Pan recién horneado, croissants y café de especialidad.",
        "Lunes-Sábado: 7:00-19:00, Domingo: 8:00-14:00",
        12.4345, -86.8807, "Calle Rubén Darío, contiguo al Teatro", "2311-5678",
        "$", "🥐", "#F4A460"),
    
    # HOTELES
    Lugar(29, "Bigfoot Hostel", "Hoteles", "Hostal",
        "Hostal popular entre mochileros.",
        "Conocido por sus tours al Cerro Negro y ambiente social.",
        "Recepción 24 horas",
        12.4348, -86.8792, "Calle Real, 1 cuadra al oeste de la Catedral", "2311-6432",
        "$10-25 por noche", "🏨", "#9370DB"),
    
    Lugar(30, "Hotel El Convento", "Hoteles", "Boutique",
        "Hotel boutique en edificio histórico.",
        "Antiguo convento convertido en hotel de lujo. Patio central colonial.",
        "Recepción 24 horas",
        12.4339, -86.8801, "Calle Rubén Darío, frente al Parque", "2311-7055",
        "$80-150 por noche", "🏨", "#4B0082"),
    
    Lugar(31, "Hotel La Perla", "Hoteles", "Económico",
        "Hotel económico céntrico.",
        "Habitaciones limpias y cómodas. Ideal para viajeros con presupuesto.",
        "Recepción 24 horas",
        12.4351, -86.8788, "Calle Real, 2 cuadras al este", "2311-2345",
        "$25-40 por noche", "🏨", "#4169E1"),
    
    Lugar(32, "Hotel Austria", "Hoteles", "Medio",
        "Hotel familiar con buena ubicación.",
        "Desayuno incluido. Terraza con vista a la ciudad.",
        "Recepción 24 horas",
        12.4323, -86.8794, "Calle Central, 3 cuadras al norte", "2311-8765",
        "$40-70 por noche", "🏨", "#6495ED"),
    
    Lugar(33, "Hotel Café Azul", "Hoteles", "Boutique",
        "Hotel boutique con cafetería.",
        "Ambiente artístico. Cada habitación decorada por artistas locales.",
        "Recepción 7:00-22:00",
        12.4367, -86.8812, "Barrio San Felipe", "2311-9087",
        "$50-90 por noche", "🏨", "#0000CD"),
    
    Lugar(34, "Hotel Tranquilo", "Hoteles", "Económico",
        "Hostal tranquilo con ambiente relajado.",
        "Jardín tropical. Ideal para descansar.",
        "Recepción 7:00-21:00",
        12.4378, -86.8823, "Barrio Guadalupe", "2311-3452",
        "$15-30 por noche", "🏨", "#00CED1"),
    
    Lugar(35, "Hotel Vizcaíno", "Hoteles", "Medio",
        "Hotel con piscina en el centro.",
        "Piscina, restaurante y estacionamiento. Buena relación calidad-precio.",
        "Recepción 24 horas",
        12.4341, -86.8776, "Calle Real, 4 cuadras al este", "2311-6543",
        "$45-80 por noche", "🏨", "#5F9EA0"),
    
    Lugar(36, "Aaki Hotel", "Hoteles", "Ecológico",
        "Hotel eco-friendly en Las Peñitas.",
        "Construido con materiales naturales. Frente al mar.",
        "Recepción 8:00-20:00",
        12.3423, -87.0245, "Playa Las Peñitas", "2311-0987",
        "$60-100 por noche", "🏨", "#2E8B57"),
    
    Lugar(37, "Somar Surf Lodge", "Hoteles", "Surf",
        "Lodge especializado para surfistas.",
        "Clases de surf, alquiler de tablas. Ambiente joven y deportivo.",
        "Recepción 7:00-22:00",
        12.3767, -87.0223, "Playa Poneloya", "2311-7654",
        "$35-60 por noche", "🏨", "#008B8B"),
    
    Lugar(38, "Cabañas Puesta del Sol", "Hoteles", "Cabañas",
        "Cabañas frente al mar en Las Peñitas.",
        "Cabañas rústicas con vista al océano. Atardeceres inolvidables.",
        "Recepción 9:00-18:00",
        12.3412, -87.0267, "Playa Las Peñitas, extremo oeste", "2311-5432",
        "$40-75 por noche", "🏨", "#FF6347"),
]

# ==================== FUNCIONES DE UTILIDAD ====================

def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Fórmula de Haversine para calcular distancia en km"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def obtener_lugares_cercanos(lat: float, lon: float, radio: float = 5) -> List[Lugar]:
    """Obtiene lugares dentro de un radio en km"""
    cercanos = []
    for lugar in LUGARES:
        dist = calcular_distancia(lat, lon, lugar.lat, lugar.lon)
        if dist <= radio:
            cercanos.append((dist, lugar))
    return [l for _, l in sorted(cercanos, key=lambda x: x[0])]

def generar_ruta(origen: Tuple[float, float], destino: Lugar) -> Dict:
    """Simula el cálculo de una ruta"""
    distancia = calcular_distancia(origen[0], origen[1], destino.lat, destino.lon)
    
    # Simular puntos de ruta (en una app real, esto vendría de una API de mapas)
    puntos = []
    num_puntos = 5
    for i in range(num_puntos + 1):
        lat = origen[0] + (destino.lat - origen[0]) * (i / num_puntos)
        lon = origen[1] + (destino.lon - origen[1]) * (i / num_puntos)
        puntos.append([lat, lon])
    
    tiempo_auto = distancia / 40 * 60  # 40 km/h promedio
    tiempo_caminando = distancia / 5 * 60  # 5 km/h caminando
    
    return {
        "distancia_km": round(distancia, 2),
        "tiempo_auto_min": round(tiempo_auto),
        "tiempo_caminando_min": round(tiempo_caminando),
        "puntos": puntos,
        "instrucciones": [
            f"Dirígete al {'norte' if destino.lat > origen[0] else 'sur'} desde tu ubicación",
            f"Continúa por {distancia/3:.1f} km",
            "Gira en la intersección principal",
            f"Continúa recto hasta llegar a {destino.nombre}"
        ]
    }

# ==================== MAPA INTERACTIVO ====================

def crear_mapa_leon(center: List[float] = [12.4344, -86.8794], 
                   zoom: int = 14, 
                   marcadores: List[Lugar] = None,
                   ruta: Dict = None) -> folium.Map:
    """
    Crea un mapa detallado de León con estilo realista
    """
    
    # Crear mapa con tiles de alta calidad
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True
    )
    
    # Agregar tiles adicionales para más detalle
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satélite',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        name='Claro',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='Oscuro',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Agregar minimapa
    minimap = plugins.MiniMap()
    m.add_child(minimap)
    
    # Agregar buscador
    plugins.Geocoder().add_to(m)
    
    # Agregar ubicación del usuario (simulada)
    folium.Marker(
        center,
        popup="📍 Tu ubicación actual",
        icon=folium.Icon(color='red', icon='user', prefix='fa'),
        tooltip="Estás aquí"
    ).add_to(m)
    
    # Círculo de proximidad
    folium.Circle(
        center,
        radius=2000,  # 2km
        popup="Zona cercana",
        color="blue",
        fill=True,
        fill_opacity=0.1
    ).add_to(m)
    
    # Agregar marcadores de lugares
    if marcadores:
        for lugar in marcadores:
            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="color: {lugar.color}; margin: 0;">{lugar.icono} {lugar.nombre}</h4>
                <p style="margin: 5px 0;"><b>{lugar.categoria}</b> | {lugar.subcategoria}</p>
                <p style="font-size: 12px; margin: 5px 0;">{lugar.descripcion[:100]}...</p>
                <p style="font-size: 11px; color: #666; margin: 5px 0;">🕐 {lugar.horario}</p>
                <p style="font-size: 11px; color: #666; margin: 5px 0;">💰 {lugar.precio}</p>
            </div>
            """
            
            folium.Marker(
                [lugar.lat, lugar.lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{lugar.icono} {lugar.nombre}",
                icon=folium.Icon(
                    color='darkblue',
                    icon_color=lugar.color,
                    icon='info-sign',
                    prefix='glyphicon'
                )
            ).add_to(m)
    
    # Dibujar ruta si existe
    if ruta and "puntos" in ruta:
        folium.PolyLine(
            ruta["puntos"],
            color="#FF6B6B",
            weight=5,
            opacity=0.8,
            tooltip="Ruta sugerida"
        ).add_to(m)
        
        # Agregar flechas de dirección
        plugins.AntPath(
            ruta["puntos"],
            color="#FF6B6B",
            weight=4,
            opacity=0.7
        ).add_to(m)
    
    # Agregar control de capas
    folium.LayerControl().add_to(m)
    
    # Agregar fullscreen
    plugins.Fullscreen().add_to(m)
    
    # Agregar medidor de distancia
    plugins.MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)
    
    return m

# ==================== INTERFAZ DE USUARIO ====================

def main():
    # Header
    st.markdown('<h1 class="main-header">🏛️ Nic Touring</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Descubre la ciudad más colonial de Nicaragua</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Catedral_de_Le%C3%B3n_Nicaragua.jpg/640px-Catedral_de_Le%C3%B3n_Nicaragua.jpg", 
                use_column_width=True)
        st.title("🧭 Panel de Control")
        
        # Simulación de GPS
        st.subheader("📍 Tu Ubicación")
        modo_ubicacion = st.radio("Modo:", ["GPS Automático", "Seleccionar manual"])
        
        if modo_ubicacion == "GPS Automático":
            user_lat, user_lon = 12.4344, -86.8794  # Centro de León
            st.success(f"GPS activo\nLat: {user_lat:.4f}\nLon: {user_lon:.4f}")
        else:
            col1, col2 = st.columns(2)
            user_lat = col1.number_input("Latitud", value=12.4344, format="%.4f")
            user_lon = col2.number_input("Longitud", value=-86.8794, format="%.4f")
        
        st.divider()
        
        # Menú de navegación
        pagina = st.selectbox("Ir a:", [
            "🏠 Inicio",
            "🗺️ Mapa Interactivo",
            "📍 Qué hay cerca de mí",
            "🎯 Planificar ruta",
            "🔍 Buscar lugares",
            "📋 Ver todos los lugares"
        ])
        
        st.divider()
        
        # Filtros rápidos
        st.subheader("⚡ Filtros Rápidos")
        filtro_categoria = st.multiselect("Categorías:", 
            list(set([l.categoria for l in LUGARES])),
            default=[]
        )
    
    # Contenido principal según página seleccionada
    if pagina == "🏠 Inicio":
        mostrar_inicio(user_lat, user_lon)
    elif pagina == "🗺️ Mapa Interactivo":
        mostrar_mapa_completo(user_lat, user_lon, filtro_categoria)
    elif pagina == "📍 Qué hay cerca de mí":
        mostrar_cercanos(user_lat, user_lon)
    elif pagina == "🎯 Planificar ruta":
        mostrar_planificador_ruta(user_lat, user_lon)
    elif pagina == "🔍 Buscar lugares":
        mostrar_buscador()
    elif pagina == "📋 Ver todos los lugares":
        mostrar_todos_lugares(filtro_categoria)

def mostrar_inicio(lat: float, lon: float):
    """Página de inicio con estadísticas y destacados"""
    
    # Estadísticas
    cols = st.columns(4)
    stats = {
        "🏛️ Museos": len([l for l in LUGARES if l.categoria == "Museos"]),
        "⛪ Iglesias": len([l for l in LUGARES if l.categoria == "Iglesias"]),
        "🏖️ Playas": len([l for l in LUGARES if l.categoria == "Playas"]),
        "🌋 Volcanes": len([l for l in LUGARES if l.categoria == "Volcanes"])
    }
    
    for col, (icono, cantidad) in zip(cols, stats.items()):
        with col:
            st.metric(icono, cantidad)
    
    st.divider()
    
    # Mapa pequeño de vista general
    st.subheader("🗺️ Vista General de León")
    m = crear_mapa_leon([lat, lon], 13, LUGARES[:15])  # Primeros 15 lugares
    st_folium(m, width=700, height=400, returned_objects=[])
    
    st.divider()
    
    # Lugares destacados
    st.subheader("⭐ Lugares Imperdibles")
    
    destacados = [l for l in LUGARES if l.id in [1, 4, 16, 18, 21]]  # Catedral, Revolución, Ruinas, Cerro Negro, Las Peñitas
    
    for lugar in destacados:
        with st.expander(f"{lugar.icono} {lugar.nombre} - {lugar.categoria}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{lugar.subcategoria}**")
                st.write(lugar.descripcion)
                st.info(f"🕐 {lugar.horario} | 💰 {lugar.precio}")
            with col2:
                dist = calcular_distancia(lat, lon, lugar.lat, lugar.lon)
                st.metric("Distancia", f"{dist:.1f} km")
                if st.button(f"📍 Ver ruta", key=f"ruta_dest_{lugar.id}"):
                    st.session_state["destino_ruta"] = lugar.id
                    st.rerun()

def mostrar_mapa_completo(lat: float, lon: float, filtros: List[str]):
    """Mapa interactivo completo con todos los filtros"""
    
    st.subheader("🗺️ Mapa Detallado de León")
    
    # Filtrar lugares
    lugares_mostrar = LUGARES
    if filtros:
        lugares_mostrar = [l for l in LUGARES if l.categoria in filtros]
    
    # Opciones de visualización
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_mapa = st.selectbox("Tipo de mapa:", ["Estándar", "Satélite", "Claro", "Oscuro"])
    with col2:
        zoom = st.slider("Zoom", 10, 18, 14)
    with col3:
        mostrar_ruta = st.checkbox("Mostrar todas las rutas", False)
    
    # Crear mapa
    tiles_map = {
        "Estándar": "OpenStreetMap",
        "Satélite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "Claro": "CartoDB positron",
        "Oscuro": "CartoDB dark_matter"
    }
    
    m = folium.Map([lat, lon], zoom_start=zoom, tiles=tiles_map.get(tipo_mapa, "OpenStreetMap"))
    
    # Agregar marcadores personalizados con colores por categoría
    for lugar in lugares_mostrar:
        color_cat = {
            "Museos": "purple", "Iglesias": "lightred", "Parques": "green",
            "Playas": "blue", "Volcanes": "darkred", "Restaurantes": "orange",
            "Hoteles": "cadetblue", "Cultura": "pink", "Naturaleza": "darkgreen"
        }.get(lugar.categoria, "gray")
        
        html_popup = f"""
        <div style="width: 250px; font-family: Arial;">
            <h4 style="color: {lugar.color}; margin-bottom: 8px;">{lugar.icono} {lugar.nombre}</h4>
            <p style="margin: 4px 0; font-size: 13px;"><b>{lugar.categoria}</b></p>
            <p style="margin: 4px 0; font-size: 12px; color: #555;">{lugar.descripcion[:120]}...</p>
            <hr style="margin: 8px 0;">
            <p style="margin: 4px 0; font-size: 11px;">📍 {lugar.direccion}</p>
            <p style="margin: 4px 0; font-size: 11px;">🕐 {lugar.horario}</p>
            <p style="margin: 4px 0; font-size: 11px;">💰 {lugar.precio}</p>
            <p style="margin: 4px 0; font-size: 11px;">📞 {lugar.telefono}</p>
        </div>
        """
        
        folium.Marker(
            [lugar.lat, lugar.lon],
            popup=folium.Popup(html_popup, max_width=300),
            tooltip=f"{lugar.icono} {lugar.nombre}",
            icon=folium.Icon(color=color_cat, icon='info-sign', prefix='glyphicon')
        ).add_to(m)
    
    # Marcador de usuario
    folium.Marker(
        [lat, lon],
        popup="Tu ubicación",
        icon=folium.Icon(color='red', icon='user', prefix='fa'),
        tooltip="Estás aquí"
    ).add_to(m)
    
    # Plugins
    plugins.Fullscreen().add_to(m)
    plugins.MeasureControl().add_to(m)
    folium.LayerControl().add_to(m)
    
    st_folium(m, width=800, height=600, returned_objects=[])

def mostrar_cercanos(lat: float, lon: float):
    """Muestra lugares cercanos a la ubicación del usuario"""
    
    st.subheader("📍 Lugares Cerca de Ti")
    
    radio = st.slider("Radio de búsqueda (km)", 0.5, 20.0, 3.0)
    
    cercanos = []
    for lugar in LUGARES:
        dist = calcular_distancia(lat, lon, lugar.lat, lugar.lon)
        if dist <= radio:
            cercanos.append((dist, lugar))
    
    cercanos.sort(key=lambda x: x[0])
    
    if not cercanos:
        st.warning("No se encontraron lugares en ese radio. Intenta aumentar la distancia.")
        return
    
    st.success(f"Se encontraron {len(cercanos)} lugares dentro de {radio} km")
    
    # Mapa con círculo de búsqueda
    m = folium.Map([lat, lon], zoom_start=14)
    folium.Circle([lat, lon], radius=radio*1000, color='blue', fill=True, fill_opacity=0.1).add_to(m)
    
    for dist, lugar in cercanos[:10]:  # Top 10 más cercanos
        folium.Marker(
            [lugar.lat, lugar.lon],
            popup=f"{lugar.nombre} ({dist:.2f} km)",
            icon=folium.Icon(color='green' if dist < 1 else 'orange' if dist < 3 else 'red')
        ).add_to(m)
    
    folium.Marker([lat, lon], icon=folium.Icon(color='red', icon='user')).add_to(m)
    st_folium(m, width=700, height=400, returned_objects=[])
    
    # Lista detallada
    st.divider()
    for dist, lugar in cercanos:
        with st.expander(f"{lugar.icono} {lugar.nombre} - {dist:.2f} km"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{lugar.categoria}** | {lugar.subcategoria}")
                st.write(lugar.descripcion)
                st.write(f"🕐 {lugar.horario}")
            with col2:
                if st.button(f"🗺️ Ruta", key=f"ruta_{lugar.id}"):
                    st.session_state["destino_ruta"] = lugar.id
                    st.rerun()

def mostrar_planificador_ruta(lat: float, lon: float):
    """Planificador de rutas con instrucciones detalladas"""
    
    st.subheader("🎯 Planificador de Rutas")
    
    # Seleccionar destino
    destino_id = st.selectbox(
        "Selecciona tu destino:",
        options=[(l.id, f"{l.icono} {l.nombre}") for l in LUGARES],
        format_func=lambda x: x[1]
    )
    
    if destino_id:
        destino = next(l for l in LUGARES if l.id == destino_id[0])
        
        # Calcular ruta
        ruta = generar_ruta((lat, lon), destino)
        
        # Mostrar mapa con ruta
        m = crear_mapa_leon([lat, lon], 13, [destino], ruta)
        st_folium(m, width=800, height=500, returned_objects=[])
        
        # Información de la ruta
        st.markdown('<div class="route-box">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Distancia", f"{ruta['distancia_km']} km")
        col2.metric("En auto", f"{ruta['tiempo_auto_min']} min")
        col3.metric("Caminando", f"{ruta['tiempo_caminando_min']} min")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Instrucciones paso a paso
        st.subheader("🧭 Instrucciones")
        for i, instruccion in enumerate(ruta['instrucciones'], 1):
            st.write(f"{i}. {instruccion}")
        
        # Detalles del destino
        st.divider()
        st.subheader(f"{destino.icono} Sobre tu destino")
        st.write(f"**{destino.nombre}**")
        st.write(destino.descripcion)
        st.write(f"📍 {destino.direccion}")
        st.write(f"🕐 {destino.horario}")
        st.write(f"💰 {destino.precio}")
        st.write(f"📞 {destino.telefono}")

def mostrar_buscador():
    """Buscador de lugares"""
    
    st.subheader("🔍 Buscar en Nic Touring")
    
    busqueda = st.text_input("Escribe el nombre o tipo de lugar:")
    categoria = st.multiselect("Filtrar por categoría:", 
        list(set(l.categoria for l in LUGARES)))
    
    resultados = LUGARES
    if busqueda:
        resultados = [l for l in resultados if busqueda.lower() in l.nombre.lower() 
                     or busqueda.lower() in l.descripcion.lower()]
    if categoria:
        resultados = [l for l in resultados if l.categoria in categoria]
    
    st.write(f"Se encontraron {len(resultados)} resultados")
    
    for lugar in resultados:
        with st.expander(f"{lugar.icono} {lugar.nombre}"):
            st.write(f"**{lugar.categoria}** - {lugar.subcategoria}")
            st.write(lugar.descripcion)
            st.write(f"📍 {lugar.direccion} | 🕐 {lugar.horario} | 💰 {lugar.precio}")

def mostrar_todos_lugares(filtros: List[str]):
    """Lista completa de todos los lugares"""
    
    st.subheader("📋 Directorio Completo de León")
    
    lugares = LUGARES
    if filtros:
        lugares = [l for l in lugares if l.categoria in filtros]
    
    # Agrupar por categoría
    por_categoria = {}
    for l in lugares:
        por_categoria.setdefault(l.categoria, []).append(l)
    
    for categoria, lista in sorted(por_categoria.items()):
        st.divider()
        st.subheader(f"{lista[0].icono if lista else '•'} {categoria} ({len(lista)})")
        
        cols = st.columns(2)
        for idx, lugar in enumerate(lista):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                    <div style="padding: 10px; border-left: 4px solid {lugar.color}; 
                              background-color: #f8f9fa; margin: 5px 0; border-radius: 5px;">
                        <b>{lugar.icono} {lugar.nombre}</b><br>
                        <small>{lugar.subcategoria} | {lugar.precio}</small><br>
                        <small>{lugar.horario}</small>
                    </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
