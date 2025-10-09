from .db_manager import create_db_connection

def get_db_connection(service, **config):
    """
    Obtains a database connection object based on the specified service and configuration parameters.

    This function utilizes the `create_db_connection` utility to establish a connection to either a local 
    or cloud-based database (e.g., AWS). The configuration parameters required depend on the database service specified.
    is_proxy parameter should be set to "True" only if using AWS proxy host else False.

    Parameters:
        service (str): Type of the database service to connect to. Supported values include 'aws' and 'local'.
        **config: Additional configuration parameters for the database connection, such as is_proxy, host, user, password,
                  database, port, and any other necessary options for the specific service.

    Returns:
        Database connection object: The connection object for the specified database service, or None if an error occurs.

    Raises:
        Exception: If there is an error while attempting to establish the connection, which is logged to the console.

    Examples:
        >>> # Get a local database connection
        >>> conn = get_db_connection('local', is_proxy=False, host='localhost', user='user', password='password', database='my_db')

        >>> # Get an AWS RDS database connection
        >>> conn = get_db_connection('aws', is_proxy=False, host='db-instance.123456789012.us-east-1.rds.amazonaws.com',
                                            user='admin', password='password', database='my_db', region='us-east-1')

    Notes:
        This function logs any exceptions that occur during the connection process, returning None if unsuccessful.
    """
    try:
        return create_db_connection(service=service, **config)
    except Exception as e:
        print(f"Error getting DB connection: {e}")
        return