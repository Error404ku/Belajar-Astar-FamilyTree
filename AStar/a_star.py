import heapq
from neo4j_operation import get_generation, get_neighbors

def heuristic(current_name, goal_name):
    # Fungsi heuristik untuk algoritma A* yang mengukur perbedaan generasi antara dua individu
    return abs(get_generation(current_name) - get_generation(goal_name))

def a_star_search(start_name, goal_name):
    # Mengimplementasikan algoritma A* untuk menemukan jalur antara dua individu dalam silsilah keluarga
    open_set = []
    initial_h = heuristic(start_name, goal_name)
    heapq.heappush(open_set, (initial_h, 0, start_name, [start_name]))
    closed_set = set()
    steps = []

    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        h = f - g  # Menghitung h(n) dari f(n) dan g(n)

        steps.append({
            "Aksi": "Ambil dari Open Set",
            "Orang": current,
            "f(n)": f,
            "g(n)": g,
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
                tentative_g = g + 1
                tentative_h = heuristic(neighbor, goal_name)
                tentative_f = tentative_g + tentative_h
                heapq.heappush(open_set, (tentative_f, tentative_g, neighbor, path + [neighbor]))
                steps.append({
                    "Aksi": "Tambahkan ke Open Set",
                    "Orang": neighbor,
                    "f(n)": tentative_f,
                    "g(n)": tentative_g,
                    "h(n)": tentative_h,
                    "Jalur": " -> ".join(path + [neighbor])
                })

    steps.append({
        "Aksi": "Tidak Ada Jalur",
        "Orang": goal_name,
        "Jalur": "Tidak ditemukan jalur."
    })
    return None, steps
