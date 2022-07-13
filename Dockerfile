FROM python:3.9

EXPOSE 9997

RUN mkdir /project
WORKDIR /project

COPY ./requirements.txt .
RUN pip install -r requirements.txt

ADD . .
CMD python -m src.api.app