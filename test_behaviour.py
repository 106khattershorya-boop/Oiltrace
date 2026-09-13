from behaviour_analysis import (
    analyze_vessel_behaviour
)


# ============================================================
# SAMPLE VESSEL BEHAVIOUR
# ============================================================

result = analyze_vessel_behaviour(

    # Speed anomaly
    speed=0.70,

    # Stopping anomaly
    stop=0.80,

    # Course deviation
    course=0.60,

    # AIS gap
    ais_gap=0.40,

    # Loitering
    loitering=0.70
)


# ============================================================
# PRINT RESULT
# ============================================================

print("=" * 60)
print("VESSEL BEHAVIOUR ANALYSIS")
print("=" * 60)

print(
    "\nBehaviour score:",
    result["behaviour_score"]
)

print(
    "Behaviour level:",
    result["behaviour_level"]
)

print(
    "\nReasons:"
)

for reason in result["reasons"]:

    print(
        "-",
        reason
    )

print("\n")
print("=" * 60)
print("BEHAVIOUR ANALYSIS COMPLETE")
print("=" * 60)