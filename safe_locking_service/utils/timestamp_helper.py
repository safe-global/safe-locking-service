import datetime


def get_formated_timestamp(timestamp: datetime):
    """

    :param timestamp:
    :return: return formatted timestamp YYYY-MM-DDTHH:MM:SSZ
    """
    return timestamp.isoformat().replace("+00:00", "Z")
