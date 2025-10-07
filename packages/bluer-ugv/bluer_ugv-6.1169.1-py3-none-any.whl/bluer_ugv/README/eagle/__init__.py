from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.README.eagle.items import items
from bluer_ugv.eagle.parts import dict_of_parts

docs = [
    {
        "items": items,
        "path": "../docs/eagle",
    },
    {
        "path": "../docs/eagle/parts.md",
        "items": db_of_parts.as_images(
            dict_of_parts,
            reference="../parts",
        ),
        "macros": {
            "parts:::": db_of_parts.as_list(
                dict_of_parts,
                reference="../parts",
                log=False,
            ),
        },
    },
]
