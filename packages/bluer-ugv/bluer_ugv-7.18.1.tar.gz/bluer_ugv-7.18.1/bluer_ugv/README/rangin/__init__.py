from bluer_objects.README.items import ImageItems
from bluer_sbc.parts.db import db_of_parts

from bluer_ugv.README.rangin.items import items
from bluer_ugv.rangin.parts import dict_of_parts
from bluer_ugv.README.rangin.consts import rangin_mechanical_design

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
                reference="../parts",
                log=False,
            ),
        },
    },
    {
        "path": "../docs/rangin/mechanical.md",
        "cols": 2,
        "items": ImageItems(
            {
                f"{rangin_mechanical_design}/robot.png": f"{rangin_mechanical_design}/robot.stl",
            }
        ),
    },
]
