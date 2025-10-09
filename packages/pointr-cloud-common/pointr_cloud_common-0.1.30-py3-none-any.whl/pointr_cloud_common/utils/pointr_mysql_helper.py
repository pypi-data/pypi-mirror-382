from sqlalchemy import create_engine, MetaData, text
from retrying import retry
import mysql.connector
from typing import Dict, Any, Optional
import os

class MySQLHelper:
    """MySQL database helper with configurable connection."""
    
    def __init__(self) -> None:
        MYSQL_HOSTNAME_INTERNAL=os.environ["MYSQL_HOSTNAME_INTERNAL"]
        MYSQL_PORT_INTERNAL=os.environ["MYSQL_PORT_INTERNAL"]
        MYSQL_DATABASE_NAME=os.environ["MYSQL_DATABASE_NAME"]
        MYSQL_USER_NAME=os.environ["MYSQL_USER_NAME"]
        MYSQL_USER_PASSWORD=os.environ["MYSQL_USER_PASSWORD"]
        
        self.hostname = MYSQL_HOSTNAME_INTERNAL
        self.port = MYSQL_PORT_INTERNAL
        self.database = MYSQL_DATABASE_NAME
        self.username = MYSQL_USER_NAME
        self.password = MYSQL_USER_PASSWORD
        
        # Define the database connection
        self.database_url = f"mysql+mysqlconnector://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"
        
        # Create the SQLAlchemy engine
        self.engine = create_engine(self.database_url, echo=False)
        
        # Reflect the database schema (load metadata)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
    def execute_sql(self, sql: str, parameters: Dict[str, Any] = {}) -> Any:
        """Execute SQL query with retry logic."""
        query = text(sql)
        
        with self.engine.connect() as connection:
            result = connection.execute(query, parameters)
            return result.mappings()


# Legacy function for backward compatibility
@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def executeSQL(sql: str, parameters: Dict[str, Any] = {}) -> Any:
    """Legacy function for backward compatibility."""
    helper = MySQLHelper()
    return helper.execute_sql(sql, parameters) 