from python:latest

  RUN mkdir -p /opt/app
  WORKDIR /opt/app/

  COPY . /opt/app/
  WORKDIR /opt/app/src

  RUN pip install pymysql hashlib urllib3 uuid requests logging wakeonlan

  CMD ["python", "controller.py"]
