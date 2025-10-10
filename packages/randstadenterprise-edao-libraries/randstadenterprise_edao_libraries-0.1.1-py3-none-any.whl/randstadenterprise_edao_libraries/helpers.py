# randstadenterprise_edao_libraries/helpers.py
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field 

# Import the new data objects file
from . import objects 

# =======================================================================
# CORE HELPER FUNCTIONS
# =======================================================================

def get_http_headers (inst_dev_token: str) -> Dict[str, str]:
# =======================================================================
# GENERATES STANDARD DOMO API HEADERS
# =======================================================================
    # START def get_http_headers
    """
    Generates the standard HTTP headers required for Domo's private APIs.
    
    :param inst_dev_token: The developer token for 'X-DOMO-Developer-Token'.
    :returns: Dictionary of standard HTTP headers.
    """
    return {
        'X-DOMO-Developer-Token': inst_dev_token,
        'X-DOMO-Authentication': 'null', 
        'Content-Type': 'application/json;charset=utf-8',
        'Accept': 'application/json, text/plain, */*'
    }
# END def get_http_headers

def dataframe_to_csv (dataframe: pd.DataFrame) -> str:
# =======================================================================
# CONVERTS A PANDAS DATAFRAME TO CSV STRING
# =======================================================================
    # START def dataframe_to_csv
    """
    Converts a pandas DataFrame into a CSV string (without header/index).
    
    :param dataframe: The pandas DataFrame to convert.
    :returns: The resulting CSV data as a string.
    """
    return dataframe.to_csv(header=False, index=False)
# END def dataframe_to_csv

def array_to_csv (array: List[List[Any]], cols: List[str]) -> str:
# =======================================================================
# CONVERTS A 2D LIST ARRAY TO CSV STRING VIA DATAFRAME
# =======================================================================
    # START def array_to_csv
    """
    Converts a list of lists (array) into a CSV string (without header/index).
    
    :param array: The 2D list of data.
    :param cols: The list of column names.
    :returns: The resulting CSV data as a string.
    """
    # 1. Convert list of lists to DataFrame
    dataframe = pd.DataFrame(array, columns=cols)
    # 2. Convert DataFrame to CSV string
    return dataframe_to_csv(dataframe)
# END def array_to_csv

def load_instance_map (inst_df: pd.DataFrame) -> Dict[str, objects.Instance]:
# =======================================================================
# LOADS INSTANCE CONFIGURATIONS FROM DATAFRAME
# =======================================================================
    # START def load_instance_map
    """
    Parses a DataFrame containing Domo instance configurations and returns a 
    dictionary mapping instance URL to a typed Instance object.
    
    :param inst_df: The pandas DataFrame containing instance configurations.
    :returns: A dictionary mapping {Instance_URL (str): objects.Instance (object)}.
    """
    instance_map: Dict[str, objects.Instance] = {}
    
    # Get the fields from the objects.Instance dataclass
    instance_fields = [f.name for f in objects.Instance.__dataclass_fields__.values()]
    
    # 1. Map DataFrame column names to Instance object field names
    for i in inst_df.index:
        # START for i in inst_df.index
        
        # Build arguments dynamically, defaulting to None if column is missing
        kwargs = {}
        for field_name in instance_fields:
            # Convert snake_case field name to Title Case column name (e.g., Instance_URL -> Instance URL)
            df_col_name = field_name.replace('_', ' ')
            
            # Use .get with default list to handle potentially missing columns safely
            value = inst_df.get(df_col_name, [None] * len(inst_df))[i]
            
            # Clean and store the value
            if field_name == 'Order' and value is not None and pd.notna(value):
                # Handle integer conversion for 'Order'
                kwargs[field_name] = int(value)
            elif value is not None and pd.notna(value):
                # All other fields are treated as strings
                kwargs[field_name] = str(value)
            else:
                kwargs[field_name] = None
        
        inst_url = kwargs.get('Instance_URL', str(i))
        
        # 2. Create the Instance object using collected keyword arguments
        instance_obj = objects.Instance(**kwargs)
        
        # 3. Map instance object using Instance URL as the key
        instance_map[inst_url] = instance_obj
        # END for i in inst_df.index
        
    return instance_map
# END def load_instance_map