FROM python:3.8
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN xargs -L 1 pip install < requirements.txt
EXPOSE 8080
COPY . /app
CMD streamlit run --server.port 8080 --server.enableCORS false app.py