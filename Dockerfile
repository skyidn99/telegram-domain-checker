# Gunakan Python image resmi sebagai base image
FROM python:3.9-slim-buster

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt dan instal dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi folder src ke dalam /app di container
COPY src/ ./

# Perintah untuk menjalankan aplikasi Anda
CMD ["python", "main.py"]
