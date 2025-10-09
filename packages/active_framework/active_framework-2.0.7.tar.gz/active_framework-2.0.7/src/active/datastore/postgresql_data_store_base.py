import decimal
import json
import psycopg

from  active.datastore.data_store import DataStore

class PostgresqlDataStoreBase(DataStore):
    '''
    A DataStore for saving and retrieving data from a PostgreSQL database.
    
    ACTIVE Environment parameters prototype:
    
    {
        "database": "mydb",
        "host": "localhost",
        "password": "password1",
        "port": "5432",
        "schema": {
            "table1": {
                "column1": "integer",
                "column2": "decimal"
            }
        },
        "user": "username"
    }
    
    Parameters:
        schema Dictionary definition of the database schema, from table names to dictionaries of column names to 
            string column PostgreSQL types.
    '''
    
    def __init__(self, database="", host="", password="", port="", schema={}, user=""):
        '''
        The default constructor.
    
        Args:
            database: PostgreSQL database name as a string
            host: Hostname for the database, as a string
            password: User's password for the database, as a string
            port: Port number forthe database, as a string
            schema: Dictionary from table names to dictionaries of column names to string column PostgreSQL types.
            user: Username to validate with, as a string
        '''
            
        self.schema = schema
        
        # Create the psycopg string to connect to the database
        self.db_connect_string = "host=" + host + " port=" + port + " dbname=" + database + " user=" + user \
            + " password=" + password
            
        # Connect to database
        with psycopg.connect(self.db_connect_string) as conn:
        
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                
                # Try to create each table if it doesn't exist
                for table in schema:
                    
                    # Create a string that will create the table
                    execution_string = "CREATE TABLE IF NOT EXISTS " + table + "("
                    
                    # Exit if table schema is not specified
                    if not schema[table]:
                        print("Could not instantiate PostgreSQL table " + table + " without columns defined in " \
                              + "PostgreSQLDataStore")
                        return
                    
                    for column in schema[table]:
                        execution_string += column + " " + schema[table][column] + ","
                        
                    execution_string = execution_string[0:-1] + ");"
                    cur.execute(execution_string)
                 
                # Commit the creation of all the tables
                conn.commit()   
        
        
    def copy(self, id, input):
        '''
        Copy the data to the given table
        
        Args:
            id: The table name
            input: The new row to append, as a json string from column names to values
        '''
        
        # Load the input into a dictionary
        input_dict = json.loads(input)

        # Don't make an empty commit
        if not input_dict:
            return
                    
        # Connect to the database
        with psycopg.connect(self.db_connect_string) as conn:
        
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                
                # Create a string to define inserting the new data
                execution_string = "INSERT INTO " + id + "("
                column_string = ""
                value_string = ""
                
                for parameter in input_dict:
                    
                    if not isinstance(input_dict[parameter], list):
                        column_string += parameter + ","
                        value_string += "'" + str(input_dict[parameter]) + "',"
                        
                    else:
                        
                        # Convert lists into proper sql array format
                        column_string += parameter + ","
                        converted_list = str(input_dict[parameter])
                        converted_list = "{" + converted_list[1:-1] + "}"
                        value_string += "'" + converted_list + "',"
                    
                column_string = column_string[0:-1]
                value_string = value_string[0:-1]
                
                execution_string += column_string + ") VALUES (" + value_string + ")"
                
                cur.execute(execution_string)
                
                conn.commit()
                
    def get_visualization_type(self):
        '''
        Get a human readable visualization type, describing how data in this data store might be visualized.
        
        Return:
           The string "DATAFRAME 
        '''
        
        return "DATAFRAME"
                
    def load(self, id, name=None, num_items=None):
        '''
        Load data from the given table
        
        Args:
            id: The name of the table to load from
            name: Ignored
            num_items: The number of rows to read. If None, read the entire table
        '''
        
        # Connect to the database
        with psycopg.connect(self.db_connect_string) as conn:
        
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                
                
                # Perform the appropriate fetch for the number of rows sought
                if num_items == 1:
                    
                    # Select all the columns from the table
                    cur.execute("SELECT * FROM " + id)
                    data = cur.fetchone()
                
                elif num_items is None:
                    
                    # Select all the columns from the table
                    cur.execute("SELECT * FROM " + id)
                    data = cur.fetchall()
                
                else:
                    
                    cols = self.get_column_names(id)
                    
                    if "measurement_taken" in cols:
                        col = "measurement_taken"
                    else:
                        col = cols[0]
                    
                    # Select all the columns from the table
                    cur.execute("SELECT * FROM " + id + " ORDER BY " + col + " DESC LIMIT " + str(num_items))
                    data = cur.fetchall()
                    
                output_data = []
                    
                for row in data:
                    
                    curr_row = []
                    
                    for i in range(len(row)):
                        if type(row[i]) == decimal.Decimal:
                            curr_row.append(float(row[i]))
                        else:
                            curr_row.append(row[i])

                    output_data.append(curr_row)
                    
                if not num_items is None and num_items != 1:
                    output_data = list(reversed(output_data))
                    
                return output_data
                
    def get_column_names(self, id):
        
        # Connect to the database
        with psycopg.connect(self.db_connect_string) as conn:
        
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
        
                cur.execute("Select * FROM " + id + " LIMIT 0")
                
                return [d[0] for d in cur.description]
                
    def get_ids(self):
        
        tables = []
        
        
        # Connect to the database
        with psycopg.connect(self.db_connect_string) as conn:
        
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                
                cur.execute("""SELECT table_name FROM information_schema.tables
                   WHERE table_schema = 'public'""")
                for table in cur.fetchall():
                    
                    tables.append(table[0])
                    
        return tables

