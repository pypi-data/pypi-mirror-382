# randstadenterprise_edao_libraries/datasets.py
import requests
import threading
from typing import List, Dict, Any, Optional, Callable, Union
from pydomo.datasets import DataSetRequest, Schema, Column
from pydomo import Domo

from . import helpers # Provides get_http_headers, array_to_csv
from . import logs    # Provides log function (for type hinting)
from . import objects # Import all dataclasses

# Type for the custom log function needed for API retrieval to keep the dependency chain clean
LogFunc = Callable[[str], None] 

# =======================================================================
# UTILITY FUNCTIONS
# =======================================================================

def get_dataset_stats (inst_url: str, inst_dev_token: str) -> Dict[str, Any]:
# =======================================================================
# RETRIEVES HIGH-LEVEL DATASET STATISTICS
# =======================================================================
    # START def get_dataset_stats
    """
    Retrieves high-level customer stats (like total dataset count) for an instance.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :returns: Dictionary containing instance stats, or raises an HTTPError.
    """
    # 1. Prepare API endpoint and headers
    api_url = f'https://{inst_url}.domo.com/api/query/v1/datasources/customer-stats'
    headers = helpers.get_http_headers(inst_dev_token)
    
    # 2. Execute request
    resp = requests.get(api_url, headers=headers)
    resp.raise_for_status() 
    
    return resp.json()
# END def get_dataset_stats

# =======================================================================
# DATASET RETRIEVAL AND LOOKUP
# =======================================================================

def get_dataset_by_name (
    inst_url: str, inst_dev_token: str, dataset_name: str, log_func: LogFunc
) -> Optional[objects.Dataset]:
# =======================================================================
# SEARCHES FOR AN EXACT DATASET MATCH BY NAME
# =======================================================================
    # START def get_dataset_by_name
    """
    Searches for a dataset by name using the Domo UI Search API (wildcard) 
    and returns the exact match.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param dataset_name: The exact name of the dataset to find.
    :param log_func: Pre-bound logging function.
    :returns: The objects.Dataset object if found, otherwise None.
    """
    
    log_func(f"_______________ get_dataset_by_name({dataset_name})")
    
    # 1. Fetch search results (using private helper, although currently implemented inline)
    api_url = f'https://{inst_url}.domo.com/api/data/ui/v3/datasources/search'
    headers = helpers.get_http_headers(inst_dev_token)

    body = {
        "entities": ["DATASET"],
        "filters": [{"field": "name_sort", "filterType": "wildcard", "query": f"*{dataset_name}*"}],
        "combineResults": "true",
        "query": "*",
        "count": 30, 
        "offset": 0,
        "sort": {"isRelevance": "false", "fieldSorts": [{"field": "create_date", "sortOrder": "DESC"}]}
    }

    datasets_res = requests.post(api_url, headers=headers, json=body)
    datasets_res.raise_for_status()
    
    datasets_json = datasets_res.json()
    datasets_search_results = None
    
    # 2. Iterate through results to find the exact name match
    if "dataSources" in datasets_json:
        # START if "dataSources" in datasets_json
        for ds in datasets_json["dataSources"]: 
            # START for ds in datasets_json["dataSources"]
            if ds.get("name") == dataset_name:
                # START if ds.get("name") == dataset_name
                datasets_search_results = ds
                break
                # END if ds.get("name") == dataset_name
            # END for ds in datasets_json["dataSources"]
        # END if "dataSources" in datasets_json
    
    log_func('_______________ END get_dataset_by_name()')

    # 3. Convert raw dict to object.Dataset
    if datasets_search_results:
        # START if datasets_search_results
        return objects.Dataset(
            id=datasets_search_results.get('id', ''),
            name=datasets_search_results.get('name', ''),
            data_provider_name=datasets_search_results.get('dataProviderName'),
            description=datasets_search_results.get('description'),
            row_count=datasets_search_results.get('rows'),
            column_count=datasets_search_results.get('columns'),
            owners=[] # Ownership data often requires separate API call, stubbing for now
        )
    # END if datasets_search_results
    return None
