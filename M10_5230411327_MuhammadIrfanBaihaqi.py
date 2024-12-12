import mysql.connector
from mysql.connector import Error

def koneksi():
    try:
        # Koneksi ke database
        connection = mysql.connector.connect(
            host='localhost',       
            database='penjualan',  
            user='root',       
            password='' 
        )
        return connection

    except Error as e:
        print("Error saat mencoba menghubungkan ke MySQL", e)


from tabulate import tabulate
import string
import random
import os
# pip install reportlab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class Pegawai:
    def __init__(self) -> None:
        pass

    @classmethod
    def tambahpegawai(cls):
        while True:
            nikstr = input("Masukkan NIK pegawai: ")
            cek = nikstr.isdigit()
            if cek == True: 
                nik = int(nikstr)
                nama = input("Masukkan Nama pegawai: ")
                alamat = input("Masukkan alamat pegawai: ")
                conn = koneksi()
                cur = conn.cursor()
                cur.execute("INSERT INTO pegawai VALUES(%s,%s,%s)", (nik,nama,alamat))
                conn.commit()
                conn.close()
                # cls.daftarpegawai.append(pegawaibaru) #objek dimasukkan ke dalam list class
                os.system('cls')
                print("PEGAWAI BERHASIL DITAMBAHKAN...")
                os.system('pause')
                return True
            else:
                print("NIK HARUS BERUPA ANGKA")
                #debug
                
    @classmethod
    def tampilsemuapegawai(cls):
        conn = koneksi()
        if conn is None:
            print("Koneksi ke database gagal.")
            return
        cur = conn.cursor()
        cur.execute("SELECT * FROM pegawai")
        data = cur.fetchall()
        conn.close()
        header = ["NIK", "Nama Pegawai", "Alamat Pegawai"]
        # Mengakses elemen tuple menggunakan indeks
        dataUser = [[data[0], data[1], data[2]] for data in data]
        print(tabulate(dataUser, headers=header, tablefmt="grid"))

    @classmethod
    def hapuspegawai(cls):
        try:
            conn = koneksi()
            if conn is None:
                print("Koneksi ke database gagal.")
                return
            cur = conn.cursor()
            Pegawai.tampilsemuapegawai()
            try:
                nik_hapus = int(input("Masukkan NIK pegawai yang akan dihapus: "))
            except ValueError:
                print("NIK harus berupa angka.")
                return
            cur.execute("SELECT * FROM pegawai WHERE nik_pegawai = %s", (nik_hapus,))
            pegawai = cur.fetchone()
            if pegawai:
                cur.execute("DELETE FROM pegawai WHERE nik_pegawai = %s", (nik_hapus,))
                conn.commit()
                conn.close()
                print("Pegawai berhasil dihapus.")
                return True
            else:
                print("Pegawai tidak ditemukan.")
                return
        except mysql.connector.Error as e: #pegawai sudah pernah melakukan transaksi
            print("Error saat menghapus data pegawai:", e)
            return
        

    @staticmethod
    def generate_id(): #METHOD UNTUK MEMBUAT ID
        characters = string.ascii_letters + string.digits
        unique_id = ''.join(random.choices(characters, k=4))
        return unique_id
        


    @classmethod
    def tambahtransaksi(cls):
        try:
            totalBayar = 0
            cls.tampilsemuapegawai()
            conn = koneksi()
            cur = conn.cursor()
            nik_pegawai = input("Masukkan kode pegawai yang membuat transaksi: ")
            cur.execute("SELECT * FROM pegawai WHERE nik_pegawai = %s", (nik_pegawai,))
            pegawai = cur.fetchone()
            if pegawai:
                    id_struk = cls.generate_id() 
                    # customer melakukan transaksi pembelian beberapa barang dalam 1 waktu > maka akan menghasilkan 1 struk
                    # setiap pembelian barang menghasilkan id trasaksi , tetapi masih 1 id struk yang sama JIKA MASIH UNTUK CUSTOMER ITU DAN DALAM WAKTU ITU.
                    while True:
                        Produk.tampilkanproduk()
                        produkbeli = input("SILAHKAN MASUKKAN KODE PRODUK: ")
                        cur.execute("SELECT * FROM produk WHERE id_produk = %s", (produkbeli,))
                        produk = cur.fetchone()
                        if produk:
                            id_transaksi = cls.generate_id()
                            try:
                                jumlah_produk = int(input("Masukkan jumlah produk yang dibeli: "))
                                if jumlah_produk > 0:
                                    Transaksi.createTransaksi(id_transaksi)
                                    # print("P berhasil membuat transaksi") #debug
                                    Struk.createStruk(id_struk, id_transaksi, produkbeli, nik_pegawai, jumlah_produk)
                                    totalBayar += produk[3] * jumlah_produk
                                    sudah = input("Apakah TRANSAKSI SUDAH SELESAI (y/n)?: ")
                                    if sudah.lower() == "y":
                                        cls.pembayaran(id_struk, totalBayar)
                                        Struk.buat_struk_pdf_dari_db(id_struk) #akan membuat pdf file untuk struk kali ini
                                        return True
                                    else:
                                        continue
                                else: #debug
                                    print("gagal menambahkan produk beli, jumlah beli harus lebih dari 0")
                                    os.system('pause')
                            except ValueError:
                                print("JUMLAH PRODUK HARUS BERUPA ANGKA")
                                print("gagal menambahkan produk beli")
                                os.system('pause')
                                continue
                        else:
                            print("PRODUK TIDAK ADA")
                            os.system('pause')
                            os.system('cls')
                            continue       
            else:
                print("Pegawai Tidak Ada , GAGAL MELAKUKAN TRANSAKSI...")
                os.system('pause')
                return True
        except Exception as e:
            print("Error:", e)

    @classmethod
    def pembayaran(cls, id_struk, totalBayar):
        conn = koneksi()
        cur = conn.cursor()
        metodeBayar = {
            "1" : "TUNAI",
            "2" : "DANA",
            "3" : "OVO",
            "4" : "GOPAY",
            "5" : "LINKAJA",
            "6" : "SHOPEEPAY"
        }
        while True: 
            for key, value in metodeBayar.items():
                print(f"{key}. {value}")
            metode_bayar = input("Pilih metode pembayaran (1-6): ")
            membayar = input("Masukkan jumlah uang yang dibayarkan: ")
            cek = membayar.isdigit()
            if metode_bayar in metodeBayar and cek == True:
                membayar = int(membayar)
                if membayar < totalBayar:
                    print("Uang tidak cukup.")
                    os.system('pause')
                    continue
                else:
                    conn = koneksi()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO Pembayaran(id_pembayaran, id_struk, metode_bayar, membayar) VALUES (%s, %s, %s, %s)", (cls.generate_id() ,id_struk, metode_bayar, membayar))
                    conn.commit()
                    print("Pembayaran berhasil.")
                    os.system('pause')
                    return True
            else:
                print("Metode pembayaran tidak valid. Silakan pilih metode yang benar.")

    def printStruckToPDFbyID(cls, id_struk):
        Struk.tampilsemuastruk()
        id_struk = input("Masukkan ID Struk: ")
        conn = koneksi()
        cur = conn.cursor()
        cur.execute("SELECT * FROM struk WHERE id_struk = %s", (id_struk,))
        struk = cur.fetchone()
        if struk:
            Struk.buat_struk_pdf_dari_db(id_struk)
            return True
        print("Struk tidak ditemukan.")
        os.system('pause')
        os.system('cls')
        return False

