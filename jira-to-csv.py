import requests
import csv
import os
from dotenv import load_dotenv
load_dotenv()
import json
import time
import pandas as pd
from json.decoder import JSONDecodeError
import re


# todoist_token = os.getenv("TODOIST_TOKEN")
base_url = os.getenv("BASE_URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
# ranges = [(952800, 952802), (952300, 952303), (951300, 951303)]
ranges = [(952818, 952830)]

timestamp = int(time.time() * 1000)
json_column_name = "fields.customfield_10232"
csv_output_path = os.getenv("JIRA_EXPORTED_CSV_PATH")

def call_api (issue_number, username, password):
    url = f"{base_url}MSS-{issue_number}"
    response = requests.get(url, auth=(username, password))

    if response.status_code == 200:
        data = response.json()
    else:
        data = {}
    return data

def flatten_json(json_data, flattened_data, prefix=''):
    if isinstance(json_data, list):
        for i, item in enumerate(json_data):
            new_prefix = f"{prefix}.{i}" if prefix else str(i)
            flatten_json(item, flattened_data, prefix=new_prefix)
    elif isinstance(json_data, dict):
        for key, value in json_data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            flatten_json(value, flattened_data, prefix=new_prefix)
    else:
        flattened_data[prefix] = json_data

def extract_custom_fields(data):
    custom_fields = data.get("fields", {})
    custom_fields_data = {}
    for key, value in custom_fields.items():
        if key.startswith("customfield_"):
            custom_fields_data[key] = value
    return custom_fields_data

def flatten_json_column(df, json_column):
    # Create a list to hold the flattened data dictionaries
    flattened_data_list = []

    # Iterate through each row of the original DataFrame
    for index, row in df.iterrows():
        try:
            # Load the JSON data from the json_column
            if not pd.isna(row[json_column]):
                # print(f"row[json_column]: {row[json_column]}")
                rowValue = row[json_column].replace("{code}","")
                rowValue = escape_single_backslashes(rowValue)
                json_data = json.loads(rowValue)

                # Flatten the JSON data and store it in a dictionary
                flattened_data = {}
                flatten_json(json_data, flattened_data)

                # Append the flattened data to the list
                flattened_data_list.append(flattened_data)
            else:
                flattened_data_list.append({})
        except JSONDecodeError as e:
            print(f"JSONDecodeError in row {index + 1}: {e}. This row is ignored but please take note of the ticket number so it can be investigated later.")
            flattened_data_list.append({})  # Add an empty dictionary for this row

    # Create a new DataFrame from the list of dictionaries
    new_df = pd.DataFrame(flattened_data_list)

    # Concatenate the new DataFrame with the original DataFrame
    df = pd.concat([df, new_df], axis=1)

    return df

def escape_single_backslashes(input_string):
    output_string = ""
    index = 0
    while index < len(input_string):
        if input_string[index] == "\\":
            if index + 1 < len(input_string) and input_string[index + 1] != "\\":
                output_string += "\\\\"
            else:
                output_string += input_string[index]
            index += 1
        else:
            output_string += input_string[index]
        index += 1
    return output_string

def mask_ip_addresses(text):
    # Regular expression to match IPv4 addresses
    ip_regex = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    # Replace IP addresses with a masked value
    masked_text = re.sub(ip_regex, "xxx.xxx.xxx.xxx", text)
    return masked_text

def mask_hostnames(text):
    # Regular expression to match hostnames
    hostname_regex = r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    # Replace hostnames with a masked value
    masked_text = re.sub(hostname_regex, "example.com", text)
    return masked_text

def move_characters_to_next_three(text):

    result = ""
    if(text):
        # Initialize an empty string to store the manipulated result
        for char in text:
            # Check if the character is an alphabet letter
            if char.isalpha():
                # Get the ASCII code of the character
                ascii_code = ord(char)
                # Move the ASCII code three positions later
                new_ascii_code = ascii_code + 3
                # If the new ASCII code goes beyond 'z', wrap around to 'a'
                if char.islower():
                    if new_ascii_code > ord('z'):
                        new_ascii_code -= 26
                # If the new ASCII code goes beyond 'Z', wrap around to 'A'
                elif char.isupper():
                    if new_ascii_code > ord('Z'):
                        new_ascii_code -= 26
                # Append the character with the new ASCII code to the result
                result += chr(new_ascii_code)
            else:
                # Append non-alphabet characters unchanged
                result += char
    return result

def process_jira_response(jira_response_json):
    try:
        # temp = jira response json
        # print(f"jira_response_json: {jira_response_json}")
        log_source = jira_response_json["fields"]["customfield_10223"]
        tempStr = json.dumps(jira_response_json)
        manipulated_log_source = move_characters_to_next_three(log_source)
        # tempStr = tempStr.replace(log_source, manipulated_log_source)

        # Perform a case-insensitive replacement using re.sub()
        if(log_source):
            tempStr = re.sub(re.escape(log_source), manipulated_log_source, tempStr, flags=re.IGNORECASE)

        tempStr = mask_ip_addresses(tempStr)
        tempStr = mask_hostnames(tempStr)
        jira_response_json = json.loads(tempStr)
    except:
        print("Error during processing jira response.")
    return jira_response_json

def main():
    flattened_data_list = []
    # Loop through the issue numbers and call the API for each one
    for start_issue_number, end_issue_number in ranges:
        for issue_number in range(start_issue_number, end_issue_number + 1):
            jira_response_json = call_api(issue_number, username, password)
            jira_response_json = process_jira_response(jira_response_json)
            flattened_jira_response_json = {}
            flatten_json(jira_response_json, flattened_jira_response_json)
            #returns flattened json as newTemp
            flattened_data_list.append(flattened_jira_response_json)
            print(f"Issue MSS-{issue_number} processed.")
    
    # after the for loop, returns an array (flattened_data_list) of flattened json data
    df = pd.DataFrame(flattened_data_list)

    # Convert the JSON column to multiple columns
    df = flatten_json_column(df, json_column_name)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(csv_output_path, index=False)

if __name__ == "__main__":
    main()
