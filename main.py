import codecs
from flask import Flask, render_template
import csv
from collections import defaultdict
import os

app = Flask(__name__)

def parse_csv(file_path):
    incidents = defaultdict(lambda: defaultdict(int))
    dates = set()  # Collect unique dates

    with codecs.open(file_path, 'r', encoding='latin-1') as file:  # Specify the correct encoding
        reader = csv.DictReader(file)
        for row in reader:
            customer = row["Custom field (Log Source Domain)"]
            # print(row["Updated"])
            created = row["Updated"].split()[0]  # Extract the date only
            incidents[customer][created] += 1
            dates.add(created)  # Collect unique dates

    sorted_dates = sorted(dates)  # Sort the dates

    return dict(incidents), sorted_dates

@app.route('/')
def incident_table():
    csv_file = 'csv/Jan/merged2.csv'  # Replace with your CSV file path
    incidents, sorted_dates = parse_csv(csv_file)
    return render_template('incident_table_with_overlay.html', incidents=dict(incidents), dates=sorted_dates)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
