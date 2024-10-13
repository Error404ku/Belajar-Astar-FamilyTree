import streamlit as st
import pandas as pd
from neo4j_operation import (
    create_person,
    tambah_relasi,
    get_person,
    get_all_individuals
)
from greedy_best_first import greedy_best_first_search

# Aplikasi Streamlit

st.title("Sistem Silsilah Keluarga dengan Neo4j")

st.header("Input Individu")
nama_individu_baru = st.text_input("Nama individu baru:")
jenis_kelamin_baru = st.selectbox("Jenis kelamin individu baru:", ("laki-laki", "perempuan"))

if st.button("Tambah Individu"):
    if nama_individu_baru:
        create_person(nama_individu_baru, jenis_kelamin_baru)
        st.success(f"{nama_individu_baru} ({jenis_kelamin_baru}) telah ditambahkan ke dalam sistem.")
    else:
        st.error("Nama individu tidak boleh kosong.")

all_individuals = get_all_individuals()

if all_individuals:
    st.header("Pilih Individu untuk Ditampilkan")
    current_person = st.selectbox("Pilih individu:", options=all_individuals, key='current_person')

    if current_person:
        data_individu = get_person(current_person)
        if data_individu:
            st.write(f"**Individu saat ini:** {data_individu['name']} ({data_individu['jenis_kelamin']})")
            pasangan = ', '.join(data_individu['pasangan']) if data_individu['pasangan'] else 'Tidak ada pasangan'
            st.write(f"Pasangan: {pasangan}")
            anak = ', '.join(data_individu['anak']) if data_individu['anak'] else 'Tidak ada anak'
            st.write(f"Anak: {anak}")
        else:
            st.error("Data individu tidak ditemukan.")

        st.subheader("Tambahkan Relasi")
        jenis_relasi = st.selectbox("Pilih jenis relasi:", ("Ayah", "Ibu", "Anak", "Suami", "Istri"), key='jenis_relasi')
        nama_relasi = st.text_input(f"Nama {jenis_relasi.lower()}:", key='nama_relasi')
        jenis_kelamin_relasi = st.selectbox(
            "Jenis kelamin:",
            ("laki-laki", "perempuan"),
            key='jenis_kelamin_relasi'
        ) if jenis_relasi in ["Anak", "Suami", "Istri"] else None

        if st.button(f"Tambahkan {jenis_relasi}"):
            if nama_relasi:
                tambah_relasi(
                    current_person,
                    jenis_relasi,
                    nama_relasi,
                    jenis_kelamin_relasi if jenis_kelamin_relasi else None
                )
                st.success(
                    f"{jenis_relasi} {nama_relasi} telah ditambahkan untuk {current_person}."
                )
            else:
                st.error(f"Nama {jenis_relasi.lower()} tidak boleh kosong.")

    st.header("Cari dan Tampilkan Silsilah dengan A*")
    if len(all_individuals) >= 2:
        # Input untuk memilih individu awal dan tujuan
        starting_person = st.selectbox("Pilih individu awal untuk pencarian:", options=all_individuals, index=0, key='starting_person')
        individu_tujuan = st.selectbox("Pilih individu tujuan yang ingin dicari silsilahnya:", options=all_individuals, index=0, key='individu_tujuan')

        if starting_person and individu_tujuan:
            if st.button("Cari Silsilah dengan A*"):
                path, steps = greedy_best_first_search(starting_person, individu_tujuan)
                if path:
                    st.success(f"Silsilah dari **{starting_person}** ke **{individu_tujuan}** ditemukan:")
                    st.write(" -> ".join(path))
                else:
                    st.error(f"Tidak ada silsilah yang ditemukan dari **{starting_person}** ke **{individu_tujuan}**.")

                if steps:
                    st.header("Langkah-Langkah Proses A*")
                    steps_df = pd.DataFrame(steps)
                    st.dataframe(steps_df)
    else:
        st.warning("Tambahkan lebih banyak individu untuk melakukan pencarian silsilah.")
else:
    st.warning("Belum ada individu dalam sistem. Tambahkan individu terlebih dahulu.")

# Pastikan untuk menutup driver saat aplikasi dihentikan
# Catatan: Streamlit tidak memiliki event on_session_end, jadi kita dapat membiarkan driver tetap terbuka
