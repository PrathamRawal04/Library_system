FROM python:3.10

WORKDIR /app

RUN pip install --no-cache-dir streamlit requests

COPY app.py ./

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"] 