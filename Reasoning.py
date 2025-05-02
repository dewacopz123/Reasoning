import pandas as pd

# Fungsi Keanggotaan Servis
def fuzzify_service(x):
    rendah = 0
    sedang = 0
    tinggi = 0

    # Rendah: 1 hingga 10, turun sampai 0 di 50
    if x <= 10:
        rendah = 1
    elif 10 < x < 50:
        rendah = (50 - x) / (50 - 10)
    elif x >= 50:
        rendah = 0

    # Sedang: 0 di 30, naik sampai 1 di 50, tetap 1 sampai 60, turun sampai 0 di 80
    if 30 < x < 50:
        sedang = (x - 30) / (50 - 30)
    elif 50 <= x <= 60:
        sedang = 1
    elif 60 < x < 80:
        sedang = (80 - x) / (80 - 60)
    else:
        sedang = max(0, sedang)

    # Tinggi: 0 di 60, naik ke 1 di 90, tetap 1 sampai 100
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


# Fungsi Keanggotaan Harga
def fuzzify_harga(x):
    murah = 0
    sedang = 0
    mahal = 0

    # Murah: 1 dari 0–25.000, turun ke 0 di 35.000
    if x <= 25000:
        murah = 1
    elif 25000 < x < 35000:
        murah = (35000 - x) / (35000 - 25000)
    elif x >= 35000:
        murah = 0

    # Sedang: 0 di 30.000, naik ke 1 di 40.000, turun ke 0 di 50.000
    if 30000 < x < 40000:
        sedang = (x - 30000) / (40000 - 30000)
    elif 40000 <= x <= 45000:
        sedang = 1
    elif 45000 < x < 50000:
        sedang = (50000 - x) / (50000 - 45000)
    else:
        sedang = max(0, sedang)

    # Mahal: 0 di 45000, naik ke 1 di 55000, tetap 1 sampai 70000
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


# Skor Output
output_scores = {
    'tidak layak': 20,
    'kurang': 35,
    'cukup': 50,
    'layak': 75,
    'sangat layak': 90
}

# Inferensi Berdasarkan Aturan
def inferensi(servis, harga):
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

# Defuzzifikasi (Centroid)
def defuzzify(fuzzy_output):
    numerator = sum(alpha * output_scores[kat] for kat, alpha in fuzzy_output.items())
    denominator = sum(fuzzy_output.values())
    return numerator / denominator if denominator != 0 else 0

# Main Program
def main():
    df = pd.read_excel("restoran.xlsx")

    hasil = []

    for index, row in df.iterrows():
        id_pelanggan = row["id Pelanggan"]
        pelayanan = row["Pelayanan"]
        harga = row["harga"]

        fuzzy_s = fuzzify_service(pelayanan)
        fuzzy_h = fuzzify_price(harga)
        fuzzy_output = inferensi(fuzzy_s, fuzzy_h)
        skor = defuzzify(fuzzy_output)

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
