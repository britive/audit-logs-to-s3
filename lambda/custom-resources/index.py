from crhelper import CfnResource
import athena_database
import athena_table
import athena_view
import s3_object_nuker
import json

helper = CfnResource(sleep_on_delete=60)

valid_resource_types = [
    'Custom::AthenaDatabase',
    'Custom::AthenaTable',
    'Custom::AthenaView',
    'Custom::S3ObjectNuker'
]


@helper.create
def create(event, context):
    resource_type = event['ResourceType']
    if resource_type == 'Custom::AthenaDatabase':
        return athena_database.create(helper, event)
    if resource_type == 'Custom::AthenaTable':
        return athena_table.create(helper, event)
    if resource_type == 'Custom::AthenaView':
        return athena_view.create(helper, event)
    if resource_type == 'Custom::S3ObjectNuker':
        return s3_object_nuker.create(helper, event)


@helper.update
def update(event, context):
    resource_type = event['ResourceType']
    if resource_type == 'Custom::AthenaDatabase':
        return athena_database.update(helper, event)
    if resource_type == 'Custom::AthenaTable':
        return athena_table.update(helper, event)
    if resource_type == 'Custom::AthenaView':
        return athena_view.update(helper, event)
    if resource_type == 'Custom::S3ObjectNuker':
        return s3_object_nuker.update(helper, event)


@helper.delete
def delete(event, context):
    resource_type = event['ResourceType']
    if resource_type == 'Custom::AthenaDatabase':
        return athena_database.delete(helper, event)
    if resource_type == 'Custom::AthenaTable':
        return athena_table.delete(helper, event)
    if resource_type == 'Custom::AthenaView':
        return athena_view.delete(helper, event)
    if resource_type == 'Custom::S3ObjectNuker':
        return s3_object_nuker.delete(helper, event)


def handler(event, context):
    print(f'event: {json.dumps(event,default=str)}')
    resource_type = event['ResourceType']
    if resource_type not in valid_resource_types:
        raise Exception(f'invalid ResourceType of {resource_type}')
    helper(event, context)
