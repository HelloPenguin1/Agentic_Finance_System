FROM python:3.12.12-slim

#environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

#makes logs appear immediately

#set current directory
WORKDIR /app

#install uv
RUN pip install --no-cache-dir uv

#copy dependencies files first
#for better Docker caching 
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

#copy the rest of the project
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]