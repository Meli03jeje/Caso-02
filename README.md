# Scripts de verificacion (no son parte de la app)

Estos dos scripts se usaron para **comprobar de forma independiente** que
230 km es el optimo global antes de construir la app:

- `solve_reference.py` : resuelve el mismo modelo MTZ con PuLP/CBC (referencia).
- `held_karp_check.py` : resuelve el TSP con programacion dinamica exacta
  (Held-Karp), un metodo totalmente distinto que no depende de MILP.

Ambos coinciden en 230 km y en la misma secuencia de visita, lo cual
confirma que la solucion reportada es la optima global (no una heuristica).

Ejecutar: `python3 solve_reference.py` o `python3 held_karp_check.py`
