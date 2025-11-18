FROM python:3.11-slim
WORKDIR /app
COPY requirements.prod.txt /app/requirements.prod.txt
RUN pip install --no-cache-dir -r /app/requirements.prod.txt
COPY server.py /app/server.py
ENV PORT=8000
EXPOSE 8000
CMD ["python","-m","uvicorn","server:app","--host","0.0.0.0","--port","8000"]