class Transaksi:

    def __init__(self) -> None:
        pass

    @classmethod
    def createTransaksi(cls, id_transaksi): # METHOD UNTUK MEMBUAT TRANSAKSI BARU
        conn = koneksi()
        if conn is None:
            print("Koneksi ke database gagal.")
            return
        cur = conn.cursor()

        try:
            masukan_catatan = input("Apakah ingin Masukkan catatan untuk transaksi barang ini? (y/n): ")
            if masukan_catatan.lower() == "y":
                catatan = input("Masukkan catatan: ")
                detail_transaksi = catatan
                cur.execute("INSERT INTO transaksi (id_transaksi, detail_transaksi) VALUES (%s, %s)", (id_transaksi, detail_transaksi))
            else:
                detail_transaksi = ""
                cur.execute("INSERT INTO transaksi (id_transaksi, detail_transaksi) VALUES (%s, %s)", (id_transaksi, detail_transaksi))
            
            conn.commit()
            # print("berhasil dibuat.")
        except mysql.connector.Error as e:
            print("Error saat memasukkan data ke tabel transaksi:", e)
        except Exception as ex:
            print("Unexpected error:", ex)
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        

class Struk:

    def __init__(self) -> None:
        pass
    
    @classmethod
    def createStruk(cls, id_struk, id_transaksi, produkbeli, nik_pegawai, jumlah_produk):
        try:

            conn = koneksi()
            if conn is None:
                print("Koneksi ke database gagal.")
                return

            cur = conn.cursor()
            query = ("INSERT INTO struk (id_struk, id_transaksi, id_produk, nik_pegawai, jumlah_produk) "
                     "VALUES (%s, %s, %s, %s, %s)")
            values = (id_struk, id_transaksi, produkbeli, nik_pegawai, jumlah_produk)

            cur.execute(query, values)
            conn.commit()
            conn.close()

        except mysql.connector.Error as e:
            print("Error saat memasukkan data ke tabel struk:", e)
        except Exception as ex:
            print("Unexpected error:", ex)
        finally:
            if conn.is_connected():
                cur.close()
                conn.close()

    
    @classmethod
    def tampilsemuastruk(cls):
        conn = koneksi()
        cur = conn.cursor()
        cur.execute("SELECT s.id_struk, s.id_transaksi, p.nama_produk, s.jumlah_produk, p.harga, s.waktu_transaksi, pg.nama_pegawai FROM struk s JOIN produk p ON s.id_produk = p.id_produk JOIN pegawai pg ON s.nik_pegawai = pg.nik_pegawai")
        data = cur.fetchall()
        header = ["ID Struk", "ID Transaksi", "Nama Produk", "Nama Pegawai", "Jumlah Produk","Harga Produk", "Total Harga", "Waktu Transaksi"]
        datastruk = [[o[0], o[1], o[2], o[6], o[3], o[4], o[3] * o[4], o[5]] for o in data]
        conn.close()
        print(tabulate(datastruk, headers=header, tablefmt="grid"))
        os.system('pause')

    @classmethod
    def tampilstrukbywaktu(cls):
        try:
            tanggal = input("Masukkan tanggal (YYYY-MM-DD): ")
            conn = koneksi()
            cur = conn.cursor()
            cur.execute("SELECT s.id_struk, s.id_transaksi, p.nama_produk, s.jumlah_produk, p.harga, s.waktu_transaksi, pg.nama_pegawai FROM struk s JOIN produk p ON s.id_produk = p.id_produk JOIN pegawai pg ON s.nik_pegawai = pg.nik_pegawai WHERE DATE(s.waktu_transaksi) = %s", (tanggal,))
            data = cur.fetchall()
            header = ["ID Struk", "ID Transaksi", "Nama Produk", "Nama Pegawai", "Jumlah Produk","Harga Produk", "Total Harga", "Waktu Transaksi"]
            datastruk = [[o[0], o[1], o[2], o[6], o[3], o[4], o[3] * o[4], o[5]] for o in data]
            conn.close()
            if datastruk:
                print(tabulate(datastruk, headers=header, tablefmt="grid"))
            else:
                print("Tidak ada data struk pada tanggal tersebut.")
                os.system('pause')
            os.system('pause')
        except Exception as e:
            print("Error:", e)
            os.system('pause')

    @classmethod
    def buat_struk_pdf_dari_db(cls, id_struk="0000", nama_file="struk.pdf"):
        # Koneksi ke database
        conn = koneksi()
        if conn is None:
            print("Koneksi ke database gagal.")
            return
        cur = conn.cursor(dictionary=True)

        try:
            # Query untuk header dan item transaksi
            cur.execute(
                """
                SELECT
                    struk.id_struk,
                    struk.id_transaksi, 
                    struk.waktu_transaksi, 
                    pegawai.nama_pegawai AS kasir, 
                    produk.nama_produk AS nama, 
                    produk.harga AS harga_satuan, 
                    struk.jumlah_produk, 
                    (struk.jumlah_produk * produk.harga) AS subtotal,
                    pembayaran.membayar AS Bayar,
                    pembayaran.metode_bayar AS Metode_Bayar
                FROM struk 
                JOIN produk ON struk.id_produk = produk.id_produk 
                JOIN pegawai ON struk.nik_pegawai = pegawai.nik_pegawai
                JOIN pembayaran ON struk.id_struk = pembayaran.id_struk 
                WHERE struk.id_struk = %s
                """,
                (id_struk,)
            )
            print("Query berhasil dijalankan.")

            data_items = cur.fetchall()
            # print(f"Data items berhasil diambil: {data_items}") # Debugging print statement

            if not data_items:
                print("Tidak ada data transaksi dengan ID tersebut.")
                os.system("pause")
                return

            # Debugging print statement
            # print(f"Isi Data items setelah pengecekan: {data_items}")

            # Data untuk header
            data_struk = {
                'id_transaksi': data_items[0]['id_struk'],
                'tanggal': data_items[0]['waktu_transaksi'],
                'kasir': data_items[0]['kasir'],
                'item': [
                    {
                        'nama': item['nama'],
                        'qty': item['jumlah_produk'],
                        'harga_satuan': item['harga_satuan'],
                        'subtotal': item['subtotal'],
                    }
                    for item in data_items
                ],
                'total': sum(item['subtotal'] for item in data_items),
                'pembayaran': data_items[0]['Bayar'],  # Sesuaikan dengan data pembayaran di database
                'kembalian': data_items[0]['Bayar'] - sum(item['subtotal'] for item in data_items),  
            }

        except mysql.connector.Error as e:
            print("Error saat mengambil data dari database:", e)
            return
        except Exception as e:
            print("Unexpected error:", e)
            return
        finally:
            # Tutup koneksi database
            cur.close()
            conn.close()

        # Set ukuran halaman dan buat canvas
        nama_file = f"Struk_{id_struk}.pdf"
        print(f"Menyimpan file PDF dengan nama: {nama_file}")  # Debugging
        c = canvas.Canvas(nama_file, pagesize=letter)
        width, height = letter

        try:
            # Header Struk
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(width / 2, height - 50, "Warung Bebas Galau")
            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, height - 65, "Jl. Kebahagiaan No. 42, Yogyakarta")
            c.drawCentredString(width / 2, height - 80, "Telp: 0812-3456-7890")

            # Informasi Transaksi
            c.setFont("Helvetica", 10)
            y_position = height - 120
            c.drawString(50, y_position, f"ID Transaksi: {data_struk['id_transaksi']}")
            c.drawString(50, y_position - 15, f"Tanggal    : {data_struk['tanggal']}")
            c.drawString(50, y_position - 30, f"Kasir      : {data_struk['kasir']}")

            # Garis pemisah
            c.line(50, y_position - 40, width - 50, y_position - 40)

            # Header Item
            y_position -= 60
            c.drawString(50, y_position, "Item")
            c.drawString(200, y_position, "Qty")
            c.drawString(250, y_position, "Harga Satuan")
            c.drawString(350, y_position, "Subtotal")

            # Isi Item
            y_position -= 20
            for item in data_struk['item']:
                c.drawString(50, y_position, item['nama'])
                c.drawString(200, y_position, str(item['qty']))
                c.drawString(250, y_position, f"Rp {item['harga_satuan']:,}")
                c.drawString(350, y_position, f"Rp {item['subtotal']:,}")
                y_position -= 15

            # Garis pemisah kedua
            c.line(50, y_position - 5, width - 50, y_position - 5)

            # Total dan Pembayaran
            y_position -= 30
            c.drawString(250, y_position, "Total:")
            c.drawString(350, y_position, f"Rp {data_struk['total']:,}")

            y_position -= 15
            c.drawString(250, y_position, "Pembayaran:")
            c.drawString(350, y_position, f"Rp {data_struk['pembayaran']:,}")

            y_position -= 15
            c.drawString(250, y_position, "Kembalian:")
            c.drawString(350, y_position, f"Rp {data_struk['kembalian']:,}")

            # Footer Struk
            y_position -= 40
            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, y_position, "Terima kasih telah berbelanja di Warung Bebas Galau")

            # Simpan file PDF
            c.save()
            print("File PDF berhasil disimpan.")  # Debugging
        except Exception as e:
            print("Error saat membuat PDF:", e)






