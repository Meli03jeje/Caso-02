"""
app.py
---------------------------------------------------------------------
Optimizacion de rutas de distribucion (TSP) - 1 deposito + 12 clientes
Universidad de Costa Rica - Ingenieria Industrial

Resuelve el modelo de ruteo (Problema del Agente Viajero) que minimiza
la distancia total recorrida por un vehiculo que sale del deposito,
visita una unica vez a cada uno de los 12 clientes y regresa al deposito.
---------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from solver.tsp_solver import load_distance_matrix, solve_tsp, get_mds_coordinates

st.set_page_config(
    page_title="Optimizacion de Rutas - TSP",
    page_icon="🚚",
    layout="wide",
)

DEPOSITO = 0

# =====================================================================
# CARGA DE DATOS (cacheada para no recalcular en cada interaccion)
# =====================================================================
@st.cache_data
def get_data():
    nodos, D = load_distance_matrix("data/distancias.csv")
    return nodos, D


@st.cache_data
def get_solution(nodos, D):
    return solve_tsp(nodos, D, depot=DEPOSITO)


@st.cache_data
def get_coords(nodos, D):
    return get_mds_coordinates(nodos, D)


nodos, D = get_data()
clientes = [n for n in nodos if n != DEPOSITO]
n_total = len(nodos)

# =====================================================================
# ENCABEZADO
# =====================================================================
st.title("🚚 Optimizacion de Rutas de Distribucion")
st.markdown(
    "**Problema del Agente Viajero (TSP)** · Una empresa de distribucion debe "
    "salir del deposito, visitar **12 clientes** exactamente una vez cada uno, "
    "y regresar al deposito, recorriendo la **menor distancia total** posible."
)

tabs = st.tabs([
    "📌 Valores fijos",
    "🧮 Valores parametricos",
    "📐 Modelo matematico",
    "✅ Resultados",
    "🗺️ Grafo de la ruta",
])

# =====================================================================
# TAB 1: VALORES FIJOS
# =====================================================================
with tabs[0]:
    st.header("Valores fijos del problema")
    st.markdown(
        """
        Estos son los datos **dados** del problema; no cambian durante la optimizacion
        y provienen directamente del enunciado (matriz de distancias entre los 13 puntos).
        """
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Deposito", f"Nodo {DEPOSITO}")
    col2.metric("Numero de clientes", len(clientes))
    col3.metric("Total de puntos a visitar", n_total)

    st.markdown(f"**Lista de clientes:** {' · '.join(str(c) for c in clientes)}")

    st.subheader("Matriz de distancias d(i, j) — en kilometros")
    df_dist = pd.DataFrame(D, index=nodos, columns=nodos)
    st.dataframe(
        df_dist.style.background_gradient(cmap="Blues").format(precision=0),
        width="stretch",
    )
    st.caption("Matriz simetrica: d(i,j) = d(j,i) · diagonal = 0 · fila/columna 0 = deposito.")

# =====================================================================
# TAB 2: VALORES PARAMETRICOS
# =====================================================================
with tabs[1]:
    st.header("Valores parametricos del modelo")
    st.markdown(
        """
        Estos son los **conjuntos y parametros** tal como se declaran en el modelo
        de optimizacion (AMPL), construidos a partir de los valores fijos anteriores.
        """
    )

    st.subheader("Conjuntos")
    st.markdown(
        f"""
        - **NODOS** = {{{', '.join(str(n) for n in nodos)}}}   *(deposito + clientes, |NODOS| = n = {n_total})*
        - **NODOS_SIN_DEPOSITO** = NODOS \\ {{0}} = {{{', '.join(str(c) for c in clientes)}}}
        """
    )

    st.subheader("Parametros")
    st.markdown(
        f"""
        - **d[i, j]** : distancia entre el punto *i* y el punto *j*, para todo *i, j* ∈ NODOS, *i* ≠ *j* (km)
        - **n** = |NODOS| = {n_total}
        """
    )

    st.subheader("Variables de decision")
    st.markdown(
        r"""
        - $x_{ij} \in \{0,1\}$ : 1 si la ruta va directamente del punto *i* al punto *j*; 0 en caso contrario
        - $u_i \in [1,\ n-1]$ : variable auxiliar (orden/posicion de visita del punto *i*), definida solo para *i* ≠ deposito — usada en la eliminacion de subciclos (MTZ)
        """
    )

# =====================================================================
# TAB 3: MODELO MATEMATICO
# =====================================================================
with tabs[2]:
    st.header("Formulacion matematica del modelo")

    st.subheader("Conjuntos y parametros")
    st.latex(r"""
    \begin{aligned}
    N &: \text{conjunto de todos los puntos (deposito + clientes)}, \quad |N| = n = 13 \\
    N_0 &= N \setminus \{0\} : \text{puntos sin el deposito} \\
    d_{ij} &: \text{distancia entre el punto } i \text{ y el punto } j, \quad \forall\, i,j \in N
    \end{aligned}
    """)

    st.subheader("Variables de decision")
    st.latex(r"""
    x_{ij} =
    \begin{cases}
    1 & \text{si la ruta va directamente del punto } i \text{ al punto } j \\
    0 & \text{en caso contrario}
    \end{cases}
    \qquad \forall\, i,j \in N,\ i \neq j
    """)
    st.latex(r"""
    u_i : \text{posicion de visita del punto } i \text{ en la ruta}, \qquad \forall\, i \in N_0,\quad 1 \le u_i \le n-1
    """)

    st.subheader("Funcion objetivo")
    st.markdown("Minimizar la distancia total recorrida en el ciclo cerrado:")
    st.latex(r"""
    \min Z = \sum_{i \in N} \sum_{\substack{j \in N \\ j \neq i}} d_{ij}\, x_{ij}
    """)

    st.subheader("Restricciones de salida unica y entrada unica")
    st.markdown("**(1) Salida unica** — de cada punto sale exactamente un arco:")
    st.latex(r"""
    \sum_{\substack{j \in N \\ j \neq i}} x_{ij} = 1 \qquad \forall\, i \in N
    """)
    st.markdown("**(2) Entrada unica** — a cada punto entra exactamente un arco:")
    st.latex(r"""
    \sum_{\substack{i \in N \\ i \neq j}} x_{ij} = 1 \qquad \forall\, j \in N
    """)

    st.subheader("Restricciones de eliminacion de subciclos")
    st.markdown(
        """
        Las restricciones (1) y (2) por si solas no impiden que la solucion se forme
        con **varios ciclos pequeños desconectados** (subtours) en lugar de un unico
        recorrido que pase por los 13 puntos. Existen dos formulaciones equivalentes:
        """
    )

    st.markdown("**Formulacion clasica (Dantzig–Fulkerson–Johnson, DFJ)** — conceptual:")
    st.latex(r"""
    \sum_{i \in S} \sum_{j \in S,\, j \neq i} x_{ij} \le |S| - 1
    \qquad \forall\, S \subset N,\ 2 \le |S| \le n-1
    """)
    st.caption(
        "Para cada subconjunto propio S de puntos, el numero de arcos dentro de S debe ser "
        "menor que |S|, evitando que S se cierre en un subciclo aislado. Esta formulacion es "
        "correcta pero genera un numero exponencial de restricciones (2¹³ subconjuntos), por lo "
        "que no se implementa de forma literal."
    )

    st.markdown("**Formulacion implementada (Miller–Tucker–Zemlin, MTZ)** — equivalente, lineal y practica:")
    st.latex(r"""
    u_i - u_j + (n-1)\, x_{ij} \le n - 2 \qquad \forall\, i,j \in N_0,\ i \neq j
    """)
    st.latex(r"""
    1 \le u_i \le n-1 \qquad \forall\, i \in N_0
    """)
    st.caption(
        "Las variables u(i) asignan un orden de visita a cada cliente. Si x(i,j)=1, la "
        "restriccion fuerza u(j) ≥ u(i) + 1, es decir, obliga a que el orden de visita crezca "
        "a lo largo de la ruta y rompe cualquier posibilidad de subciclos, usando solo O(n²) "
        "restricciones en vez de 2ⁿ. Esta es la version que se resuelve en AMPL y en Python."
    )

    st.subheader("Naturaleza de las variables")
    st.latex(r"""
    x_{ij} \in \{0,1\} \qquad \forall\, i,j \in N,\ i \neq j
    """)
    st.latex(r"""
    u_i \in \mathbb{R},\quad 1 \le u_i \le n - 1 \qquad \forall\, i \in N_0
    """)

# =====================================================================
# RESOLVER EL MODELO
# =====================================================================
solution = get_solution(nodos, D)

# =====================================================================
# TAB 4: RESULTADOS
# =====================================================================
with tabs[3]:
    st.header("Resultados de la optimizacion")
    st.markdown(
        """
        El modelo (formulacion MTZ) se resuelve de forma **exacta** mediante un solver
        de programacion lineal entera mixta (MILP). Esta misma formulacion esta disponible
        para ejecutarse en **AMPL** dentro de `ampl_model/` (`tsp.mod`, `tsp.dat`, `tsp.run`);
        ambos motores entregan el mismo optimo porque resuelven exactamente el mismo modelo
        matematico.
        """
    )

    if solution["status"] != "Optimal":
        st.error(f"El solver no encontro una solucion optima. Estado: {solution['status']}")
    else:
        st.success(f"Solucion **optima** encontrada — Estado: {solution['status']}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Distancia total optima", f"{solution['total_distance']:.0f} km")
        col2.metric("Arcos seleccionados", len(solution["arcs"]))
        col3.metric("Puntos visitados", solution["n_nodos"])

        st.subheader("Arcos seleccionados en la ruta optima")
        df_arcs = pd.DataFrame(solution["arcs"], columns=["Desde (i)", "Hacia (j)", "Distancia (km)"])
        df_arcs.index = df_arcs.index + 1
        st.dataframe(df_arcs, width="stretch")

        st.subheader("Secuencia de visita")
        secuencia_str = "  →  ".join(str(s) for s in solution["sequence"])
        st.markdown(f"### `{secuencia_str}`")
        st.caption("La ruta inicia y termina en el deposito (nodo 0).")

# =====================================================================
# TAB 5: GRAFO
# =====================================================================
with tabs[4]:
    st.header("Grafo de la secuencia de visita")
    st.markdown(
        """
        Las posiciones de los nodos se calcularon mediante **escalamiento multidimensional
        (MDS)** a partir de la matriz de distancias, de modo que la separacion visual entre
        puntos se aproxime a su distancia real. No son coordenadas geograficas reales.
        """
    )

    coords = get_coords(nodos, D)
    seq = solution["sequence"]

    fig = go.Figure()

    # Lineas de la ruta (en orden de visita)
    route_x = [coords[n][0] for n in seq]
    route_y = [coords[n][1] for n in seq]
    fig.add_trace(go.Scatter(
        x=route_x, y=route_y,
        mode="lines",
        line=dict(color="#2563eb", width=2.5),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Flechas de direccion sobre cada arco
    for i in range(len(seq) - 1):
        x0, y0 = coords[seq[i]]
        x1, y1 = coords[seq[i + 1]]
        fig.add_annotation(
            x=x1, y=y1, ax=x0, ay=y0,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=1.6,
            arrowcolor="#2563eb",
            standoff=14, startstandoff=14,
        )

    # Nodos clientes
    clientes_x = [coords[c][0] for c in clientes]
    clientes_y = [coords[c][1] for c in clientes]
    fig.add_trace(go.Scatter(
        x=clientes_x, y=clientes_y,
        mode="markers+text",
        marker=dict(size=26, color="#bfdbfe", line=dict(color="#1d4ed8", width=2)),
        text=[str(c) for c in clientes],
        textposition="middle center",
        textfont=dict(size=12, color="#1e3a8a"),
        name="Clientes",
        hovertext=[f"Cliente {c}" for c in clientes],
        hoverinfo="text",
    ))

    # Nodo deposito (resaltado)
    dx, dy = coords[DEPOSITO]
    fig.add_trace(go.Scatter(
        x=[dx], y=[dy],
        mode="markers+text",
        marker=dict(size=34, color="#f59e0b", line=dict(color="#92400e", width=2.5), symbol="square"),
        text=["0"],
        textposition="middle center",
        textfont=dict(size=13, color="white"),
        name="Deposito",
        hovertext=["Deposito (nodo 0)"],
        hoverinfo="text",
    ))

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=560,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
    )

    st.plotly_chart(fig, width="stretch")
    st.markdown(f"**Distancia total recorrida: {solution['total_distance']:.0f} km**")

st.divider()
st.caption(
    "Industrial Engineering · Modelo TSP resuelto con formulacion MTZ "
    "(salida unica, entrada unica, eliminacion de subciclos). "
    "Archivos AMPL disponibles en `ampl_model/`."
)
