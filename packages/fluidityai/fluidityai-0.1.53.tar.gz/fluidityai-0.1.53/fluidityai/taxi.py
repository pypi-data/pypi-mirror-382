from datetime import datetime, timedelta
from textblob import TextBlob

import requests
import json

result = "Thank you."
missing = []

postcode_airport_terminal = {
    "M90 1QX": "Manchester Airport Terminals 1 & 2",
    "M90 3NZ": "Manchester Airport Terminal 3",
    "RH6 0PJ": "Gatwick Airport North Terminal",
    "RH6 0NP": "Gatwick Airport South Terminal",
    "TW6 1EW": "Heathrow Airport Terminal 2",
    "TW6 1QG": "Heathrow Airport Terminal 3",
    "TW6 3XA": "Heathrow Airport Terminal 4",
    "TW6 2GA": "Heathrow Airport Terminal 5"
}

def is_airport(txt):
    t = TextBlob(txt).lower()
    if "heathrow" in t or "gatwick" in t or "stansted" in t or "airport" in t:
        return True

    return False

if task_outputs["Booking"].get("FillOrUpdate", "Fill") == "Update" and all(v == 'Unknown' for v in task_outputs["Fields"].values()):
    # No further changes
    Utils.print("Ok, I'm searching for the best cab quotes for your trip...", remote_client)

    # Searching for taxi quotes not implemented, so stop here
    next_task = "STOP"
