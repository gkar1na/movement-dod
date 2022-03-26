FROM python:3.8-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /home/database
WORKDIR /home/database

RUN python -m pip install -r requirements.txt
RUN python -m pip install -Ue .

CMD ["python", "create_table.py"]