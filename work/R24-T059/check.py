from pathlib import Path
import importlib.util
import random
import time
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
file_path = root / "algorithms" / "array" / "merge_intervals.py"

spec = importlib.util.spec_from_file_location("merge_intervals", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Interval = module.Interval
merge_intervals = module.merge_intervals

def test_anchors():
    res1 = Interval.merge([Interval(1, 3), Interval(2, 6)])
    assert res1 == [Interval(1, 6)], f"Anchor 1 failed: {res1}"

    res2 = Interval.print_intervals([Interval(1, 3)])
    assert res2 == "Interval (1, 3)", f"Anchor 2 failed: {res2}"

    res3 = merge_intervals([[1, 3], [2, 6], [8, 10]])
    assert res3 == [[1, 6], [8, 10]], f"Anchor 3 failed: {res3}"
    print("All anchor tests passed.")

def test_neighbors():
    disjoint = Interval.merge([Interval(1, 3), Interval(4, 7)])
    assert disjoint == [Interval(1, 3), Interval(4, 7)], f"Neighbor failed: {disjoint}"

    nested = Interval.merge([Interval(1, 10), Interval(2, 5)])
    assert nested == [Interval(1, 10)], f"Neighbor failed: {nested}"

    chain = Interval.merge([Interval(1, 4), Interval(2, 6), Interval(5, 8)])
    assert chain == [Interval(1, 8)], f"Neighbor failed: {chain}"
    print("All neighbor tests passed.")

def verify_correctness(merged_list):
    # Verify intervals are ordered and non-overlapping
    for i in range(len(merged_list) - 1):
        assert merged_list[i].end < merged_list[i + 1].start, (
            f"Overlapping intervals detected: {merged_list[i]} and {merged_list[i + 1]}"
        )

def run_scaling_experiment():
    sizes = [500, 2000, 8000]
    repetitions = 5
    rng = random.Random(42)

    results = {}
    for size in sizes:
        timings = []
        for _ in range(repetitions):
            # Generate fresh inputs outside timing window
            raw_intervals = []
            for _ in range(size):
                start = rng.randint(0, size * 10)
                span = rng.randint(1, 50)
                raw_intervals.append(Interval(start, start + span))

            # Timed pure algorithm operation
            t0 = time.perf_counter()
            merged = Interval.merge(raw_intervals)
            t1 = time.perf_counter()
            timings.append(t1 - t0)

            # Correctness verification outside timed interval
            verify_correctness(merged)

        timings.sort()
        median = timings[repetitions // 2]
        t_min = timings[0]
        t_max = timings[-1]
        results[size] = (median, t_min, t_max)
        print(f"Size N={size:4d}: median={median*1000:.3f}ms, min={t_min*1000:.3f}ms, max={t_max*1000:.3f}ms")

    return results

if __name__ == "__main__":
    test_anchors()
    test_neighbors()
    results = run_scaling_experiment()
    print("Complexity experiment and correctness assertions completed successfully!")
