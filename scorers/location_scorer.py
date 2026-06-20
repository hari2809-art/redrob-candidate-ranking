# scorers/location_scorer.py

def score_location(candidate):

    location = (
        candidate["profile"]
        .get("location", "")
        .lower()
    )

    relocate = (
        candidate["redrob_signals"]
        .get("willing_to_relocate", False)
    )

    if "pune" in location:
        return 1.0

    if "noida" in location:
        return 1.0

    if any(city in location for city in [
        "hyderabad",
        "mumbai",
        "delhi",
        "gurgaon",
        "gurugram"
    ]):
        return 0.8

    if relocate:
        return 0.6

    return 0.3