# Cloud DB Connector

This package provides a flexible and secure way to establish connections to various database types, including AWS RDS, Azure SQL, Google Cloud MySQL, and local databases. It includes factory functions and connection classes, as well as helper functions to execute queries and handle database interactions with retry logic.

## Package Structure

```plaintext
- db_manager.py        # Factory function to create DB connection based on the service type
- db_connection.py     # Interface to get DB connection
- aws_db.py            # AWS RDS MySQL connection class
- azure_db.py          # Azure SQL Database connection class
- gcp_db.py            # Google Cloud MySQL connection class
- local_db.py          # Local MySQL database connection class
- rds_execute.py       # Utility to execute SQL queries on the databases
```

## Installation
Ensure all necessary dependencies are installed:
```python
pip install clouddatabridge
```

## Additional Requirements for Azure SQL Database
To connect to an Azure SQL Database, an ODBC driver is required. Install the appropriate driver for your operating system:

- macOS: [Microsoft ODBC Driver for SQL Server on macOS](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)
- Linux: [Microsoft ODBC Driver for SQL Server on Linux](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)
- Windows: [Microsoft ODBC Driver for SQL Server on Windows](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)

Follow the official installation instructions on the linked pages for your OS.

## Usage
### Setting Up a Database Connection
The db_manager.py file contains a factory function, create_db_connection, to create a connection based on the chosen service (local, aws, azure, gcp). You can also use the get_db_connection function in db_connection.py for easier configuration management.

```python
from clouddatabridge.rds_execute import rds_execute

query = "SELECT * FROM person"

local_result = rds_execute(
    service="gcp",
    query=query,
    is_proxy=False,
    host="your-azure-sql-hostname",
    user="your-username",
    password="your-password",
    database="your-database",
    port=3306
    )

print(local_result)
```

## Components Overview
```
db_manager.py
```

This module provides a factory function create_db_connection that creates the appropriate database connection object based on the specified service parameter.

- Supported Services: ```local```, ```aws```, ```azure```, ```gcp```
- Parameters: ```is_proxy```, ```host```, ```user```, ```password```, ```database```, ```port```, ```region``` (for AWS)

```
db_connection.py
```

Contains the ```get_db_connection``` function, which uses ```create_db_connection``` to return the correct connection object and handles errors gracefully.

## Database-Specific Connection Classes
Each database type has its own connection class with retry logic and automatic connection handling.

1. ```AWSRDSConnection``` (aws_db.py)
    
    Manages a connection to an AWS RDS MySQL database and generates an authentication token for secure access.

2. ```AzureSQLConnection``` (azure_db.py)

    Handles connections to Azure SQL Database, supporting automatic retries. Ensure you install the ODBC driver to connect successfully.

3. ```GCPMySQLConnection``` (gcp_db.py)

    Supports MySQL connections on Google Cloud with similar retry and connection management logic.

4. ```LocalDBConnection``` (local_db.py)

    Provides connections to a local MySQL database.

```
rds_execute.py
```
Provides a high-level rds_execute function that executes queries across supported databases. It detects the SQL operation type and handles transactions for INSERT, UPDATE, and DELETE operations, committing changes automatically.

* Operations Supported: ```SELECT```, ```INSERT```, ```UPDATE```, ```DELETE```
* Parameters:
    * ```service```: Type of database service (```local```, ```aws```, ```azure```, ```gcp```)
    * ```query```: SQL query to execute
    * ```params```: Parameters for parameterized query (tuple or list of tuples for batch execution)

## Error Handling
- **Connection Errors**: Retries connection attempts with configurable retry delays for increased robustness.
- **Operational Errors**: Prints specific messages on failure and re-raises the error if maximum retries are exceeded.

## License

This package is licensed under the MIT License.