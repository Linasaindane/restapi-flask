FROM python:3.10
EXPOSE 5000

COPY . /project

COPY requirements.txt /tmp/requirements.txt
WORKDIR ./project

RUN pip install -r /tmp/requirements.txt      
ENTRYPOINT ["python"]
CMD ["app.py"]