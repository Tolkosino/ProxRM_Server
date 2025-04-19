from python:latest

  RUN mkdir -p /opt/app
  WORKDIR /opt/app/

  COPY . /opt/app/
  WORKDIR /opt/app/src

  RUN python -m pip install pymysql bcrypt urllib3 uuid requests logging wakeonlan tomli cryptography

  CMD ["python", "controller.py"]
