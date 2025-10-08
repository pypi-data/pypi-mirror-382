from bluer_objects.README.items import ImageItems

from bluer_ugv.README.consts import algo_docs
from bluer_ugv.README.swallow.consts import swallow_assets2
from bluer_ugv.README.swallow.digital.algo.navigation import items as navigation_items
from bluer_ugv.README.swallow.digital.algo.yolo import items as yolo_items

items = (
    [
        {
            "path": "../docs/swallow/digital/algo",
        },
        {
            "path": "../docs/swallow/digital/algo/driving.md",
        },
    ]
    + navigation_items
    + [
        {
            "path": "../docs/swallow/digital/algo/tracking",
            "items": ImageItems(
                {
                    f"{swallow_assets2}/target-selection.png": f"{algo_docs}/socket.md",
                }
            ),
        }
    ]
    + yolo_items
)
