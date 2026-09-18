import json
import pickle
from datetime import datetime

import numpy as np
import tensorflow as tf


# ============================================================
#  FIREGROUND INTELLIGENCE SYSTEM - INTEGRATED PROTOTYPE
# ============================================================
#
# Pipeline:
#
# Sensor window
#       ↓
# Multi-task CNN
#       ↓
# Activity + Environment + Physiological state
#       ↓
# Local situational fusion
#       ↓
# Firefighter event
#       ↓
# Location
#       ↓
# Fireground fusion
#       ↓
# Truck resources
#       ↓
# Command Center
#
# NOTE:
# All risk thresholds and sensor values in this program
# are synthetic demonstration values.
# They are NOT validated operational safety thresholds.
# ============================================================


# ============================================================
# 1. LOAD TRAINED MODEL
# ============================================================

print()
print("Loading Fireground AI model...")

model = tf.keras.models.load_model(
    "../models/multitask_fireground_cnn.keras"
)


# ============================================================
# 2. LOAD SCALER
# ============================================================

with open(
    "../models/scaler.pkl",
    "rb"
) as file:

    scaler = pickle.load(file)


# ============================================================
# 3. CLASS LABELS
# ============================================================

activity_labels = [
    "crawling",
    "standing",
    "walking"
]

environment_labels = [
    "normal",
    "risk"
]

physiological_labels = [
    "elevated",
    "high",
    "normal"
]


# ============================================================
# 4. CREATE SENSOR WINDOW
# ============================================================
#
# 10 time steps × 9 sensor features
#
# Feature order:
#
# 0 = heart_rate
# 1 = acc_x
# 2 = acc_y
# 3 = acc_z
# 4 = gyro_x
# 5 = gyro_y
# 6 = gyro_z
# 7 = gas
# 8 = temperature
# ============================================================

sensor_window = np.array([

    [82, 0.20, 0.30, 9.70, 0.02, 0.03, 0.02, 20, 30],

    [87, 0.30, 0.30, 9.60, 0.03, 0.03, 0.02, 25, 31],

    [92, 0.40, 0.40, 9.60, 0.04, 0.04, 0.03, 32, 33],

    [97, 0.50, 0.40, 9.50, 0.05, 0.05, 0.04, 45, 35],

    [102, 0.60, 0.40, 9.40, 0.06, 0.05, 0.04, 60, 37],

    [104, 0.60, 0.40, 9.40, 0.06, 0.06, 0.04, 63, 38],

    [106, 0.60, 0.40, 9.30, 0.07, 0.06, 0.05, 67, 39],

    [108, 0.70, 0.40, 9.30, 0.07, 0.06, 0.05, 70, 40],

    [110, 0.70, 0.50, 9.20, 0.08, 0.07, 0.06, 74, 41],

    [112, 0.70, 0.50, 9.20, 0.08, 0.07, 0.06, 78, 42]

])


# ============================================================
# 5. NORMALIZE SENSOR WINDOW
# ============================================================

window_2d = sensor_window.reshape(
    -1,
    9
)

window_scaled = scaler.transform(
    window_2d
)

window_scaled = window_scaled.reshape(
    1,
    10,
    9
)


# ============================================================
# 6. RUN MULTI-TASK CNN
# ============================================================

print()
print("Running CNN...")

predictions = model.predict(
    window_scaled,
    verbose=0
)


# ============================================================
# 7. GET OUTPUT PROBABILITIES
# ============================================================

activity_probabilities = predictions[0][0]

environment_probabilities = predictions[1][0]

physiological_probabilities = predictions[2][0]


# ============================================================
# 8. GET PREDICTED CLASSES
# ============================================================

activity_index = int(
    np.argmax(activity_probabilities)
)

environment_index = int(
    np.argmax(environment_probabilities)
)

physiological_index = int(
    np.argmax(physiological_probabilities)
)


activity = activity_labels[
    activity_index
]

environment = environment_labels[
    environment_index
]

physiological = physiological_labels[
    physiological_index
]


# ============================================================
# 9. GET CONFIDENCE
# ============================================================

activity_confidence = float(
    activity_probabilities[
        activity_index
    ]
)

environment_confidence = float(
    environment_probabilities[
        environment_index
    ]
)

physiological_confidence = float(
    physiological_probabilities[
        physiological_index
    ]
)


# ============================================================
# 10. LOCAL SITUATIONAL FUSION
# ============================================================

risk_score = 0


if environment == "risk":

    risk_score += 2


if activity == "crawling":

    risk_score += 1


if physiological == "high":

    risk_score += 2


if risk_score >= 4:

    situational_status = "HIGH"

elif risk_score >= 2:

    situational_status = "ELEVATED"

else:

    situational_status = "NORMAL"


# ============================================================
# 11. EVENT TYPE
# ============================================================

if situational_status == "HIGH":

    event_type = "deterioration"

elif situational_status == "ELEVATED":

    event_type = "environment_change"

else:

    event_type = "status_update"


# ============================================================
# 12. CREATE FIREFIGHTER EVENT
# ============================================================

firefighter_event = {

    "node_id": "FF01",

    "timestamp":
        datetime.now().isoformat(),

    "activity":
        activity,

    "activity_confidence":
        round(
            activity_confidence,
            4
        ),

    "environment":
        environment,

    "environment_confidence":
        round(
            environment_confidence,
            4
        ),

    "physiological_state":
        physiological,

    "physiological_confidence":
        round(
            physiological_confidence,
            4
        ),

    "risk_score":
        risk_score,

    "situational_status":
        situational_status,

    "event_type":
        event_type,

    "x":
        10,

    "y":
        20

}


