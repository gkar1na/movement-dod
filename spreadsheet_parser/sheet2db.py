import os
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql.expression import text


async def get_creds(creds_file_name: str, token_file_name: str) -> Credentials:
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
              'https://www.googleapis.com/auth/drive']

    creds = None
    if os.path.exists(token_file_name):
        creds = Credentials.from_authorized_user_file(token_file_name, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file_name, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file_name, 'w') as token:
            token.write(creds.to_json())

    return creds


async def get_data(
        spreadsheet_id: str,
        creds_file_name: str = 'credentials.json',
        token_file_name: str = 'token.json'
) -> dict:
    tables = dict()

    creds = await get_creds(creds_file_name, token_file_name)

    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

    request = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        includeGridData=True
    )
    response = request.execute()

    sheets = response['sheets']

    for sheet in sheets:
        sheet_title = sheet['properties']['title']
        tables[sheet_title] = []

        rowData = sheet['data']
        for k, data in enumerate(rowData):
            if 'rowData' not in data.keys():
                continue
            rowData[k] = rowData[k]['rowData']
            for i, row in enumerate(rowData[k]):
                if 'values' in row.keys():
                    for j, value in enumerate(row['values']):
                        if value and 'formattedValue' in value.keys():
                            row['values'][j] = value['formattedValue']
                        else:
                            row['values'][j] = None
                    tables[sheet_title].append(row['values'])

                else:
                    tables[sheet_title].append(None)

    return tables


async def fill_db(connection: AsyncConnection, tables: dict):
    for table_name in tables.keys():
        if not tables[table_name]:
            continue
        if not re.search('^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$', table_name):
            print(f'ERROR {table_name}: Incorrect table name')
            continue
        rows = tables[table_name][1:]
        columns = list(tables[table_name][0])
        try:
            while columns.index(None) != -1:
                columns.remove(None)
        except ValueError:
            pass
        number_of_columns = len(columns)

        query = f'CREATE TABLE tmp_{table_name} (uid uuid DEFAULT uuid_generate_v4() PRIMARY KEY'
        columns_are_correct = True
        for column in columns:
            if column:
                if not re.search('^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$', column):
                    columns_are_correct = False
                    break
                query += f', {column} varchar(120)'
        if not columns_are_correct:
            print(f'ERROR {table_name}: Incorrect column name')
            continue
        query += ')'

        queries = [query]
        await connection.execute(text(f'DROP TABLE IF EXISTS tmp_{table_name} cascade'))
        try:
            await connection.execute(text(query))

        except ProgrammingError:
            await connection.execute(text(f'DROP TABLE IF EXISTS tmp_{table_name} cascade'))
            await connection.execute(text(query))

        values_are_current = True
        for i, row in enumerate(rows):
            row = list(row[:number_of_columns])
            if not any(row):
                continue
            params = ''
            for value in row:
                if value is None:
                    params += f'null, '
                else:
                    params += f"'{value}', "
            if params[-2] == ',':
                params = params[:len(params) - 2]
            query = f"INSERT INTO tmp_{table_name} ({', '.join(columns)}) VALUES ({params})"
            try:
                await connection.execute(text(query))
            except Exception as e:
                print(f'ERROR {table_name}: {e}')
                values_are_current = False
                break
            queries.append(query)

        if not values_are_current:
            continue

        await connection.execute(text(f'DROP TABLE tmp_{table_name} cascade'))
        await connection.execute(text(f'DROP TABLE IF EXISTS {table_name} cascade'))
        for query in queries:
            query = query.replace('tmp_', '', 1)
            await connection.execute(text(query))

        await connection.commit()


async def convert(
        spreadsheet_id: str,
        db_url: str,
        creds_file_name: str = 'credentials.json',
        token_file_name: str = 'token.json',
):
    tables = await get_data(
        spreadsheet_id=spreadsheet_id,
        creds_file_name=creds_file_name,
        token_file_name=token_file_name
    )

    engine = create_async_engine(db_url)

    async with engine.connect() as connection:
        await fill_db(connection, tables)
