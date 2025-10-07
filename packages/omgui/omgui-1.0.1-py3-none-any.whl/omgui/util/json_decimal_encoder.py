"""
ijson turns floating numbers into Decimal objects,
which are not JSON serializable. This is a workaround
so we don't have to rely on another module like simplejson
https://stackoverflow.com/a/1960649

Usage:
    import json
    from omgui.util.json_decimal_encoder import JSONDecimalEncoder
    data = {"a": Decimal("1.1")}
    print(json.dumps(data, cls=JSONDecimalEncoder))
"""

import json
from decimal import Decimal


class JSONDecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(JSONDecimalEncoder, self).default(obj)