# END def get_dataset_by_name

def get_dataset_by_id (inst_url: str, inst_dev_token: str, dataset_id: str, log_func: LogFunc) -> Optional[objects.Dataset]:
# =======================================================================
# RETRIEVES A SINGLE DATASET BY ID
# =======================================================================
    # START def get_dataset_by_id
    """
    Stubs out functionality to retrieve a single dataset by its ID.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param dataset_id: The string ID of the dataset.
    :param log_func: Pre-bound logging function.
    :returns: The objects.Dataset object, or None if not found.
    """
    print(f"STUB: Getting dataset {dataset_id} from {inst_url}")
    return None
# END def get_dataset_by_id

# =======================================================================
# PRIVATE API HELPER FUNCTIONS
# =======================================================================

def _get_datasets_page (
    inst_url: str, domo_ds_api: Domo.datasets, count: int, offset: int, 
    log_func: LogFunc
) -> List[Dict[str, Any]]:
# =======================================================================
# PRIVATE: RETRIEVE A SINGLE PAGE OF DATASETS VIA PYDOMO
# =======================================================================
    # START def _get_datasets_page
    """
    (PRIVATE) Retrieves a single page of datasets using the PyDomo SDK.
    
    :param inst_url: The Domo instance URL prefix (for logging).
    :param domo_ds_api: The PyDomo datasets client object.
    :param count: The number of records to retrieve (limit).
    :param offset: The starting offset.
    :param log_func: Pre-bound logging function.
    :returns: A list of dataset dictionary objects.
    """
    
    log_func(f"__________ _get_datasets_page(count={count}, offset={offset})")
    
    try:
        # START try
        # PyDomo list() method returns dataset objects
        datasets_array = list(domo_ds_api.list(limit=count, offset=offset))
    # END try
    except Exception as e:
        # START except Exception as e
        log_func(f"ERROR listing datasets via PyDomo SDK: {e}")
        return []
        # END except Exception as e

    log_func('__________ END _get_datasets_page()')
    
    return datasets_array
# END def _get_datasets_page


def _get_page_search (
    inst_url: str, inst_dev_token: str, count: int, offset: int, log_func: LogFunc
) -> Optional[List[dict]]:
# =======================================================================
# PRIVATE: FETCHES A PAGINATED LIST OF DATASETS (EXCLUDING DATASET VIEWS)
# =======================================================================
    # START def _get_page_search
    """
    (PRIVATE) Fetches a paginated list of datasets, excluding "DataSet View" type via search API.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param count: The requested number of results (limit).
    :param offset: The starting offset.
    :param log_func: Pre-bound logging function.
    :returns: A list of dataset dictionaries, or None on critical failure.
    """
    log_func(f'_______________ Calling _get_page_search (UI/V3) count: {count}, offset: {offset}')
    api_url = f'https://{inst_url}.domo.com/api/data/ui/v3/datasources/search'
    
    # 1. Define search body with a filter to exclude 'DataSet View'
    body = {
        "entities": ["DATASET"],
        "filters": [{
            "filterType": "term",
            "field": "dataprovidername_facet",
            "value": "DataSet View", 
            "not": True 
        }],
        "combineResults": True, 
        "query": "*", 
        "count": count,
        "offset": offset,
        "sort": {
            "isRelevance": False, 
            "fieldSorts": [{"field": "create_date", "sortOrder": "DESC"}]
        }
    }

    try:
        # START try
        resp = requests.post(api_url, headers=helpers.get_http_headers(inst_dev_token), json=body, timeout=30)
        resp.raise_for_status() 

        response_json = resp.json()
        datasets_array = response_json.get("dataSources")
        if datasets_array is None: 
            # START if datasets_array is None
             log_func(f"WARN: 'dataSources' key not found in response. Response: {response_json}")
             return [] 
            # END if datasets_array is None
        return datasets_array 
    
    # END try
    except requests.exceptions.RequestException as e:
        # START except requests.exceptions.RequestException as e
        log_func(f"ERROR: RequestException in _get_page_search: {type(e).__name__} - {e}")
        return None
        # END except requests.exceptions.RequestException as e
