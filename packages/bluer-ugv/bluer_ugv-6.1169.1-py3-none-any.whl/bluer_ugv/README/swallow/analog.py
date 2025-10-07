from bluer_objects.README.items import ImageItems

from bluer_ugv.README.swallow.consts import swallow_electrical_design

items = [
    {
        "path": "../docs/swallow/analog",
        "items": ImageItems(
            {
                f"{swallow_electrical_design}/analog.png": f"{swallow_electrical_design}/analog.svg",
            }
        ),
    }
]
