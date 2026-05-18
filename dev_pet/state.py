import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

DEFAULT_STATE = {
    "hunger": 50,
    "boredom": 50,
    "energy": 100,
    "knowledge": 0
}

def load_state():
    if not os.path.exists(STATE_FILE):
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return DEFAULT_STATE.copy()

def save_state(state):
    # Ensure stats stay within bounds (0-100) except knowledge
    state['hunger'] = max(0, min(100, state.get('hunger', 50)))
    state['boredom'] = max(0, min(100, state.get('boredom', 50)))
    state['energy'] = max(0, min(100, state.get('energy', 100)))

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def update_stat(stat_name, amount):
    state = load_state()
    if stat_name in state:
        state[stat_name] += amount
        save_state(state)
    return state
