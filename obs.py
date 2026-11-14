import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
import datetime
import time
import shutil
import subprocess

# 1. Load credentials and settings from .env file
load_dotenv()

username = os.getenv("MY_USERNAME")
password = os.getenv("MY_PASSWORD")
myphone = os.getenv("MY_PHONE")
sender_phone = os.getenv("SENDER_PHONE")
auth_token = os.getenv("AUTH_TOKEN")
account_sid = os.getenv("ACCOUNT_SID")
donem_id = os.getenv("DONEM_ID")  # Add DONEM_ID to your .env file!


def log_task(message):
    """Safely log messages to task.txt"""
    try:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task.txt")
        with open(log_path, "a", encoding="utf-8") as date_file:
            date_file.write(f"{datetime.datetime.now()} - {message}\n")
    except Exception as e:
        print(f"Failed to write to log: {e}")


def login_and_fetch_grades():
    login_page_url = "https://giris.eskisehir.edu.tr/login?redirect_uri=https://obs.eskisehir.edu.tr"
    post_url = "https://giris.eskisehir.edu.tr/login/ad"
    dashboard_url = "https://obs.eskisehir.edu.tr/"
    notlar_url = f"https://obs.eskisehir.edu.tr/ogrenci/not-gor?donemId={donem_id}"

    # 2. Use a Session to automatically handle Cookies!
    with requests.Session() as session:
        # Standard browser headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        })

        # Step A: Get the login page and extract hidden tokens
        response = session.get(login_page_url)
        if response.status_code != 200:
            log_task(
                f"Failed to load login page. Status: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", {"name": "_csrf_token"})["value"]
        code = soup.find("input", {"name": "code"})["value"]

        params = {
            "_csrf_token": csrf_token,
            "code": code,
            "username": username,
            "password": password
        }

        # Step B: Perform the actual login
        login_response = session.post(post_url, data=params)
        if login_response.status_code != 200:
            log_task(
                f"Login failed. Status Code: {login_response.status_code}")
            return None

        # Step C: Visit dashboard to get the API CSRF token
        dash_response = session.get(dashboard_url)
        dash_soup = BeautifulSoup(dash_response.text, "html.parser")
        api_csrf = dash_soup.find("meta", {"name": "_csrf"})

        if api_csrf:
            session.headers.update({
                'X-CSRF-TOKEN': api_csrf["content"],
                'Accept': 'application/json, text/plain, */*',
                'Referer': dashboard_url,
            })

        # Step D: Fetch the grades JSON!
        grades_response = session.get(notlar_url)
        if grades_response.status_code != 200:
            log_task(
                f"Failed to fetch grades. Status: {grades_response.status_code}")
            return None

        data = grades_response.json()

        with open("grades.json", 'w', encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=3)

        return data


def process_grades(data):
    if not data or not data.get("ogrenciBirimList"):
        print("Invalid data received.")
        return

    data1 = data["ogrenciBirimList"][0]["tnotlarNotes"]
    data2 = data["ogrenciBirimList"][0]["sinavTurleriList"]

    rows = []
    columns = []
    grades = []

    for properties in data1:
        rows.append(properties["labelViewModel"]["languageMap"]["TR"])
        for item in properties["notTreeSet"]["items"]:
            columns.append(item["labelViewModel"]["languageMap"]["TR"])

    for properties in data2["items"]:
        grades.append(properties["labelViewModel"]["languageMap"]["TR"])

    if not rows:
        print("No grades found for this semester.")
        return

    l_arr = int(len(columns) / len(rows))

    def split_array(arr, size):
        for i in range(0, len(arr), size):
            yield arr[i:i + size]

    filename = "grades.csv"
    columns = list(split_array(columns, l_arr))

    new_table = pd.DataFrame(columns, index=rows, columns=grades)
    new_table.replace(["--", ""], np.nan, inplace=True)
    new_table.index.name = "Courses"

    try:
        old_table = pd.read_csv(filename, index_col=0, dtype=str)
        old_table.index.name = "Courses"
    except FileNotFoundError:
        old_table = pd.DataFrame(columns=grades, index=rows)

    # Align the tables to ensure they have the same columns and indices
    # This prevents ValueError if a new exam or course is added.
    new_table_aligned, old_table_aligned = new_table.align(old_table)
    difference = new_table_aligned.compare(
        old_table_aligned, result_names=('new', 'old'))
    # print(new_table)
    
    if difference.empty:
        print("No changes")
    else:
        new_table.to_csv(filename)
        change_summary = format_grade_changes(difference)
        print("Some Grades Have Changed!")
        print(change_summary)
        play_alarm(change_summary)
    return new_table, difference


def format_grade_changes(difference):
    """Extract course names, exam types, and new values from the pandas compare DataFrame."""
    changes = []
    for course, row in difference.iterrows():
        for (exam_type, state), val in row.items():
            if state == "new" and pd.notna(val):
                old_val = row.get((exam_type, "old"), "N/A")
                old_str = "None" if pd.isna(old_val) else str(old_val)
                changes.append(f"{course} [{exam_type}]: {old_str} -> {val}")
    return "\n".join(changes) if changes else "Grade table updated."

def play_alarm(details="New grades posted!"):
    if shutil.which("termux-notification"):
        subprocess.run([
            "termux-notification",
            "--title", "OBS Grade Update",
            "--content", details,
            "--sound",
            "--priority", "max",
            "--vibrate", "500,300,500,300,500",
        ], check=False)


if __name__ == "__main__":
    log_task(f"The script Started Running")

    if not donem_id:
        print("ERROR: DONEM_ID is missing from .env file!")
        log_task("ERROR: DONEM_ID is missing")
    else:
        grades_data = login_and_fetch_grades()
        if grades_data:
            new_table, diff = process_grades(grades_data)
        else:
            print("Failed to fetch data.")
