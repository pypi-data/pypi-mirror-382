import pymysql
import time

class GCPMySQLConnection:
    """
    A class to manage a connection to a Google Cloud Platform (GCP) MySQL Database.

    This class provides methods to establish a connection to a GCP MySQL database, execute queries, and manage the 
    connection lifecycle, including automatic retries for connection attempts.

    Attributes:
        host (str): The host name or IP address of the GCP MySQL Database.
        user (str): The username for authentication.
        password (str): The password for authentication.
        database (str): The name of the database to connect to.
        port (int): The port number for the connection (default is 3306).
        db_connection: The database connection object (initially None).
    """

    def __init__(self, host, user, password, database, port=3306):
        """
        Initializes the GCPMySQLConnection with the specified parameters.

        Parameters:
            host (str): The host name or IP address of the GCP MySQL Database.
            user (str): The username for the database connection.
            password (str): The password for the database user.
            database (str): The name of the database.
            port (int, optional): The port for the connection. Defaults to 3306.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.db_connection = None

    def get_db_connection(self, max_retries=5, retry_delay=5):
        """
        Establishes a connection to the GCP MySQL database with retry logic.

        This method attempts to connect to the database up to a specified number of retries. If the connection is 
        successful, it returns the connection object; otherwise, it raises an error.

        Parameters:
            max_retries (int, optional): Maximum number of connection attempts. Defaults to 5.
            retry_delay (int, optional): Delay in seconds between retries. Defaults to 5.

        Returns:
            pymysql.Connection: A connection object to the GCP MySQL Database if successful.

        Raises:
            pymysql.OperationalError: If the connection fails after the maximum number of retries.
        """
        if self.db_connection and self.db_connection.open:
            return self.db_connection

        retries = 0
        while retries < max_retries:
            try:
                self.db_connection = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    db=self.database,
                    port=self.port,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    ssl={"use": True}
                )
                return self.db_connection

            except pymysql.OperationalError as e:
                retries += 1
                print(f"OperationalError: {e}. Retrying {retries}/{max_retries}...") 
                time.sleep(retry_delay)

        raise pymysql.OperationalError(f"Failed to connect to the database after {max_retries} retries.")

    def execute_query(self, query):
        """
        Execute a SQL query and fetch all rows.

        This method executes the provided SQL query and retrieves the results. It handles exceptions 
        related to MySQL errors and ensures that the connection is closed afterward.

        Parameters:
            query (str): The SQL query to execute.

        Returns:
            list: A list of rows fetched from the database if the query was successful.

        Raises:
            pymysql.MySQLError: If an error occurs while executing the query.
        """
        try:
            connection = self.get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
        except pymysql.MySQLError as e:
            print(f"MySQL Error: {e}")
        finally:
            self.close_connection()

    def close_connection(self):
        """
        Closes the database connection if it is open.

        This method ensures that the connection is properly closed and sets the connection object to None.
        """
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None