# END def _get_page_search


def get_dataset_permissions (
    inst_url: str, inst_dev_token: str, ds_id: str, log_func: LogFunc
) -> Optional[Dict[str, dict]]:
# =======================================================================
# RETRIEVES USER/GROUP PERMISSIONS FOR A DATASET
# =======================================================================
    # START def get_dataset_permissions
    """
    Retrieves all user/group permissions for a given dataset ID.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param ds_id: The ID of the dataset.
    :param log_func: Pre-bound logging function.
    :returns: Map of {Permission_Name (original case): Permission_Details}, or None on critical failure.
    """
    log_func(f'____________________ Calling get_dataset_permissions for DS ID: {ds_id}')
    api_url = f'https://{inst_url}.domo.com/api/data/v3/datasources/{ds_id}/permissions'
    
    dataset_perms_map: Dict[str, dict] = {}
    try:
        # START try
        # 1. Fetch permissions
        resp = requests.get(api_url, headers=helpers.get_http_headers(inst_dev_token), timeout=20)
        resp.raise_for_status()
        
        permissions_json = resp.json()
        # 2. Extract and map permissions
        if "list" in permissions_json and isinstance(permissions_json["list"], list):
            # START if "list" in permissions_json and isinstance(permissions_json["list"], list)
            for perm_entry in permissions_json["list"]:
                # START for perm_entry in permissions_json["list"]
                if isinstance(perm_entry, dict) and "name" in perm_entry:
                    # START if isinstance(perm_entry, dict) and "name" in perm_entry
                    dataset_perms_map[perm_entry["name"]] = perm_entry
                    # END if isinstance(perm_entry, dict) and "name" in perm_entry
                # END for perm_entry in permissions_json["list"]
            return dataset_perms_map
        else:
            # START else
            log_func(f"WARN (DS_ID: {ds_id}): 'list' key not found or not a list in permissions response.")
            return {} 
            # END else
        # END if "list" in permissions_json and isinstance(permissions_json["list"], list)
    # END try
    except requests.exceptions.RequestException as e:
        # START except requests.exceptions.RequestException as e
        log_func(f"ERROR (DS_ID: {ds_id}): RequestException in get_dataset_permissions: {type(e).__name__} - {e}")
        return None
        # END except requests.exceptions.RequestException as e
# END def get_dataset_permissions


# =======================================================================
# PUBLIC PAGINATION FUNCTIONS
# =======================================================================

def get_all_instance_datasets (
    inst_url: str, inst_dev_token: str, domo_ds_api: Domo.datasets, inst_name: str, 
    lock: threading.Lock, logs_array: List[List[Any]], page_size: int = 100
) -> List[objects.Dataset]:
# =======================================================================
# RETRIEVES ALL DATASETS VIA PYDOMO SDK PAGINATION
# =======================================================================
    # START def get_all_instance_datasets
    """
    Retrieves ALL datasets from a Domo instance by handling full pagination 
    of the PyDomo SDK's list() method.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token (included for consistency, but unused here).
    :param domo_ds_api: The PyDomo datasets client object.
    :param inst_name: The instance name (for logging context).
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :param page_size: The number of results per page (defaults to 100).
    :returns: A list containing all objects.Dataset objects.
    """
    
    log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock)
    log_func(f"__________ get_all_instance_datasets: Starting full retrieval.")
    
    all_datasets_raw = []
    offset = 0
    current_page_count = page_size # Initialize to ensure loop starts

    # 1. Fetch all raw data
    while current_page_count == page_size:
        # START while current_page_count == page_size
        
        # Fetch the next page of datasets using the private helper
        datasets_page = _get_datasets_page(
            inst_url, domo_ds_api, page_size, offset, log_func
        )
        
        current_page_count = len(datasets_page)
        
        if current_page_count > 0:
            # START if current_page_count > 0
            all_datasets_raw.extend(datasets_page)
            offset += current_page_count
            # END if current_page_count > 0
        
        # If the page size is less than the limit, we've reached the end
        if current_page_count < page_size:
            # START if current_page_count < page_size
            break
            # END if current_page_count < page_size

    log_func(f"__________ get_all_instance_datasets: Finished. Total datasets: {len(all_datasets_raw)}")
    
    # 2. Convert raw dictionaries to objects.Dataset
    all_datasets_objects: List[objects.Dataset] = []
    for ds in all_datasets_raw:
        # START for ds in all_datasets_raw
        all_datasets_objects.append(objects.Dataset(
            id=str(ds.get('id', '')),
            name=ds.get('name', ''),
            data_provider_name=ds.get('dataProviderName'),
            description=ds.get('description'),
            row_count=ds.get('rows'),
            column_count=ds.get('columns'),
            owners=[] # Requires separate API call for full ownership list
        ))
        # END for ds in all_datasets_raw
        
    return all_datasets_objects
