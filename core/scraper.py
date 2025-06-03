# ----- REQUIRED IMPORTS -----

import os
import json
import core.helper as helper
import itertools
from dotenv import load_dotenv
from dateutil.parser import parse
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# ---- CONSTANTS ----

VALID_TIME = [f"{h:02}:{m:02}" for h in range(24) for m in (0, 30)]
VALID_ROOM_CAPACITY_FORMATTED = [
    "LessThan5Pax", "From6To10Pax", "From11To15Pax", "From16To20Pax",
    "From21To50Pax", "From51To100Pax", "MoreThan100Pax"
]
VALID_BUILDING = [
    "Administration Building", "Campus Open Spaces - Events/Activities", "Concourse - Room/Lab",
    "Lee Kong Chian School of Business", "Li Ka Shing Library", "Prinsep Street Residences",
    "School of Accountancy", "School of Computing & Information Systems 1",
    "School of Economics/School of Computing & Information Systems 2",
    "School of Social Sciences/College of Integrative Studies", "SMU Connexion",
    "Yong Pung How School of Law/Kwa Geok Choo Law Library"
]
VALID_FLOOR = [
    "Basement 0", "Basement 2", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5",
    "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12", "Level 13", "Level 14"
]
VALID_FACILITY_TYPE = [
    "Chatterbox", "Classroom", "Group Study Room", "Hostel Facilities", "Meeting Pod",
    "MPH / Sports Hall", "Phone Booth", "Project Room", "Project Room (Level 5)", "Seminar Room",
    "SMUC Facilities", "Student Activities Area", "Study Booth"
]
VALID_EQUIPMENT = [
    "Classroom PC", "Classroom Prompter", "Clip-on Mic", "Doc Camera", "DVD Player",
    "Gooseneck Mic", "Handheld Mic", "Hybrid (USB connection)", "In-room VC System",
    "Projector", "Rostrum Mic", "Teams Room", "Teams Room NEAT Board", "TV Panel",
    "USB Connection VC room", "Video Recording", "Wired Mic", "Wireless Projection"
]

SCREENSHOT_FILEPATH = "./screenshot_log/"
BOOKING_LOG_FILEPATH = "./booking_log/"

# ---- HELPER FUNCTIONS ----

def generate_30_min_intervals():
    """Generate all possible 30-minute intervals from 00:00 to 23:59"""
    intervals = []
    start = datetime.strptime("00:00", "%H:%M")
    end = datetime.strptime("23:59", "%H:%M")
    while start <= end:
        interval_end = (start + timedelta(minutes=30)).strftime("%H:%M")
        intervals.append(f"{start.strftime('%H:%M')}-{interval_end}")
        start += timedelta(minutes=30)
    return intervals

def fill_missing_timeslots(room_schedule):
    """Fill in missing 30-min timeslots in a sorted room schedule"""
    timeline = helper.remove_duplicates_preserve_order(
        list(itertools.chain.from_iterable(slot["timeslot"].split("-") for slot in room_schedule))
    )
    intervals = [f"{timeline[i]}-{timeline[i+1]}" for i in range(len(timeline)-1)]
    new_schedule = []
    intervals_iter = iter(intervals)
    for slot in room_schedule:
        expected = next(intervals_iter, None)
        if slot["timeslot"] == expected:
            new_schedule.append(slot)
        else:
            new_schedule.append({
                "timeslot": expected,
                "available": True,
                "status": "Available for booking",
                "details": None
            })
            new_schedule.append(slot)
    return new_schedule

def convert_room_capacity(raw):
    """Convert integer room capacity to FBS string value"""
    if raw < 5:
        return "LessThan5Pax"
    elif 5 <= raw <= 10:
        return "From6To10Pax"
    elif 11 <= raw <= 15:
        return "From11To15Pax"
    elif 16 <= raw <= 20:
        return "From16To20Pax"
    elif 21 <= raw <= 50:
        return "From21To50Pax"
    elif 51 <= raw <= 100:
        return "From51To100Pax"
    else:
        return "MoreThan100Pax"

