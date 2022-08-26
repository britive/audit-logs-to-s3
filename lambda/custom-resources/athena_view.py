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
    view_name = properties['ViewName']
    view_definition = properties['ViewDefinition']

    # we need to clear out the view first if it already exists
    execute_query(catalog, workgroup, database, f'drop view if exists {view_name}')
    execute_query(catalog, workgroup, database, view_definition)

    helper.Data.update({'ViewName': view_name})

    return f'{database}.{view_name}-athena-table'


def update(helper, event):
    properties = event['ResourceProperties']
    catalog = properties['Catalog']
    database = properties['Database']
    workgroup = properties['Workgroup']
    view_name = properties['ViewName']
    view_definition = properties['ViewDefinition']

    # we need to clear out the view first if it already exists
    execute_query(catalog, workgroup, database, f'drop view if exists {view_name}')
    execute_query(catalog, workgroup, database, view_definition)

    helper.Data.update({'ViewName': view_name})

    old_view_name = event['OldResourceProperties']['ViewName']
    if old_view_name != view_name:
        # cf doesnt seem to want to call the delete operation on the old resource so just handle it here
        execute_query(catalog, workgroup, database, f'drop view if exists {old_view_name}')
        return f'{database}.{view_name}-athena-table'


def delete(helper, event):
    properties = event['ResourceProperties']
    catalog = properties['Catalog']
    database = properties['Database']
    workgroup = properties['Workgroup']
    view_name = properties['ViewName']

    execute_query(catalog, workgroup, database, f'drop view if exists {view_name}')