# END def get_all_instance_datasets


# =======================================================================
# DATASET MODIFICATION/ACTION FUNCTIONS
# =======================================================================

def save_dataset (inst_url: str, inst_dev_token: str, domo_ds_api: Domo.datasets, dataset_obj: objects.Dataset, log_func: LogFunc) -> Optional[str]:
# =======================================================================
# SAVES (CREATES OR UPDATES) A DATASET
# =======================================================================
    # START def save_dataset
    """
    Stubs out functionality to create or update a dataset.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param domo_ds_api: The PyDomo datasets client object.
    :param dataset_obj: The objects.Dataset object (dataclass instance) to be saved.
    :param log_func: Pre-bound logging function.
    :returns: The string ID of the saved dataset, or None on failure.
    """
    print(f"STUB: Saving dataset {dataset_obj.name} to {inst_url}")
    return dataset_obj.id
# END def save_dataset

def delete_dataset (inst_url: str, inst_dev_token: str, dataset_id: str, log_func: LogFunc) -> bool:
# =======================================================================
# DELETES A DATASET BY ID
# =======================================================================
    # START def delete_dataset
    """
    Stubs out functionality to delete a dataset.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param dataset_id: The string ID of the dataset to delete.
    :param log_func: Pre-bound logging function.
    :returns: True on success, False on failure.
    """
    print(f"STUB: Deleting dataset {dataset_id} from {inst_url}")
    return True
# END def delete_dataset

def share_dataset (
    inst_url: str, inst_dev_token: str, ds_id: str, share_type: str, share_id: str, 
    share_name: str, access_lvl: str, log_func: LogFunc
) -> bool:
# =======================================================================
# SHARES A DATASET WITH A USER OR GROUP
# =======================================================================
    # START def share_dataset
    """
    Shares a dataset with a user or group.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param ds_id: The ID of the dataset to share.
    :param share_type: The type of entity being shared with ('USER' or 'GROUP').
    :param share_id: The ID of the user or group.
    :param share_name: The display name of the user or group.
    :param access_lvl: The access level ('CO_OWNER', 'CAN_EDIT', 'CAN_SHARE').
    :param log_func: Pre-bound logging function.
    :returns: True on success, False on failure.
    """
    log_func(f'____________________ Calling share_dataset for DS ID: {ds_id} with {share_type} ID: {share_id} at level {access_lvl}')
    api_url = f'https://{inst_url}.domo.com/api/data/v3/datasources/{ds_id}/permissions'

    # 1. Lookup access level details
    lbl_desc_lookup = {
        "CO_OWNER": {"label": "Co-owner", "description": "Allows for editing and deleting DataSet (same as owner)"},
        "CAN_EDIT": {"label": "Can Edit", "description": "Allows for editing and sharing DataSet, but can't delete"},
        "CAN_SHARE": {"label": "Can Share", "description": "Allows for sharing, but can't edit DataSet at all"}
    }
    
    if access_lvl not in lbl_desc_lookup:
        # START if access_lvl not in lbl_desc_lookup
        log_func(f"ERROR (DS_ID: {ds_id}): Invalid access_lvl '{access_lvl}' in share_dataset.")
        return False
        # END if access_lvl not in lbl_desc_lookup

    access_details = lbl_desc_lookup[access_lvl]
    
    # 2. Define API body
    body = {
        "accessLevel": access_lvl,
        "accessObject": {
            "accessLevel": access_lvl,
            "label": access_details["label"],
            "description": access_details["description"]
        },
        "id": str(share_id), 
        "name": share_name,
        "type": share_type
    }

    try:
        # START try
        # 3. Execute PUT request
        resp = requests.put(api_url, headers=helpers.get_http_headers(inst_dev_token), json=body, timeout=20)
        resp.raise_for_status()
        return True
    # END try
    except requests.exceptions.RequestException as e:
        # START except requests.exceptions.RequestException as e
        log_func(f"ERROR (DS_ID: {ds_id}): RequestException in share_dataset with {share_name}: {type(e).__name__} - {e}")
        return False
        # END except requests.exceptions.RequestException as e
