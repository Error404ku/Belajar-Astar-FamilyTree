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
    # Relasi dapat berupa Ayah, Ibu, Anak, Suami, atau Istri

    # Pastikan kedua individu ada di database
    create_person(orang)
    create_person(nama, jenis_kelamin)

    if relasi == "Ayah":
        # Membuat relasi AYAH antara 'father' dan 'child'
        query = """
        MATCH (child:Person {name: $child_name})
        MATCH (father:Person {name: $parent_name})
        MERGE (father)-[:AYAH]->(child)
        """          

        # Membuat relasi MERTUA antara orang tua 'orang' (suami) dan 'nama' (istri)
        query_mertua = """
        MATCH (child:Person {name: $child_name})
        MATCH (father:Person {name: $parent_name})
        OPTIONAL MATCH (pasangan:Person)-[:IBU]->(child)
        OPTIONAL MATCH (mertua:Person)-[:AYAH|IBU]->(pasangan)
        FOREACH (m IN CASE WHEN mertua IS NOT NULL THEN [mertua] ELSE [] END |
            MERGE (m)-[:MERTUA]->(father)
        )
        """         

        # Membuat relasi SAUDARA antara 'father' dan paman/bibi anaknya
        query_saudarapaman = """
        MATCH (child:Person {name: $child_name})
        MATCH (father:Person {name: $parent_name})
        OPTIONAL MATCH (uncleAunt:Person)-[:PAMAN|BIBI]->(child)
        FOREACH (ua IN CASE WHEN uncleAunt IS NOT NULL THEN [uncleAunt] ELSE [] END |
            MERGE (father)-[:SAUDARA]-(ua)
        )
        """

        with driver.session() as session:
            # Menjalankan query untuk membuat relasi AYAH antara 'father' dan 'child'
            session.run(query, {'child_name': orang, 'parent_name': nama})
            # Menjalankan query untuk membuat relasi MERTUA antara 'father' dan pasangan anak
            session.run(query_mertua, {'child_name': orang, 'parent_name': nama})
            # Menjalankan query untuk membuat relasi SAUDARA antara 'father' dan paman/bibi anaknya
            session.run(query_saudarapaman, {'child_name': orang, 'parent_name': nama})

    elif relasi == "Ibu":
        # Membuat relasi IBU antara 'mother' dan 'child'
        query = """
        MATCH (child:Person {name: $child_name})
        MATCH (mother:Person {name: $parent_name})
        MERGE (mother)-[:IBU]->(child)
        """ 

        # Membuat relasi MERTUA antara orang tua 'orang' (suami) dan 'nama' (istri)
        query_mertua = """
        MATCH (child:Person {name: $child_name})
        MATCH (mother:Person {name: $parent_name})
        OPTIONAL MATCH (pasangan:Person)-[:AYAH]->(child)
        OPTIONAL MATCH (mertua:Person)-[:AYAH|IBU]->(pasangan)
        FOREACH (m IN CASE WHEN mertua IS NOT NULL THEN [mertua] ELSE [] END |
            MERGE (m)-[:MERTUA]->(mother)
        )
        """  

        # Membuat relasi SAUDARA antara 'mother' dan paman/bibi anaknya
        query_saudarapaman = """
        MATCH (child:Person {name: $child_name})
        MATCH (mother:Person {name: $parent_name})
        OPTIONAL MATCH (uncleAunt:Person)-[:PAMAN|BIBI]->(child)
        FOREACH (ua IN CASE WHEN uncleAunt IS NOT NULL THEN [uncleAunt] ELSE [] END |
            MERGE (mother)-[:SAUDARA]-(ua)
        )
        """
        with driver.session() as session:
            # Menjalankan query untuk membuat relasi SAUDARA antara 'mother' dan paman/bibi anaknya
            session.run(query_saudarapaman, {'child_name': orang, 'parent_name': nama})
            # Menjalankan query untuk membuat relasi IBU antara 'mother' dan 'child'
            session.run(query, {'child_name': orang, 'parent_name': nama})
            # Menjalankan query untuk membuat relasi MERTUA antara orang tua (suami/istri) dan 'mother'
            session.run(query_mertua, {'child_name': orang, 'parent_name': nama})

    elif relasi == "Anak":

        # Query untuk membuat relasi AYAH
        query_ayah = """
        MATCH (parent:Person {name: $parent_name})
        MATCH (child:Person {name: $child_name})
        WHERE parent.jenis_kelamin = 'laki-laki'
            MERGE (child)-[:AYAH]->(parent)
        """

         # Query untuk membuat relasi IBU
        query_ibu = """
        MATCH (parent:Person {name: $parent_name})
        MATCH (child:Person {name: $child_name})
        WHERE parent.jenis_kelamin = 'perempuan'
            MERGE (child)-[:IBU]->(parent)
        """
        # Query untuk membuat relasi PAMAN
        query_paman = """
        MATCH (parent:Person {name: $parent_name})
        MATCH (child:Person {name: $child_name})
        OPTIONAL MATCH (paman:Person)-[:SAUDARA]-(parent)
        WHERE paman.jenis_kelamin = 'laki-laki'
            FOREACH (ua IN CASE WHEN paman IS NOT NULL THEN [paman] ELSE [] END |
                MERGE (ua)-[:PAMAN]->(child)
            )
        """

        # Query untuk membuat relasi BIBI
        query_bibi = """
        MATCH (parent:Person {name: $parent_name})
        MATCH (child:Person {name: $child_name})
        OPTIONAL MATCH (bibi:Person)-[:SAUDARA]-(parent)
        WHERE bibi.jenis_kelamin = 'perempuan'
            FOREACH (ua IN CASE WHEN bibi IS NOT NULL THEN [bibi] ELSE [] END |
                MERGE (ua)-[:BIBI]->(child)
            )
        """

        # Query untuk membuat relasi SAUDARA antara anak baru dan anak-anak lain dari orang tua yang sama
        query_saudara = """
        MATCH (parent:Person {name: $parent_name})
        MATCH (child:Person {name: $child_name})
        OPTIONAL MATCH (parent)-[:AYAH|IBU]->(otherChild:Person)
        FOREACH (oc IN CASE WHEN otherChild IS NOT NULL THEN [otherChild] ELSE [] END |
            MERGE (child)-[:SAUDARA]-(oc)
        )
        """

        # Query untuk menetapkan pasangan orang tua AYAH
        query_ayah_spouse = """
        MATCH (parent:Person {name: $parent_name})
        MATCH (child:Person {name: $child_name})
        OPTIONAL MATCH (spouse:Person)-[:PASANGAN]-(parent)
        WHERE spouse.jenis_kelamin = 'laki-laki'
            FOREACH (s IN CASE WHEN spouse IS NOT NULL THEN [spouse] ELSE [] END |
                MERGE (spouse)-[:AYAH]->(child)
            )     
        """

        # Query untuk menetapkan pasangan orang tua IBU
        query_ibu_spouse = """
        MATCH (parent:Person {name: $parent_name})
        MATCH (child:Person {name: $child_name})
        OPTIONAL MATCH (spouse:Person)-[:PASANGAN]-(parent)
        WHERE spouse.jenis_kelamin = 'perempuan'
            FOREACH (s IN CASE WHEN spouse IS NOT NULL THEN [spouse] ELSE [] END |
                     MERGE (spouse)-[:IBU]->(child)
                )  
        """

        # Jalankan semua query dalam satu sesi
        with driver.session() as session:
            # Menjalankan query AYAH
            session.run(query_ayah, {'parent_name': nama, 'child_name': orang})
            # Menjalankan query IBU
            session.run(query_ibu, {'parent_name': nama, 'child_name': orang})
            # Menjalankan query PAMAN       
            session.run(query_paman, {'parent_name': nama, 'child_name': orang})
            # Menjalankan query BIBI
            session.run(query_bibi, {'parent_name': nama, 'child_name': orang})
            # Menjalankan query SAUDARA
            session.run(query_saudara, {'parent_name': orang, 'child_name': nama})
            # Menjalankan query untuk menetapkan pasangan sebagai AYAH
            session.run(query_ayah_spouse, {'parent_name': nama, 'child_name': orang})
            # Menjalankan query untuk menetapkan pasangan sebagai IBU
            session.run(query_ibu_spouse, {'parent_name': nama, 'child_name': orang})

    elif relasi in ["Suami", "Istri"]:
         # Tentukan jenis relasi dan gender pasangan
        if jenis_kelamin == 'laki-laki':
            main_relation = "SUAMI"
        else:
            main_relation = "ISTRI"

        # Query untuk membuat relasi SUAMI atau ISTRI
        query_main_spouse = f"""
        MATCH (person1:Person {{name: $person1_name}})
        MATCH (person2:Person {{name: $person2_name}})
        MERGE (person1)-[:PASANGAN]-(person2)
        """

        # Query untuk membuat relasi SAUDARA antara Anda dan saudara pasangan
        query_saudara_pasangan = """
        MATCH (spouse:Person {name: $spouse_name})
        MATCH (person:Person {name: $person_name})
        OPTIONAL MATCH (sibling:Person)-[:SAUDARA]-(spouse)
        FOREACH (s IN CASE WHEN sibling IS NOT NULL THEN [sibling] ELSE [] END |
            MERGE (person)-[:SAUDARA]-(s)
        )
        """

        # Query untuk membuat relasi AYAH atau IBU antara Anda dan anak-anak pasangan
        query_children = f"""
        MATCH (spouse:Person {{ name: $spouse_name }})
        MATCH (person:Person {{ name: $person_name }})
        OPTIONAL MATCH (spouse)-[:AYAH|IBU]->(child:Person)
        FOREACH (c IN CASE WHEN child IS NOT NULL THEN [child] ELSE [] END |
            MERGE (person)-[:{'AYAH' if main_relation == 'SUAMI' else 'IBU'}]->(c)
        )
        """

        # Query untuk membuat relasi PAMAN antara paman pasangan dan Anda
        query_paman = """
        MATCH (spouse:Person {name: $spouse_name})
        MATCH (person:Person {name: $person_name})
        OPTIONAL MATCH (uncleAunt:Person)-[:PAMAN]->(spouse)
        FOREACH (ua IN CASE WHEN uncleAunt IS NOT NULL THEN [uncleAunt] ELSE [] END |
            MERGE (ua)-[:PAMAN]->(person)
        )
        """

        # Query untuk membuat relasi BIBI antara bibi pasangan dan Anda
        query_bibi = """
        MATCH (spouse:Person {name: $spouse_name})
        MATCH (person:Person {name: $person_name})
        OPTIONAL MATCH (uncleAunt:Person)-[:BIBI]->(spouse)
        FOREACH (ua IN CASE WHEN uncleAunt IS NOT NULL THEN [uncleAunt] ELSE [] END |
            MERGE (ua)-[:BIBI]->(person)
        )
        """

        # Query untuk membuat relasi MERTUA antara orang tua pasangan dan Anda
        query_mertua = """
        MATCH (spouse:Person {name: $spouse_name})
        MATCH (person:Person {name: $person_name})
        OPTIONAL MATCH (parent:Person)-[:AYAH|IBU]->(spouse)
        FOREACH (p IN CASE WHEN parent IS NOT NULL THEN [parent] ELSE [] END |
            MERGE (p)-[:MERTUA]->(person)
        )
        """

        with driver.session() as session:
            # Menjalankan query SUAMI atau ISTRI
            session.run(query_main_spouse, {'person1_name': orang, 'person2_name': nama})
            # Menjalankan query SAUDARA pasangan
            session.run(query_saudara_pasangan, {'spouse_name': orang, 'person_name': nama})
            # Menjalankan query AYAH atau IBU untuk anak-anak pasangan
            session.run(query_children, {'spouse_name': orang, 'person_name': nama})
            # Menjalankan query PAMAN untuk paman pasangan
            session.run(query_paman, {'spouse_name': orang, 'person_name': nama})
            # Menjalankan query BIBI untuk bibi pasangan
            session.run(query_bibi, {'spouse_name': orang, 'person_name': nama})
            # Menjalankan query MERTUA untuk orang tua pasangan
            session.run(query_mertua, {'spouse_name': orang, 'person_name': nama})

    else:
        st.error("Relasi tidak dikenal.")

