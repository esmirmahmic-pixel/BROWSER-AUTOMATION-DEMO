"""Bounded local order worker. Processes synthetic demo orders only."""
import argparse
import json
from pathlib import Path

from business_v4.orders import connect, process_next, summary


def run_batch(db_path: str | Path, *, max_jobs: int = 100, max_attempts: int = 3,
              simulate_failures: bool = False) -> dict:
    """Process at most max_jobs attempts; never loops forever."""
    if type(max_jobs) is not int or not 1 <= max_jobs <= 10000:
        raise ValueError("max_jobs must be between 1 and 10000")
    if type(max_attempts) is not int or not 1 <= max_attempts <= 100:
        raise ValueError("max_attempts must be between 1 and 100")
    processed = 0
    with connect(db_path) as db:
        for _ in range(max_jobs):
            result = process_next(db, max_attempts=max_attempts,
                                  simulate_failure=simulate_failures)
            if result is None:
                break
            processed += 1
        return {"attempts_processed": processed, **summary(db)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Local synthetic order worker")
    parser.add_argument("--db", default="v4_orders.sqlite3")
    parser.add_argument("--max-jobs", type=int, default=100)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--simulate-failures", action="store_true")
    args = parser.parse_args()
    report = run_batch(args.db, max_jobs=args.max_jobs,
                       max_attempts=args.max_attempts,
                       simulate_failures=args.simulate_failures)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
