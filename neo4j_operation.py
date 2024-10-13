import streamlit as st
from config import driver  # Mengimpor driver Neo4j dari modul config

def create_person(name, jenis_kelamin=None):
    # Membuat node 'Person' baru di database Neo4j jika belum ada
    # Menggunakan MERGE untuk memastikan node tidak diduplikasi
    query = """
    MERGE (p:Person {name: $name})
    ON CREATE SET p.jenis_kelamin = $jenis_kelamin
    ON MATCH SET p.jenis_kelamin = coalesce(p.jenis_kelamin, $jenis_kelamin)
    """
    with driver.session() as session:
        session.run(query, {'name': name, 'jenis_kelamin': jenis_kelamin})  # Menjalankan query

def tambah_relasi(orang, relasi, nama, jenis_kelamin=None):
    # Menambahkan relasi antara dua individu di database Neo4j
    # Relasi bisa berupa Ayah, Ibu, Anak, Suami, atau Istri

    # Pastikan kedua individu (orang dan nama) ada di database, jika tidak buat baru
    create_person(orang)
    create_person(nama, jenis_kelamin)

    if relasi == "Ayah":
        # Menambahkan relasi 'AYAH' antara individu dan ayahnya
        query = """
        MATCH (child:Person {name: $child_name})
        MATCH (father:Person {name: $parent_name})
        MERGE (father)-[:AYAH]->(child)
        """
        with driver.session() as session:
            session.run(query, {'child_name': orang, 'parent_name': nama})  # Menjalankan query

    elif relasi == "Ibu":
        # Menambahkan relasi 'IBU' antara individu dan ibunya
        query = """
        MATCH (child:Person {name: $child_name})
        MATCH (mother:Person {name: $parent_name})
        MERGE (mother)-[:IBU]->(child)
        """
        with driver.session() as session:
            session.run(query, {'child_name': orang, 'parent_name': nama})

    elif relasi == "Anak":
        # Menambahkan relasi 'AYAH' atau 'IBU' tergantung jenis kelamin orang tua
        if jenis_kelamin == 'laki-laki':
            query = """
            MATCH (parent:Person {name: $parent_name})
            MATCH (child:Person {name: $child_name})
            MERGE (parent)-[:AYAH]->(child)
            """
        else:
            query = """
            MATCH (parent:Person {name: $parent_name})
            MATCH (child:Person {name: $child_name})
            MERGE (parent)-[:IBU]->(child)
            """
        with driver.session() as session:
            session.run(query, {'parent_name': orang, 'child_name': nama})

    elif relasi in ["Suami", "Istri"]:
        # Menambahkan relasi dua arah sebagai 'PASANGAN'
        query = """
        MATCH (p1:Person {name: $name1})
        MATCH (p2:Person {name: $name2})
        MERGE (p1)-[:PASANGAN]->(p2)
        MERGE (p2)-[:PASANGAN]->(p1)
        """
        with driver.session() as session:
            session.run(query, {'name1': orang, 'name2': nama})

    else:
        st.error("Relasi tidak dikenal.")  # Menampilkan error jika relasi tidak dikenali

def get_person(name):
    # Mengambil informasi individu dari database Neo4j, termasuk pasangan dan anak-anaknya
    query = """
    MATCH (p:Person {name: $name})
    OPTIONAL MATCH (p)-[:PASANGAN]->(spouse:Person)
    OPTIONAL MATCH (p)-[:AYAH|IBU]->(child:Person)
    RETURN p.name AS name, p.jenis_kelamin AS jenis_kelamin,
           collect(DISTINCT spouse.name) AS pasangan,
           collect(DISTINCT child.name) AS anak
    """
    with driver.session() as session:
        result = session.run(query, {'name': name})  # Menjalankan query
        record = result.single()  # Mengambil hasil tunggal
        if record:
            # Mengembalikan informasi individu, pasangan, dan anak jika ditemukan
            return {
                'name': record['name'],
                'jenis_kelamin': record['jenis_kelamin'],
                'pasangan': [n for n in record['pasangan'] if n],  # Menghapus nilai None
                'anak': [n for n in record['anak'] if n]
            }
        else:
            return None  # Jika individu tidak ditemukan, kembalikan None

def get_all_individuals():
    # Mengambil daftar semua individu yang ada dalam database Neo4j
    query = "MATCH (p:Person) RETURN p.name AS name"
    with driver.session() as session:
        result = session.run(query)
        return [record['name'] for record in result]  # Mengembalikan daftar nama individu

def get_neighbors(person_name):
    # Mengambil daftar individu yang memiliki relasi langsung dengan individu tertentu
    # Termasuk ayah, ibu, pasangan, dan anak-anak
    query = """
    MATCH (p:Person {name: $name})
    OPTIONAL MATCH (p)-[:AYAH|IBU|PASANGAN]-(relative:Person)
    OPTIONAL MATCH (p)<-[:AYAH|IBU]-(child:Person)
    WITH collect(DISTINCT relative.name) + collect(DISTINCT child.name) AS neighbors
    UNWIND neighbors AS neighbor
    RETURN DISTINCT neighbor
    """
    with driver.session() as session:
        result = session.run(query, {'name': person_name})
        return [record['neighbor'] for record in result if record['neighbor']]  # Menghapus nilai None

def get_generation(person_name, generation=0, visited=None):
    # Menghitung tingkat generasi individu berdasarkan jumlah level orang tua (ayah atau ibu)
    if visited is None:
        visited = set()  # Membuat set untuk melacak individu yang sudah dikunjungi
    if person_name in visited:
        return generation  # Mencegah loop jika sudah dikunjungi
    visited.add(person_name)
    
    query = """
    MATCH (p:Person {name: $name})
    OPTIONAL MATCH (p)-[:AYAH]->(father:Person)
    OPTIONAL MATCH (p)-[:IBU]->(mother:Person)
    RETURN father.name AS father_name, mother.name AS mother_name
    """
    with driver.session() as session:
        result = session.run(query, {'name': person_name})
        record = result.single()
        if not record or (record['father_name'] is None and record['mother_name'] is None):
            return generation  # Jika tidak ada orang tua, kembalikan generasi saat ini
        # Rekursif menghitung generasi berdasarkan orang tua
        father_gen = get_generation(record['father_name'], generation + 1, visited) if record['father_name'] else generation
        mother_gen = get_generation(record['mother_name'], generation + 1, visited) if record['mother_name'] else generation
        return max(father_gen, mother_gen)  # Mengambil generasi terbesar dari ayah atau ibu