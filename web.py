# -*- coding: utf-8 -*-
"""Web.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1x-HRcUd0J5Q0uMltA3o9-2rMTIlUTidq
"""

import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
#import statsmodels.api as sm
import calendar
import matplotlib.pyplot as plt
from tensorflow import keras
import io
import base64
import joblib
from tensorflow.keras.models import load_model
from scipy import stats
from datetime import datetime
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.preprocessing import MinMaxScaler

st.sidebar.title("Harga Telur Ayam Ras Jawa Tengah")
menu = st.sidebar.radio("Navigasi", ["About", "Home", "Prediksi", 'Peramalan Masa Depan'])
st.sidebar.header("Informasi")
st.sidebar.info("""
    Model yang digunakan:
    - ARIMAX (2,0,0)
    - LSTM 1 layer, dengan 128 neuron
""")

if menu == "About":
  def show_about_page():
    st.set_page_config(page_title="Tentang Aplikasi", layout="wide")

    # Bagian 1: Header dengan Logo
    col1, col2 = st.columns([1, 4])

    with col1:
        # Pastikan file 'logo_jateng.png' ada di direktori yang sama
        try:
            logo_jateng = Image.open('logo_jateng.png')
            st.image(logo_jateng, width=150)
        except:
            st.warning("Logo tidak ditemukan")

    with col2:
        st.title("📝 Tentang Aplikasi Prediksi Harga Telur Ayam Ras")

    st.markdown("---")

    st.markdown("""
    ## 🎯 Tujuan Aplikasi
    Aplikasi ini dikembangkan untuk memprediksi harga telur ayam ras di Jawa Tengah dengan mempertimbangkan berbagai faktor eksternal
    yang memengaruhi fluktuasi harganya.
    """)

    st.markdown("""
    ## 🔍 Cakupan Data
    **Sumber Data:**
    - Data resmi dari [Pusat Informasi Harga Pangan Strategis (PIHPS)](https://www.bi.go.id/hargapangan)

    **Periode Data:**
    - Januari 2019 hingga Desember 2024

    **Lokasi:**
    - Wilayah Jawa Tengah
    """)

    st.markdown("""
    ## 📊 Faktor yang Dipertimbangkan
    Aplikasi ini melakukan prediksi mempertimbangkan beberapa faktor eksternal dalam prediksi harga telur:

    - **Harga Telur Ayam Ras** (Variabel Target)
    - **Harga Daging Ayam** (Faktor Eksternal)
    - **Harga Daging Sapi** (Faktor Eksternal)
    - **Pekan Sebelum Libur Nasional** (Faktor Eksternal)
    """)

    st.markdown("""
    ## 🧠 Metode Prediksi
    Sistem prediksi menggunakan pemodelan Hybrid ARIMAX-LSTM
    """)

    st.markdown("""
    ## 👨‍💻 Pengembang
    Aplikasi ini dikembangkan oleh:
    - [Divayanti Febri Sakina]
    - [divayantiferbisakina20@gmail.com]
    """)

    st.markdown("""
    ## 📜 Lisensi
    Aplikasi ini bersifat open-source dan dapat dikembangkan lebih lanjut oleh pihak yang berkepentingan.
    """)

  if __name__ == "__main__":
    show_about_page()