def calculate_end_time(valid_times, start_time, duration_hrs):
    """Calculate end time based on start time and duration"""
    h, m = map(int, start_time.split(":"))
    total_minutes = h * 60 + m + int(duration_hrs * 60)
    end_h, end_m = divmod(total_minutes, 60)
    end_time = f"{end_h % 24:02}:{end_m:02}"
    closest = min(valid_times, key=lambda t: abs((int(t.split(":")[0]) * 60 + int(t.split(":")[1])) - (end_h * 60 + end_m)))
    return [closest, end_time]

def split_bookings_by_day(bookings):
    """Split bookings list by day"""
    days, current_day = [], []
    for booking in bookings:
        if "(not available)" in booking:
            current_day.append(booking)
            days.append(current_day)
            current_day = []
        else:
            if current_day:
                current_day.append(booking)
    return days

def scrape_smu_fbs(base_url="https://fbs.intranet.smu.edu.sg/home", building_array=[], floor_array=[], facility_type_array=[], equipment_array=[]):
    """Main Scraper Function to automate login and scrape SMU FBS booked timeslots for filtered rooms"""
    errors = []
    credentials = helper.read_credentials()
    if not credentials:
        return ["Missing credentials."]
    date_raw = "23 december 2024"
    date_formatted = helper.format_date(date_raw)
    duration_hrs = 2.5
    start_time = "14:00"
    end_time = calculate_end_time(VALID_TIME, start_time, duration_hrs)[0]
    room_capacity_formatted = convert_room_capacity(7)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=1000)
            page = browser.new_page()
            try:
                page.goto(base_url)
                page.wait_for_selector("input[type='email']")
                page.wait_for_selector("input[type='password']")
                page.wait_for_selector("span#submitButton")
                print(f"Navigating to {base_url}")
                page.fill("input[type='email']", credentials["username"])
                page.fill("input[type='password']", credentials["password"])
                page.click("span#submitButton")
                page.wait_for_timeout(6000)
                page.wait_for_load_state("networkidle")
                frame = page.frame(name="frameBottom")
                if not frame:
                    errors.append("Frame 'frameBottom' not found.")
                    return errors
                frame = page.frame(name="frameContent")
                while True:
                    current_date = frame.query_selector("input#DateBookingFrom_c1_textDate").get_attribute("value")
                    if current_date == date_formatted:
                        print(f"Final day is {current_date}")
                        break
                    print(f"Current day is {current_date}, navigating to the next day...")
                    frame.click("a#BtnDpcNext.btn")
                    frame.wait_for_timeout(1500)
                frame.evaluate(f'document.querySelector("select#TimeFrom_c1_ctl04").value = "{start_time}"')
                print(f"Selected start time: {start_time}")
                frame.evaluate(f'document.querySelector("select#TimeTo_c1_ctl04").value = "{end_time}"')
                print(f"Selected end time: {end_time}")
                frame.wait_for_timeout(3000)

                def select_multi_dropdown(selector, values):
                    if frame.is_visible(selector):
                        frame.click(selector)
                        for val in values:
                            frame.click(f'text="{val}"')
                            print(f"Selecting {val}...")
                        frame.evaluate("popup.hide()")
                        page.wait_for_load_state("networkidle")
                        frame.wait_for_timeout(3000)

                select_multi_dropdown("#DropMultiBuildingList_c1_textItem", building_array)
                select_multi_dropdown("#DropMultiFloorList_c1_textItem", floor_array)
                select_multi_dropdown("#DropMultiFacilityTypeList_c1_textItem", facility_type_array)
                select_multi_dropdown("#DropMultiEquipmentList_c1_textItem", equipment_array)

                frame.evaluate(f'document.querySelector("select#DropCapacity_c1").value = "{room_capacity_formatted}"')
                print(f"Selected room capacity: {room_capacity_formatted}")
                frame.wait_for_timeout(3000)

                page.screenshot(path=f"{SCREENSHOT_FILEPATH}0.png")

                frame.wait_for_selector("table#GridResults_gv")
                rows = frame.query_selector_all("table#GridResults_gv tbody tr")
                matching_rooms = [
                    row.query_selector_all("td")[1].inner_text().strip()
                    for row in rows if len(row.query_selector_all("td")) > 1
                ]
                if not matching_rooms:
                    print("No rooms fitting description found.")
                    return errors

                print(f"{len(matching_rooms)} rooms fitting description found.")
                for room in matching_rooms:
                    print(f"- {room}")

                frame.click("a#CheckAvailability")
                print("Submitting search availability request...")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(6000)
                page.screenshot(path=f"{SCREENSHOT_FILEPATH}1.png")

                frame = page.frame(name="frameBottom")
                frame = page.frame(name="frameContent")
                room_names_raw = [
                    room.inner_text()
                    for room in frame.query_selector_all("div.scheduler_bluewhite_rowheader_inner")
                ]
                room_names = [el for el in room_names_raw if el not in VALID_BUILDING]
                bookings_raw = [
                    b.get_attribute("title")
                    for b in frame.query_selector_all("div.scheduler_bluewhite_event.scheduler_bluewhite_event_line0")
                ]
                bookings_by_day = split_bookings_by_day(bookings_raw)
                room_timeslot_map = {}

                for idx, booking_array in enumerate(bookings_by_day):
                    booking_details = []
                    for booking in booking_array:
                        if booking.startswith("Booking Time:"):
                            room_details = {el.split(": ")[0]: el.split(": ")[1] for el in booking.split("\n") if ": " in el}
                            local_timeslot = next((el.lstrip("Booking Time: ") for el in booking.split("\n") if el.startswith("Booking Time:")), "")
                            booking_details.append({
                                "timeslot": local_timeslot,
                                "available": False,
                                "status": "Booked",
                                "details": room_details
                            })
                        elif booking.endswith("(not available)"):
                            time = booking.split(") (")[0].lstrip("(")
                            booking_details.append({
                                "timeslot": time,
                                "available": False,
                                "status": "Not available",
                                "details": None
                            })
                        else:
                            print(f"Unrecognised timeslot format: {booking}")
                    room_timeslot_map[room_names[idx]] = fill_missing_timeslots(booking_details)

                final_booking_log = {
                    "metrics": {"scraping_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                    "scraped": {
                        "config": {
                            "date": date_formatted,
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration": duration_hrs,
                            "building_names": building_array,
                            "floors": floor_array,
                            "facility_types": facility_type_array,
                            "room_capacity": room_capacity_formatted,
                            "equipment": equipment_array,
                        },
                        "result": room_timeslot_map,
                    },
                }
                helper.pretty_print_json(final_booking_log)
                helper.write_json(final_booking_log, f"{BOOKING_LOG_FILEPATH}scraped_log.json")

            except Exception as e:
                errors.append(f"Error processing {base_url}: {e}")

            finally:
                print("Closing browser...")
                browser.close()

    except Exception as e:
        errors.append(f"Failed to initialize Playwright: {e}")

    return errors

# ---- SAMPLE EXECUTION ----

if __name__ == "__main__":
    TARGET_URL = "https://fbs.intranet.smu.edu.sg/home"
    BUILDING_ARRAY = ["Administration Building", "Li Ka Shing Library", "Li Ka Shing Library"]
    FLOOR_ARRAY = ["Level 1", "Level 2"]
    FACILITY_TYPE_ARRAY = ["Classroom"]
    EQUIPMENT_ARRAY = ["Classroom PC"]
    print(f"errors: {scrape_smu_fbs(TARGET_URL, BUILDING_ARRAY, FLOOR_ARRAY, FACILITY_TYPE_ARRAY, EQUIPMENT_ARRAY)}")