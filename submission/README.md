# Proyek Analisis Data: Beijing Multi-Site Air Quality Dataset (2013–2017)

**Oleh:** Jason Adriel Gerard Abidano  
**Program:** Belajar Analisis Data dengan Python – Dicoding

## Deskripsi Proyek
Proyek ini menganalisis kualitas udara dari **12 stasiun pemantauan di Beijing** ([Beijing Multi-Site Air Quality Dataset - UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data) / Folder Google Drive [PRSA_Data_20130301-20170228](https://drive.google.com/drive/folders/1G6a79gLjlo-87N0E15Nmt65DzROxus_X) / [Air-quality-dataset.zip](https://drive.google.com/file/d/1RhU3gJlkteaAQfyn9XOVAz7a5o1-etgr/view?usp=drivesdk), 420.768 baris observasi per jam) untuk menjawab 3 pertanyaan bisnis berstandar **SMART** serta menyajikan teknik analisis lanjutan berupa **Clustering (Manual Grouping & Binning berdasarkan [US EPA PM2.5 AQI Breakpoints](https://www.epa.gov/sites/default/files/2016-04/documents/2012_aqi_factsheet.pdf) dan [AQICN Revised PM2.5 Breakpoints](https://aqicn.org/faq/2013-09-09/revised-pm25-aqi-breakpoints/))** dan **Geospatial Analysis**.

## Struktur Direktori Submission
```
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── PRSA_Data_Aotizhongxin_20130301-20170228.csv
│   └── ... (12 file CSV stasiun Beijing)
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Cara Menjalankan Dashboard Streamlit di Local

1. **Persiapan Environment (Conda atau venv)**
   ```bash
   conda create --name main-ds python=3.11
   conda activate main-ds
   pip install -r requirements.txt
   ```

2. **Menjalankan Aplikasi Streamlit**
   ```bash
   streamlit run dashboard/dashboard.py
   ```
   *(Atau jika berada di dalam folder yang sama: `streamlit run dashboard.py`)*
