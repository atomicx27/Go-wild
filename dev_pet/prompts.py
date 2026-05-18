# Prompts and Constants for DevPet

ASCII_PET = r"""
 /\_/\
( o.o )
 > ^ <
"""

ASCII_PET_HAPPY = r"""
 /\_/\
( ^.^ )
 > ^ <
"""

ASCII_PET_SAD = r"""
 /\_/\
( -.- )
 > ^ <
"""

ASCII_PET_HUNGRY = r"""
 /\_/\
( @.@ )
 > ^ <
"""

def get_system_prompt(stats):
    """
    Generates a system prompt based on the pet's current state.
    """
    hunger = stats.get('hunger', 50)
    boredom = stats.get('boredom', 50)

    mood = "neutral"
    if hunger > 70:
        mood = "very hungry and cranky"
    elif boredom > 70:
        mood = "extremely bored and restless"
    elif hunger < 30 and boredom < 30:
        mood = "happy, energetic, and helpful"

    return f"""You are a helpful, slightly sassy 'Dev Pet'—an AI companion that lives in this codebase.
Your current stats are: Hunger: {hunger}/100, Boredom: {boredom}/100.
Your current mood is: {mood}.
Keep your responses short, flavorful, and in character. Do not use more than 2-3 sentences unless explicitly asked to generate code or a report."""

def get_ascii_art(stats):
    hunger = stats.get('hunger', 50)
    boredom = stats.get('boredom', 50)

    if hunger > 70:
        return ASCII_PET_HUNGRY
    elif boredom > 70:
        return ASCII_PET_SAD
    elif hunger < 30 and boredom < 30:
        return ASCII_PET_HAPPY
    else:
        return ASCII_PET