elif menu == "Home":
  # Judul Aplikasi
  st.set_page_config(page_title="Harga Komoditas Jawa Tengah", layout="wide")
  st.title('📊 Analisis Harga Komoditas Jawa Tengah')
  st.markdown("Visualisasi Harga Harian Komoditas Periode Januari 2019 - Desember 2024 (Senin-Jumat)")

  # Pastikan data sudah dimuat dengan benar
  try:
      df = pd.read_excel('data_penelitian.xlsx')  # Sesuaikan dengan sumber data Anda

      # Konversi kolom Tanggal ke datetime jika belum
      if not pd.api.types.is_datetime64_any_dtype(df['Tanggal']):
          df['Tanggal'] = pd.to_datetime(df['Tanggal'])

      # Dapatkan range tahun dari data
      min_year = df['Tanggal'].dt.year.min()
      max_year = df['Tanggal'].dt.year.max()

  except Exception as e:
      st.error(f"Gagal memuat data: {str(e)}")
      st.stop()

  # Dapatkan range tahun dari data
  min_year = df['Tanggal'].dt.year.min()
  max_year = df['Tanggal'].dt.year.max()

  # Konfigurasi bulan
  months = {
      "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
      "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
      "September": 9, "Oktober": 10, "November": 11, "Desember": 12
  }

  # UI Filter Tanggal
  with st.form("date_filter"):
      col1, col2, col3 = st.columns([2, 2, 1.5])

      with col1:
          st.subheader("Mulai")
          start_year = st.selectbox("Tahun Mulai", options=range(min_year, max_year+1), index=0)
          start_month = st.selectbox("Bulan Mulai", options=list(months.keys()), index=0)
          _, num_days = calendar.monthrange(start_year, months[start_month])
          start_day = st.selectbox("Hari Mulai", options=range(1, num_days+1), index=0)

      with col2:
          st.subheader("Akhir")
          end_year = st.selectbox("Tahun Akhir", options=range(min_year, max_year+1),
                            index=len(range(min_year, max_year+1))-1)
          end_month = st.selectbox("Bulan Akhir", options=list(months.keys()), index=11)
          _, num_days = calendar.monthrange(end_year, months[end_month])
          end_day = st.selectbox("Hari Akhir", options=range(1, num_days+1), index=num_days-1)

      with col3:
          st.subheader("Visualisasi")
          st.write("")
          submit_button = st.form_submit_button("Tampilkan", type="primary")

  # Proses Filter Data dan Tampilkan Visualisasi
  if submit_button:
      try:
          start_date = datetime(start_year, months[start_month], start_day)
          end_date = datetime(end_year, months[end_month], end_day)

          if start_date > end_date:
              st.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir!")
              end_date = start_date

          filtered_df = df[(df['Tanggal'] >= pd.to_datetime(start_date)) &
                          (df['Tanggal'] <= pd.to_datetime(end_date))]

          # Visualisasi
          st.subheader("Grafik Harga Komoditas")

          fig, ax = plt.subplots(figsize=(12, 6))
          filtered_df.plot(x='Tanggal', y=['Harga_Telur', 'Harga_Daging_Ayam', 'Harga_Daging_Sapi'],
                          ax=ax, title='Perkembangan Harga Komoditas')
          ax.set_ylabel("Harga (Rp)")
          ax.grid(True)
          st.pyplot(fig)

      except Exception as e:
          st.error(f"Error: {str(e)}")
  else:
      st.info("Silakan pilih rentang tanggal dan klik 'Tampilkan' untuk melihat visualisasi data")

