from bluer_ugv.README.rangin.items import items
from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.rangin.parts import dict_of_parts

docs = [
    {
        "items": items,
        "path": "../docs/rangin",
    },
    {
        "path": "../docs/rangin/parts.md",
        "items": db_of_parts.as_images(
            dict_of_parts,
            reference="../parts",
        ),
        "macros": {
            "parts:::": db_of_parts.as_list(
                dict_of_parts,
                reference="./parts",
                log=False,
            ),
        },
    },
]
