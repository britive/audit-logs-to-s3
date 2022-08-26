import boto3
import time

athena = boto3.client('athena')


def execute_query(catalog, workgroup, database, query):
    printable_query = query.replace('\n', ' ')
    print(f"executing query: {printable_query}")
    execution_id = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database,
            'Catalog': catalog
        },
        WorkGroup=workgroup
    )['QueryExecutionId']

    while True:
        time.sleep(1)
        response = athena.get_query_execution(
            QueryExecutionId=execution_id
        )['QueryExecution']

        status = response['Status']['State']
        if status in ['SUCCEEDED']:
            print('query succeeded')
            break
        if status in ['CANCELLED', 'FAILED']:
            print('resource creation error')
            print(response['Status']['StateChangeReason'])
            break
        if status in ['QUEUED', 'RUNNING']:
            continue


def create(helper, event):
    properties = event['ResourceProperties']
    catalog = properties['Catalog']
    database = properties['Database']
    workgroup = properties['Workgroup']
    table_name = properties['TableName']
    table_definition = properties['TableDefinition']

    # we need to clear out the table first if it already exists
    execute_query(catalog, workgroup, database, f'drop table if exists {table_name}')
    execute_query(catalog, workgroup, database, table_definition)

    helper.Data.update({'TableName': table_name})

    return f'{database}.{table_name}-athena-table'


def update(helper, event):
    properties = event['ResourceProperties']
    catalog = properties['Catalog']
    database = properties['Database']
    workgroup = properties['Workgroup']
    table_name = properties['TableName']
    table_definition = properties['TableDefinition']

    execute_query(catalog, workgroup, database, f'drop table if exists {table_name}')
    execute_query(catalog, workgroup, database, table_definition)

    helper.Data.update({'TableName': table_name})

    old_table_name = event['OldResourceProperties']['TableName']
    if old_table_name != table_name:
        # cf doesnt seem to want to call the delete operation on the old resource so just handle it here
        execute_query(catalog, workgroup, database, f'drop table if exists {old_table_name}')
        return f'{database}.{table_name}-athena-table'


def delete(helper, event):
    properties = event['ResourceProperties']
    catalog = properties['Catalog']
    database = properties['Database']
    workgroup = properties['Workgroup']
    table_name = properties['TableName']

    execute_query(catalog, workgroup, database, f'drop table if exists {table_name}')
