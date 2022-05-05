FROM python:3.8-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY database /home/database
COPY spreadsheet_parser /home/spreadsheet_parser
COPY telegram_bot /home/telegram_bot

WORKDIR /home/database
RUN python -m pip install -r requirements.txt
RUN python -m pip install -Ue .
CMD ["python", "/home/database/create_table.py"]

WORKDIR /home/spreadsheet_parser
RUN python -m pip install -r requirements.txt
RUN python -m pip install -Ue .

WORKDIR /home/telegram_bot
RUN python -m pip install -r requirements.txt
RUN python -m pip install -Ue .

#CMD ["python", "../database/create_table.py"]
#CMD ["python", "../spreadsheet_parser/load_first.py"]
CMD ["python", "main.py"]
