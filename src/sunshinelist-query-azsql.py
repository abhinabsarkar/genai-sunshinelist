# Reference - https://devblogs.microsoft.com/azure-sql/building-your-own-db-copilot-for-azure-sql-with-azure-openai-gpt-4/

import os
import time
import logging
from langchain_community.utilities import SQLDatabase
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from langchain_community.agent_toolkits.sql.base import create_sql_agent, SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_openai.chat_models import AzureChatOpenAI
# from azure.identity import EnvironmentCredential, get_bearer_token_provider
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType

# Configure logging
# logging.basicConfig(level=logging.DEBUG)

# Set up database connection parameters  
os.environ["SQL_SERVER_USERNAME"] = "***" 
os.environ["SQL_SERVER_ENDPOINT"] = "***.database.windows.net"
os.environ["SQL_SERVER_PASSWORD"] = "***"  
os.environ["SQL_SERVER_DATABASE"] = "***"
server = '***.database.windows.net'
database = '***'
username = '***'
password = '***'
driver = '{ODBC Driver 18 for SQL Server}' 

db_config = {  
    'drivername': 'mssql+pyodbc',  
    'username': os.environ["SQL_SERVER_USERNAME"] + '@' + os.environ["SQL_SERVER_ENDPOINT"],  
    'password': os.environ["SQL_SERVER_PASSWORD"],  
    'host': os.environ["SQL_SERVER_ENDPOINT"],  
    'port': 1433,  
    'database': os.environ["SQL_SERVER_DATABASE"],  
    'query': {'driver': 'ODBC Driver 18 for SQL Server'}  
} 
db_url = URL.create(**db_config)
db = SQLDatabase.from_uri(db_url)

#setting Azure OpenAI env variables
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "***"
os.environ["OPENAI_API_KEY"] = "***"

llm = AzureChatOpenAI(deployment_name="gpt-4o", 
                      api_key=os.getenv("OPENAI_API_KEY"),
                      azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                      temperature=0, max_tokens=4000)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

query = "Count the number of records in the SunshineList table"
response = agent_executor.invoke(query)
print(response)