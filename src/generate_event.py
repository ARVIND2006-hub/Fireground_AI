from datetime import datetime
import json


# ---------------------------------------
# Example CNN/fusion results
# ---------------------------------------

activity = "crawling"
environment = "risk"
physiological = "high"

risk_score = 5
situational_status = "HIGH"


# ---------------------------------------
# Create event
# ---------------------------------------

event = {
    "node_id": "FF01",
    "timestamp": datetime.now().isoformat(),

    "activity": activity,
    "environment": environment,
    "physiological_state": physiological,

    "risk_score": risk_score,
    "situational_status": situational_status,

    "event_type": "deterioration"
}


# ---------------------------------------
# Convert event to JSON
# ---------------------------------------

event_json = json.dumps(
    event,
    indent=4
)


# ---------------------------------------
# Display event
# ---------------------------------------

print("======================================")
print(" FIREGROUND EVENT")
print("======================================")
print(event_json)


# ---------------------------------------
# Save event
# ---------------------------------------

with open(
    "../results/firefighter_event.json",
    "w"
) as file:

    file.write(event_json)


print()
print("Event saved successfully!")
print("Saved to: ../results/firefighter_event.json")