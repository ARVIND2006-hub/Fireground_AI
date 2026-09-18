import json


# ---------------------------------------
# Example firefighter events
# ---------------------------------------

events = [

    {
        "node_id": "FF01",
        "zone": "A",
        "activity": "crawling",
        "environment": "risk",
        "physiological_state": "high",
        "situational_status": "HIGH"
    },

    {
        "node_id": "FF02",
        "zone": "A",
        "activity": "walking",
        "environment": "risk",
        "physiological_state": "elevated",
        "situational_status": "ELEVATED"
    },

    {
        "node_id": "FF03",
        "zone": "B",
        "activity": "standing",
        "environment": "normal",
        "physiological_state": "normal",
        "situational_status": "NORMAL"
    }
]


# ---------------------------------------
# Group events by zone
# ---------------------------------------

zones = {}


for event in events:

    zone = event["zone"]

    if zone not in zones:
        zones[zone] = []

    zones[zone].append(event)


# ---------------------------------------
# Analyze each zone
# ---------------------------------------

zone_status = {}


for zone, zone_events in zones.items():

    high = 0
    elevated = 0
    risk = 0

    for event in zone_events:

        if event["situational_status"] == "HIGH":
            high += 1

        elif event["situational_status"] == "ELEVATED":
            elevated += 1

        if event["environment"] == "risk":
            risk += 1

    if high >= 2:
        status = "HIGH"

    elif high >= 1 or risk >= 2:
        status = "ELEVATED"

    else:
        status = "NORMAL"

    zone_status[zone] = {
        "firefighters": len(zone_events),
        "high_events": high,
        "elevated_events": elevated,
        "environment_risk": risk,
        "status": status
    }


# ---------------------------------------
# Display zone information
# ---------------------------------------

print("======================================")
print(" FIREGROUND ZONE ANALYSIS")
print("======================================")

for zone, status in zone_status.items():

    print()
    print("Zone:", zone)
    print("Firefighters:", status["firefighters"])
    print("HIGH events:", status["high_events"])
    print("ELEVATED events:", status["elevated_events"])
    print("Environment risk:", status["environment_risk"])
    print("Zone status:", status["status"])


# ---------------------------------------
# Save
# ---------------------------------------

with open(
    "../results/fireground_zones.json",
    "w"
) as file:

    json.dump(
        zone_status,
        file,
        indent=4
    )


print()
print("Zone analysis saved!")
print("Saved to: ../results/fireground_zones.json")