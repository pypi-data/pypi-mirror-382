from google.cloud import bigquery
from google.cloud.exceptions import NotFound


def table_exists(table_id: str, gbq_client: bigquery.Client) -> bool:
    """
    Checks whether a table exists

    Args:
        table_id (str): Name of the table
        gbq_client (bigquery.Client): BigQuery client

    Raises:
        e: Some error

    Returns:
        bool: True if table exists
    """
    try:
        gbq_client.get_table(table_id)  # Make an API request.
        return True
    except NotFound:
        return False
    except Exception as e:
        raise e
