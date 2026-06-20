/* =====================================================================
   MODELO: Problema del Agente Viajero (TSP)
   Empresa de distribucion - 1 deposito + 12 clientes (13 puntos)
   Formulacion: Miller-Tucker-Zemlin (MTZ) para eliminacion de subciclos
   ===================================================================== */

# --------------------------- CONJUNTOS ---------------------------------
set NODOS;                                   # Deposito + clientes (13 puntos)
set NODOS_SIN_DEPOSITO = NODOS diff {0};     # Todos menos el deposito (para MTZ)

# --------------------------- PARAMETROS ---------------------------------
param d {NODOS, NODOS} >= 0;                 # Matriz de distancias d(i,j), en km
param n := card(NODOS);                      # Numero total de puntos (13)

# --------------------------- VARIABLES DE DECISION -----------------------
# x[i,j] = 1 si la ruta va directamente del punto i al punto j; 0 en otro caso
var x {i in NODOS, j in NODOS: i <> j} binary;

# u[i] = posicion (orden) de visita del punto i en la ruta (variable auxiliar MTZ)
var u {i in NODOS_SIN_DEPOSITO} >= 1, <= n - 1;

# --------------------------- FUNCION OBJETIVO ----------------------------
# Minimizar la distancia total recorrida en el ciclo cerrado
minimize DistanciaTotal:
    sum {i in NODOS, j in NODOS: i <> j} d[i,j] * x[i,j];

# --------------------------- RESTRICCIONES --------------------------------

# (1) Salida unica: de cada punto sale exactamente un arco
subject to Salida_Unica {i in NODOS}:
    sum {j in NODOS: j <> i} x[i,j] = 1;

# (2) Entrada unica: a cada punto entra exactamente un arco
subject to Entrada_Unica {j in NODOS}:
    sum {i in NODOS: i <> j} x[i,j] = 1;

# (3) Eliminacion de subciclos - formulacion MTZ
#     Garantiza que la solucion sea UN UNICO ciclo que pasa por los 13 puntos,
#     y no varios ciclos pequeños desconectados entre si.
subject to Eliminacion_Subciclos {i in NODOS_SIN_DEPOSITO, j in NODOS_SIN_DEPOSITO: i <> j}:
    u[i] - u[j] + (n - 1) * x[i,j] <= n - 2;
