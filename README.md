# soc-ticket-insight-dashboard

1. pip install -r requirements.txt
2. set a .env locally

OPENAI_API_KEY=

BASE_URL=https://xxxx.xxxxx.com/rest/api/2/issue/
USERNAME=(Jira username)
PASSWORD=(Jira password)

JIRA_EXPORTED_CSV_PATH=(Recommended) csv/xxx.csv
DASHBOARD_DATASOURCE_CSV_PATH=(Recommended) csv/xxx.csv

3. to pull jira data - python jira-to-csv.py
(if python3 is used) python3 jira-to-csv.py

4. to show the jira dashboard
   python main.py
   (if python3 is used) python3 main.py
