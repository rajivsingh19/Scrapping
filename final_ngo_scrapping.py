import requests
from bs4 import BeautifulSoup
import csv
import os
import re


def get_ci_session_data(url):
    try:
        # Make a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        response.raise_for_status()

        # Extract 'ci_session' cookie from the response
        ci_session_cookie = response.cookies.get("ci_session")

        if ci_session_cookie:
            print("ci_session data:", ci_session_cookie)
            return ci_session_cookie
        else:
            print("ci_session cookie not found in response.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to get ci_session data: {e}")
        return None

def get_csrf_token(url, ci_session):
    try:
        headers = {
            "Accept": "application/json, text/javascript, /; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Connection": "keep-alive",
            "Host": "ngodarpan.gov.in",
            "Referer": "https://ngodarpan.gov.in/index.php/search/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        # Make a GET request to the URL with 'ci_session' in cookies
        response = requests.get(
            url, headers=headers, cookies={"ci_session": ci_session}
        )

        # Check if the request was successful (status code 200)
        response.raise_for_status()

        # Extract CSRF token from the JSON response
        csrf_token = response.json().get("csrf_token")

        if csrf_token:
            print("CSRF Token:", csrf_token)
            return csrf_token
        else:
            print("CSRF token not found in response.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to get CSRF token: {e}")
        return None

def post_to_final_url(url, ci_session, csrf_token, payload_data,stateName,page_no):
    try:
        headers = {
            "Accept": "/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": f"ci_session={ci_session}; csrf_cookie_name={csrf_token}",
            "Host": "ngodarpan.gov.in",
            "Origin": "https://ngodarpan.gov.in",
            "Referer": "https://ngodarpan.gov.in/index.php/search/",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        # Make a POST request to the URL with payload data
        response = requests.post(url+page_no, headers=headers, data=payload_data)

        # Check if the request was successful (status code 200)
        response.raise_for_status()
        if response.status_code == 200:
            print("Successfully submittted form data.")

        # Print or use the response content as needed
        # print("Response from Final URL:")
        #   print(response.content)
        print("<<<<<<<----------Data Processing---------->>>>>>>")
        #   print(response.text)
        soup = BeautifulSoup(response.content, "html.parser")
        # Extract header names
        header_row = soup.find("thead").find("tr")
        headers = [header.get_text(strip=True) for header in header_row.find_all("th")]

        # Extract data from the table body
        data = []
        for row in soup.find("tbody").find_all("tr"):
            columns = row.find_all(["td", "th"])
            row_data = [column.get_text(strip=True) for column in columns]
            data.append(row_data)
        # print(data)

        # Save data to CSV
        write_to_csv(data, headers,stateName,payload_data.get("state_search",''))
        print("Data saved Successfully in CSV file.")

        res=[]
        # if(page_no==str(0)):
        lastPage = extract_pagination_info(response.content)
        start, end = extract_numbers(lastPage)
        res.append(start)
        res.append(end)
        return res
        # return []
    except requests.exceptions.RequestException as e:
        print(f"Failed to make POST request: {e}")

def write_to_csv(data, headers, stateName, file_key):
    
    # Construct the file name
    file_name = f"{stateName}_data.csv"

    csv_file_path = file_name  # File path for the CSV file
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        if not file_exists or os.stat(csv_file_path).st_size == 0: 
            print("file not found creating...") # Check if file is empty
            csv_writer.writerow(headers)  # Write headers only if file is empty
        csv_writer.writerows(data)
    print("file name",file_name)

def extract_pagination_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination_info = soup.find('div', class_='grid-container-footer paginations bs-docs-grid')

    if pagination_info:
        pagination_text = pagination_info.find('span').text.strip()
        return pagination_text
    else:
        return None

def extract_numbers(input_str):
    # Using regular expression to find all numbers in the string
    numbers = re.findall(r'\b\d+\b', input_str)

    # If there are at least two numbers found, return the first and last numbers
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[-1])
    else:
        return None, None


# <---------------------------- Code Initialize from here ---------------------------->

final_url = "https://ngodarpan.gov.in/index.php/ajaxcontroller/search_index_new/"
stage1_url = "https://ngodarpan.gov.in/index.php/search/"
stage2_url = "https://ngodarpan.gov.in/index.php/ajaxcontroller/get_csrf"


stateNo=0
stateName=""

state = {
    'ANDAMAN_and_NICOBAR_ISLANDS': '35',
    'ANDHRA_PRADESH': '28',
    'ARUNACHAL_PRADESH': '12',
    'ASSAM': '18',
    'BIHAR': '10',
    'CHANDIGARH': '4',
    'CHHATTISGARH': '22',
    'DADRA_and_NAGAR_HAVELI': '26',
    'DAMAN_and_DIU': '25',
    'DELHI': '7',
    'GOA':'30',
    'GUJRAT':'24',
    'HARYANA':'6',
    'HIMACHAL PRADESH':'2',
    'JAMMU & KASHMIR':'1',
    'JHARKHAND':'20',
    'KARNATAKA':'29',
    'KERALA':'32',
    'LADAKH':'37',
    'LAKSHADWEEP':'31',
    'MADHYA PRADESH':'23',
    'MAHARASHTRA': '27',
    'MANIPUR': '14',
    'MEGHALAYA': '17',
    'MIZORAM': '15',
    'NAGALAND': '13',
    'ORISSA': '21',
    'PUDUCHERRY': '34',
    'PUNJAB': '3',
    'RAJASTHAN': '8',
    'SIKKIM': '11',
    'TAMIL_NADU': '33',
    'TELANGANA': '36',
    'TRIPURA': '16',
    'UTTAR_PRADESH': '9',
    'UTTARAKHAND': '5',
    'WEST_BENGAL': '19'
}

# Displaying state names with index numbers
print("State Names:")
for index, state_name in enumerate(state, start=1):
    print(f"{index}. {state_name}")

# Ask user to select the index number of a state
selected_index = int(input("Enter the index number of the state you want to select: "))
# selected_index=1

# Validate the selected index
if 1 <= selected_index <= len(state):
    selected_state_name = list(state.keys())[selected_index - 1]
    print(f"You selected: {selected_state_name}")
    stateName=selected_state_name
    stateNo=state.get(selected_state_name,'')
    print("Data fetching from site of state "+selected_state_name+" and its number "+stateNo+" .")
      
else:
    print("Invalid index number")

page_no=str(0)

print("<<<<<<<----------Fetching data from site---------->>>>>>>")

#Getting session id
ci_session_data = get_ci_session_data(stage1_url)

while(page_no!=str(-1)):
    print("Page_no --------> "+page_no)
    if ci_session_data:
        csrf_token = get_csrf_token(stage2_url, ci_session_data)

        if csrf_token:
            # print("Data fetching from site of"+state_name+" and its no"+stateNo)
            payload_data = {
                "state_search": stateNo,
                "district_search": "",
                "sector_search": "null",
                "ngo_type_search": "null",
                "ngo_name_search": "",
                "unique_id_search": "",
                "view_type": "detail_view",
                "csrf_test_name": csrf_token,
            }
            res=post_to_final_url(final_url, ci_session_data, csrf_token, payload_data,stateName,page_no)
            if(res[0]==res[1]):
                break
            print(res)
            page_no=str(res[0]+9)
           
            if(int(page_no)<=(res[1]//10*10)):
                continue
            else:
                break
    else:
        print("Session Data not found !!")
        break
