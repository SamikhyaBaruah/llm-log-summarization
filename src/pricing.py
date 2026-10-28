def apply_discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError("bad percent")
    return round(price * (1 - percent / 100), 2)