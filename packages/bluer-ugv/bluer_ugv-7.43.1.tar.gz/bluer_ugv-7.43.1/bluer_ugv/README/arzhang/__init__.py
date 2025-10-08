from bluer_ugv.README.arzhang.items import items
from bluer_ugv.README.arzhang import design, algo, flag, validation

docs = (
    [
        {
            "items": items,
            "path": "../docs/arzhang",
        }
    ]
    + algo.docs
    + design.docs
    + flag.docs
    + validation.docs
)
