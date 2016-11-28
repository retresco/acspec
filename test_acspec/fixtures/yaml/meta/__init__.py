import os

from acspec.yspec import Yspec


types_path = models_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'types', 'types.yml'
)
types = Yspec.load(types_path)

test = types.TypeModel({
    "type": {
        "simple": "string"
    }
})

test = types.TypeModel({
    "type": {
        "list": {
            "simple": "string"
        }
    }
})

test = types.TypeModel({
    "type": {
        "model": "string"
    }
})

import pdb
pdb.set_trace()

print()
