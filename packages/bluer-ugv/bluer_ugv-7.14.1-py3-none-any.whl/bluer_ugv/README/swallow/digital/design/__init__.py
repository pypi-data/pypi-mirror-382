from bluer_objects.README.items import ImageItems
from bluer_sbc.parts.db import db_of_parts

from bluer_ugv.README.swallow.consts import (
    swallow_assets2,
    swallow_electrical_designs,
)
from bluer_ugv.swallow.parts import dict_of_parts
from bluer_ugv.README.swallow.digital.design.mechanical import items as mechanical_items
from bluer_ugv.README.swallow.digital.design.ultrasonic_sensor import (
    items as ultrasonic_sensor_items,
)


items = (
    [
        {
            "path": "../docs/swallow/digital/design",
        },
        {
            "path": "../docs/swallow/digital/design/operation.md",
            "items": ImageItems(
                {
                    f"{swallow_assets2}/20251005_113232.jpg": "",
                }
            ),
        },
        {
            "path": "../docs/swallow/digital/design/parts.md",
            "items": db_of_parts.as_images(
                dict_of_parts,
                reference="../../../parts",
            ),
            "macros": {
                "parts:::": db_of_parts.as_list(
                    dict_of_parts,
                    reference="../../../parts",
                    log=False,
                ),
            },
        },
        {
            "path": "../docs/swallow/digital/design/terraform.md",
            "items": ImageItems(
                {
                    f"{swallow_assets2}/20250611_100917.jpg": "",
                    f"{swallow_assets2}/lab.png": "",
                    f"{swallow_assets2}/lab2.png": "",
                }
            ),
        },
        {
            "path": "../docs/swallow/digital/design/steering-over-current-detection.md",
            "items": ImageItems(
                {
                    f"{swallow_electrical_designs}/steering-over-current.png": f"{swallow_electrical_designs}/steering-over-current.svg",
                }
            ),
        },
        {
            "path": "../docs/swallow/digital/design/rpi-pinout.md",
        },
    ]
    + mechanical_items
    + ultrasonic_sensor_items
)
