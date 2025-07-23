import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from twilio.rest import Client
from dotenv import load_dotenv
import os
import datetime
username = os.getenv("MY_USERNAME")
password = os.getenv("MY_PASSWORD")
myphone = os.getenv("MY_PHONE")
sender_phone = os.getenv("SENDER_PHONE")
auth_token = os.getenv("AUTH_TOKEN")
account_sid = os.getenv("ACCOUNT_SID")

# Initialize WebDriver
# URLs
login_page_url = "https://giris.eskisehir.edu.tr/login?redirect_uri=https://obs.eskisehir.edu.tr"
post_url = "https://giris.eskisehir.edu.tr/login/ad"
notlar_url = "https://obs.eskisehir.edu.tr/ogrenci/not-gor?donemId=d4befca10abdaa3bbb221ef7e389422b3f424a7bbaec7545c0d54c075a0c167d"

cookies = {
    '_ga': 'GA1.1.1563472227.1730220497',
    '_ga_LR76K2XVTS': 'GS1.1.1730222988.2.1.1730223103.0.0.0',
    '_ga_QY8L9SLDT1': 'GS1.1.1730289510.1.1.1730289515.0.0.0',
    'PHPSESSID': 'g3ng60k0nskiu3mpe92uanfgt6',
    'TS01be3f98026': '015ec440e06bc63e61d2d14e657820e73ee5f2375ac26a388d92544ca7ff82f33e0c66e40e799a1456dba64d879da3a7a7a0329d7d7b51d964d411904082c43dbbbf37a8d2',
    'x': '!QTM0Yews4xq9E+i3d1bh7qfqHU8YFxNLD0LBdNE1+hX9Xi+Tx/pAM7SWA/6+bLBqtbimeTgnSDtj9ys=',
    'TS01be3f98': '01e3fa981e52f39aef55206856ff5c3f51df7ef862709121402b4bafb0a7991f8b4fd636d1040bf1b10759dcff32ec44b1a208e3ca83eb44a496d8e44a9119dd111f7571bab7c437d3cd2650b04ad862417460b702',
}


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '_ga=GA1.1.1563472227.1730220497; _ga_LR76K2XVTS=GS1.1.1730222988.2.1.1730223103.0.0.0; _ga_QY8L9SLDT1=GS1.1.1730289510.1.1.1730289515.0.0.0; PHPSESSID=g3ng60k0nskiu3mpe92uanfgt6; TS01be3f98026=015ec440e06bc63e61d2d14e657820e73ee5f2375ac26a388d92544ca7ff82f33e0c66e40e799a1456dba64d879da3a7a7a0329d7d7b51d964d411904082c43dbbbf37a8d2; x=!QTM0Yews4xq9E+i3d1bh7qfqHU8YFxNLD0LBdNE1+hX9Xi+Tx/pAM7SWA/6+bLBqtbimeTgnSDtj9ys=; TS01be3f98=01e3fa981e52f39aef55206856ff5c3f51df7ef862709121402b4bafb0a7991f8b4fd636d1040bf1b10759dcff32ec44b1a208e3ca83eb44a496d8e44a9119dd111f7571bab7c437d3cd2650b04ad862417460b702',
    'Origin': 'https://giris.eskisehir.edu.tr',
    'Referer': 'https://giris.eskisehir.edu.tr/login?client_id=8fdd3087-f95e-11ed-bf57-0050569a48d3&code=sso67852ef296e10',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

cookies2 = {
    '_ga': 'GA1.1.1563472227.1730220497',
    '_ga_MPRHPKY8XS': 'GS1.1.1742476332.1.0.1742476354.0.0.0',
    '_ga_QY8L9SLDT1': 'GS1.1.1742651579.2.0.1742651708.0.0.0',
    '_ga_LR76K2XVTS': 'GS1.1.1745426266.47.0.1745426266.0.0.0',
    'NG_TRANSLATE_LANG_KEY': '%22tr%22',
    'tmhDynamicLocale.locale': '%22tr%22',
    'SESSION': 'OWMwNTgwYTItYWY3MS00NWZjLWJmY2UtNGEzOWVhMjkwNWZi',
    'x': '!CD+RovD1mCJTg+xFUXwXnUCNq8fVc2QPm94EAK3WBvCXKj8LW5roT+gL3NAipXm1Oz6FTQD148G7WQ==',
    'TS01f8733f': '01e3fa981e228261a1a8ce57b7804963bc67c5491fc74aa8f9961d3bdc0e6c861a1dd1783ce78a0d089ffb9a089e11ddc4c712f83bec1e3ae676d15bfdd1debd114f16e8f9b20cb9e2126a230e0de1831989d13db8',
}

headers2 = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'tr',
    'Connection': 'keep-alive',
    'Referer': 'https://obs.eskisehir.edu.tr/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'X-CSRF-TOKEN': '52469987-295b-4f42-a0f0-96f50009fd67',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': '_ga=GA1.1.1563472227.1730220497; _ga_MPRHPKY8XS=GS1.1.1742476332.1.0.1742476354.0.0.0; _ga_QY8L9SLDT1=GS1.1.1742651579.2.0.1742651708.0.0.0; _ga_LR76K2XVTS=GS1.1.1745426266.47.0.1745426266.0.0.0; NG_TRANSLATE_LANG_KEY=%22tr%22; tmhDynamicLocale.locale=%22tr%22; SESSION=OWMwNTgwYTItYWY3MS00NWZjLWJmY2UtNGEzOWVhMjkwNWZi; x=!CD+RovD1mCJTg+xFUXwXnUCNq8fVc2QPm94EAK3WBvCXKj8LW5roT+gL3NAipXm1Oz6FTQD148G7WQ==; TS01f8733f=01e3fa981e228261a1a8ce57b7804963bc67c5491fc74aa8f9961d3bdc0e6c861a1dd1783ce78a0d089ffb9a089e11ddc4c712f83bec1e3ae676d15bfdd1debd114f16e8f9b20cb9e2126a230e0de1831989d13db8',
}


date = open(r'C:\Users\PC\task.txt', '+w')
date.write(f"{datetime.datetime.now}-The script Started Running")

with requests.Session() as session:

    response = session.get(login_page_url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        print(
            f"Failed to load login page. Status Code: {response.status_code}")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    csrf_token_element = soup.find("input", {"name": "_csrf_token"})
    if not csrf_token_element:
        print("CSRF token not found in the login page.")
        exit()

    code_element = soup.find("input", {"name": "code"})
    if not code_element:
        print("Code not found")
        exit()

    code = code_element["value"]
    print(f"Extracted code value : {code}")

    csrf_token = csrf_token_element["value"]
    print(f"Extracted CSRF Token: {csrf_token}")

    params = {
        "_csrf_token": csrf_token,
        "code": code,
        "username": username,
        "password": password
    }

    login_response = session.post(
        post_url, data=params, headers=headers, cookies=cookies)
    if login_response.status_code == 200:
        print("Login successful!")
    else:
        print(f"Login failed. Status Code: {login_response.status_code}")
        print(f"Response Text: {login_response.text}")
        exit()

    response = session.get(notlar_url, cookies=cookies2, headers=headers2)
    data = response.json()
    with open("grades.json", 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=3)


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

print(new_table)


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
        body=f"Grades:\n\n {difference}"
    )
