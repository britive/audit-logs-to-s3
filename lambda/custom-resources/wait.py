import time


def create(helper, event):
    wait_seconds = int(event['ResourceProperties']['WaitSeconds'])
    time.sleep(wait_seconds)


def update(helper, event):
    create(helper, event)


# no op
def delete(helper, event):
    pass
