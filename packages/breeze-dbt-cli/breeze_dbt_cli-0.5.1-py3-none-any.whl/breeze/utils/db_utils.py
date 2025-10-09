# breeze/utils/db_utils.py

from typing import List, Tuple, Optional
from breeze.utils.dbt_utils import get_profile, get_profile_name_from_dbt_project, get_target_from_profile

# Attempt to import database drivers
try:
    import pyodbc  # For SQL Server
except ImportError:
    pyodbc = None

try:
    import psycopg2  # For PostgreSQL and Redshift
except ImportError:
    psycopg2 = None

try:
    import snowflake.connector  # For Snowflake
except ImportError:
    snowflake = None

try:
    from google.cloud import bigquery  # For BigQuery
except ImportError:
    bigquery = None

try:
    import databricks.sql as databricks  # For Databricks SQL
except ImportError:
    databricks = None

def connect_to_sqlserver(target) -> 'pyodbc.Connection':
    """
    Establish a connection to a SQL Server database using `pyodbc`.

    Args:
        - target (dict): A dictionary containing connection details (host, dbname, user, password).

    Returns:
        - pyodbc.Connection: An active connection to the SQL Server database.

    Raises:
        - Exception: If `pyodbc` is not installed or the connection fails
    """
    if pyodbc is None:
        raise Exception("\u274c pyodbc is not installed. Please install it with 'pip install pyodbc'.")

    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={target.get('host')};"
            f"DATABASE={target.get('dbname')};"
            f"UID={target.get('user')};"
            f"PWD={target.get('password')}"
        )
        return conn
    except pyodbc.Error as e:
        raise Exception(f"Error connecting to SQL Server: {e}")

def connect_to_postgres(target) -> 'psycopg2.extensions.connection':
    """
    Establish a connection to a PostgreSQL or Redshift database using `psycopg2`.

    Args:
        target (dict): A dictionary containing connection details (dbname, user, password, host, port).

    Returns:
        psycopg2.extensions.connection: An active connection to the PostgreSQL or Redshift database.

    Raises:
        Exception: If `psycopg2` is not installed or the connection fails.
    """
    if psycopg2 is None:
        raise Exception("\u274c psycopg2 is not installed. Please install it with 'pip install psycopg2-binary'.")

    try:
        conn = psycopg2.connect(
            dbname=target.get("dbname"),
            user=target.get("user"),
            password=target.get("password") or target.get("pass"),
            host=target.get("host"),
            port=target.get("port", 5432),
        )
        return conn
    except psycopg2.Error as e:
        raise Exception(f"\u274c Error connecting to PostgreSQL: {e}")

def connect_to_snowflake(target) -> 'snowflake.connector.SnowflakeConnection':
    """
    Establish a connection to a Snowflake database using `snowflake.connector`.

    Args:
        target (dict): A dictionary containing connection details (user, password, account, database, schema, role, warehouse).

    Returns:
        snowflake.connector.SnowflakeConnection: An active connection to the Snowflake database.

    Raises:
        Exception: If `snowflake.connector` is not installed or the connection fails.
    """
    if snowflake is None:
        raise Exception("\u274c snowflake-connector-python is not installed. Please install it with 'pip install snowflake-connector-python'.")

    try:
        conn = snowflake.connector.connect(
            user=target.get("user"),
            password=target.get("password") or target.get("pass"),
            account=target.get("account"),
            database=target.get("database"),
            schema=target.get("schema"),
            role=target.get("role"),
            warehouse=target.get("warehouse"),
        )
        return conn
    except snowflake.connector.errors.ProgrammingError as e:
        raise Exception(f"\u274c Error connecting to Snowflake: {e}")

