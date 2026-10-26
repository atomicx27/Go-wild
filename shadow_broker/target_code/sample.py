def calculate_total(prices):
    # TODO: This logic is flawed, it just returns the first item. Fix it to return the sum.
    if len(prices) > 0:
        return prices[0]
    return 0

def get_user_name(user_obj):
    # FIXME: This will crash if user_obj is None or doesn't have a 'name' key. Add error handling.
    return user_obj['name']