class Produk:
    def __init__(self):
        pass
    
    @staticmethod
    def generate_id(): #METHOD UNTUK MEMBUAT ID PRODUK OTOMATIS
        characters = string.ascii_letters + string.digits
        unique_id = ''.join(random.choices(characters, k=4))
        return unique_id

    @classmethod
    def tampilkanproduk(cls):
        conn = koneksi()
        if conn is None:
            print("Koneksi ke database gagal.")
            return
        cur = conn.cursor()
        cur.execute("SELECT * FROM produk")
        data = cur.fetchall()
        conn.close()
        header = ["Kode Produk", "Nama Produk", "Jenis", "Harga"]
        # Mengakses elemen tuple menggunakan indeks
        dataUser = [[o[0], o[1], o[2], o[3]] for o in data]
        print(tabulate(dataUser, headers=header, tablefmt="grid"))


    @classmethod
    def tambahproduk(cls):
        try:
            nama_produk = input("Masukkan nama produk: ")
            kategori = {
                "1": "Snack",
                "2": "Minuman",
                "3": "Makanan"
            }
            while True:
                print("Pilih kategori produk:")
                for key, value in kategori.items():
                    print(f"{key}. {value}")
                han = input("Masukkan pilihan Anda: ")
                if han in kategori:
                    jenis_produk = kategori[han]
                else:
                    print("Pilihan tidak valid. Silakan pilih Kategori kembali.")
                    continue
                
                hargastr = input("Masukkan Harga Produk Satuan: ")
                cek = hargastr.isdigit()
                if cek == True:
                    harga = int(hargastr)
                    conn = koneksi()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO produk VALUES (%s,%s,%s,%s)", (cls.generate_id(), nama_produk, jenis_produk, harga))
                    conn.commit()
                    conn.close()
                    print(f"produk {nama_produk}, berhasi ditambahkan")
                    return True
                else:
                    print("harga harus angka")
                    continue
        except ValueError as e:
            print(f"Terjadi kesalahan: {e}")

    @classmethod
    def hapusProduk(cls):
        try:
            cls.tampilkanproduk()
            produk = input("Masukkan kode produk yang ingin dihapus: ")
            conn = koneksi()
            cur = conn.cursor()
            cur.execute("SELECT * FROM produk WHERE id_produk = %s", (produk,))
            data = cur.fetchone()
            if data:
                cur.execute("DELETE FROM produk WHERE id_produk = %s", (produk,))
                conn.commit()
                conn.close()
                print(f"Produk dengan kode {produk} berhasil dihapus.")
                return True
            else:
                print(f"Produk dengan kode {produk} tidak ditemukan.")
                return False
        except mysql.connector.Error as e: #produk sudah pernah dibeli. untuk menjaga integritas data > maka tidak bisa dihapus
            print(f"Terjadi kesalahan: {e}")
        