def connect_to_bigquery(target) -> 'bigquery.Client':
    """
    Establish a connection to a BigQuery project using the Google Cloud BigQuery library.

    Args:
        target (dict): A dictionary containing connection details (project).

    Returns:
        bigquery.Client: A BigQuery client object.

    Raises:
        Exception: If `google-cloud-bigquery` is not installed or the connection fails.
    """
    if bigquery is None:
        raise Exception("\u274c google-cloud-bigquery is not installed. Please install it with 'pip install google-cloud-bigquery'.")

    try:
        client = bigquery.Client(project=target.get("project"))
        return client
    except Exception as e:
        raise Exception(f"\u274c Error connecting to BigQuery: {e}")

def connect_to_databricks(target) -> "databricks.Connection":

    """
    Establish a connection to a Databricks SQL Warehouse using the Databricks Python SDK.

    Args:
    - target: A dictionary containing the Databricks connection details (host, token, http_path).

    Returns:
    - A Databricks connection object.

    Raises:
    - Exception if the connection fails or databricks-sql-python is not installed.
    """
    if databricks is None:
        raise Exception(
            "❌ Databricks SQL connector is not installed. Install it with 'pip install databricks-sql-python'."
        )

    try:
        conn = databricks.connect(
            server_hostname=target["host"],
            http_path=target["http_path"],
            access_token=target["token"],
        )
        return conn
    except Exception as e:
        raise Exception(f"❌ Error connecting to Databricks: {e}")

def get_columns_from_database(database: str, schema: str, identifier: str) -> List[Tuple[str, str]]:
    """
    Retrieve column names and their data types from a specified table in the database.

    Args:
        - database (str): The name of the database.
        - schema (str): The schema where the table resides.
        - identifier (str): The name of the table (identifier).

    Returns:
        - List[Tuple[str, str]]: A list of tuples containing column names and data types.

    Raises:
        - Exception: If the table is not found or the database type is not supported.
    """
    profile = get_profile()
    profile_name = get_profile_name_from_dbt_project()
    target = get_target_from_profile(profile, profile_name)
    db_type = target["type"]

    if not identifier:
        raise Exception(f"\u274c Could not determine the table name {identifier}.")

    if db_type == "postgres":
        conn = connect_to_postgres(target)
        return get_columns_using_connection(conn, schema, identifier)
    elif db_type == "redshift":
        conn = connect_to_postgres(target)
        return get_columns_using_connection(conn, schema, identifier)
    elif db_type == "snowflake":
        conn = connect_to_snowflake(target)
        return get_columns_using_connection(conn, schema, identifier)
    elif db_type == "bigquery":
        client = connect_to_bigquery(target)
        return get_columns_bigquery(client, schema, identifier)
    elif db_type == "sqlserver":
        conn = connect_to_sqlserver(target)
        return get_columns_using_connection(conn, schema, identifier)
    elif db_type == "databricks":
        catalog = target["catalog"]
        conn = connect_to_databricks(target)
        return get_columns_using_connection_databricks(conn, database, schema, identifier)
    else:
        raise Exception(f"\u274c Database type '{db_type}' is not supported.")

