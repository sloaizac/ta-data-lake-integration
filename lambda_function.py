import json
import traceback
import requests
from jwtAuthentication import get_token

auth_object = {
    token: None,
    exp: None
}

def handler(event, context):

    # convert all headers to lower-case (http spec states they are to be treated as case-insensitive)
    # this makes gets easier later on
    if event.get('headers'):
        event['headers'] = {k.lower(): v for k, v in event['headers'].items()}

    response = None
    try:
        if event['rawPath'].startswith(f'/data-lake-gateway/schema'):
            store = get_store(event)
            response = handle_schema(event, store)
        elif event['rawPath'].startswith(f'/data-lake-gateway/insert'):
            store = get_store(event)
            response = handle_insert(event, store)
        elif event['rawPath'].startswith(f'/data-lake-gateway/test'):
            ##response = handle_test(event)
            response = {
                'msg': 'hello world'
            }
        else:
            response = {
                'statusCode': '404',
                'body': json.dumps(
                    {
                        'error': 'NOT FOUND',
                    }
                ),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return to_response(response)
    except Exception as e:
        # for now expose uncaught errors
        return error_to_response(e)  


def error_to_response(err):
    return {
        'statusCode': '500',
        'body': json.dumps(
            {
                "error": str(err),
                "stack_trace": traceback.format_exc()
            }
        ),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }


def to_response(response):
    return {
        'statusCode': '200',
        'body': json.dumps(response) if response else "",
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def get_store(event):
    store = {}
    if 'headers' in event:
        x_destination_key = event['headers'].get('x-destination-key', None)
        x_table = event['headers'].get('x-table', None)
        
        if x_destination_key and x_destination_key.startswith('snowflake'):
            destination_data = x_destination_key.split('_')
            if len(destination_data) == 4:
                store['database'] = destination_data[1]
                store['schema'] = destination_data[2] + '_' + destination_data[3]
        
        if x_table:
            store['table'] = x_table
    
    return store

def handle_insert(event, store):
    response = {}
    if store.get('database') and store.get('schema') and store.get('table'):
        records = event['body']['records']
        query = ''
        logs = []
        for record in records:
            insert_query = 'INSERT INTO ' + store['database'].upper() + '.' + store['schema'].upper() + '.' + store['table'].upper() + ' ('
            columns = []
            values = []
            for key in record:
                columns.append(key)
                values.append(record[key])
            insert_query += ','.join(columns) + ') VALUES (' + ','.join(values) + ');'
            query += insert_query + '\n'
            auth_object = get_token(auth_object['token'], auth_object['exp'])
            headers = {
                'content-type': 'application/json', 
                'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT', 
                'Accept': 'application/json', 
                'User-Agent': 'myApplication/1.0',
                'Authorization': 'Bearer ' + auth_object['token']
            }
            body = {
                "statement": insert_query,
                "timeout": 60,
                "database": store['database'].upper(),
                "schema": store['schema'].upper(),
                "warehouse": "TEST_WAREHOUSE", #Change TEST_WAREHOUSE to your warehouse name
                "role": "ACCOUNTADMIN"         #Change to your snowflake role
            }
            snowflake_response = requests.post('https://<account_identifier>.snowflakecomputing.com/api/v2/statements', data=json.dumps(body) , headers=headers)
            response['query_to_snowflake'] = query
            if snowflake_response.status_code() != 200:
                logs.append({
                    'status_code': snowflake_response.status_code(),
                    'error': snowflake_response.json(),
                    'record': record
                })
        response['logs'] = logs
    else:
        response = {
            'statusCode': '400',
            'body': json.dumps(
                {
                    'error': 'missing required data to insert operation (missing x-table or incorrect x-destination-key)',
                }
            ),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    return response
        
def handle_schema(event, store):
    response = {}
    if store.get('database') and store.get('schema') and store.get('table'):
        response = event['body']
    else:
        response = {
            'statusCode': '400',
            'body': json.dumps(
                {
                    'error': 'missing required data to update schema operation (missing x-table or incorrect x-destination-key)',
                }
            ),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    return response
