FROM python:3.9

WORKDIR /app

# Copy only the requirements file to leverage caching
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV AWS_REGION=ap-southeast-1

# Copy the rest of the application code
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
