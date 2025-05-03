FROM python:3.11-slim
# get git
RUN apt-get update && \
	apt-get install -y --no-install-recommends git && \
	rm -rf /var/lib/apt/lists/*

WORKDIR /root/
COPY requirements.txt .

RUN python -m pip install --upgrade pip &&\
	pip install -r requirements.txt

	
COPY src src
	
ENV MODEL_SERVICE_URL=http://localhost:8081/predict

#EXPOSE 8080 

ENTRYPOINT ["python"]
CMD ["src/app.py"]
