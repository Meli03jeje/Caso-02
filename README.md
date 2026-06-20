# 🚚 Optimizacion de Rutas de Distribucion — TSP (13 puntos)

Modelo de optimizacion para una empresa de distribucion que sale de un
**deposito** (nodo `0`), visita **12 clientes** exactamente una vez cada uno
(nodos `3, 10, 21, 22, 35, 40, 41, 47, 65, 71, 76, 77`) y regresa al deposito,
recorriendo la **menor distancia total** posible.

Es un **Problema del Agente Viajero (TSP)** clasico, formulado como un
modelo de Programacion Lineal Entera Mixta (MILP) con la formulacion
**Miller–Tucker–Zemlin (MTZ)** para la eliminacion de subciclos.

---

## 📁 Estructura del repositorio

```
.
├── app.py                     # Aplicacion Streamlit (interfaz interactiva)
├── requirements.txt           # Dependencias de Python
├── data/
│   └── distancias.csv         # Matriz de distancias (13x13)
├── ampl_model/
│   ├── tsp.mod                 # Modelo AMPL (conjuntos, parametros, variables, restricciones)
│   ├── tsp.dat                 # Datos AMPL (los 13 nodos + matriz de distancias)
│   └── tsp.run                 # Script de ejecucion y reporte de resultados
├── solver/
│   └── tsp_solver.py           # Misma formulacion MTZ resuelta con PuLP/CBC (motor de la app)
└── .streamlit/
    └── config.toml             # Tema visual de la app
```

---

## 🧮 El modelo matematico (resumen)

**Conjuntos**
- `N` : los 13 puntos (deposito + clientes)
- `N₀ = N \ {0}` : puntos sin el deposito

**Parametros**
- `d[i,j]` : distancia entre el punto *i* y el punto *j* (km)
- `n = |N| = 13`

**Variables**
- `x[i,j] ∈ {0,1}` : 1 si la ruta va directamente de *i* a *j*
- `u[i] ∈ [1, n-1]`, para *i* ∈ N₀ : posicion de visita de *i* (variable auxiliar MTZ)

**Funcion objetivo**

```
min Z = Σ Σ d[i,j] * x[i,j]      para todo i,j en N, i ≠ j
```

**Restricciones**

1. **Salida unica** (de cada punto sale exactamente un arco):
   `Σⱼ x[i,j] = 1   ∀ i ∈ N`

2. **Entrada unica** (a cada punto entra exactamente un arco):
   `Σᵢ x[i,j] = 1   ∀ j ∈ N`

3. **Eliminacion de subciclos**
   - Formulacion clasica (DFJ, conceptual): `Σᵢ∈S Σⱼ∈S x[i,j] ≤ |S|-1` para todo subconjunto propio `S ⊂ N`. Es correcta pero genera 2ⁿ restricciones.
   - Formulacion implementada (**MTZ**, equivalente y practica):
     `u[i] - u[j] + (n-1)*x[i,j] ≤ n-2   ∀ i,j ∈ N₀, i ≠ j`

La explicacion completa, con la notacion en LaTeX y el detalle de cada
restriccion, esta tambien dentro de la app (pestaña **"Modelo matematico"**).

---

## ✅ Resultado optimo (verificado con dos metodos exactos)

| | |
|---|---|
| **Distancia total optima** | **230 km** |
| **Estado** | Optimo (verificado) |
| **Secuencia de visita** | `0 → 65 → 41 → 71 → 21 → 35 → 22 → 76 → 3 → 40 → 47 → 77 → 10 → 0` |

Este resultado se verifico con **dos algoritmos exactos independientes**:
1. MILP con formulacion MTZ (AMPL / PuLP+CBC)
2. Programacion dinamica Held–Karp (cota inferior teorica exacta para TSP)

Ambos coinciden en **230 km**, por lo que la solucion es la optima global
(no una aproximacion heuristica).

---

## ▶️ Como ejecutar la app de Streamlit

### Localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

### En Streamlit Community Cloud

1. Sube este repositorio a GitHub (ver seccion siguiente).
2. Entra a [share.streamlit.io](https://share.streamlit.io), conecta tu cuenta de GitHub.
3. Selecciona el repositorio y el archivo `app.py` como punto de entrada.
4. Streamlit instalara automaticamente `requirements.txt` y publicara la app.

---

## 🐙 Como subir este proyecto a GitHub

```bash
cd nombre-de-la-carpeta
git init
git add .
git commit -m "Modelo TSP - optimizacion de rutas de distribucion"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/<tu-repositorio>.git
git push -u origin main
```

---

## 🖥️ Como ejecutar el modelo en AMPL

Los archivos en `ampl_model/` son un modelo AMPL completo y autocontenido.
Puedes ejecutarlo de varias formas:

**Opcion A — AMPL IDE / linea de comandos (si tienes AMPL instalado):**
```bash
cd ampl_model
ampl tsp.run
```

**Opcion B — NEOS Server (gratis, sin instalar nada):**
1. Entra a [https://neos-server.org/neos/](https://neos-server.org/neos/)
2. Sube `tsp.mod` como modelo y `tsp.dat` como datos.
3. Elige un solver MILP (ej. CBC, HiGHS, Gurobi) y envia el trabajo.

**Opcion C — Google Colab con `amplpy` (modulos gratuitos):**
```python
!pip install amplpy
!python -m amplpy.modules install highs
from amplpy import AMPL
ampl = AMPL()
ampl.read("tsp.mod")
ampl.read_data("tsp.dat")
ampl.option["solver"] = "highs"
ampl.solve()
print(ampl.get_value("DistanciaTotal"))
```

El `tsp.run` ya incluye la logica para imprimir la distancia total,
los arcos seleccionados y la secuencia de visita reconstruida.

> **Nota sobre la app de Streamlit:** para que la aplicacion web funcione
> siempre, sin depender de licencias o de la disponibilidad de modulos
> externos de AMPL, el motor que usa `app.py` es **PuLP + CBC** (codigo
> abierto, sin licencia). Es la **misma formulacion matematica MTZ**
> linea por linea que `tsp.mod`/`tsp.dat`/`tsp.run`, por lo que el
> resultado optimo es identico (230 km) sin importar cual de los dos
> motores se use para resolverlo.

---

## 🗺️ Grafo de la ruta

La pestaña "Grafo de la ruta" de la app dibuja los 13 puntos usando
**escalamiento multidimensional (MDS)** sobre la matriz de distancias,
de modo que la posicion relativa de los nodos se aproxime a la distancia
real entre ellos (no son coordenadas geograficas reales, ya que el
enunciado solo entrega distancias, no coordenadas). Sobre esa disposicion
se dibuja la ruta optima con flechas que indican el sentido del recorrido,
y el deposito se resalta con un marcador distinto.

---

## 🛠️ Tecnologias usadas

- **AMPL** — formulacion y resolucion formal del modelo matematico
- **Python / PuLP (CBC)** — motor de optimizacion embebido en la app web
- **Streamlit** — interfaz web interactiva
- **Plotly** — visualizacion del grafo de la ruta
- **scikit-learn (MDS)** — proyeccion 2D de los nodos a partir de distancias
