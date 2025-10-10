from pynput import keyboard
import json
import time
import datetime
import threading
import os
import sys
from termcolor import colored
from pyTwistyScrambler import (scrambler333, scrambler222, scrambler444,
                                scrambler555, scrambler666, scrambler777,
                                skewbScrambler, megaminxScrambler, squareOneScrambler, pyraminxScrambler)

if len(sys.argv) > 1:
    solve_file = str(sys.argv[1])
    path = sys.argv[2] if len(sys.argv) > 2 else "C:/timerapp/"
else: 
    solve_file = "solves.json"
    path = "C:/timerapp/"

os.makedirs(path, exist_ok=True)
save_path = os.path.join(path, solve_file)

session_num = 1
session = f"session{session_num}"
solving = False
starting = False
prev_stats = []
time_stats = []
times = []
formatted_times = [time / 1000 for time in times] if times else []
EVENTS = [None, "222so", "444wca", "555wca", "666wca", "777wca", "mgmp", "pyrso", "skbso", "sqrs"]
EVENT_NAMES = ["3x3", "2x2", "4x4", "5x5", "6x6", "7x7", "Megaminx", "Pyraminx", "Skewb", "Sq-1"]
event_index = 0
scramble = None
in_main = True
time_check = False
event = None
choice = None
reset_menu = False
dumb_msg = None

scramble_types = {None: scrambler333.get_WCA_scramble,
                  "222so": scrambler222.get_WCA_scramble,
                  "444wca": scrambler444.get_random_state_scramble,
                  "555wca": scrambler555.get_WCA_scramble,
                  "666wca": scrambler666.get_WCA_scramble,
                  "777wca": scrambler777.get_WCA_scramble,
                  "skbso": skewbScrambler.get_WCA_scramble,
                  "mgmp": megaminxScrambler.get_WCA_scramble,
                  "pyrso": pyraminxScrambler.get_WCA_scramble,
                  "sqrs": squareOneScrambler.get_WCA_scramble}

# // Data Handling

def save_data(time_stats):
    global solve_file
    try:
        with open(save_path) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}

    if session not in data:
        data[session] = []

    data[session].append(time_stats)
    prev_stats.append(time_stats)

    with open(save_path, "w") as f:
        json.dump(data, f, indent=4)


def load_data(save_path):
    global times, event
    try:
        with open(save_path) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
            data = {}
    
    try:
        session_data_str = data["properties"]["sessionData"]
        session_data = json.loads(session_data_str)
        session_info = session_data[str(session_num)]
        event = session_info["opt"]["scrType"]
        if not event:
            event = None
    except Exception:
        event = None

    solves = data.get(session)
    times = []
    prev_stats.clear()
    if solves:
        for solve in solves:
            time = solve[0][1] + solve[0][0]
            times.append(time)
            prev_stats.append(solve)
    else:
        times = []

