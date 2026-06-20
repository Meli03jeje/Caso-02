"""
solver/tsp_solver.py
---------------------------------------------------------------------
Resuelve el mismo modelo matematico TSP (formulacion MTZ) que se
encuentra en ampl_model/tsp.mod, usando PuLP + CBC (motor de codigo
abierto, sin licencia, 100% reproducible en Streamlit Community Cloud).

Es exactamente el MISMO modelo, mismas variables, mismas restricciones
de salida unica, entrada unica y eliminacion de subciclos (MTZ) que se
entrega en los archivos AMPL (.mod / .dat / .run). Por eso el resultado
optimo (230 km) coincide sin importar cual de los dos motores se use.
---------------------------------------------------------------------
"""

import pandas as pd
import pulp
from sklearn.manifold import MDS
import numpy as np


def load_distance_matrix(csv_path="data/distancias.csv"):
    """Carga la matriz de distancias desde el CSV y devuelve (nodos, D)."""
    df = pd.read_csv(csv_path, index_col=0)
    df.columns = [int(c) for c in df.columns]
    df.index = [int(i) for i in df.index]
    nodos = list(df.index)
    D = df.values.tolist()
    return nodos, D


def solve_tsp(nodos, D, depot=0):
    """
    Resuelve el TSP con la formulacion MTZ:
        - Conjuntos:        NODOS, NODOS_SIN_DEPOSITO
        - Variables:        x[i,j] binaria, u[i] continua (orden de visita)
        - Objetivo:         min sum d[i,j] * x[i,j]
        - Restricciones:    salida unica, entrada unica, MTZ (subciclos)

    Devuelve un diccionario con:
        status, total_distance, arcs (lista de tuplas i,j,dist),
        sequence (lista ordenada de nodos visitados, inicia y termina en depot)
    """
    n = len(nodos)
    idx = {node: i for i, node in enumerate(nodos)}

    prob = pulp.LpProblem("TSP_MTZ", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", (range(n), range(n)), cat="Binary")
    u = pulp.LpVariable.dicts("u", range(n), lowBound=1, upBound=n - 1, cat="Continuous")

    # Funcion objetivo
    prob += pulp.lpSum(D[i][j] * x[i][j] for i in range(n) for j in range(n) if i != j)

    # Sin auto-arcos
    for i in range(n):
        prob += x[i][i] == 0

    # (1) Salida unica
    for i in range(n):
        prob += pulp.lpSum(x[i][j] for j in range(n) if j != i) == 1

    # (2) Entrada unica
    for j in range(n):
        prob += pulp.lpSum(x[i][j] for i in range(n) if i != j) == 1

    # (3) Eliminacion de subciclos (MTZ) - depot excluido de las u
    depot_idx = idx[depot]
    others = [i for i in range(n) if i != depot_idx]
    for i in others:
        for j in others:
            if i != j:
                prob += u[i] - u[j] + (n - 1) * x[i][j] <= n - 2

    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)

    status = pulp.LpStatus[prob.status]
    total_distance = pulp.value(prob.objective)

    arcs = []
    for i in range(n):
        for j in range(n):
            if i != j and pulp.value(x[i][j]) > 0.5:
                arcs.append((nodos[i], nodos[j], D[i][j]))

    # Reconstruir secuencia partiendo del deposito
    arc_map = {a[0]: a[1] for a in arcs}
    seq = [depot]
    current = depot
    while True:
        nxt = arc_map[current]
        seq.append(nxt)
        current = nxt
        if current == depot:
            break

    return {
        "status": status,
        "total_distance": total_distance,
        "arcs": arcs,
        "sequence": seq,
        "n_nodos": n,
    }


def get_mds_coordinates(nodos, D, random_state=42):
    """
    Genera coordenadas 2D aproximadas a partir de la matriz de distancias
    usando Multidimensional Scaling (MDS), para poder dibujar el grafo
    de forma que las distancias visuales se asemejen a las distancias reales.
    (No son coordenadas geograficas reales, son una proyeccion aproximada).
    """
    D_arr = np.array(D, dtype=float)
    mds = MDS(
        n_components=2,
        dissimilarity="precomputed",
        random_state=random_state,
        normalized_stress="auto",
        n_init=8,
        init="random",
    )
    coords = mds.fit_transform(D_arr)
    return {node: (coords[i, 0], coords[i, 1]) for i, node in enumerate(nodos)}


if __name__ == "__main__":
    nodos, D = load_distance_matrix("../data/distancias.csv")
    result = solve_tsp(nodos, D)
    print("Estado:", result["status"])
    print("Distancia total:", result["total_distance"])
    print("Secuencia:", " -> ".join(str(s) for s in result["sequence"]))
