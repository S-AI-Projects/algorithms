# R24-T015 Repeatability Analysis for RandomizedSet

Source: `algorithms/map/randomized_set.py`

## Dependency Seam
- `RandomizedSet.__init__(rng: random.Random | None = None)`
- Allows injecting a deterministic pseudo-random number generator.
- Defaults to `None`, using system `random` for backward compatibility.

## Repeatability & Isolation Verification
- Run 1 (fresh instance): PASS
- Run 2 (repeat run): PASS
- Run 3 (after other instance ops): PASS
- Seeded RNG repeatability check: PASS
