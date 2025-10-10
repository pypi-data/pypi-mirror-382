from typing import Dict

from bluer_objects.README.consts import assets2

from bluer_sandbox.README.consts import ai4k_assets2

dict_of_experiments: Dict[str, Dict] = {
    "multimeter": {
        "marquee": f"{ai4k_assets2}/20250616_112027.jpg",
        "description": [
            "measure the voltage of batteries, AC, battery-bus w/ different lights + on charger, what else?",
            "measure the resistance of water, metal, what else?",
            "what else?",
        ],
    },
    "caliper": {
        "marquee": f"{ai4k_assets2}/20251009_114411.jpg",
        "description": [
            "measure the thickness of hair, paper, finger (what's wrong?)",
            "measure the different sides of a spoon, what else?",
            "what else?",
        ],
    },
    "ultrasonic": {
        "marquee": f"{assets2}/ultrasonic-sensor-tester/00.jpg?raw=true",
        "description": [
            "work with the [ultrasonic sensor tester](https://github.com/kamangir/bluer-sbc/blob/main/bluer_sbc/docs/ultrasonic-sensor-tester.md), make sense of how it works, measure with one sensor.",
            "drive [arzhang](https://github.com/kamangir/bluer-ugv/tree/main/bluer_ugv/docs/arzhang) and measure how far from an obstacle it stops.",
        ],
    },
    "template": {
        "marquee": "template",
        "description": [
            "",
        ],
    },
}
