# TP3_AyED
# Generador Inteligente de Itinerarios Turísticos 

Un planificador de viajes dinámico e inteligente diseñado para resolver el problema de enrutamiento turístico en la Ciudad de Buenos Aires. Esta aplicación web permite a los usuarios generar itinerarios diarios optimizados, combinando recorridos peatonales y la red de buses turísticos reales.

## Características Principales

* **Motor de Búsqueda (Algoritmo de Dijkstra):** Calcula los caminos más cortos en tiempo entre hoteles, atracciones, restaurantes y paradas de bus, evaluando tiempos de caminata y de transporte público.
* **Decisión Voraz (Greedy Algorithm):** Construye el itinerario diario priorizando la cercanía inmediata de las atracciones, respetando siempre el límite de horas configurado por el usuario y garantizando el retorno al hotel.
* **Paradas Gastronómicas Inteligentes:** Si el usuario acumula más de 5 horas de recorrido activo, el sistema desvía la ruta hacia el establecimiento gastronómico más cercano antes de continuar.
* **Mapas Interactivos:** Generación dinámica de mapas por cada día de viaje utilizando **Leaflet.js**, mostrando las rutas peatonales (punteadas) y las rutas de autobús (líneas continuas rojas o amarillas).

## Fuentes de Datos (Datasets)

El grafo de la ciudad se construyó procesando y adaptando bases de datos reales en formato CSV:
1.  **Alojamientos Turísticos:** Hoteles de 4 y 5 estrellas.
2.  **Establecimientos Gastronómicos:** Bodegones, cafeterías y restaurantes.
3.  **Paradas de Bus Turístico:** Coordenadas de los puntos de ascenso y descenso.
4.  **Recorridos de Bus Turístico:** Trazados vectoriales y tiempos de viaje de las líneas Amarilla y Roja.

## Instalación y Uso

Dado que es una aplicación que se ejecuta íntegramente del lado del cliente, no requiere instalación de dependencias ni un entorno de servidor complejo.

1.  Clona este repositorio
2.  Abre la carpeta del proyecto.
3.  Haz doble clic en el archivo `itinerario.html` 
4.  Selecciona tu hotel, la cantidad de días, las horas por día y genera tu itinerario.


---
*Este proyecto fue desarrollado como una solución algorítmica aplicada para optimizar la planificación turística mediante estructuras de datos reales.*