else:
    if task_outputs["Booking"]["FromPostcode"] == "Unknown":
        if is_airport(task_outputs["Booking"]["From"]):
            s = "The name including the terminal of the airport you're starting from"
        else:
            s = "The street address, including full postcode, of your starting place"
            if task_outputs["Booking"]["From"] != 'Unknown':
                s += " (" + task_outputs["Booking"]["From"].title() + ")"
                task_outputs["Booking"]["From"] = 'Unknown'

        missing.append(s)

    if task_outputs["Booking"]["ToPostcode"] == "Unknown":
        if is_airport(task_outputs["Booking"]["To"]):
            s = "The name including the terminal of the airport you're going to"
        else:
            s = "The street address, including full postcode, of your destination"
            if task_outputs["Booking"]["To"] != 'Unknown':
                s += " (" + task_outputs["Booking"]["To"].title() + ")"
                task_outputs["Booking"]["To"] = 'Unknown'
            
        missing.append(s)

    if task_outputs["Booking"]["Date"] == 'Unknown':
        if "Date omitted" not in task_outputs["Booking"]:
            missing.append("The date you are travelling")
            task_outputs["Booking"]["Date omitted"] = True

    if task_outputs["Booking"]["Time"] == 'Unknown':
        if task_outputs["Booking"]["Date"] == 'Unknown' and "Date omitted" in task_outputs["Booking"]:
            # Set date and time to 6 hours from now
            current_datetime = datetime.now()
            time_to_add = timedelta(hours=6)
            new_datetime = current_datetime + time_to_add
            task_outputs["Booking"]["Date"] = new_datetime.strftime("%Y-%m-%d")
            task_outputs["Booking"]["Time"] = new_datetime.strftime("%H:%M")
        elif "Time omitted" not in task_outputs["Booking"]:
            missing.append("The time (to the nearest 10 minutes) you want to leave")
            task_outputs["Booking"]["Time omitted"] = True
        else:
            # Use default departure times
            s = task_outputs["Booking"]["Session"].lower()
            if s == "morning":
                task_outputs["Booking"]["Time"] = "10:00"
            elif s == "lunchtime":
                task_outputs["Booking"]["Time"] = "13:00"
            elif s == "afternoon":
                task_outputs["Booking"]["Time"] = "15:00"
            elif s == "evening":
                task_outputs["Booking"]["Time"] = "18:00"
            elif s == "night":
                task_outputs["Booking"]["Time"] = "20:00"
            elif s == "midnight":
                task_outputs["Booking"]["Time"] = "00:10"
            else:
                task_outputs["Booking"]["Time"] = "15:00"

    # Any booking for midnight is shifted forward 10 minutes
    if task_outputs["Booking"]["Time"] == "00:00":
        task_outputs["Booking"]["Time"] = "00:10"

    if task_outputs["Booking"]["Passengers"] == 'Unknown':
        missing.append("The number of passengers")
    elif task_outputs["Booking"]["Passengers"] > 16:
        missing.append(f"Are you sure {task_outputs['Booking']['Passengers']} people are travelling? Maximum vehicle size is 16 passengers")
        task_outputs["Booking"]["Passengers"] = 'Unknown'

    if task_outputs["Booking"]["Luggage"] == 'Unknown':
        if task_outputs["Booking"].get("FillOrUpdate", "Fill") == "Fill":
            missing.append("Your luggage - please include the type and number of each item")
    else:
        if "Luggage Items" not in task_outputs["Booking"]:
            task_outputs["Booking"]["Luggage Items"] = {}

        if isinstance(task_outputs["Booking"]["Luggage"], dict):
            task_outputs["Booking"]["Luggage Items"].update(task_outputs["Booking"]["Luggage"])
            task_outputs["Booking"]["Luggage"] = 'Unknown'

    if len(missing) > 0:
        task_outputs["Booking"]["FillOrUpdate"] = "Fill"

        if "Request Made" not in task_outputs["Booking"]:
            result += " I need some more information: "
            task_outputs["Booking"]["Request Made"] = True
        else:
            result += " I still need more information: "

        if len(missing) == 1:
            result += f"{missing[0]} "
        else:
            for i, msg in enumerate(missing):
                result += f"{i + 1}. {msg} "
    else:
        # All fields retrieved, so from now on we only update
        task_outputs["Booking"]["FillOrUpdate"] = "Update"

        # Set the airport name and terminal by postcode
        if task_outputs["Booking"]["FromPostcode"] in postcode_airport_terminal:
            task_outputs["Booking"]["From"] = postcode_airport_terminal[task_outputs["Booking"]["FromPostcode"]]

        if task_outputs["Booking"]["ToPostcode"] in postcode_airport_terminal:
            task_outputs["Booking"]["To"] = postcode_airport_terminal[task_outputs["Booking"]["ToPostcode"]]

        date_incl_weekday = datetime.strptime(task_outputs["Booking"]["Date"], "%Y-%m-%d").strftime("%A, %d-%b-%Y")
        early_morning_warning = ""
        n = task_outputs["Booking"]["Passengers"]
        if task_outputs["Booking"]["Time"].startswith("00:"):
            weekday = date_incl_weekday[:date_incl_weekday.find(',')]
            early_morning_warning = f" (early {weekday} morning)"

        luggage_msg = ""
        luggage = task_outputs["Booking"]["Luggage Items"]
        if len(luggage) > 0:
            luggage_items = [str(v) + ' ' + k.replace('_', ' ') for k, v in luggage.items()]
            luggage_msg = ', '.join(luggage_items)

            luggage_items = []
            for k, v in luggage.items():
                k = k.lower()
                if (v > 1 or v == 0):
                    # Plural: may need to add 's' or 'es'
                    if 'mattress' in k or 'box' in k:
                        if 'mattresses' not in k:
                            k = k.replace('mattress', 'mattresses')
                            
                        if 'boxes' not in k:
                            k = k.replace('box', 'boxes')

                    elif not k.endswith('s'):
                        k += 's'

                luggage_items.append(str(v) + ' ' + k.replace('_', ' '))

            luggage_msg = ', '.join(luggage_items)
        else:
            luggage_msg = 'None'

        result += f" So to confirm your booking, {n} {'people' if n > 1 else 'person'} {'are' if n > 1 else 'is'} travelling from"\
            + f" {task_outputs['Booking']['From']} {task_outputs['Booking']['FromPostcode']} to {task_outputs['Booking']['To']} {task_outputs['Booking']['ToPostcode']} on {date_incl_weekday}"\
            + f" at {task_outputs['Booking']['Time'] + early_morning_warning}. Luggage: {luggage_msg}. Tell me if you want to change anything: "
