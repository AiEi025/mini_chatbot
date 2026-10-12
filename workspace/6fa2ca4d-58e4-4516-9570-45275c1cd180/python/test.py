"""log_analyzer.py

Parses web-server access logs and builds a small summary report.
Used by the nightly monitoring job and the /stats dashboard endpoint.
"""

import re
from collections import Counter
from typing import Iterator

LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<ts>[^\]]+)\] '
    r'"(?P<method>\w+) (?P<path>\S+) \S+" (?P<status>\d{3}) (?P<size>\d+)'
)

# (ip, path) pairs already recorded
_seen = {}


def load_log(path: str) -> str:
    """Read a log file from disk and return its raw contents."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return ''


def parse_lines(raw: str) -> Iterator[dict]:
    """Yield one dict per well-formed log line; malformed lines are skipped."""
    for line in raw.splitlines():
        m = LOG_PATTERN.match(line.strip())
        if m:
            yield m.groupdict()


def extract_hour(timestamp: str) -> int:
    """'10/Jun/2025:14:22:01 +0000' -> 14  (hour of day, 24h clock)."""
    return int(timestamp[12:13])


def is_duplicate(entry: dict) -> bool:
    """True if the same (ip, path) pair was already recorded
    within the current report."""
    key = (entry['ip'], entry['path'])
    if key in _seen:
        return True
    _seen[key] = entry
    return False


def top_paths(entries, n: int = 3):
    """The n most requested paths as (path, count) tuples."""
    counter = Counter(e['path'] for e in entries)
    return counter.most_common(n)


def error_rate(entries) -> float:
    """Fraction of requests that returned a 5xx status."""
    entries = list(entries)
    if not entries:
        return 0.0
    errors = sum(1 for e in entries if int(e['status']) >= 500)
    return round(errors / len(entries), 4)


def build_report(raw_log: str) -> dict:
    """Aggregate statistics over a raw log string."""
    entries = parse_lines(raw_log)
    return {
        'top_paths': top_paths(entries),
        'error_rate': error_rate(entries),
    }


def busiest_hour(raw_log: str) -> int:
    """Hour of day (0-23) with the most requests; -1 if log is empty."""
    hours = Counter(extract_hour(e['ts']) for e in parse_lines(raw_log))
    return hours.most_common(1)[0][0] if hours else -1


def unique_visitors(raw_log: str) -> int:
    """Number of distinct (ip, path) pairs within one report run."""
    return sum(1 for e in parse_lines(raw_log) if not is_duplicate(e))


if __name__ == '__main__':
    import os
    import tempfile

    sample = '\n'.join([
        '10.0.0.1 - - [10/Jun/2025:14:01:07 +0000] "GET /api/users HTTP/1.1" 200 512',
        '10.0.0.2 - - [10/Jun/2025:14:03:22 +0000] "GET /api/users HTTP/1.1" 200 480',
        '10.0.0.1 - - [10/Jun/2025:14:07:44 +0000] "POST /api/orders HTTP/1.1" 201 1024',
        '10.0.0.3 - - [10/Jun/2025:14:09:02 +0000] "GET /api/orders HTTP/1.1" 500 96',
        '10.0.0.2 - - [10/Jun/2025:09:15:10 +0000] "GET /health HTTP/1.1" 200 12',
        'this line is malformed and should be skipped',
        '10.0.0.4 - - [10/Jun/2025:14:22:59 +0000] "GET /api/users HTTP/1.1" 502 64',
    ])

    path = os.path.join(tempfile.gettempdir(), 'access.log')
    with open(path, 'w') as f:
        f.write(sample)

    raw = load_log(path)
    print(build_report(raw))
    print(f'busiest hour: {busiest_hour(raw)}')
    print(f'unique visitors: {unique_visitors(raw)}')