import re


def compress_string_spaces(s):
    return re.sub(r"\s+", " ", s).strip()
