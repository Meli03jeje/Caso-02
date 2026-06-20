import itertools

nodes = [0,3,10,21,22,35,40,41,47,65,71,76,77]
n = len(nodes)
D = [
 [0,29,18,16,24,32,17,28,29,27,27,33,34],
 [29,0,38,40,29,48,15,57,27,53,55,24,44],
 [18,38,0,31,42,49,22,27,21,19,36,50,16],
 [16,40,31,0,21,18,32,25,45,30,16,34,47],
 [24,29,42,21,0,20,30,46,46,48,36,14,56],
 [32,48,49,18,20,0,45,40,60,47,25,33,65],
 [17,15,22,32,30,45,0,44,16,39,45,32,30],
 [28,57,27,25,46,40,44,0,48,11,17,59,41],
 [29,27,21,45,46,60,16,48,0,40,54,48,18],
 [27,53,19,30,48,47,39,11,40,0,26,60,30],
 [27,55,36,16,36,25,45,17,54,26,0,50,52],
 [33,24,50,34,14,33,32,59,48,60,50,0,62],
 [34,44,16,47,56,65,30,41,18,30,52,62,0],
]

# Held-Karp exact DP, depot = 0
others = list(range(1, n))
C = {}
for k in others:
    C[(1 << others.index(k), k)] = (D[0][k], 0)

for subset_size in range(2, len(others)+1):
    for subset in itertools.combinations(others, subset_size):
        bits = 0
        for o in subset:
            bits |= 1 << others.index(o)
        for k in subset:
            prev_bits = bits & ~(1 << others.index(k))
            res = []
            for m in subset:
                if m == k: continue
                if (prev_bits, m) in C:
                    res.append((C[(prev_bits, m)][0] + D[m][k], m))
            if res:
                C[(bits, k)] = min(res)

bits = (1 << len(others)) - 1
res = []
for k in others:
    if (bits, k) in C:
        res.append((C[(bits, k)][0] + D[k][0], k))
opt, last = min(res)
print("Held-Karp optimal distance:", opt)

# reconstruct path
path = [0]
bits_cur = bits
k = last
seq_rev = [k]
while True:
    cost, prev = C[(bits_cur, k)]
    if prev == 0:
        break
    seq_rev.append(prev)
    bits_cur &= ~(1 << others.index(k))
    k = prev
seq_rev.append(0)
seq_rev.reverse()
full_seq = [0] + seq_rev[1:]
print("Sequence (indices):", full_seq)
print("Sequence (node ids):", [nodes[i] for i in full_seq])
