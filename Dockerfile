FROM python:3.12.9-slim
# get git
RUN apt-get update && \
	apt-get install -y --no-install-recommends git && \
	rm -rf /var/lib/apt/lists/*

WORKDIR /root/
COPY requirements.txt .

RUN python -m pip install --upgrade pip &&\
	pip install -r requirements.txt


COPY src src

ENTRYPOINT ["python"]
CMD ["src/app.py"]