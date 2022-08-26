import io
import os
from britive.britive import Britive
from datetime import datetime, timedelta
import boto3
import jsonlines
import gzip
import json


# history
history_days = int(os.getenv('history_days'))

# s3 stuff
s3 = boto3.resource('s3')
bucket_name = os.getenv('bucket')
bucket = s3.Bucket(bucket_name)

# get the britive tenant
tenant = os.getenv('tenant')

# get the secret
secret_arn = os.getenv('secret')
token = json.loads(
        boto3.client('secretsmanager').get_secret_value(SecretId=secret_arn)['SecretString']
)['token']


# global keys
last_timestamp_key = 'config/last_timestamp.txt'

# establish britive connection
b = Britive(tenant=tenant, token=token)


def last_timestamp_key_exists():
    result = s3.meta.client.list_objects_v2(Bucket=bucket_name, Prefix=last_timestamp_key)
    if 'Contents' in result:
        return True
    return False


def get_start_time(end):
    if last_timestamp_key_exists():
        start = datetime.fromisoformat(bucket.Object(last_timestamp_key).get()['Body'].read().decode('utf-8'))
        print(f'last end time found in S3 - {start.isoformat()}')
        return start + timedelta(seconds=1)
    else:
        print(f'no last end time found in S3 (first run) - going back {history_days} day(s) for the start time')
        return end - timedelta(days=history_days)


def update_last_timestamp(end):
    bucket.Object(last_timestamp_key).put(
        Body=end.isoformat().encode('utf-8')
    )


def process():
    end = datetime.fromisoformat(datetime.utcnow().isoformat(timespec='seconds'))
    start = get_start_time(end)
    print(f'start date {start.isoformat()}')
    print(f'end date {end.isoformat()}')

    items = b.audit_logs.query(
        from_time=start,
        to_time=end
    )

    if len(items) == 0:
        print('no items returned from audit logs query')
    else:
        print(f'found {len(items)} audit log entries')

        # clean up some data fields
        for item in items:
            item['timestamp_original'] = item['timestamp']
            item['timestamp'] = item['timestamp'].replace('+0000', '').replace('T', ' ')

        # convert from array of maps to 1 map per row - splunk prefers this format
        with io.BytesIO() as fp:
            with jsonlines.Writer(fp) as writer:
                writer.write_all(items)
                fp.seek(0)  # seek back to the beginning of the file
            compressed_content = gzip.compress(fp.read())

        # write the compressed content to S3
        object_key = f'logs/{end.date().isoformat()}/{end.isoformat()}-{start.isoformat()}.jsonl.gz'
        bucket.Object(object_key).put(Body=compressed_content)
        print(f'wrote object to {object_key}')

    # update the last timestamp object so the next run can pick it up
    update_last_timestamp(end)


def handler(event, context):
    process()


if __name__ == '__main__':
    process()
