FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . ./
RUN uv build && uv pip install --system dist/*.whl

EXPOSE 8000

CMD ["python", "-m", "nua"]
