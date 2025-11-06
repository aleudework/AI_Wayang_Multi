from sqlalchemy import create_engine
import pandas as pd
from pandas import DataFrame
import json
import os
from typing import List

class SchemaLoader():
    """
    Loads schemas and examples for system prompts to agents

    """

    def __init__(self, config, output_folder):
        self.config = config["input_config"]
        self.output_folder = output_folder

    def get_and_save_textfile_schemas(self) -> str:
        """
        Get all textfile names avaliable to use
        If a textfile already is noted, they are not updated

        Returns:
            str: Schemas on available text files

        """

        try:
            # Make path for output folder
            output_folder = os.path.join(self.output_folder, "text_files")
            # Input folder
            folder = self.config["input_folder"]

            # Check that input folder exists
            if not os.path.exists(folder):
                raise Exception("Input folder doesn't exists")

            # Check that output folder exists
            if not os.path.exists(output_folder):
                raise Exception("Textfile output folder doesn't exists")
            
            # Get all .txt file paths in folder
            paths = [os.path.join(folder, f) 
                     for f in os.listdir(folder) 
                     if f.endswith(".txt")]

            # Add all .txt files metadata as .json to output
            for path in paths:
                # Only get file name
                file = os.path.splitext(os.path.basename(path))[0]

                # List for file data
                file_data = []

                # Add top 3 rows in file_data
                with open(path, "r", encoding="utf-8") as f:
                    for _ in range(3):
                        line = f.readline()

                        if not line:
                            break

                        file_data.append(line.rstrip("\n"))

                # Create full path for output json file
                path = os.path.join(output_folder, f"{file}.json")

                # Variables to count added schemas
                schema_exists_counter = 0
                schema_added_counter = 0

                # Continue if schema exists
                if os.path.exists(path):
                    schema_exists_counter += 1
                    continue
                
                # Format schema to json structure
                schema = self._format_to_json_textfile(file, file_data)

                # Convert everything to strings (errors with other datatypes)
                schema = json.loads(json.dumps(schema, default=str))

                # Write schema to json file
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(schema, f, indent=2, ensure_ascii=False)
                
                print(f"[INFO] {file} schema added to {output_folder}")
                schema_added_counter += 1

            msg = f"[INFO] Added textfile schemas. Added {schema_added_counter} schemas and {schema_exists_counter} schemas already exists"
            print(msg)

            return msg
                        
        except Exception as e:
            print(f"[Error] {e}")

    
    def get_and_save_table_schemas(self) -> str:
        """
        Get all tables in the database, get two example records of each tables. Adds them to data_schema_examples folder.
        If a table already exists, it is not added again.

        Returns:
            str: Information on number of added schemas.

        """

        try:
            # Make path for output folder
            output_folder = os.path.join(self.output_folder, "tables")

            # Check that output folder exists
            if not os.path.exists(output_folder):
                raise Exception("Table output folder doesn't exists")
            
            # Get schemas from db
            schemas = self._get_schemas()
            # Add example records to schemas
            schemas = self._add_record_examples(schemas)

            schema_exists_counter = 0
            schema_added_counter = 0

            # Go over each unique table in the schema:
            for table_name, table_data in schemas.groupby("table_name"):
                
                # Get filepath to output schema
                filepath = f"{output_folder}/{table_name}.json"

                # Continueto next if file already exists
                if os.path.isfile(filepath):
                    schema_exists_counter += 1
                    continue

                # Format schema to json structure
                schema = self._format_to_json_jdbc(table_name, table_data)

                # Convert everything to strings (errors with other datatypes)
                schema = json.loads(json.dumps(schema, default=str))

                # Write schema to json file
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(schema, f, indent=2, ensure_ascii=False)
                
                print(f"[INFO] {table_name} schema added to {output_folder}")
                schema_added_counter += 1

            msg = f"[INFO] Added table schemas. Added {schema_added_counter} schemas and {schema_exists_counter} schemas already exists"
            print(msg)

            return msg
        
        except Exception as e:
            print(f"[Error] {e}")

    
    def _get_schemas(self) -> DataFrame:
        """
        Helper function to get schema from database, postgress

        Returns:
            DataFrame: DF of schemas
        
        """

        # Create engine to get schemas
        engine = create_engine(f"postgresql+psycopg2://{self.config['jdbc_username']}:{self.config['jdbc_password']}@{self.config['jdbc_uri'].split('://')[1]}")

        # Query to get schemas
        query = """
        SELECT 
        table_name,
        column_name,
        data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """

        # Load schemas into dataframe
        schemas = pd.read_sql(query, engine)

        # Return dataframe
        return schemas
    
    
    def _add_record_examples(self, schemas: DataFrame) -> DataFrame:
        """
        Helper function. Take the schemas in DF and returns two examples of each column from each available table

        Args:
            schemas (DataFrame): schemas in DF

        Returns: 
            DataFrame: Updated DF ved schema and examples
        """

        # Engine to get data
        engine = create_engine(f"postgresql+psycopg2://{self.config['jdbc_username']}:{self.config['jdbc_password']}@{self.config['jdbc_uri'].split('://')[1]}")

        # Initialize example columns
        schemas_examples = schemas.copy()
        schemas_examples['example_1'] = None
        schemas_examples['example_2'] = None

        # Go over each table in the schema
        for table_name, _ in schemas.groupby("table_name"):
            
            # Take two random examples from table name
            query = f'SELECT * FROM "{table_name}" ORDER BY RANDOM() LIMIT 2;'

            # Load data into DF
            examples = pd.read_sql(query, engine)

            # Go over each column in the table
            for col in examples.columns:
                try: 
                    # Get the table and column in the schema
                    row =  (schemas_examples["table_name"] == table_name) & (schemas_examples["column_name"] == col)

                    # Add examples as example 1 and 2
                    schemas_examples.loc[row, "example_1"] = examples[col].iloc[0]
                    schemas_examples.loc[row, "example_2"] = examples[col].iloc[1]
                
                except Exception as e:
                    print(f"[Error] {e}")

        return schemas_examples
    
    def _format_to_json_textfile(self, file_name: str, file_data: List) -> str:
        """
        Helper function. Take input textfile and returns JSON

        Args:
            file_name (str): Name of textfile
            file_data (List): Example lines from file
        
        Returns:
            str: JSON of formatted textfile
            
        """

        # Create json_schema for textfileinpuit
        schema_json = {
            file_name: {
                "file_description": None,
                "input_type": "textfile_input",
                "examples_lines_from_file": file_data
            }
        }

        return schema_json

    

    def _format_to_json_jdbc(self, table_name: str, table_data: DataFrame) -> str:
        """
        Helper function. Take a schema and examples for a table and returns it as JSON

        Args:
            table_name (str): Name of table
            table_data (DataFrame): Column and data from table
        
        Returns:
            str: JSON of formatted schema with example

        """

        # Add table name and initialize new dict
        schema_json = {
            table_name: {
                "table_description": None,
                "input_type": "jdbc_input",
                "columns": {}
            }
        }

        # Go over each row of table data
        for _, row in table_data.iterrows():
            # Get fields
            column_name = row["column_name"]
            data_type = row["data_type"]
            example_1 = row["example_1"]
            example_2 = row["example_2"]

            # Add field to json
            schema_json[table_name]["columns"][column_name] = {
                "type": data_type,
                "examples": [example_1, example_2]
            }

        return schema_json
