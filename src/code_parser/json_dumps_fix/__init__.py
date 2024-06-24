# Fix json.dumps to convert Object via __json__ methods

from json import JSONEncoder

def wrapped_default(self, obj):
    return getattr(obj.__class__, "__json__", wrapped_default.default)(obj)
wrapped_default.default = JSONEncoder().default

JSONEncoder.original_default = JSONEncoder.default
JSONEncoder.default = wrapped_default