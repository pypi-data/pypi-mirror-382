import sys
from datetime import datetime, timedelta
from typing import List


def parse_time(time_str: str) -> datetime:
    """Parse a time string in HH:MM format to a datetime object."""
    return datetime.strptime(time_str, "%H:%M")


def calculate_end_time(times: List[str], target_hours: float = 8.0) -> str:
    """
    Calculate the end time needed to complete target_hours of work.

    Args:
        times: List of time strings in HH:MM format representing work intervals
        target_hours: Target work hours (default: 8.0)

    Returns:
        Time string in HH:MM format when you can finish work
    """
    if len(times) < 2:
        print("Error: Please provide at least 2 time entries (start and current time)")
        sys.exit(1)

    # Parse all times
    parsed_times = [parse_time(t) for t in times]

    # Calculate total worked hours by pairing times
    total_worked = timedelta()
    for i in range(0, len(parsed_times) - 1, 2):
        start = parsed_times[i]
        end = parsed_times[i + 1]
        total_worked += end - start

    # Calculate remaining hours needed
    target_duration = timedelta(hours=target_hours)
    remaining = target_duration - total_worked

    # Last time entry is the current time (resume time)
    current_time = parsed_times[-1]

    # Calculate end time
    end_time = current_time + remaining

    return end_time.strftime("%H:%M")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: hmt <time1> <time2> [time3] ...")
        print("Example: hmt 8:00 12:00 14:00")
        print("  -> Calculates when you finish after working 8:00-12:00 and resuming at 14:00")
        sys.exit(1)

    times = sys.argv[1:]

    try:
        end_time = calculate_end_time(times)
        print(end_time)
    except ValueError as e:
        print(f"Error: Invalid time format. Please use HH:MM format (e.g., 8:00 or 08:00)")
        sys.exit(1)


if __name__ == "__main__":
    main()
