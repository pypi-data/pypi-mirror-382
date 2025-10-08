from bluer_objects.README.items import ImageItems

from bluer_ugv.README.swallow.consts import (
    swallow_assets2,
    swallow_electrical_designs,
)

items = ImageItems(
    {
        f"{swallow_electrical_designs}/digital.png": f"{swallow_electrical_designs}/digital.svg",
        f"{swallow_assets2}/20250609_164433.jpg": "",
        f"{swallow_assets2}/20250614_102301.jpg": "",
        f"{swallow_assets2}/20250614_114954.jpg": "",
        f"{swallow_assets2}/20250615_192339.jpg": "",
        f"{swallow_assets2}/20250703_153834.jpg": "",
        f"{swallow_assets2}/design/v2/01.jpg": "",
        f"{swallow_assets2}/design/v3/01.jpg": "",
        f"{swallow_assets2}/design/v4/01.jpg": "",
        f"{swallow_assets2}/20250925_213013.jpg": "",
        f"{swallow_assets2}/20250925_214017.jpg": "",
        f"{swallow_assets2}/20250928_160425.jpg": "",
        f"{swallow_assets2}/20250928_160449.jpg": "",
        f"{swallow_assets2}/design/head-v1/01.jpg": "",
        f"{swallow_assets2}/20251002_103712.jpg": "",
        f"{swallow_assets2}/20251002_103720.jpg": "",
        f"{swallow_assets2}/design/v5/01.jpg": "",
        f"{swallow_electrical_designs}/nuts-bolts-spacers.png": f"{swallow_electrical_designs}/nuts-bolts-spacers.svg",
    }
)


docs = [
    {
        "path": "../docs/swallow/digital/design/shield.md",
        "items": items,
    },
]
