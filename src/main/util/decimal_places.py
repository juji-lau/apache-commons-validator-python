import re

def max_decimal_places(regex_pattern: str):
    pattern = regex_pattern.strip('^$')

    match = re.search(r"\.\s*(\\d(?:\{\d+(?:,\d*)?\}|(?:\\d)*|\+|\*))", pattern)
    if not match:
        return 0
    
    decimal_part = match.group(1)
    quant_match = re.match(r"\\d\{(\d+)(?:,(\d*))?\}", decimal_part)
    if quant_match:
        min_digits = int(quant_match.group(1))
        max_digits = quant_match.group(2)
        if max_digits:
            return int(max_digits)
        return min_digits
    
    repeated_digits = re.findall(r"\\d", decimal_part)
    if repeated_digits:
        return len(repeated_digits)
    
    if r"\d+" in decimal_part or r"\d*" in decimal_part:
        return -1
