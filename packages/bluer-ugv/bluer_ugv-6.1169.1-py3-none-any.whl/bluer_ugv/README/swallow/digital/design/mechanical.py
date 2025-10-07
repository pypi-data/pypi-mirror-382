from bluer_objects.README.items import ImageItems

from bluer_ugv.README.swallow.consts import swallow_mechanical_design

items = [
    {
        "path": "../docs/swallow/digital/design/mechanical",
        "items": ImageItems(
            {
                f"{swallow_mechanical_design}/robot.png": f"{swallow_mechanical_design}/robot.stl",
                f"{swallow_mechanical_design}/cage.png": f"{swallow_mechanical_design}/cage.stl",
                f"{swallow_mechanical_design}/measurements.png": "",
            }
        ),
    },
    {
        "path": "../docs/swallow/digital/design/mechanical/v1.md",
        "items": ImageItems(
            {
                f"{swallow_mechanical_design}/v1/robot.png": f"{swallow_mechanical_design}/v1/robot.stl",
                f"{swallow_mechanical_design}/v1/cage.png": f"{swallow_mechanical_design}/v1/cage.stl",
                f"{swallow_mechanical_design}/v1/measurements.png": "",
            }
        ),
    },
]
