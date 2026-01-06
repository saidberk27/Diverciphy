from datetime import datetime
import statistics

def is_timestamp_consistent(date_objects):
    if not date_objects:
        return

    THRESHOLD_MS = 10000 
    timestamps_ms = [int(dt.timestamp() * 1000) for dt in date_objects]
    timestamp_median = statistics.median(timestamps_ms)
    
    outliers_found = False
    for ts in timestamps_ms:
        diff = abs(ts - timestamp_median)
        if diff > THRESHOLD_MS:
            outliers_found = True
            original_dt = datetime.fromtimestamp(ts / 1000.0)
            print(f"ACID Warning: Outlier detected!")
            print(f" - Incorrect Time: {original_dt}")
            print(f" - Median Value: {datetime.fromtimestamp(timestamp_median / 1000.0)}")
            print(f" - Difference: {diff / 1000:.2f} seconds\n")

    return not outliers_found

if __name__ == "__main__":
    # Test data
    dates = [
        datetime(2024, 5, 20, 10, 0, 1),
        datetime(2024, 5, 20, 10, 0, 2),
        datetime(2024, 5, 20, 10, 0, 3),
        datetime(2024, 5, 20, 10, 0, 12) 
    ]

    timestamp_consistency_checker(dates)