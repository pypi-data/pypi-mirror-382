# HMT - How Much Time

A simple CLI tool to calculate when you can finish your 8-hour workday.

## Installation

```bash
pip install hmt
```

## Usage

```bash
hmt 8:00 12:00 14:00
```

This calculates when you can finish work after:
- Working from 8:00 to 12:00 (4 hours)
- Resuming at 14:00 (after lunch break)
- Output: `18:00` (4 more hours needed)

## How it works

- Takes time entries as arguments in HH:MM format
- Pairs consecutive times as work intervals (start-end, start-end, etc.)
- Calculates total worked hours
- Uses the last time as your resume time
- Calculates when you'll complete 8 hours total

## Examples

```bash
# Morning work + lunch break
hmt 8:00 12:00 14:00
# Output: 18:00

# Different schedule
hmt 9:00 12:30 13:30
# Output: 18:00

# Multiple breaks
hmt 8:00 10:00 11:00 12:00 13:00
# Output: 18:00
```

## License

MIT
