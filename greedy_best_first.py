import heapq
from neo4j_operation import get_generation, get_neighbors

def heuristic(current_name, goal_name):
    # Fungsi heuristik yang mengukur perbedaan generasi antara dua individu
    return abs(get_generation(current_name) - get_generation(goal_name))

def greedy_best_first_search(start_name, goal_name):
    # Mengimplementasikan Greedy Best First Search untuk menemukan jalur antara dua individu dalam silsilah keluarga
    open_set = []
    initial_h = heuristic(start_name, goal_name)
    heapq.heappush(open_set, (initial_h, start_name, [start_name]))
    closed_set = set()
    steps = []

    while open_set:
        h, current, path = heapq.heappop(open_set)
        
        steps.append({
            "Aksi": "Ambil dari Open Set",
            "Orang": current,
            "h(n)": h,
            "Jalur": " -> ".join(path)
        })

        if current == goal_name:
            steps.append({
                "Aksi": "Tujuan Ditemukan",
                "Orang": current,
                "Jalur": " -> ".join(path)
            })
            return path, steps

        if current in closed_set:
            continue

        closed_set.add(current)

        neighbors = get_neighbors(current)

        for neighbor in neighbors:
            if neighbor not in closed_set:
                neighbor_h = heuristic(neighbor, goal_name)
                heapq.heappush(open_set, (neighbor_h, neighbor, path + [neighbor]))
                steps.append({
                    "Aksi": "Tambahkan ke Open Set",
                    "Orang": neighbor,
                    "h(n)": neighbor_h,
                    "Jalur": " -> ".join(path + [neighbor])
                })

    steps.append({
        "Aksi": "Tidak Ada Jalur",
        "Orang": goal_name,
        "Jalur": "Tidak ditemukan jalur."
    })
    return None, steps
