from bluer_ugv.README.arzhang.items import items
from bluer_ugv.README.arzhang.algo import items as algo_items
from bluer_ugv.README.arzhang.design import items as design_items
from bluer_ugv.README.arzhang.validation import items as validation_items

docs = (
    [
        {
            "items": items,
            "path": "../docs/arzhang",
        }
    ]
    + design_items
    + algo_items
    + validation_items
)