# END def share_dataset

def unshare_dataset (
    inst_url: str, inst_dev_token: str, ds_id: str, share_type: str, share_id: str, log_func: LogFunc
) -> bool:
# =======================================================================
# UNSHARES A DATASET FROM A USER OR GROUP
# =======================================================================
    # START def unshare_dataset
    """
    Unshares a dataset with a user or group.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param ds_id: The ID of the dataset.
    :param share_type: The type of entity being unshared from ('USER' or 'GROUP').
    :param share_id: The ID of the user or group.
    :param log_func: Pre-bound logging function.
    :returns: True on success or if permission is already gone (404), False on other failures.
    """
    log_func(f'____________________ Calling unshare_dataset for DS ID: {ds_id} from {share_type} ID: {share_id}')
    api_url = f'https://{inst_url}.domo.com/api/data/v3/datasources/{ds_id}/permissions/{share_type}/{share_id}'
    
    try:
        # START try
        # 1. Execute DELETE request
        resp = requests.delete(api_url, headers=helpers.get_http_headers(inst_dev_token), timeout=20)
        resp.raise_for_status()
        return True
    # END try
    except requests.exceptions.HTTPError as hpe:
        # START except requests.exceptions.HTTPError as hpe
        # 2. Check for 404 (acceptable if permission is already gone)
        if hpe.response.status_code == 404:
            # START if hpe.response.status_code == 404
            log_func(f"WARN (DS_ID: {ds_id}): Attempted unshare, resource not found (likely already removed).")
            return True
            # END if hpe.response.status_code == 404
        log_func(f"ERROR (DS_ID: {ds_id}): HTTPError in unshare_dataset from {share_id}. Status: {hpe.response.status_code}. Response: {hpe.response.text}")
        return False
        # END except requests.exceptions.HTTPError as hpe
    except requests.exceptions.RequestException as e:
        # START except requests.exceptions.RequestException as e
        log_func(f"ERROR (DS_ID: {ds_id}): RequestException in unshare_dataset from {share_id}: {type(e).__name__} - {e}")
        return False
        # END except requests.exceptions.RequestException as e
# END def unshare_dataset

