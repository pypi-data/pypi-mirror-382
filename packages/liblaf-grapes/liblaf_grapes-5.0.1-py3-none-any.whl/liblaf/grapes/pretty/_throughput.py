import about_time


def pretty_throughput(value: float, unit: str = "") -> str:
    throughput: about_time.HumanThroughput = about_time.HumanThroughput(value, unit)
    return throughput.as_human()
