import mysql.connector

# Konfigurasi koneksi ke database
config = {
    'user': 'root',          # Ganti dengan username MySQL Anda
    'password': '',      # Ganti dengan password MySQL Anda
    'host': 'localhost',         # atau alamat IP server MySQL Anda
    'database': 'sispakdao'      # Nama database Anda
}

try:
    # Membuat koneksi
    conn = mysql.connector.connect(**config)
    
    if conn.is_connected():
        print("Berhasil terhubung ke database sispakdao!")
        
        # Membuat cursor
        cursor = conn.cursor()
        
        # Mengambil semua data dari tabel
        cursor.execute("SELECT * FROM user")
        
        # Menampilkan hasil query
        results = cursor.fetchall()
        for row in results:
            print("Nama_User:", row[0])
            print("Email_User:", row[1])
            print("Password_User:", row[2])
            print("No_User:", row[3])
            print()  # Baris kosong untuk memisahkan setiap row
    
except mysql.connector.Error as err:
    print(f"Terjadi kesalahan: {err}")

finally:
    # Menutup koneksi
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("Koneksi ke database ditutup.")