def create_dataset (
    inst_url: str, inst_dev_token: str, domo_ds_api: Domo.datasets, 
    dataset_array: List[List[Any]], dataset_name: str, dataframe_cols: List[str], 
    dataset_cols: List[Column], add_tag: str, pre_existing_dataset_id: Optional[str] = None,
    delete_instance_datasets: bool = False, lock: threading.Lock = threading.Lock(), 
    logs_array: List[List[Any]] = []
) -> Optional[str]:
# =======================================================================
# CREATES OR UPDATES A DATASET AND IMPORTS DATA
# =======================================================================
    # START def create_dataset
    """
    Creates, updates metadata, or soft-deletes and recreates a dataset based on flags 
    and checks if an ID is provided or can be found by name.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param domo_ds_api: The PyDomo datasets client object.
    :param dataset_array: The 2D array of data to import.
    :param dataset_name: The name of the dataset.
    :param dataframe_cols: List of column names (for CSV creation).
    :param dataset_cols: List of pydomo.Column objects (for metadata/schema).
    :param add_tag: A tag to potentially add (though unused in the current body).
    :param pre_existing_dataset_id: An optional ID to update.
    :param delete_instance_datasets: Flag to force soft-delete and recreate if found.
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :returns: The final dataset ID, or None if creation failed.
    """
    
    log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock)
    current_dataset_id = pre_existing_dataset_id

    log_func(f"__________ create_dataset({dataset_name})")

    # 1. If ID is missing, try to find it by name
    if current_dataset_id is None:
        # START if current_dataset_id is None
        try:
            # START try
            # Use a separate log function for the lookup
            lookup_log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock) 
            ext_instance_dataset = get_dataset_by_name(inst_url, inst_dev_token, dataset_name, lookup_log_func)
            
            if ext_instance_dataset and ext_instance_dataset.id:
                # START if ext_instance_dataset and ext_instance_dataset.id
                current_dataset_id = ext_instance_dataset.id
                
                # Apply general DELETE_INSTANCE_DATASETS flag
                if delete_instance_datasets:
                    # START if delete_instance_datasets
                    log_func(f"_______ Deleting dataset {current_dataset_id} due to flag.")
                    # Soft-delete the existing dataset
                    delete_ds_url = f'https://{inst_url}.domo.com/api/data/v3/datasources/{current_dataset_id}?deleteMethod=soft'
                    requests.delete(delete_ds_url, headers=helpers.get_http_headers(inst_dev_token))
                    current_dataset_id = None # Forces recreation below
                else:
                    # START else
                    log_func(f"_______ Update metadata for {dataset_name} ({current_dataset_id})")
                    # Update metadata on the existing dataset
                    dsr = DataSetRequest(name=dataset_name, description=dataset_name, schema=Schema(dataset_cols))
                    domo_ds_api.update(current_dataset_id, dsr)
                    # END else
                # END if delete_instance_datasets
                # END if ext_instance_dataset and ext_instance_dataset.id
            
        # END try
        except Exception as e:
            # START except Exception as e
            log_func(f"ERROR during dataset lookup/metadata update: {e}")
            # END except Exception as e
        # END if current_dataset_id is None
            
    # 2. Create new dataset if ID is still None
    if current_dataset_id is None:
        # START if current_dataset_id is None
        log_func(f"Attempting to CREATE new dataset: {dataset_name}")
        try:
            # START try
            # Create the dataset request and call the PyDomo create method
            dsr = DataSetRequest(name=dataset_name, description=dataset_name, schema=Schema(dataset_cols))
            dataset = domo_ds_api.create(dsr)
            current_dataset_id = dataset['id']
            log_func(f"Dataset CREATED with ID: {current_dataset_id}")
        # END try
        except Exception as e:
            # START except Exception as e
            log_func(f"CRITICAL ERROR creating dataset {dataset_name}: {e}")
            return None
            # END except Exception as e
        # END if current_dataset_id is None
    
    # 3. Import Data
    if current_dataset_id and dataset_array:
        # START if current_dataset_id and dataset_array
        # Convert data array to CSV string
        dataset_csv = helpers.array_to_csv(dataset_array, dataframe_cols)
        try:
            # START try
            # Import data via PyDomo
            domo_ds_api.data_import(current_dataset_id, dataset_csv)
            log_func(f"SUCCESS: Data import to {dataset_name}.")
        # END try
        except Exception as e:
            # START except Exception as e
            log_func(f"ERROR: Data import failed for {dataset_name}. Exception: {e}")
            # END except Exception as e
        # END if current_dataset_id and dataset_array
            
    log_func("__________ END create_dataset()")
    
    return current_dataset_id
# END def create_dataset