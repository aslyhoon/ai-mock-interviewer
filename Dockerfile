# AI Mock Interviewer — single-container production image.
# Stage 1 builds the React frontend; stage 2 runs FastAPI, which serves both
# the API and the built frontend on $PORT (default 8000).
# Works on Render / Fly.io / Railway / any Docker host.
#
# Build:  docker build -t ai-mock-interviewer .
# Run:    docker run -p 8000:8000 ai-mock-interviewer

# ---- Stage 1: build the frontend ----
FROM node:20-alpine AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: runtime ----
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install -r backend/requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-build /build/frontend/dist ./frontend/dist

WORKDIR /app/backend
EXPOSE 8000
# DATABASE_URL and GEMINI_API_KEY can be passed as env vars; without them the
# app uses a local SQLite file and the built-in question bank.
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
