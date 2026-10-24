# Phase 01 — Memahami Data Transaksi Nyata

## Apa yang ingin dijawab?

> Berapa nilai penjualan tercatat, produk apa yang mendominasi, negara mana yang menyumbang aktivitas penjualan, dan seberapa bisa dipercaya perhitungannya?

Dataset UCI tidak berbentuk `1 baris = 1 order`. **Satu baris = satu item pada satu invoice**. Satu `InvoiceNo` bisa muncul di banyak baris jika sebuah pesanan membeli lebih dari satu jenis produk.

## Kolom asli

- `InvoiceNo`: nomor invoice; dimulai `C` untuk cancellation
- `StockCode`: ID produk (bukan angka numerik untuk dijumlahkan)
- `Description`: nama produk
- `Quantity`: jumlah unit pada baris item
- `InvoiceDate`: tanggal/waktu invoice
- `UnitPrice`: harga per unit **GBP (£)**
- `CustomerID`: identitas pelanggan, bisa kosong
- `Country`: negara

## Praktik Pandas

Setelah file resmi diletakkan di `data/raw/Online Retail.xlsx`, buat file sementara atau jalankan Python console:

```python
import pandas as pd

df = pd.read_excel("data/raw/Online Retail.xlsx", dtype={"InvoiceNo":"string", "StockCode":"string"})
print(df.head())
print(df.shape)
print(df.dtypes)
print(df.isna().sum())
print("Distinct invoices:", df["InvoiceNo"].nunique())
print("Cancellation lines:", df["InvoiceNo"].str.upper().str.startswith("C",na=False).sum())
```

Kenapa `dtype="string"`? Nomor invoice dan stok adalah **identifier**, bukan jumlah yang perlu dihitung. Kita tidak ingin kehilangan format atau salah menganggapnya angka.

### Cara membaca fungsi

- `pd.read_excel()` membuka workbook ke bentuk DataFrame.
- `.head()` menampilkan lima baris pertama.
- `.shape` menghasilkan `(jumlah_baris, jumlah_kolom)`.
- `.dtypes` memeriksa tipe data.
- `.isna().sum()` menghitung missing values tiap kolom.
- `.nunique()` menghitung jumlah nilai unik (bukan jumlah baris).
- `.str.startswith("C")` membantu mengenali pembatalan invoice berdasarkan dokumentasi sumber.

## Hal yang perlu dipikirkan

1. Mengapa menjumlahkan baris tidak sama dengan menghitung order?
2. Mengapa invoice yang diawali `C` tidak langsung kita masukkan ke grafik penjualan biasa?
3. Mengapa `CustomerID` kosong tidak berarti penjualannya harus dihapus?
4. Bagaimana cara mengetahui suatu metrik **tidak bisa** dihitung dari dataset (misalnya profit margin)?

### Latihan mandiri

Coba hitung jumlah negara unik, rata-rata `Quantity`, dan proporsi baris yang kehilangan `CustomerID`. Catat apakah rata-rata `Quantity` dipengaruhi transaksi negatif.

## Tugas berikutnya

Jalankan `python -m scripts.prepare`, baca `data/processed/data_quality.json`, dan jelaskan masing-masing kelompok baris (`sale`, `cancellation`, `other_or_invalid`).
