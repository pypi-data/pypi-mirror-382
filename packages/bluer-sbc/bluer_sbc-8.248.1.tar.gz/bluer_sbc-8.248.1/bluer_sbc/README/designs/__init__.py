from bluer_sbc.README.designs.cheshmak import items as cheshmak_items
from bluer_sbc.README.designs.battery_bus import items as battery_bus_items
from bluer_sbc.README.designs.swallow import items as swallow_items
from bluer_sbc.README.designs.swallow_head import items as swallow_head_items
from bluer_sbc.README.designs.bryce import items as bryce_items
from bluer_sbc.README.designs.nafha import items as nafha_items
from bluer_sbc.README.designs.shelter import items as shelter_items
from bluer_sbc.README.designs.x import items as x_items
from bluer_sbc.README.designs.ultrasonic_sensor_tester import (
    items as ultrasonic_sensor_tester_items,
)

docs = [
    {
        "cols": 4,
        "items": design_items,
        "path": f"../docs/{design_name}.md",
    }
    for design_name, design_items in {
        "battery-bus": battery_bus_items,
        "bryce": bryce_items,
        "cheshmak": cheshmak_items,
        "nafha": nafha_items,
        "shelter": shelter_items,
        "swallow-head": swallow_head_items,
        "swallow": swallow_items,
        "ultrasonic-sensor-tester": ultrasonic_sensor_tester_items,
        "x": x_items,
    }.items()
]
