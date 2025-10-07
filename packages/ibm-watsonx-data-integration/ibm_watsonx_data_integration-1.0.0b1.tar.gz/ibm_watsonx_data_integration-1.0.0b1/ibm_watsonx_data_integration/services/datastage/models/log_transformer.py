import re
from datetime import datetime

_LOG_LEVEL_MAP = {"E": "ERROR", "I": "INFO", "D": "DEBUG", "W": "WARN"}


def transform_logs(logs: list[str]):
    i = 1
    for l in logs:
        tf = _transform_line(l)
        if tf == l:
            yield l
        else:
            yield str(i) + " " + _transform_line(l)
            i += 1


def _transform_line(line: str) -> str:
    if not line.startswith("##"):
        return line

    results = re.match(
        r"##([A-za-z]) ([A-Za-z0-9-]+) (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})(?:\([0-9]+\))? (.*)",
        line,
    )
    if not results:
        return line

    level_code = results[1].upper()
    iis_code = results[2].upper()
    date = results[3]
    timestamp = results[4]
    message = results[5]

    dt = datetime.strptime(date, "%Y-%m-%d")

    return " ".join(
        [
            f"{dt.month}/{dt.day:02}/{dt.year}",
            timestamp,
            _LOG_LEVEL_MAP.get(level_code, "INFO"),
            iis_code,
            message,
        ]
    )
