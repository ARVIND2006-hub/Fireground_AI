import json


# ---------------------------------------
# Example events from multiple firefighters
# ---------------------------------------

events = [

    {
        "node_id": "FF01",
        "activity": "crawling",
        "environment": "risk",
        "physiological_state": "high",
        "situational_status": "HIGH",
        "event_type": "deterioration"
    },

    {
        "node_id": "FF02",
        "activity": "walking",
        "environment": "risk",
        "physiological_state": "elevated",
        "situational_status": "ELEVATED",
        "event_type": "environment_change"
    },

    {
        "node_id": "FF03",
        "activity": "standing",
        "environment": "normal",
        "physiological_state": "normal",
        "situational_status": "NORMAL",
        "event_type": "status_update"
    }
]


# ---------------------------------------
# Count conditions
# ---------------------------------------

high_count = 0
elevated_count = 0
risk_environment_count = 0


for event in events:

    if event["situational_status"] == "HIGH":
        high_count += 1

    elif event["situational_status"] == "ELEVATED":
        elevated_count += 1

    if event["environment"] == "risk":
        risk_environment_count += 1


# ---------------------------------------
# Determine fireground status
# ---------------------------------------

if high_count >= 2:

    fireground_status = "HIGH"

elif high_count >= 1 or risk_environment_count >= 2:

    fireground_status = "ELEVATED"

else:

    fireground_status = "NORMAL"


# ---------------------------------------
# Create fireground picture
# ---------------------------------------

fireground = {
    "number_of_firefighters": len(events),
    "high_events": high_count,
    "elevated_events": elevated_count,
    "environment_risk_nodes": risk_environment_count,
    "fireground_status": fireground_status
}


# ---------------------------------------
# Display
# ---------------------------------------

print("======================================")
print(" FIREGROUND-LEVEL FUSION")
print("======================================")

print()

print("Firefighters:", len(events))
print("HIGH events:", high_count)
print("ELEVATED events:", elevated_count)
print("Environment-risk nodes:", risk_environment_count)

print()
print("Fireground status:", fireground_status)


# ---------------------------------------
# Save result
# ---------------------------------------

with open(
    "../results/fireground_status.json",
    "w"
) as file:

    json.dump(
        fireground,
        file,
        indent=4
    )


print()
print("Fireground status saved!")
print("Saved to: ../results/fireground_status.json")