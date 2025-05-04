import pandas as pd

# -------------------------------
# FUZZIFICATION: Fungsi Keanggotaan untuk Kualitas Servis
# Linguistik: Rendah, Sedang, Tinggi (Range: 1–100)
# -------------------------------
def fuzzify_service(x):
    rendah = 0
    sedang = 0
    tinggi = 0

    # Rendah: Derajat keanggotaan penuh (1) jika x <= 10, turun linear sampai 0 di x = 50
    if x <= 10:
        rendah = 1
    elif 10 < x < 50:
        rendah = (50 - x) / (50 - 10)
    else:
        rendah = 0

    # Sedang: Naik dari 0 di x = 30 ke 1 di x = 50, tetap 1 hingga x = 60, turun ke 0 di x = 80
    if 30 < x < 50:
        sedang = (x - 30) / (50 - 30)
    elif 50 <= x <= 60:
        sedang = 1
    elif 60 < x < 80:
        sedang = (80 - x) / (80 - 60)
    else:
        sedang = max(0, sedang)

    # Tinggi: Naik dari 0 di x = 60 ke 1 di x = 90, tetap 1 sampai x = 100
    if 60 < x < 90:
        tinggi = (x - 60) / (90 - 60)
    elif x >= 90:
        tinggi = 1
    else:
        tinggi = max(0, tinggi)

    return {
        'rendah': rendah,
        'sedang': sedang,
        'tinggi': tinggi
    }

# -------------------------------
# FUZZIFICATION: Fungsi Keanggotaan untuk Harga
# Linguistik: Murah, Sedang, Mahal (Range: 25.000–55.000)
# -------------------------------
def fuzzify_harga(x):
    murah = 0
    sedang = 0
    mahal = 0

    # Murah: Derajat keanggotaan penuh (1) jika x <= 25000, turun ke 0 di x = 35000
    if x == 25000:
        murah = 1
    elif 25000 < x < 35000:
        murah = (35000 - x) / (35000 - 25000)
    else:
        murah = 0

    # Sedang: Naik dari 0 di x = 30000 ke 1 di x = 40000, tetap 1 hingga x = 45000, turun ke 0 di x = 50000
    if x <= 30000 or x >= 50000:
        sedang = 0
    elif 30000 < x < 40000:
        sedang = (x - 30000) / (40000 - 30000)
    elif 40000 < x < 50000:
        sedang = (50000 - x) / (50000 - 40000)
    elif x == 40000:
        sedang = 1

    # Mahal: Naik dari 0 di x = 45000 ke 1 di x = 55000, tetap 1 sampai x = 70000
    if 45000 < x < 55000:
        mahal = (x - 45000) / (55000 - 45000)
    elif x >= 55000:
        mahal = 1
    else:
        mahal = max(0, mahal)

    return {
        'murah': murah,
        'sedang': sedang,
        'mahal': mahal
    }

# -------------------------------
# Output Fuzzy Set untuk Defuzzification (Kelayakan)
# Nilai representatif untuk: Tidak Layak, Kurang, Cukup, Layak, Sangat Layak
# -------------------------------
output_scores = {
    'tidak layak': 10,
    'kurang': 35,
    'cukup': 55,
    'layak': 75,
    'sangat layak': 100
}

# -------------------------------
# INFERENSI: Menentukan hasil dari kombinasi fuzzy input
# Berdasarkan aturan fuzzy logic (BAB 2 poin 3)
# -------------------------------
def inferensi(servis, harga):
    # Aturan inferensi dalam bentuk (service, harga) => output kelayakan
    rules = {
        ('tinggi', 'murah'): 'sangat layak',
        ('tinggi', 'sedang'): 'layak',
        ('tinggi', 'mahal'): 'cukup',
        ('sedang', 'murah'): 'layak',
        ('sedang', 'sedang'): 'cukup',
        ('sedang', 'mahal'): 'kurang',
        ('rendah', 'murah'): 'cukup',
        ('rendah', 'sedang'): 'kurang',
        ('rendah', 'mahal'): 'tidak layak'
    }

    result = {}
    # Evaluasi setiap kombinasi nilai fuzzy input
    for s_kat, s_val in servis.items():
        for h_kat, h_val in harga.items():
            alpha = min(s_val, h_val)
            if alpha > 0:
                kategori = rules[(s_kat, h_kat)]
                if kategori in result:
                    result[kategori] = max(result[kategori], alpha)
                else:
                    result[kategori] = alpha
    return result

# -------------------------------
# DEFUZZIFICATION: Center of Gravity (COG)
# Mengubah fuzzy output ke skor numerik
# -------------------------------
def defuzzifikasi(output):
    pembilang = sum(alpha * output_scores[kategori] for kategori, alpha in output.items())
    penyebut = sum(alpha for alpha in output.values())
    return pembilang / penyebut if penyebut != 0 else 0

# -------------------------------
# PROGRAM UTAMA
# 1. Membaca data restoran.xlsx
# 2. Melakukan fuzzification
# 3. Menjalankan inferensi fuzzy
# 4. Defuzzifikasi untuk mendapatkan skor
# 5. Menyimpan 5 restoran terbaik ke peringkat.xlsx
# -------------------------------
def main():
    df = pd.read_excel("restoran.xlsx")

    hasil = []

    for index, row in df.iterrows():
        id_pelanggan = row["id Pelanggan"]
        pelayanan = row["Pelayanan"]
        harga = row["harga"]

        fuzzy_s = fuzzify_service(pelayanan)
        fuzzy_h = fuzzify_harga(harga)
        fuzzy_output = inferensi(fuzzy_s, fuzzy_h)
        skor = defuzzifikasi(fuzzy_output)

        hasil.append({
            'ID Pelanggan': id_pelanggan,
            'Pelayanan': pelayanan,
            'Harga': harga,
            'Skor': skor
        })

    hasil_df = pd.DataFrame(hasil)
    hasil_terbaik = hasil_df.sort_values(by='Skor', ascending=False).head(5)
    hasil_terbaik.to_excel("peringkat.xlsx", index=False)
    print("Output berhasil disimpan ke peringkat.xlsx")

if __name__ == "__main__":
    main()
