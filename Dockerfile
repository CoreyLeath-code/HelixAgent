FROM gcc:16 AS cpp-builder
WORKDIR /build
COPY agent/cpp/vector.cpp .
RUN g++ -O3 -shared -std=c++17 -fPIC vector.cpp -o libvector.so

FROM python:3.11-slim AS python-builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

FROM python:3.11-slim AS runtime
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

COPY --from=python-builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . .
COPY --from=cpp-builder /build/libvector.so agent/cpp/libvector.so

USER 10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
