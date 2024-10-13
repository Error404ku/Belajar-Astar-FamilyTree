import heapq
from neo4j_operation import get_generation, get_neighbors, get_person

def heuristic(current_name, goal_name):
    # Menggunakan jarak generasi sebagai heuristic dasar
    generation_diff = abs(get_generation(current_name) - get_generation(goal_name))
    
    # Menggunakan pembobotan relasi untuk memperkecil/memperbesar nilai heuristic
    person_data = get_person(current_name)
    
    if person_data:
        if goal_name in person_data['anak']:
            return 0.5 * generation_diff  # Lebih dekat untuk anak
        elif goal_name in person_data['pasangan']:
            return 0.7 * generation_diff  # Lebih dekat untuk pasangan
        elif goal_name in person_data['saudara']:
            return 1.0 * generation_diff  # Saudara
        elif goal_name in person_data['paman'] or goal_name in person_data['bibi']:
            return 1.5 * generation_diff  # Lebih jauh untuk paman/bibi
    
    return 2.0 * generation_diff  # Default, misalnya saudara jauh atau yang lainnya

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
                # Menggunakan jenis relasi untuk menghitung bobot heuristik (misal: relasi AYAH lebih penting dari SAUDARA)
                person_data = get_person(current)
                relation_weight = 1  # Bobot default
                if person_data:
                    if neighbor in person_data['anak']:
                        relation_weight = 0.5  # Bobot lebih rendah untuk anak
                    elif neighbor in person_data['pasangan']:
                        relation_weight = 0.7  # Bobot untuk pasangan
                
                neighbor_h = heuristic(neighbor, goal_name) * relation_weight
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