def reset():
    global reset_menu, session, save_path
    if reset_menu:
        try:
            with open(save_path) as f:
                data = json.load(f)
        except:
            data = {}

        data[session] = []

        with open(save_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        load_data(solve_file)
        print_data()
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Reset Session? -> r\nCancel -> e")

# // Properties Handling

def properties(data):
    if "properties" not in data:
        data["properties"] = {}
    if "sessionData" not in data["properties"]:
        data["properties"]["sessionData"] = json.dumps({})

    try:
        session_data = json.loads(data["properties"]["sessionData"])
    except Exception:
        session_data = {}
    
    if str(session_num) not in session_data:
        session_data[str(session_num)] = {"opt": {"scrType": ""}}
    elif "opt" not in session_data[str(session_num)]:
        session_data[str(session_num)] = {"opt": {"scrType": ""}}
    elif "scrType" not in session_data[str(session_num)]["opt"]:
        session_data[str(session_num)]["opt"]["scrType"] = ""

    return session_data

def get_scramble():
    global event
    scramble = scramble_types.get(event)
    return [scramble()] if scramble else [scrambler333.get_WCA_scramble()]

# // Timer Functions

def timer_start():
    global solving, time_stats, scramble
    start_time = time.time()
    while solving:
        current_time = time.time()
        print(f"{' ' * 50}{round(current_time - start_time, 3)}{' ' * 50}", end="\r")
        time.sleep(0.001)
    result = current_time - start_time
    time_stats = [[0, int(result * 1000 / 10) * 10], [" ".join(scramble.copy())], "", int(datetime.datetime.now().timestamp())]

    solve_check(time_stats, result)

def solve_check(time_stats, result):
    global times, in_main, time_check, choice
    choice = None
    time_check = True
    in_main = False
    os.system('cls' if os.name == 'nt' else 'clear')

    print(round(result, 3))
    print("2 -> +2 Penalty")
    print("3 -> DNF")
    print("Backspace -> Delete")
    print("Enter -> Continue")

    while True:
        if choice in ('2', '3', '', 'backspace'):
            break
        time.sleep(0.01)

    if choice == "2":
        time_stats[0][0] = 2000
    elif choice == "3":
        time_stats[0][0] = -1
    elif choice == "backspace":
        time_check = False
        print_data()
        return
    else:
        pass

    time_check = False
    save_data(time_stats)

    t = get_time(time_stats)
    times.append(t)

    print_data()

# // Key Listener

def on_press(key):
    global solving, starting, time_check, choice, reset_menu
    if key == keyboard.Key.space:
        if in_main:
            if not solving:
                starting = True
                print(f"{' ' * 50}{colored('0.000', 'green')}{' ' * 50}", end="\r")
                return
            else:
                solving = False

    if time_check:
        if key == keyboard.Key.enter:
            choice = ''
        elif key == keyboard.Key.backspace:
            choice = 'backspace'

    if key == keyboard.Key.right:
        change_sess(1)
    elif key == keyboard.Key.left:
        change_sess(-1)

    if key == keyboard.Key.up:
        change_event(1)
    elif key == keyboard.Key.down:
        change_event(-1)

    try:
        if key.char == 'r':
            reset_menu = not reset_menu
            reset()
        if key.char == 'q':
            view_stats()
        if key.char == 'e':
            print_data()
        if key.char == 'h':
            help_menu()
        if time_check:
            if key.char == '2':
                choice = '2'
            elif key.char == '3':
                choice = '3'
    except Exception:
        pass
   
def on_release(key):
    global solving, starting
    if key == keyboard.Key.space:
        if starting and not solving:
            solving = True
            threading.Thread(target=timer_start).start()
            starting = False

# // Time Calculations

def get_time(solve):
    penalty = solve[0][0]
    base_time = solve[0][1]

    if penalty == -1:
        return None
    return base_time + penalty

def calculate_avgs(solves, n):
    last_n = solves[-n:]
    dnfs = sum(1 for time in last_n if time is None)
    if dnfs >= 2:
        return "DNF"
    
    avg = [time if time is not None else float('inf') for time in last_n]

    min_time = min(time for time in avg if time != float('inf'))
    max_time = max(avg)
    wca_avg = sum(avg) - min_time - max_time

    return round(wca_avg / (n - 2), 3)

# // Change Session / Event

def change_sess(n):
    global session, session_num, EVENTS, event_index, session_num, solve_file
    i = session_num + n
    if i < 1:
        return
    session_num = i
    session = f"session{session_num}"
    load_data(solve_file)
    print_data()

def change_event(n):
    global EVENTS, event_index, event
    event_index = (event_index + n) % len(EVENTS)
    event = EVENTS[event_index]

    try:
        with open(solve_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}

    session_data = properties(data)
    session_data[str(session_num)]["opt"]["scrType"] = "" if event is None else event
    data["properties"]["sessionData"] = json.dumps(session_data)

    with open(solve_file, "w") as f:
        json.dump(data, f, indent=4)

    print_data()

# // Print Data

def help_menu():
    global in_main
    in_main = False
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nCommand Line Arguments:\n")
    print("[filename.json] [directory]")
    print("\nGeneral:\n")
    print("e -> Return")
    print("q -> View Session Data")
    print("r -> Reset Session")
    print("\nIn Main Menu:\n")
    print("Left/Right -> Change Session by one")
    print("Up/Down -> Change event by one")

def view_stats():
    global prev_stats, in_main, EVENT_NAMES, event_index
    in_main = False
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Event: {EVENT_NAMES[event_index]}")
    for i, solve in enumerate(prev_stats, 1):
        time = get_time(solve)
        if time is None:
            time = "DNF"
        else:
            time = round(time / 1000, 3)
        scramble = " ".join(solve[1])
        date = datetime.datetime.fromtimestamp(solve[3]).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}) {colored(time, 'green')} | {colored(scramble, 'yellow')} | {colored(date, 'magenta')}")
    print("\ne -> Return")

def print_data():
    global scramble, formatted_times, time_stats, in_main
    in_main = True
    os.system('cls' if os.name == 'nt' else 'clear')

    formatted_times = []

    single = float("inf")
    ao5 = None
    ao12 = None
    prev_solve = None

    for time in times:
        formatted_times.append(time / 1000 if time is not None else None)

    if formatted_times:
        prev_solve = formatted_times[-1]
        if not prev_solve:
            prev_solve = "DNF"
        try:
            single = min([time for time in formatted_times if time is not None])
        except:
            single = "DNF"

    if len(formatted_times) >= 5:
        ao5 = calculate_avgs(formatted_times, 5)
        if ao5 is None:
            ao5 = "DNF"
    if len(formatted_times) >= 12:
        ao12 = calculate_avgs(formatted_times, 12)

    print_header(prev_solve, ao5, ao12, single)

    if time_stats:
        global dumb_msg
        dumb_msg = None
        unformatted_times = [time for time in times[:-1] if time is not None]
        unformatted_single = min(unformatted_times, default=None)

        if unformatted_single is not None and time_stats[0][1] < unformatted_single:
            dumb_msg = "New PB!! (it isn't WR so don't get too excited)"
        if time_stats[0][0] == -1:
            dumb_msg = "dude how can you dnf a solve. smh"
        elif time_stats[0][0] == 2000:
            dumb_msg = "cmon really, +2s dont count at home"
        else:
            if len(prev_stats) > 1:
                prev_s = prev_stats[-2]
                if prev_s[0][0] == 2000:
                    dumb_msg = "okay you took the +2s dont count at home seriously didnt you"

    if dumb_msg:
        print(dumb_msg)

    scramble = get_scramble()
    print(colored(" ".join(scramble), 'yellow'))
    print(f"\n{' ' * 50}0.000{' ' * 50}", end="\r")

def print_header(prev_solve, ao5, ao12, single):
    print(f"{'-' * 50} {colored(session, 'red')} === {colored(EVENT_NAMES[event_index], 'blue')} {'-' * 50}")
    print(f"{' ' * 25} {colored('Previous', 'grey',)} - {prev_solve if prev_solve else 'N/A'}    {colored('PB', 'cyan')} - {'N/A' if single == float('inf') else single}    {colored('Ao5', 'blue')} - {ao5 if ao5 else 'N/A'}    {colored('Ao12', 'blue')} - {ao12 if ao12 else 'N/A'} {' ' * 25}")
    print("-" * (107 + int(len(session)) + int(len(EVENT_NAMES[event_index]))))

def main():
    load_data(save_path)
    print_data()
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()

if __name__ == "__main__":
    main()