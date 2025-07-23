import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from twilio.rest import Client
from dotenv import load_dotenv
import os

username = os.getenv("MY_USERNAME")
password = os.getenv("MY_PASSWORD")
myphone = os.getenv("MY_PHONE")
sender_phone = os.getenv("SENDER_PHONE")
auth_token = os.getenv("AUTH_TOKEN")
account_sid = os.getenv("ACCOUNT_SID")

with open("grades.json", 'r', encoding="utf-8") as file:
    data = json.load(file)

data1 = data["ogrenciBirimList"][0]["tnotlarNotes"]
data2 = data["ogrenciBirimList"][0]["sinavTurleriList"]

rows = []
columns = []
grades = []


for properties in data1:

    rows.append(properties["labelViewModel"]["languageMap"]["TR"])
    # print(properties['labelViewModel']['languageMap']['TR'])
    for item in properties["notTreeSet"]["items"]:

        columns.append(item["labelViewModel"]["languageMap"]["TR"])
        # print(item['labelViewModel']['languageMap']['TR'])

for properties in data2["items"]:
    grades.append(properties["labelViewModel"]["languageMap"]["TR"])


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


difference = new_table.compare(old_table, result_names=('new', 'old'))


if difference.empty:
    print("No changes")


else:
    client = Client(account_sid, auth_token)
    new_table.to_csv(filename)
    print("Some Grades Have Changed!")
    print(difference)
    message = client.messages.create(
        from_=sender_phone,
        to=myphone,
        body=f"Grade{difference}".replace("\t", " ")
    )
    print(message.sid)
