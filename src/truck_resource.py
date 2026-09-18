import json


# ---------------------------------------
# Example fire truck status
# ---------------------------------------

truck = {
    "truck_id": "TRUCK01",

    "water_capacity_liters": 3000,
    "water_remaining_liters": 1860,

    "flow_rate_liters_per_minute": 18,

    "pump_status": "ON"
}


# ---------------------------------------
# Calculate water percentage
# ---------------------------------------

water_percentage = (
    truck["water_remaining_liters"]
    / truck["water_capacity_liters"]
) * 100


truck["water_remaining_percent"] = round(
    water_percentage,
    2
)


# ---------------------------------------
# Estimate remaining operation time
# ---------------------------------------

if truck["flow_rate_liters_per_minute"] > 0:

    remaining_minutes = (
        truck["water_remaining_liters"]
        / truck["flow_rate_liters_per_minute"]
    )

else:

    remaining_minutes = None


truck["estimated_remaining_minutes"] = round(
    remaining_minutes,
    2
)


# ---------------------------------------
# Display
# ---------------------------------------

print("======================================")
print(" FIRE TRUCK RESOURCE STATUS")
print("======================================")

print()

print("Truck ID:",
      truck["truck_id"])

print(
    "Water remaining:",
    truck["water_remaining_liters"],
    "L"
)

print(
    "Water remaining:",
    truck["water_remaining_percent"],
    "%"
)

print(
    "Flow rate:",
    truck["flow_rate_liters_per_minute"],
    "L/min"
)

print(
    "Estimated remaining time:",
    truck["estimated_remaining_minutes"],
    "minutes"
)

print(
    "Pump status:",
    truck["pump_status"]
)


# ---------------------------------------
# Save
# ---------------------------------------

with open(
    "../results/truck_status.json",
    "w"
) as file:

    json.dump(
        truck,
        file,
        indent=4
    )


print()
print("Truck status saved!")
print("Saved to: ../results/truck_status.json")