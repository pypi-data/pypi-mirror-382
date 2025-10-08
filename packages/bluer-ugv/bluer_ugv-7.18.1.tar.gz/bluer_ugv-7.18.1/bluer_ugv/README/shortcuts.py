from bluer_objects.README.items import ImageItems, Items
from bluer_objects import markdown

from bluer_ugv.README.consts import bluer_ugv_assets2
from bluer_ugv.README.swallow.consts import (
    swallow_assets2,
    swallow_electrical_designs,
)

items = markdown.generate_table(
    Items(
        [
            {
                "name": "shield",
                "url": "./bluer_ugv/docs/swallow/digital/design/shield.md",
                "marquee": f"{swallow_electrical_designs}/digital.png?raw=true",
            },
            {
                "name": "terraform",
                "url": "./bluer_ugv/docs/swallow/digital/design/terraform.md",
                "marquee": f"{swallow_assets2}/20250611_100917.jpg?raw=true",
            },
            {
                "name": "UGVs",
                "url": "./bluer_ugv/docs/UGVs",
                "marquee": f"{swallow_assets2}/20250912_211652.jpg?raw=true",
            },
        ]
    ),
)
