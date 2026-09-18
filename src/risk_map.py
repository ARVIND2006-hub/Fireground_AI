import matplotlib.pyplot as plt


# ---------------------------------------
# Example firefighter positions/status
# ---------------------------------------

firefighters = [
    {
        "node_id": "FF01",
        "x": 10,
        "y": 20,
        "status": "HIGH"
    },
    {
        "node_id": "FF02",
        "x": 12,
        "y": 21,
        "status": "ELEVATED"
    },
    {
        "node_id": "FF03",
        "x": 50,
        "y": 60,
        "status": "NORMAL"
    }
]


# ---------------------------------------
# Assign a numeric level for plotting
# ---------------------------------------

status_level = {
    "NORMAL": 1,
    "ELEVATED": 2,
    "HIGH": 3
}


# ---------------------------------------
# Plot firefighters
# ---------------------------------------

for firefighter in firefighters:

    level = status_level[
        firefighter["status"]
    ]

    plt.scatter(
        firefighter["x"],
        firefighter["y"],
        s=200
    )

    plt.text(
        firefighter["x"] + 1,
        firefighter["y"] + 1,
        firefighter["node_id"]
        + " ("
        + firefighter["status"]
        + ")"
    )


# ---------------------------------------
# Configure map
# ---------------------------------------

plt.title("Fireground Situational Map")

plt.xlabel("X Position")
plt.ylabel("Y Position")

plt.grid(True)

plt.show()