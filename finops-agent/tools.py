import datetime
import calendar

# finops-agent/tools.py

from google.cloud import bigquery

def forecast_costs_for_project(project_id: str, num_days: int) -> list[dict]:
    """
    Forecasts future Google Cloud spending for a specific project.
    """
    client = bigquery.Client()

    # Dynamically build the query string with the num_days as a literal value.
    # Note: project_id is still passed as a secure parameter to prevent SQL injection.
    query = f"""
    SELECT
      CAST(forecast_timestamp AS STRING) AS forecast_timestamp,
      forecast_value
    FROM
      AI.FORECAST( (
        SELECT
          DATE(usage_start_time) AS usage_date,
          ROUND(SUM(cost), 2) AS total_cost
        FROM
          `bqadminprojexabeam.standardbilling.gcp_billing_export_v1_018A64_FDB684_76013D`
        WHERE
          project.id = @project_id
          AND DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE('America/Los_Angeles'), INTERVAL 60 DAY)
          AND DATE(usage_start_time) < CURRENT_DATE('America/Los_Angeles')
        GROUP BY
          usage_date
        ORDER BY
          usage_date ASC),
          data_col => "total_cost",
          timestamp_col => "usage_date",
          MODEL => "TimesFM 2.0",
          horizon => {num_days}  -- Inject num_days directly as a literal
      )
    """

    # Set up the query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("project_id", "STRING", project_id),
        ]
    )

    # Run the query
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    # Format the results into a list of dictionaries
    return [dict(row) for row in results]

#print(forecast_costs_for_project('levisnetworkingpoc1', 22))

def get_monthly_horizon():
  """
  Calculates the remaining days in the month (inclusive of today)
  and returns the result in a dictionary.

  Returns:
      dict: A dictionary with the key "horizon" and the number
            of remaining days as the value.
  """
  # Get today's date
  today = datetime.date.today()

  # Use the calendar module to find the total number of days in the current month.
  _, num_days_in_month = calendar.monthrange(today.year, today.month)

  # Total days minus today's number, plus one to include today in the count.
  remaining_days = (num_days_in_month - today.day) + 1

  # Return the result in a dictionary with the key "horizon"
  return {"horizon": remaining_days}

# --- Example Usage ---
# Given the current date is 2025-06-09:
# The remaining days (inclusive) are 22.
# The function will return: {"horizon": 22}

#horizon_dict = get_monthly_horizon()

#print(f"Today's Date: {datetime.date.today()}")
#print(f"Function output: {horizon_dict}")

# You can access the value like this:
#print(f"The value of the 'horizon' key is: {horizon_dict['horizon']}")

import json
from google.cloud import pubsub_v1

def send_email(owner_message: str):
    """Publishes a message to a Pub/Sub topic.

    Args:
        owner_name: The name of the project owner.
        owner_email: The email of the project owner
        owner_message: The message to send to the project owner about the billing anomaly.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = "projects/bqadminprojexabeam/topics/notify_project_owner"
    owner_name = "Addison Galambos"
    owner_email = "addisong@google.com"
    # The data must be a bytestring.
    data = {
        "customer_name": owner_name,
        "customer_email": owner_email,
        "customer_message": owner_message,
    }
    
    # Encode the data to a bytestring.
    message_data = json.dumps(data).encode("utf-8")

    future = publisher.publish(topic_path, message_data)
    print(f"Published message ID: {future.result()}")

