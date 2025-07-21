FROM python:3.10-slim
RUN apt-get update &&     apt-get install -y build-essential libglib2.0-0 &&     pip install python-snap7 paho-mqtt
COPY run.sh /run.sh
COPY proxy.py /proxy.py
RUN chmod +x /run.sh
CMD [ "/run.sh" ]
