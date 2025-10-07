from bluer_objects.README.consts import assets_path

from bluer_ugv.README.consts import bluer_ugv_mechanical_design

swallow_assets2 = assets_path(
    "swallow",
    volume=2,
)

swallow_electrical_design = (
    f"{bluer_ugv_mechanical_design}/blob/main/swallow/electrical"
)

swallow_mechanical_design = (
    f"{bluer_ugv_mechanical_design}/blob/main/swallow/mechanical"
)

swallow_ultrasonic_sensor_design = (
    f"{bluer_ugv_mechanical_design}/blob/main/swallow/ultrasonic-sensors"
)
