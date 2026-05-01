FROM python:3.9

# Buat user baru dengan ID 1000
RUN useradd -m -u 1000 user

WORKDIR /code

# Copy requirements dan install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy seluruh file project
COPY . /code

# Ubah kepemilikan folder /code ke user 1000
RUN chown -R user:user /code

# Ganti eksekusi menjadi user 1000
USER user

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]