# ============================================================
# 13. EXAMPLE OTHER FIREFIGHTER EVENTS
# ============================================================

firefighter_events = [

    firefighter_event,

    {
        "node_id": "FF02",
        "x": 12,
        "y": 21,
        "activity": "walking",
        "environment": "risk",
        "physiological_state": "elevated",
        "situational_status": "ELEVATED",
        "event_type": "environment_change"
    },

    {
        "node_id": "FF03",
        "x": 50,
        "y": 60,
        "activity": "standing",
        "environment": "normal",
        "physiological_state": "normal",
        "situational_status": "NORMAL",
        "event_type": "status_update"
    }

]


# ============================================================
# 14. ZONE ASSIGNMENT
# ============================================================

for event in firefighter_events:

    if event["x"] < 30:

        event["zone"] = "A"

    else:

        event["zone"] = "B"


# ============================================================
# 15. FIREGROUND ZONE FUSION
# ============================================================

zones = {}


for event in firefighter_events:

    zone = event["zone"]

    if zone not in zones:

        zones[zone] = {
            "firefighters": 0,
            "high_events": 0,
            "elevated_events": 0,
            "environment_risk": 0
        }

    zones[zone]["firefighters"] += 1


    if event["situational_status"] == "HIGH":

        zones[zone]["high_events"] += 1


    elif event["situational_status"] == "ELEVATED":

        zones[zone]["elevated_events"] += 1


    if event["environment"] == "risk":

        zones[zone]["environment_risk"] += 1


# ============================================================
# 16. DETERMINE ZONE STATUS
# ============================================================

for zone, information in zones.items():

    if information["high_events"] >= 2:

        information["status"] = "HIGH"

    elif (
        information["high_events"] >= 1
        or information["environment_risk"] >= 2
    ):

        information["status"] = "ELEVATED"

    else:

        information["status"] = "NORMAL"


# ============================================================
# 17. TRUCK RESOURCE
# ============================================================

truck = {

    "truck_id":
        "TRUCK01",

    "water_capacity_liters":
        3000,

    "water_remaining_liters":
        1860,

    "flow_rate_liters_per_minute":
        18,

    "pump_status":
        "ON"

}


water_percentage = (

    truck["water_remaining_liters"]

    /

    truck["water_capacity_liters"]

) * 100


truck["water_remaining_percent"] = round(
    water_percentage,
    2
)


if truck["flow_rate_liters_per_minute"] > 0:

    truck["estimated_remaining_minutes"] = round(

        truck["water_remaining_liters"]

        /

        truck["flow_rate_liters_per_minute"],

        2

    )

else:

    truck["estimated_remaining_minutes"] = None


# ============================================================
# 18. OVERALL FIREGROUND FUSION
# ============================================================

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


if high_zones >= 2:

    overall_status = "HIGH"

elif high_zones >= 1:

    overall_status = "ELEVATED"

elif elevated_zones >= 1:

    overall_status = "ELEVATED"

elif risk_zones >= 2:

    overall_status = "ELEVATED"

else:

    overall_status = "NORMAL"


# ============================================================
# 19. ALERT PRIORITY
# ============================================================

if overall_status == "HIGH":

    alert_priority = "URGENT"

elif overall_status == "ELEVATED":

    alert_priority = "HIGH"

else:

    alert_priority = "NORMAL"


# ============================================================
# 20. COMMAND CENTER DISPLAY
# ============================================================

print()
print("==============================================")
print("       FIREGROUND INTELLIGENCE SYSTEM")
print("==============================================")


print()
print("LOCAL FIREFIGHTER AI")
print("----------------------------------------------")

print(
    "Node:",
    firefighter_event["node_id"]
)

print(
    "Activity:",
    activity
)

print(
    "Environment:",
    environment
)

print(
    "Physiological state:",
    physiological
)

print(
    "Local risk score:",
    risk_score
)

print(
    "Local status:",
    situational_status
)

print(
    "Event:",
    event_type
)


print()
print("FIREGROUND ZONES")
print("----------------------------------------------")


for zone, information in zones.items():

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
        "  Environment risk:",
        information["environment_risk"]
    )


print()
print("TRUCK")
print("----------------------------------------------")

print(
    "Truck:",
    truck["truck_id"]
)

print(
    "Water:",
    truck["water_remaining_liters"],
    "L"
)

print(
    "Water:",
    truck["water_remaining_percent"],
    "%"
)

print(
    "Flow:",
    truck["flow_rate_liters_per_minute"],
    "L/min"
)

print(
    "Estimated time:",
    truck["estimated_remaining_minutes"],
    "minutes"
)


print()
print("==============================================")
print("       OVERALL FIREGROUND STATUS")
print("==============================================")

print()

print(
    "Overall status:",
    overall_status
)

print(
    "Alert priority:",
    alert_priority
)


# ============================================================
# 21. SAVE COMPLETE SYSTEM RESULT
# ============================================================

system_result = {

    "timestamp":
        datetime.now().isoformat(),

    "firefighter_event":
        firefighter_event,

    "all_firefighter_events":
        firefighter_events,

    "zones":
        zones,

    "truck":
        truck,

    "fireground_status":
        overall_status,

    "alert_priority":
        alert_priority

}


with open(
    "../results/fireground_system_result.json",
    "w"
) as file:

    json.dump(
        system_result,
        file,
        indent=4
    )


print()
print("Complete system result saved!")
print(
    "Saved to: ../results/fireground_system_result.json"
)