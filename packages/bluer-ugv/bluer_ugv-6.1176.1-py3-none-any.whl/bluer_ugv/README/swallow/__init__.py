from bluer_ugv.README.swallow.items import items
from bluer_ugv.README.swallow.analog import items as items_analog
from bluer_ugv.README.swallow.digital import items as items_digital

docs = (
    [
        {
            "items": items,
            "path": "../docs/swallow",
        }
    ]
    + items_analog
    + items_digital
)
