FROM docker.io/python:slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -m user

WORKDIR /home/user/

COPY --chown=user:user ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user . .

USER user

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
