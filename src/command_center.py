import json


# ============================================================
# FIREGROUND COMMAND CENTER
# ============================================================
# This program reads:
# 1. The automatic CNN-generated firefighter event
# 2. Fireground zone information
# 3. Fire truck resource information
#
# It then displays a combined fireground status.
#
# NOTE:
# The risk logic below is prototype/demo logic.
# It is NOT a validated firefighter safety algorithm.
# ============================================================


# ------------------------------------------------------------
# 1. Load AUTOMATIC firefighter event
# ------------------------------------------------------------

try:

    with open(
        "../results/automatic_firefighter_event.json",
        "r"
    ) as file:

        firefighter_event = json.load(file)

except FileNotFoundError:

    print("ERROR:")
    print(
        "automatic_firefighter_event.json "
        "was not found."
    )

    print()
    print(
        "Run automatic_event.py first."
    )

    raise SystemExit


# ------------------------------------------------------------
# 2. Load fireground zone information
# ------------------------------------------------------------

try:

    with open(
        "../results/fireground_zones.json",
        "r"
    ) as file:

        zones = json.load(file)

except FileNotFoundError:

    print("ERROR:")
    print(
        "fireground_zones.json was not found."
    )

    print()
    print(
        "Run fireground_location.py first."
    )

    raise SystemExit


# ------------------------------------------------------------
# 3. Load truck information
# ------------------------------------------------------------

try:

    with open(
        "../results/truck_status.json",
        "r"
    ) as file:

        truck = json.load(file)

except FileNotFoundError:

    print("ERROR:")
    print(
        "truck_status.json was not found."
    )

    print()
    print(
        "Run truck_resource.py first."
    )

    raise SystemExit


# ============================================================
# DISPLAY HEADER
# ============================================================

print()
print("==============================================")
print("       FIREGROUND COMMAND CENTER")
print("==============================================")


# ============================================================
# FIREFIGHTER INFORMATION
# ============================================================

print()
print("FIREFIGHTER STATUS")
print("----------------------------------------------")

print(
    "Node ID:",
    firefighter_event["node_id"]
)

print(
    "Activity:",
    firefighter_event["activity"]
)

print(
    "Activity confidence:",
    firefighter_event["activity_confidence"]
)

print(
    "Environment:",
    firefighter_event["environment"]
)

print(
    "Environment confidence:",
    firefighter_event["environment_confidence"]
)

print(
    "Physiological state:",
    firefighter_event["physiological_state"]
)

print(
    "Physiological confidence:",
    firefighter_event[
        "physiological_confidence"
    ]
)

print(
    "Local risk score:",
    firefighter_event["risk_score"]
)

print(
    "Local situational status:",
    firefighter_event[
        "situational_status"
    ]
)

print(
    "Event type:",
    firefighter_event["event_type"]
)


# ============================================================
# FIREGROUND ZONES
# ============================================================

print()
print("FIREGROUND ZONES")
print("----------------------------------------------")


for zone, information in zones.items():

    print()

    print(
        "Zone",
        zone,
        "→",
        information["status"]
    )

    print(
        "  Firefighters:",
        information["firefighters"]
    )

    print(
        "  HIGH events:",
        information["high_events"]
    )

    print(
        "  ELEVATED events:",
        information["elevated_events"]
    )

    print(
        "  Environment risk:",
        information["environment_risk"]
    )


# ============================================================
# TRUCK RESOURCES
# ============================================================

print()
print("TRUCK RESOURCE")
print("----------------------------------------------")

print(
    "Truck ID:",
    truck["truck_id"]
)

print(
    "Water remaining:",
    truck[
        "water_remaining_liters"
    ],
    "L"
)

print(
    "Water remaining:",
    truck[
        "water_remaining_percent"
    ],
    "%"
)

print(
    "Flow rate:",
    truck[
        "flow_rate_liters_per_minute"
    ],
    "L/min"
)

print(
    "Estimated remaining time:",
    truck[
        "estimated_remaining_minutes"
    ],
    "minutes"
)

print(
    "Pump status:",
    truck["pump_status"]
)


# ============================================================
# OVERALL FIREGROUND FUSION
# ============================================================

print()
print("==============================================")
print("       OVERALL FIREGROUND STATUS")
print("==============================================")


# ------------------------------------------------------------
# Count high-risk zones
# ------------------------------------------------------------

high_zones = 0
elevated_zones = 0
risk_zones = 0


for information in zones.values():

    if information["status"] == "HIGH":

        high_zones += 1

    elif information["status"] == "ELEVATED":

        elevated_zones += 1


    if information["environment_risk"] > 0:

        risk_zones += 1


# ------------------------------------------------------------
# Read local firefighter status
# ------------------------------------------------------------

local_status = firefighter_event[
    "situational_status"
]


# ------------------------------------------------------------
# Prototype fusion logic
# ------------------------------------------------------------

if high_zones >= 2:

    overall_status = "HIGH"

elif local_status == "HIGH":

    overall_status = "ELEVATED"

elif high_zones >= 1:

    overall_status = "ELEVATED"

elif elevated_zones >= 1:

    overall_status = "ELEVATED"

elif risk_zones >= 2:

    overall_status = "ELEVATED"

else:

    overall_status = "NORMAL"


# ============================================================
# DISPLAY FINAL RESULT
# ============================================================

print()
print(
    "Fireground status:",
    overall_status
)

print()
print(
    "High-risk zones:",
    high_zones
)

print(
    "Elevated zones:",
    elevated_zones
)

print(
    "Environment-risk zones:",
    risk_zones
)


# ============================================================
# ALERT PRIORITY
# ============================================================

print()
print("ALERT PRIORITY")
print("----------------------------------------------")


if overall_status == "HIGH":

    alert_priority = "URGENT"

elif overall_status == "ELEVATED":

    alert_priority = "HIGH"

else:

    alert_priority = "NORMAL"


print(
    "Alert priority:",
    alert_priority
)


# ============================================================
# COMMAND CENTER SUMMARY
# ============================================================

summary = {

    "firefighter": {

        "node_id":
            firefighter_event["node_id"],

        "activity":
            firefighter_event["activity"],

        "environment":
            firefighter_event["environment"],

        "physiological_state":
            firefighter_event[
                "physiological_state"
            ],

        "situational_status":
            firefighter_event[
                "situational_status"
            ],

        "event_type":
            firefighter_event[
                "event_type"
            ]
    },

    "fireground": {

        "high_zones":
            high_zones,

        "elevated_zones":
            elevated_zones,

        "environment_risk_zones":
            risk_zones,

        "overall_status":
            overall_status,

        "alert_priority":
            alert_priority
    },

    "truck": {

        "truck_id":
            truck["truck_id"],

        "water_remaining_liters":
            truck[
                "water_remaining_liters"
            ],

        "water_remaining_percent":
            truck[
                "water_remaining_percent"
            ],

        "flow_rate_liters_per_minute":
            truck[
                "flow_rate_liters_per_minute"
            ],

        "estimated_remaining_minutes":
            truck[
                "estimated_remaining_minutes"
            ]
    }
}


# ------------------------------------------------------------
# Save command-center summary
# ------------------------------------------------------------

with open(
    "../results/command_center_status.json",
    "w"
) as file:

    json.dump(
        summary,
        file,
        indent=4
    )


# ============================================================
# COMPLETE
# ============================================================

print()
print("==============================================")
print(" Command center analysis complete.")
print("==============================================")

print()
print(
    "Saved to:"
)

print(
    "../results/command_center_status.json"
)