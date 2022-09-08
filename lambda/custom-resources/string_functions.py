
def create(helper, event):
    value = str(event['ResourceProperties']['InputString'])
    helper.Data.update({'Strip': value.strip()})
    helper.Data.update({'Lowercase': value.lower()})
    helper.Data.update({'Uppercase': value.upper()})
    helper.Data.update({'Capitalize': value.capitalize()})
    helper.Data.update({'Title': value.title()})
    helper.Data.update({'SwapCase': value.swapcase()})


def update(helper, event):
    create(helper, event)


# no op
def delete(helper, event):
    pass