def get_person(name):
    # Mengambil informasi individu dari database Neo4j, termasuk pasangan dan anak-anaknya
    query = """
    MATCH (p:Person {name: $name})
    OPTIONAL MATCH (p)-[:PASANGAN]->(spouse:Person)
    OPTIONAL MATCH (p)<-[:AYAH]-(child:Person)
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
    OPTIONAL MATCH (p)-[:AYAH|IBU|PASANGAN|SAUDARA|MERTUA|PAMAN|BIBI]-(relative:Person)
    WITH collect(DISTINCT relative.name) AS neighbors
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

    # Query untuk mengambil ayah dan ibu dalam satu kali query
    query = """
    MATCH (p:Person {name: $name})
    OPTIONAL MATCH (father:Person)-[:AYAH]->(p)
    OPTIONAL MATCH (mother:Person)-[:IBU]->(p)
    RETURN father.name AS father_name, mother.name AS mother_name
    """
    with driver.session() as session:
        result = session.run(query, {'name': person_name})
        record = result.single()

        # Jika individu tidak memiliki ayah atau ibu, kembalikan generasi saat ini
        if not record or (record['father_name'] is None and record['mother_name'] is None):
            return generation  

        # Rekursif menghitung generasi berdasarkan orang tua
        father_gen = generation
        mother_gen = generation

        if record['father_name']:
            father_gen = get_generation(record['father_name'], generation + 1, visited)
        
        if record['mother_name']:
            mother_gen = get_generation(record['mother_name'], generation + 1, visited)
        
        # Mengambil generasi terbesar dari ayah atau ibu
        return max(father_gen, mother_gen)