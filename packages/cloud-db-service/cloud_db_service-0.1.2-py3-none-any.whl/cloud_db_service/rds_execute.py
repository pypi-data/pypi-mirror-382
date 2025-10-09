import pymysql.cursors
import pymysql
from .db_connection import get_db_connection

# Global dictionary to store connections
GLOBAL_CONNECTIONS = {}

def get_operation_from_query(query):
    """
    Determines the SQL operation type from a given SQL query.

    This function parses the query to identify the SQL operation, such as 'select', 'insert', 
    'update', or 'delete'. It is used to conditionally handle operations in the database based on the query type.

    Parameters:
        query (str): The SQL query string to analyze.

    Returns:
        str: The SQL operation type in lowercase (e.g., 'select', 'insert', 'update', 'delete').

    Examples:
        >>> get_operation_from_query("SELECT * FROM users")
        'select'
        
        >>> get_operation_from_query("UPDATE users SET name = 'Alice' WHERE id = 1")
        'update'
    """
    return query.strip().split()[0].lower()

def close(connection):
    """Close the database connection if it's open."""
    if connection:
        connection.close_connection()

def chunked_data(data, chunk_size):
    """Yield successive chunk_size chunks from data."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def rds_execute(service, query, params=None, batch_size=1, **config):
    """
    Executes a specified SQL query on an RDS or local database.

    This function establishes a database connection using the specified service, executes the provided query, 
    and handles multiple SQL operation types. It supports executing single or batched queries using a 
    parameterized approach for security and efficiency.

    Parameters:
        service (str): Specifies the type of database connection to establish ('local', 'aws', 'azure', 'gcp').
        query (str): The SQL query to execute.
        params (tuple or list of tuples, optional): Parameters for the query. Use a single tuple for a single 
                                                     query execution or a list of tuples for batch execution.
        batch_size (int, optional): Number of rows to process at a time for batch executions (default is 1).
        **config: Additional configuration parameters needed to establish the database connection, such as host,
                  user, password, database, and region.

    Returns:
        list or Exception: 
            - Returns a list of rows for 'select' queries.
            - Returns an Exception if an error occurs.

    Raises:
        pymysql.OperationalError: If there is an operational error in the database (e.g., connection failure).
        Exception: For any other errors encountered during query execution.

    Examples:
        >>> # Execute a SELECT query
        >>> results = rds_execute('aws', 'SELECT * FROM users WHERE id = %s', (1,))

        >>> # Execute an INSERT query with multiple rows
        >>> rds_execute('local', 'INSERT INTO users (name, age) VALUES (%s, %s)', params=[('Alice', 30), ('Bob', 25)])

    Notes:
        - Commits changes for 'insert', 'update', and 'delete' operations automatically.
        - Closes the connection automatically after execution.
    """
    connection = None
    try:
        connection_obj = get_db_connection(service, **config)
        connection = connection_obj.get_db_connection()
        with connection.cursor() as cursor:
            if isinstance(params, list) and all(isinstance(i, (tuple, list)) for i in params):
                if batch_size > 1:
                    for batch in chunked_data(params, batch_size):
                        cursor.executemany(query, batch)
                else:
                    cursor.executemany(query, params)
            else:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

            operation = get_operation_from_query(query)
            if operation in ['insert', 'update', 'delete']:
                connection.commit()

            if operation == 'select':
                return cursor.fetchall()

    except pymysql.OperationalError as op_err:
        print(f'Operational Error in DB query: {query}')
        print(op_err)
        return op_err

    except Exception as e:
        print(f'Error while executing DB query: {query}')
        print(e)
        return e

    finally:
        if connection:
            connection_obj.close_connection()

def get_or_create_db_connection(service, config):
    """
    Retrieves an existing database connection from the global store.
    If a connection does not exist, a new one is created and stored.
    """
    global GLOBAL_CONNECTIONS  # Ensure we modify the global dictionary

    # Step 1: Check if a valid connection already exists
    # if service in GLOBAL_CONNECTIONS :
    #     active_connection = GLOBAL_CONNECTIONS[service]
    #     if active_connection:
    #         print(f"Reusing existing database connection for {service}.")
    #         return active_connection
    #     else:
    #         print(f"Connection for {service} is invalid. Re-establishing...")

    if service in GLOBAL_CONNECTIONS:
        active_connection = GLOBAL_CONNECTIONS[service]
        try:
            with active_connection.cursor() as cursor:
                cursor.execute("SELECT 1")  # Check if connection is alive
            print(f"Reusing existing database connection for {service}.")
            return active_connection
        except pymysql.OperationalError:
            print(f"Stale connection detected for {service}. Creating a new one.")

    # Step 2: If no valid connection exists, create a new one
    print(f"Establishing a new database connection for {service}.")
    db_connection_obj = get_db_connection(service, **config)

    # Ensure that a valid connection is retrieved
    active_connection = db_connection_obj.get_db_connection() if db_connection_obj else None

    if not active_connection:
        raise ValueError(f"Failed to establish a valid database connection for {service}.")

    # Store the actual connection in GLOBAL_CONNECTIONS for future use
    GLOBAL_CONNECTIONS[service] = active_connection
    # print(f"Stored the new database connection for {GLOBAL_CONNECTIONS[service]}.")

    return GLOBAL_CONNECTIONS[service]


def execute_query_with_connection(query, service, params=None, batch_size=1, db_connection=None):
    """
    Executes an SQL query using an existing database connection.
    If no connection is provided, attempts to fetch from the global store.
    """
    if not db_connection:
        print("No valid connection provided, trying to fetch from global connections.")
        # Ensure we fetch the correct connection for the requested service
        if service in GLOBAL_CONNECTIONS:
            db_connection = GLOBAL_CONNECTIONS[service]
        else:
            raise ValueError(f"No valid database connection available for service: {service}")

    try:
        with db_connection.cursor() as cursor:
            # print(f"Executing query on connection: {id(db_connection)} for service: {service}")

            if isinstance(params, list) and all(isinstance(i, (tuple, list)) for i in params):
                if batch_size > 1:
                    for batch in chunked_data(params, batch_size):
                        cursor.executemany(query, batch)
                else:
                    cursor.executemany(query, params)
            else:
                cursor.execute(query, params) if params else cursor.execute(query)

            operation = get_operation_from_query(query)
            if operation in ['insert', 'update', 'delete']:
                db_connection.commit()

            if operation == 'select':
                return cursor.fetchall()

    except pymysql.OperationalError as op_err:
        print(f"Operational Error in DB query: {query}")
        print(op_err)
        return op_err

    except Exception as e:
        print(f"Error while executing DB query: {query}")
        print(e)
        return e


    def bulk_upsert(
            table: str,
            rows: Sequence[Dict[str, Any]],
            update_cols: Sequence[str],
            batch_size: int = 1000,
            on_conflict_hint: Optional[str] = None,
            service,
            db_connection=None
        ):
            """
            INSERT ... ON DUPLICATE KEY UPDATE using MySQL 8 style with alias.
            - `rows` must be a sequence of dicts with identical keys (the insert columns).
            - The table must have a PRIMARY KEY or UNIQUE KEY to trigger the "duplicate" path.
            - Only columns listed in `update_cols` are updated on conflict.
            - If you need index hints (rare), pass `on_conflict_hint` like "USE INDEX (my_unique_idx)".

            Returns total affected rows (inserted + updated * 2 in MySQL semantics).
            """
            try:
                if not db_connection:
                    print("No valid connection provided, trying to fetch from global connections.")
                    # Ensure we fetch the correct connection for the requested service
                    if service in GLOBAL_CONNECTIONS:
                        db_connection = GLOBAL_CONNECTIONS[service]
                    else:
                        raise ValueError(f"No valid database connection available for service: {service}")

                if not rows:
                    return 0

                # Preserve column order based on first row
                cols = list(rows[0].keys())

                # Validate update columns exist in input rows
                missing = set(update_cols) - set(cols)
                if missing:
                    raise ValueError(f"update_cols not in row keys: {missing}")

                # Build SQL
                col_list = ", ".join(f"`{c}`" for c in cols)
                placeholders = ", ".join(["%s"] * len(cols))
                update_clause = ", ".join(f"`{c}`=NEW.`{c}`" for c in update_cols)
                # Optional index hint
                hint = f" {on_conflict_hint.strip()} " if on_conflict_hint else " "

                sql = f"""
                    INSERT{hint}INTO `{table}` ({col_list})
                    VALUES ({placeholders})
                    AS NEW
                    ON DUPLICATE KEY UPDATE {update_clause}
                """.strip()

                total = 0
                with db_connection.cursor() as cursor:
                    for batch in chunked(rows, batch_size):
                        params = [tuple(r[c] for c in cols) for r in batch]
                        cursor.executemany(sql, params)
                        total += cursor.rowcount
                db_connection.commit()
                return total
            except pymysql.OperationalError as op_err:
                print(f'OperationalError encountered while executing query: "{query}". Error: {op_err}')
                raise

            except ValueError as val_err:
                print(f'ValueError encountered: {val_err}')
                raise

            except Exception as e:
                print(f'An unexpected error occurred while executing query: "{query}". Error: {e}')
                raise