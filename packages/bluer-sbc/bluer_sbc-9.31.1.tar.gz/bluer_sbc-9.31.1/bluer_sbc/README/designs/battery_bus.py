from bluer_objects import README
from bluer_objects.README.items import ImageItems
from bluer_objects.README.consts import assets_url

from bluer_sbc.README.designs.consts import assets2

assets2_battery_bus = assets_url(
    suffix="battery-bus",
    volume=2,
)

marquee = README.Items(
    [
        {
            "name": "battery bus",
            "marquee": f"{assets2_battery_bus}/concept.png",
            "url": "./bluer_sbc/docs/battery-bus.md",
        }
    ]
)

items = ImageItems(
    {
        f"{assets2_battery_bus}/concept.png": "",
    }
)
