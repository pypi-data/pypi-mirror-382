from .local_db import LocalDBConnection
from .aws_db import AWSRDSConnection
from .azure_db import AzureSQLConnection
from .gcp_db import GCPMySQLConnection

def create_db_connection(service, host=None, user=None, password=None, database=None, port=3306, region=None, is_proxy=False):
    """
    Creates a database connection for either a local or cloud database (AWS, Azure, GCP).
    """
    service = service.lower()  # Normalize input
    
    if service not in ['local', 'aws', 'azure', 'gcp']:
        raise ValueError(f"Unsupported cloud provider: '{service}'. Supported providers: 'aws', 'azure', 'gcp', 'local'.")

    if not host or not user or not database:
        raise ValueError(f"Missing required parameters for {service}. 'host', 'user', and 'database' are required.")

    if service == "local":
        print("Creating Local Database Connection...")
        return LocalDBConnection(host, user, password, database, port)

    elif service == "aws":
        if not region:
            raise ValueError("Region is required for AWS connection.")
        print(f"Creating AWS RDS Connection... (is_proxy={is_proxy})")
        return AWSRDSConnection(host, user, password, database, region, port, bool(is_proxy))

    elif service == "azure":
        print("Creating Azure SQL Connection...")
        return AzureSQLConnection(host, user, database, password, port)

    elif service == "gcp":
        print("Creating GCP MySQL Connection...")
        return GCPMySQLConnection(host, user, password, database, port)

    else:
        raise ValueError("Unsupported service type. Use 'local', 'aws', 'azure', 'gcp'.")