elif menu == "Prediksi":
  def plot_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

  def mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


  # Fungsi preprocessing
  def arimax_lstm_pred(df):
      prg = st.progress(0, text="Sedang memproses data...")

      st.subheader("Data Input")
      st.dataframe(df)

      st.subheader("Preprocessing Data")

      # Pastikan kolom Tanggal ada
      if 'Tanggal' in df.columns:
          df['Tanggal'] = pd.to_datetime(df['Tanggal'])
          df = df.set_index('Tanggal')
      else:
          st.error("Kolom 'Tanggal' tidak ditemukan dalam dataset")
          return None, None

      preprocessing_results = {}

      # Missing value
      st.write("### Penanganan Missing Values")
      cols_to_check = ['Harga_Telur', 'Harga_Daging_Ayam', 'Harga_Daging_Sapi']
      available_cols = [col for col in cols_to_check if col in df.columns]

      missing_before = df[available_cols].isnull().sum()
      preprocessing_results['missing_before'] = missing_before.to_dict()

      plt.figure(figsize=(10, 5))
      missing_before.plot(kind='bar', color='red')
      plt.title('Missing Values Sebelum Penanganan')
      plt.ylabel('Jumlah')
      st.pyplot(plt)
      preprocessing_results['missing_before_plot'] = plot_to_base64()

      for col in available_cols:
          df[col] = df[col].interpolate(method='time')

      missing_after = df[available_cols].isnull().sum()
      preprocessing_results['missing_after'] = missing_after.to_dict()

      plt.figure(figsize=(10, 5))
      missing_after.plot(kind='bar', color='green')
      plt.title('Missing Values Setelah Penanganan Dengan Interpolasi')
      plt.ylabel('Jumlah')
      st.pyplot(plt)
      preprocessing_results['missing_after_plot'] = plot_to_base64()

      # Deteksi outlier
      st.write("### Deteksi Outlier")
      outlier_results = {}

      numeric_cols = df.select_dtypes(include=[np.number]).columns
      for col in numeric_cols:
          Q1 = np.percentile(df[col].dropna(), 25)
          Q3 = np.percentile(df[col].dropna(), 75)
          IQR = Q3 - Q1
          lower = Q1 - 1.5 * IQR
          upper = Q3 + 1.5 * IQR
          outliers = df[(df[col] < lower) | (df[col] > upper)]

          outlier_results[col] = {
              'Q1': Q1, 'Q3': Q3, 'IQR': IQR,
              'lower_bound': lower, 'upper_bound': upper,
              'outlier_count': len(outliers)
          }

          plt.figure(figsize=(12, 6))
          plt.plot(df.index, df[col], label='Data Normal')
          plt.scatter(outliers.index, outliers[col], color='red', label='Outlier')
          plt.title(f'Outlier Detection untuk {col}')
          plt.xlabel('Tanggal')
          plt.ylabel('Harga')
          plt.legend()
          st.pyplot(plt)

      preprocessing_results['outliers'] = outlier_results

      prg.progress(100, text="Preprocessing selesai!")

      st.write("### Statistika Deskriptif")
      st.dataframe(df[available_cols].describe())

      return df, preprocessing_results


  # Fungsi analisis
  def analyze_data(df):
      st.write("### Pembagian Data Train dan Data Test")

      train = df[:-11]
      test = df[-11:]

      # Visualisasi jumlah baris train vs test (bar chart)
      train_len = len(train)
      test_len = len(test)

      labels = ['Train', 'Test']
      values = [train_len, test_len]
      colors = ['skyblue', 'salmon']

      plt.figure(figsize=(3, 6))
      plt.bar(labels, values, color=colors)
      plt.title('Jumlah Baris Data Train dan Test')
      plt.ylabel('Jumlah Baris')
      plt.grid(axis='y', linestyle='--', alpha=0.7)

      for i, v in enumerate(values):
          plt.text(i, v + 1, str(v), ha='center', fontweight='bold')

      plt.tight_layout()
      plt.show()
      st.pyplot(plt)

      # ====== Uji ADF ======
      adf_result = adfuller(train['Harga_Telur'])

      adf_df = pd.DataFrame({
          'Metric': ['ADF Statistic', 'p-value', 'Is Stationary?'],
          'Value': [adf_result[0], adf_result[1], 'Ya' if adf_result[1] <= 0.05 else 'Tidak']
      })

      st.subheader("Uji Stasioneritas ADF")
      st.dataframe(adf_df)

      # ====== Transformasi Box-Cox ======
      st.subheader("Transformasi Box-Cox Harga Telur")
      transformed, lmbda = stats.boxcox(train['Harga_Telur'])

      # Plot sebelum dan sesudah transformasi
      fig1, ax = plt.subplots(1, 2, figsize=(12, 4))
      ax[0].plot(train['Harga_Telur'])
      ax[0].set_title("Sebelum Transformasi")
      ax[1].plot(transformed)
      ax[1].set_title("Setelah Transformasi Box-Cox")
      st.pyplot(fig1)

      # ====== Plot ACF & PACF ======
      st.subheader("📊 Plot ACF dan PACF Setelah Transformasi")
      fig2, ax = plt.subplots(2, 1, figsize=(12, 8))
      plot_acf(transformed, lags=50, ax=ax[0])
      plot_pacf(transformed, lags=50, ax=ax[1])
      st.pyplot(fig2)
      return train, test, transformed, lmbda, adf_result

  # Upload dan eksekusi
  st.header("Upload Dataset")

  uploaded_file = st.file_uploader(
      "Upload File Excel Dengan Kolom: Tanggal, Harga_Telur, Harga_Daging_Ayam, Harga_Daging_Sapi, Pekan Sebelum Libur",
      type=['xlsx'],
      help="Format harus mengandung kolom: Tanggal, Harga_Telur, Harga_Daging_Ayam, Harga_Daging_Sapi, Pekan Sebelum Libur"
  )

  if uploaded_file is not None:
      try:
          if uploaded_file.name.endswith('.xlsx'):
              df = pd.read_excel(uploaded_file)
              st.success("File berhasil diunggah!")
          else:
              st.error("Hanya file .xlsx yang diperbolehkan.")

          required_cols = ['Tanggal', 'Harga_Telur', 'Harga_Daging_Ayam', 'Harga_Daging_Sapi', 'Pekan_Sebelum_Libur']
          missing_cols = [col for col in required_cols if col not in df.columns]

          if missing_cols:
              st.error(f"Kolom yang diperlukan tidak ditemukan: {', '.join(missing_cols)}")
          else:
              if st.button("🔍 Prediksi Data Hybrid ARIMAX-LSTM"):
                with st.spinner("Memproses prediksi..."):
                  df, preprocessing_results = arimax_lstm_pred(df)
                  train, test, transformed, lmbda, adf_result = analyze_data(df)

                  # Pembagian Variabel
                  y_train = train['Harga_Telur']
                  y_test = test['Harga_Telur']
                  x_train = train[['Harga_Daging_Ayam','Harga_Daging_Sapi','Pekan_Sebelum_Libur']]
                  x_test = test[['Harga_Daging_Ayam','Harga_Daging_Sapi','Pekan_Sebelum_Libur']]

                  st.subheader("Variabel Target dan Variabel Eksogen")

                  st.write("**Variabel Target (y):**")
                  st.dataframe(y_train.reset_index())

                  st.write("**Variabel Eksogen (x)**")
                  st.dataframe(x_train.reset_index())

                  # ARIMAX
                  st.subheader("Pemodelan ARIMAX")
                  model_arimax = SARIMAX(endog=y_train, exog=x_train, order=[2, 0, 0])
                  results = model_arimax.fit()
                  results.summary()
                  st.subheader("Ringkasan Model ARIMAX [2,0,0]")
                  st.text(results.summary())

                  st.write("**Hasil Prediksi ARIMAX**")
                  forecast_arimax = results.forecast(steps=len(y_test), exog=x_test)
                  st.dataframe(forecast_arimax)

                  #Visualisasi
                  fig, ax = plt.subplots(figsize=(10, 5))
                  ax.plot(y_test.index, y_test, label="Test", color="blue")
                  ax.plot(y_test.index, forecast_arimax, label="Forecast", linestyle="--", color="red")
                  ax.set_title("Perbandingan Data Prediksi vs Data Asli")
                  ax.set_xlabel("Tanggal")
                  ax.set_ylabel("Harga Telur")
                  ax.legend()
                  ax.grid(True)
                  st.write("**Visualisasi Data Prediksi vs Data Asli**")
                  st.pyplot(fig)

                  #Evaluasi ARIMAX
                  st.success(f"MAPE ARIMAX: {mape(y_test, forecast_arimax):.2f}%")

                  # Residual
                  residuals_train = pd.DataFrame(results.resid, columns=['Residual'])
                  predictions_test = results.forecast(steps=len(y_test), exog=x_test)
                  residuals_test = pd.DataFrame(y_test - predictions_test, columns=['Residual'])
                  residuals_combined = pd.concat([residuals_train, residuals_test], axis=0).reset_index(drop=True)

                  #Visualisasi Residual
                  fig, ax = plt.subplots(figsize=(10, 5))
                  ax.plot(df.index, residuals_combined, label="Test", color="blue")
                  st.write("**Visualisasi Residual ARIMAX**")
                  st.pyplot(fig)

                  # Prepocessing Residual
                  st.subheader ("Pemodelan LSTM")
                  scaler = MinMaxScaler()
                  scaled = scaler.fit_transform(residuals_combined.values.reshape(-1, 1))
                  st.write("**Residual Scaled**")
                  st.dataframe(scaled)

                  # Bagi dataset menjadi train dan test
                  test_size = 21
                  train_lstm = scaled[:-test_size]
                  test_lstm = scaled[-test_size:]

                  seq_length = 10
                  def create_sequences(data, seq_length):
                      X, y = [], []
                      for i in range(seq_length, len(data)):
                          X.append(data[i-seq_length:i, 0])
                          y.append(data[i, 0])
                      return np.array(X), np.array(y)

                  # Buat sequence untuk train dan test
                  X_train, Y_train = create_sequences(train_lstm, seq_length)
                  X_test, Y_test = create_sequences(test_lstm, seq_length)

                  # Sesuaikan dimensi untuk LSTM (samples, time steps, features)
                  X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
                  X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

                  st.write("**Bentuk Data Setelah Reshape untuk LSTM**")
                  st.write(f"X_train shape: {X_train.shape}")
                  st.write(f"X_test shape: {X_test.shape}")

                  # Load model LSTM
                  model_lstm = load_model("model_lstm_fix.h5")

                  # Prediksi residual LSTM
                  y_pred = []
                  input_seq = X_test[0]
                  for i in range(len(X_test)):
                      pred = model_lstm.predict(input_seq.reshape(1, seq_length, 1), verbose=0)
                      y_pred.append(pred[0][0])
                      input_seq = np.append(input_seq[1:], pred[0][0])

                  y_pred_inv = scaler.inverse_transform(np.array(y_pred).reshape(-1,1))
                  st.write("**Hasil Prediksi Residual LSTM**")
                  st.dataframe(y_pred_inv)

                  #Hybrid
                  hybrid_pred = forecast_arimax + y_pred_inv.flatten()
                  st.subheader ("Hybrid ARIMAX-LSTM")
                  st.write("**Perbandingan Hasil Hybrid ARIMAX-LSTM**")
                  st.dataframe(hybrid_pred)

                  # Visualisasi
                  fig, ax = plt.subplots(figsize=(10, 5))
                  ax.plot(y_test.index, y_test, label="Actual", color="blue")
                  ax.plot(y_test.index, forecast_arimax, label="ARIMAX", linestyle="--", color="green")
                  ax.plot(y_test.index, hybrid_pred, label="Hybrid ARIMAX-LSTM", linestyle="-.", color="red")
                  ax.set_title("Visualisasi Perbandingan Hasil Prediksi")
                  ax.legend()
                  ax.grid(True)
                  st.write("**Perbandingan Prediksi Asli, ARIMAX, dan Hybrid**")
                  st.pyplot(fig)

                  #Evaluasi ARIMAX
                  st.success(f"MAPE Hybrid ARIMAX-LSTM: {mape(y_test, hybrid_pred):.2f}%")
                  st.info("Prediksi selesai.")

      except Exception as e:
          st.error(f"Error membaca file: {str(e)}")
  else:
      st.warning("Silakan upload file data terlebih dahulu.")