def tampilanMenuUtama():
        print("\n==============================")
        print("        MENU UTAMA        ")
        print("==============================")
        print("1. Tambah Pegawai")
        print("2. Tambah Produk")
        print("3. Tampilkan Seluruh Product")
        print("4. Hapus Produk")
        print("5. Tampilkan Semua Pegawai")
        print("6. Hapus Pegawai")
        print("7. Buat Transaksi Baru")
        print("8. Tampilkan Riwayat Seluruh Struk Transaksi")
        print("9. Tampilkan Riwayat Struk Transaksi pada waktu tertentu")
        print("10. Print Struk Transaksi dengan ID")
        print("0. Exit")
        print("===============================")

def menu():
    while True:
        os.system('cls')
        tampilanMenuUtama()
        pilih = input("PILIH MENU: ")
        if pilih == "1":
            Pegawai.tambahpegawai()
        elif pilih == "2":
            Produk.tambahproduk()
            os.system('pause')
        elif pilih == "3":
            Produk.tampilkanproduk()
            os.system('pause')
        elif pilih == "4":
            Produk.hapusProduk()
            os.system('pause')
        elif pilih == "5":
            Pegawai.tampilsemuapegawai()
            os.system('pause')
        elif pilih == "6":
            Pegawai.hapuspegawai()
            os.system('pause')
        elif pilih == "7":
            Pegawai.tambahtransaksi()
        elif pilih == "8":
            Struk.tampilsemuastruk()
        elif pilih == "9":
            Struk.tampilstrukbywaktu()
        elif pilih == "10":
            Struk.tampilsemuastruk()
            id_struk = input("Masukkan ID Struk: ")
            Struk.buat_struk_pdf_dari_db(id_struk)
        elif pilih == "0":
            print("Anda Keluar Program")
            return True
        else:
            print("Ulang ya")
            os.system('pause')

if __name__ == "__main__":
    menu()