def get_columns_using_connection(conn, schema, identifier) -> List[Tuple[str, str]]:
    """
    Retrieve column names and their data types using a database connection.

    Args:
        - conn: A database connection object.
        - schema (str): The schema where the table resides.
        - identifier (str): The name of the table (identifier).

    Returns:
        - List[Tuple[str, str]]: A list of tuples containing column names and data types.

    Raises:
        - Exception: If the table is not found or a query error occurs.
    """
    columns = []
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """
        cursor.execute(query, (schema, identifier))
        fetched_columns = cursor.fetchall()
        if not fetched_columns:
            raise Exception(
                f"\u274c Error: Table '{identifier}' does not exist in schema '{schema}'."
            )
        columns = [(row[0], row[1]) for row in fetched_columns]
        cursor.close()
        conn.close()
    except Exception as e:
        raise Exception(f"\u274c Error querying database: {e}")
    return columns

def get_columns_using_connection_databricks(conn, database, schema, identifier) -> List[Tuple[str, str]]:
    """
    Retrieve column names and their data types from a Databricks table.

    Args:
        conn: A Databricks connection object.
        schema (str): The schema where the table resides.
        identifier (str): The name of the table (identifier).
        catalog (str): The catalog containing the table.

    Returns:
        List[Tuple[str, str]]: A list of tuples containing column names and data types.

    Raises:
        Exception: If the table is not found or a query error occurs.
    """
    columns = []
    try:
        cursor = conn.cursor()
        
        query = f"""
            SELECT column_name, data_type
            FROM {database}.information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{identifier}'
            ORDER BY ordinal_position;
        """
        cursor.execute(query)
        fetched_columns = cursor.fetchall()
        if not fetched_columns:
            raise Exception(
                f"\u274c Error: Table '{identifier}' does not exist in schema '{schema}'."
            )
        columns = [(row[0], row[1]) for row in fetched_columns]
        cursor.close()
        conn.close()
    except Exception as e:
        raise Exception(f"\u274c Error querying database: {e}")
    return columns

def get_columns_bigquery(client, schema, identifier) -> List[Tuple[str, str]]:
    """
    Retrieve column names and their data types from a BigQuery table.

    Args:
        client (bigquery.Client): A BigQuery client object.
        schema (str): The schema where the table resides.
        identifier (str): The name of the table (identifier).

    Returns:
        List[Tuple[str, str]]: A list of tuples containing column names and data types.

    Raises:
        Exception: If the table is not found or a query error occurs.
    """
    columns = []
    try:
        dataset_ref = client.dataset(schema)
        table_ref = dataset_ref.table(identifier)
        table = client.get_table(table_ref)
        if not table.schema:
            raise Exception(
                f"\u274c Error: Table '{identifier}' does not exist in schema '{schema}'."
            )
        columns = [(field.name, field.field_type.lower()) for field in table.schema]
    except Exception as e:
        raise Exception(f"\u274c Error querying BigQuery: {e}")
    return columns

def run_query(connection, query: str, params: Optional[list] = None) -> List[str]:
    """
    Execute a query on the given connection and return results as a list of strings.
    
    Args:
    - connection: A database connection object.
    - query: The SQL query to execute.
    - params: A list of parameters for the query (optional).
    
    Returns:
    - A list of strings representing the results of the query.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            results = cursor.fetchall()
            return [row[0] for row in results]
    except Exception as e:
        raise Exception(f"❌ Error executing query: {e}")

def get_all_sources_from_schema(schema_name: str, database: str) -> List[str]:
    """
    Retrieve all table names (sources) from the given schema.
    
    Args:
    - schema_name: The schema to query.
    
    Returns:
    - A list of source names (table names) in the schema.
    """
    profile = get_profile()
    profile_name = get_profile_name_from_dbt_project()
    target = get_target_from_profile(profile, profile_name)
    db_type = target["type"]

    if db_type in ["postgres", "redshift"]:
        conn = connect_to_postgres(target)
        query = f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s;
        """
        return run_query(conn, query, [schema_name])

    elif db_type == "snowflake":
        conn = connect_to_snowflake(target)
        query = f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{schema_name.upper()}';
        """
        return run_query(conn, query)

    elif db_type == "bigquery":
        client = connect_to_bigquery(target)
        return get_tables_bigquery(client, schema_name)

    elif db_type == "sqlserver":
        conn = connect_to_sqlserver(target)
        query = f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = ?;
        """
        return run_query(conn, query, [schema_name])

    elif db_type == "databricks":
        conn = connect_to_databricks(target)
        catalog = database or target["catalog"]
        query = f"""
            SELECT table_name 
            FROM {catalog}.information_schema.tables
            WHERE table_schema = '{schema_name}';
        """        
        return run_query(conn, query)

    else:
        raise Exception(f"❌ Database type '{db_type}' is not supported.")
