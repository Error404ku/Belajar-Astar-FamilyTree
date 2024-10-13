import streamlit as st
import pandas as pd
from neo4j_operation import (
    create_person,  # Fungsi untuk membuat individu baru di Neo4j
    tambah_relasi,  # Fungsi untuk menambah relasi antara dua individu
    get_person,  # Fungsi untuk mendapatkan data satu individu berdasarkan nama
    get_all_individuals  # Fungsi untuk mendapatkan semua individu yang ada di sistem
)
from greedy_best_first import greedy_best_first_search  # Algoritma pencarian greedy best first

# Aplikasi Streamlit

st.title("Sistem Silsilah Keluarga dengan Neo4j")  # Judul aplikasi
tab1, tab2, tab3 = st.tabs(["Penambahan individu baru", "Penambahan relasi", "Pencarian data"]) # Membuat Tab

with tab1:
    st.header("Input Individu")  # Header untuk bagian input individu
    nama_individu_baru = st.text_input("Nama individu baru:")  # Input untuk nama individu baru
    jenis_kelamin_baru = st.selectbox("Jenis kelamin individu baru:", ("laki-laki", "perempuan"))  # Input jenis kelamin

    # Tombol untuk menambahkan individu baru
    if st.button("Tambah Individu"):
        if nama_individu_baru:
            create_person(nama_individu_baru, jenis_kelamin_baru)  # Memanggil fungsi create_person untuk menambah individu
            st.success(f"{nama_individu_baru} ({jenis_kelamin_baru}) telah ditambahkan ke dalam sistem.")  # Pesan sukses
        else:
            st.error("Nama individu tidak boleh kosong.")  # Pesan error jika input nama kosong

    all_individuals = get_all_individuals()  # Mengambil semua individu yang ada di sistem

with tab2:
    if all_individuals:
        st.header("Pilih Individu untuk Ditampilkan")  # Header untuk memilih individu
        current_person = st.selectbox("Pilih individu:", options=all_individuals, key='current_person')  # Dropdown untuk memilih individu

        if current_person:
            data_individu = get_person(current_person)  # Mengambil data individu yang dipilih
            if data_individu:
                # Menampilkan informasi individu yang dipilih
                st.write(f"**Individu saat ini:** {data_individu['name']} ({data_individu['jenis_kelamin']})")
                pasangan = ', '.join(data_individu['pasangan']) if data_individu['pasangan'] else 'Tidak ada pasangan'  # Menampilkan pasangan jika ada
                st.write(f"Pasangan: {pasangan}")
                anak = ', '.join(data_individu['anak']) if data_individu['anak'] else 'Tidak ada anak'  # Menampilkan anak jika ada
                st.write(f"Anak: {anak}")
            else:
                st.error("Data individu tidak ditemukan.")  # Pesan error jika data individu tidak ditemukan

            st.subheader("Tambahkan Relasi")  # Subheader untuk menambahkan relasi
            jenis_relasi = st.selectbox("Pilih jenis relasi:", ("Ayah", "Ibu", "Anak", "Suami", "Istri"), key='jenis_relasi')  # Dropdown untuk memilih jenis relasi
            nama_relasi = st.text_input(f"Nama {jenis_relasi.lower()}:", key='nama_relasi')  # Input nama relasi
            # Input jenis kelamin relasi, hanya diperlukan untuk relasi anak, suami, atau istri
            jenis_kelamin_relasi = st.selectbox(
                "Jenis kelamin:",
                ("laki-laki", "perempuan"),
                key='jenis_kelamin_relasi'
            ) if jenis_relasi in ["Anak", "Suami", "Istri"] else None

            # Tombol untuk menambahkan relasi
            if st.button(f"Tambahkan {jenis_relasi}"):
                if nama_relasi:
                    tambah_relasi(
                        current_person,
                        jenis_relasi,
                        nama_relasi,
                        jenis_kelamin_relasi if jenis_kelamin_relasi else None  # Tambahkan jenis kelamin relasi jika tersedia
                    )
                    st.success(
                        f"{jenis_relasi} {nama_relasi} telah ditambahkan untuk {current_person}."  # Pesan sukses jika relasi berhasil ditambahkan
                    )
                else:
                    st.error(f"Nama {jenis_relasi.lower()} tidak boleh kosong.")  # Pesan error jika nama relasi kosong
with tab3:
    st.header("Cari dan Tampilkan Silsilah dengan Greedy Best First")  # Header untuk pencarian silsilah
    if len(all_individuals) >= 2:
        # Input untuk memilih individu awal dan tujuan pencarian
        starting_person = st.selectbox("Pilih individu awal untuk pencarian:", options=all_individuals, index=0, key='starting_person')
        individu_tujuan = st.selectbox("Pilih individu tujuan yang ingin dicari silsilahnya:", options=all_individuals, index=0, key='individu_tujuan')

        if starting_person and individu_tujuan:
            # Tombol untuk memulai pencarian silsilah
            if st.button("Cari Silsilah dengan Greedy Best First"):
                path, steps = greedy_best_first_search(starting_person, individu_tujuan)  # Memanggil algoritma pencarian greedy best first
                if path:
                    # Menampilkan hasil pencarian jika ditemukan
                    st.success(f"Silsilah dari **{starting_person}** ke **{individu_tujuan}** ditemukan:")
                    st.write(" -> ".join(path))  # Menampilkan path yang ditemukan
                else:
                    st.error(f"Tidak ada silsilah yang ditemukan dari **{starting_person}** ke **{individu_tujuan}**.")  # Pesan error jika tidak ada path

                if steps:
                    st.header("Langkah-Langkah Proses Greedy Best First")  # Header untuk langkah-langkah proses pencarian
                    steps_df = pd.DataFrame(steps)  # Mengubah langkah-langkah menjadi DataFrame
                    st.dataframe(steps_df)  # Menampilkan langkah-langkah dalam bentuk tabel
        else:
            st.warning("Tambahkan lebih banyak individu untuk melakukan pencarian silsilah.")  # Pesan jika belum ada cukup individu untuk pencarian
    else:
        st.warning("Belum ada individu dalam sistem. Tambahkan individu terlebih dahulu.")  # Pesan jika belum ada individu yang ditambahkan

# Pastikan untuk menutup driver saat aplikasi dihentikan
# Catatan: Streamlit tidak memiliki event on_session_end, jadi kita dapat membiarkan driver tetap terbuka
