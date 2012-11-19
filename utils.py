
def to_response(code, ext={}):
    result = {}
    result['rs'] = code
    result.update(ext)
    return str(result)

def _result_to_dict(cursor):
    records = {}
    records.update(dict((record['_id'], record) for record in cursor))
    return records

