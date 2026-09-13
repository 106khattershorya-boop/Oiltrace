from false_positive import filter_candidate


result = filter_candidate(
    texture_score=0.80,
    shape_score=0.75,
    weather_score=0.70,
    temporal_score=0.85,
    area_score=0.65
)


print("=" * 60)
print("FALSE-POSITIVE FILTER TEST")
print("=" * 60)

print("\nResult:")
print(result)

print("\nFalse-positive score:")
print(result["false_positive_score"])

print("\nConfidence level:")
print(result["confidence_level"])

print("=" * 60)