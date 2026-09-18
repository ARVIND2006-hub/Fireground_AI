import json
import math


# ---------------------------------------
# Example firefighter events
# ---------------------------------------

events = [

    {
        "node_id": "FF01",
        "x": 10,
        "y": 20,
        "status": "HIGH",
        "environment": "risk"
    },

    {
        "node_id": "FF02",
        "x": 12,
        "y": 21,
        "status": "ELEVATED",
        "environment": "risk"
    },

    {
        "node_id": "FF03",
        "x": 50,
        "y": 60,
        "status": "NORMAL",
        "environment": "normal"
    }
]


# ---------------------------------------
# Calculate distance between firefighters
# ---------------------------------------

def distance(event1, event2):

    dx = event1["x"] - event2["x"]
    dy = event1["y"] - event2["y"]

    return math.sqrt(dx * dx + dy * dy)


# ---------------------------------------
# Display firefighter positions
# ---------------------------------------

print("======================================")
print(" FIREFIGHTER POSITION DATA")
print("======================================")

for event in events:

    print()
    print(event["node_id"])
    print("Position:", event["x"], ",", event["y"])
    print("Status:", event["status"])
    print("Environment:", event["environment"])


# ---------------------------------------
# Find nearby firefighters
# ---------------------------------------

print()
print("======================================")
print(" PROXIMITY ANALYSIS")
print("======================================")

threshold = 5.0

for i in range(len(events)):

    for j in range(i + 1, len(events)):

        d = distance(
            events[i],
            events[j]
        )

        print(
            events[i]["node_id"],
            "<->",
            events[j]["node_id"],
            "distance:",
            round(d, 2)
        )

        if d <= threshold:

            print("  Nearby firefighters")


# ---------------------------------------
# Create position map
# ---------------------------------------

position_map = []

for event in events:

    position_map.append({
        "node_id": event["node_id"],
        "x": event["x"],
        "y": event["y"],
        "status": event["status"]
    })


# ---------------------------------------
# Save
# ---------------------------------------

with open(
    "../results/firefighter_positions.json",
    "w"
) as file:

    json.dump(
        position_map,
        file,
        indent=4
    )


print()
print("Position data saved!")
print(
    "Saved to: ../results/firefighter_positions.json"
)