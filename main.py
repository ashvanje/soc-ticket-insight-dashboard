import codecs
import csv
import os
import requests
import openai
from flask import Flask, render_template, jsonify, request
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

#column definition
col_log_source = "fields.customfield_10223"
col_created = "fields.created"
col_issue_key = "key"
col_summary = "fields.summary"

# col_log_source = "Custom field (Log Source Domain)"
# col_created = "Created"
# col_issue_key = "Issue key"
# col_summary = "Summary"

openai.api_key = os.getenv("OPENAI_API_KEY")
csv_file = os.getenv("DASHBOARD_DATASOURCE_CSV_PATH")  # Replace with your CSV file path
def parse_csv(file_path):
    incidents = defaultdict(lambda: defaultdict(lambda: {"count": 0, "items": []}))
    dates = set()  # Collect unique dates

    with codecs.open(file_path, 'r', encoding='latin-1') as file:  # Specify the correct encoding
        reader = csv.DictReader(file)
        # print("Length of row:", len(reader))  # Print the length of sorted_dates

        for row in reader:
            print(row)
            customer = row[col_log_source]
            if row[col_created]:
                datetime_string = row[col_created]

                # Convert the datetime string to a datetime object
                datetime_obj = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%f%z")

                # Extract the date portion
                date_only = datetime_obj.date()
                created = date_only
                # created = row[col_created].split()[0]  # Extract the date only
            else :
                created = ""
            incidents[customer][created]["count"] += 1
            incidents[customer][created]["items"].append({
                "issue_key": row[col_issue_key],
                "summary": row[col_summary],
                # "Custom field (Actual time to first response)": row["Custom field (Actual time to first response)"],
                # "Custom field (Raw Alert)": row["Custom field (Raw Alert)"],
            })
            dates.add(created)  # Collect unique dates

    sorted_dates = sorted(dates)  # Sort the dates

    return dict(incidents), sorted_dates


@app.route('/')
def incident_table():
    incidents, sorted_dates = parse_csv(csv_file)
    return render_template('dashboard.html', incidents=dict(incidents), dates=sorted_dates)


@app.route('/convert-to-csv', methods=['POST'])
def convert_to_csv():
    table_data = request.json['tableData']
    csv_data = '\n'.join(','.join(map(str, row)) for row in table_data)
    print(f'csv_data: {csv_data}')
    # response = requests.post('http://openai.com/completion', json={"string": csv_data})

    # +++

    conversation2 = []
    # conversation2.append({"role": "user", "content": "Hello OpenAI"})
    prompt = f"""
    I'm working for a security operation center and i have an incident table below.
    they are incidents of the same customer
    please look for me if there's any particular trend in the incidents today
    anything my SOC analysts should be alert
    also give the count for each group / type of incidents
    {csv_data}
    """
    conversation2.append({"role": "user", "content": prompt})


    response2 = openai.ChatCompletion.create(
        # model='gpt-3.5-turbo',
        model='gpt-3.5-turbo',
        messages=conversation2
    )

    ai_response2 = response2.choices[0].message.content
    # ---
    print('chkpt3')
    # response_data = response.json()
    # return jsonify(response_data['data'])
    return {
        "data": ai_response2
    }

@app.route('/investigate', methods=['POST'])
def investigate():
    data = request.get_json()
    print('investigate:', data)  # Updated print statement
    # Perform investigation based on the provided data
    # ...
    # Replace the following example response with your actual investigation result

    # response = requests.post('http://openai.com/completion', json={"string": csv_data})

    # +++

    conversation2 = []
    # conversation2.append({"role": "user", "content": "Hello OpenAI"})
    prompt = f"""
    I'm working for a security operation center and i have an incident table below.
    they are incidents of the same customer
    help me to propose how to investigate the below incident ticket
    {data}
    """
    conversation2.append({"role": "user", "content": prompt})


    response2 = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=conversation2
    )

    ai_response2 = response2.choices[0].message.content

    investigation_result = {
        "description": ai_response2,
        "proposedFix": "Proposed fix for the issue"
    }
    return jsonify(investigation_result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
