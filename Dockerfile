From ubuntu:latest
WORKDIR /app
COPY . .

RUN apt update
RUN apt install python3 -y
RUN apt install pip -y
RUN pip install --upgrade pip
# RUN pip install opencv-python
# RUN pip install psycopg2-binary
# RUN pip install ultralytics
RUN pip install -r requirements.txt
CMD [“python”, “./main.py”, "entrada"] 