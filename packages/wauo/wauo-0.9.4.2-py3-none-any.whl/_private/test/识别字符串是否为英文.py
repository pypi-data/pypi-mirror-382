def is_ok(text: str):
    english_chars = sum(
        c.isalpha() and (c.isascii() or c.lower() in "abcdefghijklmnopqrstuvwxyz")
        for c in text
    )
    total_chars = sum(c.isalpha() for c in text)
    if total_chars == 0:
        return False
    return (english_chars / total_chars) > 0.9


text = "Я тебе кохаю!"
result = is_ok(text)
print(result)
