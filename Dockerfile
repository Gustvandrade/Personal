FROM python:3.12

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "Dashboard.py", "--server.port=8501"]