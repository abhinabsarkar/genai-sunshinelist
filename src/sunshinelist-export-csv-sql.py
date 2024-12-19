import os
import re
import pandas as pd
import pyodbc
import logging
import shutil

# Set up logging
logging.basicConfig(filename='import_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Azure SQL Database connection details
server = '***.database.windows.net'
database = '***'
username = '***'
password = '***'
driver = '{ODBC Driver 18 for SQL Server}'

# Establish the connection
conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

# Create table if not exists
create_table_query = """
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SunshineList' AND xtype='U')
CREATE TABLE SunshineList (
    Sector VARCHAR(5000),
    LastName VARCHAR(5000),
    FirstName VARCHAR(5000),
    Salary FLOAT,
    Benefits FLOAT,
    Employer VARCHAR(5000),
    JobTitle VARCHAR(5000),
    Year INT
)
"""
cursor.execute(create_table_query)
conn.commit()

# Folder containing CSV files
csv_folder = 'csv_files'
csv_processed_folder = 'csv_processed'

# Ensure the processed folder exists
if not os.path.exists(csv_processed_folder):
    os.makedirs(csv_processed_folder)

# Function to extract year from file name
def extract_year_from_filename(filename):
    # Pattern to match a 4-digit year
    match = re.search(r'(\d{4})', filename)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Year not found in filename: {filename}")


# Iterate through each CSV file in the folder
for filename in os.listdir(csv_folder):
    if filename.endswith('.csv'):
        file_path = os.path.join(csv_folder, filename)
        try:
            # Try reading with utf-8-sig encoding
            df = pd.read_csv(file_path, header=0, encoding='utf-8-sig')  # Use the first row as the header
        except UnicodeDecodeError:
            try:
                # If utf-8-sig fails, try reading with latin1 encoding
                df = pd.read_csv(file_path, header=0, encoding='latin1')
            except UnicodeDecodeError:
                logging.error(f"Error reading file {filename} with both 'utf-8-sig' and 'latin1' encodings")
                continue

        # Extract year from the file name
        try:
            year_from_filename = extract_year_from_filename(filename)
        except ValueError as e:
            logging.error(e)
            raise
        
        # Log the name of the CSV file and the count of rows
        logging.info(f"Processing file: {filename}")
        logging.info(f"Number of rows: {len(df)}")
        
        # Debugging: Print the column names of the DataFrame
        print(f"Processing file: {filename}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Map columns based on their positions
        df.columns = ['Sector', 'LastName', 'FirstName', 'Salary', 'Benefits', 'Employer', 'JobTitle', 'Year']

        # Remove dollar signs, hyphen and commas, then convert to numeric
        # df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).replace(',', '', regex=True).astype(float)
        # df['Benefits'] = df['Benefits'].replace(r'[\$,]', '', regex=True).replace(',', '', regex=True).astype(float)
        df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).replace(',', '', regex=True).replace('-', 'NaN').astype(float)
        df['Benefits'] = df['Benefits'].replace(r'[\$,]', '', regex=True).replace(',', '', regex=True).replace('-', 'NaN').astype(float)

        # Replace NaN values with 0 or another default value
        df['Salary'].fillna(0, inplace=True)
        df['Benefits'].fillna(0, inplace=True)
        
        # Replace NaN values in string columns with an empty string
        df['FirstName'].fillna('', inplace=True)
        df['LastName'].fillna('', inplace=True)
        df['Sector'].fillna('', inplace=True)
        df['Employer'].fillna('', inplace=True)
        df['JobTitle'].fillna('', inplace=True)
        # Fill missing Year values with the year from the file name
        df['Year'].fillna(year_from_filename, inplace=True)
        
        # Debugging: Print the first few rows of the DataFrame
        print(df.head())
                
        # Insert data into the SQL table in blocks of 5000 rows
        row_count = 0
        for index, row in df.iterrows():
            print(f"Inserting row {index} : {row}")
            try:
                insert_query = """
                INSERT INTO SunshineList (Sector, LastName, FirstName, Salary, Benefits, Employer, JobTitle, Year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_query, row['Sector'], row['LastName'], row['FirstName'], row['Salary'], row['Benefits'], row['Employer'], row['JobTitle'], row['Year'])
                row_count += 1
                if row_count % 5000 == 0:
                    conn.commit()
                    logging.info(f"Committed {row_count} rows")
            except pyodbc.ProgrammingError as e:
                logging.error(f"Error inserting row {index}: {e}")
                logging.error(f"Row data: Sector={row['Sector']}, LastName={row['LastName']}, FirstName={row['FirstName']}, Salary={row['Salary']}, Benefits={row['Benefits']}, Employer={row['Employer']}, JobTitle={row['JobTitle']}, Year={row['Year']}")
                raise  # Re-raise the exception to fail the code

        # Commit any remaining rows
        if row_count % 5000 != 0:
            conn.commit()
            logging.info(f"Committed remaining {row_count % 5000} rows")
    
    # Move the processed file to the csv_processed folder
    processed_file_path = os.path.join(csv_processed_folder, filename)
    shutil.move(file_path, processed_file_path)
    logging.info(f"Moved file {filename} to {csv_processed_folder}")

# Close the connection
cursor.close()
conn.close()