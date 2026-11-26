# Artefak pipeline L141: image aplikasi gerbang-cd (stdlib murni).
FROM docker.io/library/python:3.13-slim
WORKDIR /app
COPY server.py versi.txt ./
RUN useradd --uid 10001 appuser
USER appuser
EXPOSE 18141
CMD ["python", "server.py"]
