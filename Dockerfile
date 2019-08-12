FROM python

RUN mkdir -p /opt/app/twiliotutorial

ADD requirements.txt /opt/app/twiliotutorial/requirements.txt

RUN pip install -r /opt/app/twiliotutorial/requirements.txt

ADD . /opt/app/twiliotutorial

EXPOSE 8000
WORKDIR /opt/app/twiliotutorial
CMD ["/usr/local/bin/python","manage.py","runserver","0.0.0.0:8000"]