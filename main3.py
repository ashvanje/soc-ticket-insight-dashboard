import codecs
import csv
import os
import requests
import openai
from flask import Flask, render_template, jsonify, request
from collections import defaultdict

app = Flask(__name__)
# PwC CaaS 2023-07-10T16_08_51+0800.csv
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
csv_file = 'csv/Jan/PwC CaaS 2023-07-10T17_33_03+0800.csv'  # Replace with your CSV file path
def parse_csv(file_path):
    incidents = defaultdict(lambda: defaultdict(lambda: {"count": 0, "items": []}))
    dates = set()  # Collect unique dates

    with codecs.open(file_path, 'r', encoding='latin-1') as file:  # Specify the correct encoding
        reader = csv.DictReader(file)
        for row in reader:
            customer = row["Custom field (Log Source Domain)"]
            created = row["Created"].split()[0]  # Extract the date only
            incidents[customer][created]["count"] += 1
            incidents[customer][created]["items"].append({
                "issue_key": row["Issue key"],
                "summary": row["Summary"],
                "Custom field (Actual time to first response)": row["Custom field (Actual time to first response)"],
                "Custom field (Raw Alert)": row["Custom field (Raw Alert)"],
            })
            dates.add(created)  # Collect unique dates

    sorted_dates = sorted(dates)  # Sort the dates

    return dict(incidents), sorted_dates


@app.route('/')
def incident_table():
    incidents, sorted_dates = parse_csv(csv_file)
    return render_template('incident_table_dynamic_overlay2.html', incidents=dict(incidents), dates=sorted_dates)


@app.route('/convert-to-csv', methods=['POST'])
def convert_to_csv():
    print('chkpt1')
    table_data = request.json['tableData']
    csv_data = '\n'.join(','.join(map(str, row)) for row in table_data)
    print('chkpt2')
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