elif menu == "Peramalan Masa Depan":
  st.header("Peramalan Masa Depan")
  uploaded_file = st.file_uploader(
      "Upload Data Varibel Eksogen Yang Sudah Diketahui Dengan kolom: Tanggal, Harga_Daging_Ayam, Harga_Daging_Sapi, Pekan Sebelum Libur",
      type=['xlsx'],
      help="Format harus mengandung kolom: Tanggal, Harga_Daging_Ayam, Harga_Daging_Sapi, Pekan Sebelum Libur"
  )

  if uploaded_file is not None:
      try:
          if uploaded_file.name.endswith('.xlsx'):
              df_baru = pd.read_excel(uploaded_file)
              st.success("File berhasil diunggah!")
          else:
              st.error("Hanya file .xlsx yang diperbolehkan.")

          required_cols = ['Tanggal', 'Harga_Daging_Ayam', 'Harga_Daging_Sapi', 'Pekan_Sebelum_Libur']
          missing_cols = [col for col in required_cols if col not in df_baru.columns]

          if missing_cols:
              st.error(f"Kolom yang diperlukan tidak ditemukan: {', '.join(missing_cols)}")
          else:
              if st.button("🔍 Peramalan Harga Telur dengan Hybrid ARIMAX-LSTM"):
                  with st.spinner("Memproses prediksi..."):
                      df_baru = df_baru.set_index('Tanggal')
                      exog_forecast = df_baru[['Harga_Daging_Ayam', 'Harga_Daging_Sapi', 'Pekan_Sebelum_Libur']]
                      seq_length = 10

                      # Load ARIMAX
                      model_arimax = joblib.load("best_ARIMAX200.pkl")
                      arimax_pred = model_arimax.forecast(steps=len(df_baru), exog=exog_forecast)
                      arimax_pred.index = df_baru.index

                      # Load model LSTM
                      model_lstm = load_model("model_lstm_fix.h5")

                      # Dummy residual untuk memulai LSTM
                      dummy_residual = np.zeros((seq_length, 1))
                      scaler = MinMaxScaler()
                      dummy_scaled = scaler.fit_transform(dummy_residual)
                      input_seq = dummy_scaled.reshape(seq_length, 1)

                      y_pred = []

                      for i in range(len(df_baru)):
                          pred = model_lstm.predict(input_seq.reshape(1, seq_length, 1))
                          y_pred.append(pred[0][0])

                          # Tambahkan prediksi ke input dan geser window
                          input_seq = np.append(input_seq[1:], pred[0][0])

                      y_pred_inv1 = scaler.inverse_transform(np.array(y_pred).reshape(-1,1)).flatten()
                      hybrid_forecast1 = arimax_pred + y_pred_inv1

                      # Hasil Prediksi
                      df_baru['Peramalan_Harga_Telur'] = hybrid_forecast1
                      st.subheader("Hasil Peramalan Harga Telur")
                      st.dataframe(df_baru)

                      st.success("Peramalan selesai.")
      except Exception as e:
          st.error(f"Error membaca file: {str(e)}")
  else:
      st.warning("Silakan upload file data terlebih dahulu.")