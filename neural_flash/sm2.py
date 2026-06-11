def calculate_sm2(quality, repetition, interval, ease_factor):
    """
    Calculate the next interval, repetition count, and ease factor using the SM-2 algorithm.
    quality: 0-5 (0 = complete blackout, 5 = perfect response)
    """
    if quality >= 3:
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetition += 1
    else:
        repetition = 0
        interval = 1

    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < 1.3:
        ease_factor = 1.3

    return repetition, interval, ease_factor
