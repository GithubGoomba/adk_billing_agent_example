1. You need to install ADK (at least version 1.2)
2. You need to navigate to the .env file in the finops-agent/finops-agent dir and insert your api key
3. in the tools.yaml and tools.py file, there are multiple hard coded project names for SQl queries that interact with GCP. See additional instructions below
4. This demo relies on the gcp standard billing export being setup in GCP in the project you specify.
5. Other GCP dependencies (need to create a pubsub topic and then an application integration workflow to allow for sending emails. See this repo for instructions on setting up the pubsub and application integration settings. https://github.com/norlove/BigQuery-Continuous-Queries-Abandoned-Shopping-Cart-Demo
6. You need to install toolbox (step 2 here) https://googleapis.github.io/genai-toolbox/getting-started/local_quickstart/
7. run the toolbox server #toolbox start #./toolbox --tools-file "tools.yaml"
8. Run adk web in the terminal to start your ADK web interface.
9. Set the Anomaly Writer script up to run as a scheduled query in BigQuery, substitute in your table names.

In tools.py, update the following variables:

Under send_email function
   topic_path = "projects/<insert_project_id>/topics/notify_project_owner"
   owner_name = "<insert_name>"
   owner_email = "<insert_desired_email>"
Under forecast_costs_for_project, update the FROM clause of the query with your GCP billing export dataset and table
https://cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/standard-usage
FROM `<project_id>.<dataset>.<table_id>`
 
In the .env file, update with your ai studio api key:
https://aistudio.google.com/apikey
GOOGLE_API_KEY="<your_key>"


In tools.yaml, update your project name where your BQ billing and anomaly table are located.

If you use the US location for the datasets, then you don’t need to update that field.
sources:
 my-bigquery-source:
   kind: bigquery
   project: <insert_project_id>
   location: US

In the get_costs_current_month_by_project, update the from statement to target your billing table.
FROM `<project_id>.<dataset>.<billing_table_id>`

In the get_project_spending_alerts tool definition, update the project id where your anomalies table is stored.
FROM `<project_id>.anomalies.project_alerts`


