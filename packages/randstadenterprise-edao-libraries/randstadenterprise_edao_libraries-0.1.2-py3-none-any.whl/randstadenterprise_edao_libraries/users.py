# randstadenterprise_edao_libraries/users.py
import requests
import threading
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import helpers # Provides get_http_headers
from . import logs    # Provides log function (for type hinting)
from . import roles   # Imports roles functions
from . import objects # Import all dataclasses

# Define the type for the log function
LogFunc = Callable[[str], None] 
# Define the type for the print_response function (passed as an argument)
PrintResponseFunc = Callable[[str, str, requests.Response], None]
# Type for a map of attributes (key -> attribute details)
AttrMap = Dict[str, Dict[str, Any]]

# =======================================================================
# USER RETRIEVAL AND LOOKUP
# =======================================================================

def get_instance_users (
    inst_name: str, inst_url: str, inst_dev_token: str,
    lock: threading.Lock, logs_array: List[List[Any]], print_response: PrintResponseFunc, sync_attrs: Dict[str, Dict[str, Any]]
) -> Dict[str, objects.User]:
# =======================================================================
# RETRIEVES ALL USERS, ENRICHES DATA, AND MAPS BY USER ID
# =======================================================================
    # START def get_instance_users
    """
    Retrieves all instance users, enriches the data with readable fields, 
    and returns a map of the full objects.User object by User ID.
    
    :param inst_name: The display name of the instance (for context).
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :param print_response: Function to print raw API responses.
    :param sync_attrs: Dictionary mapping desired attribute keys to metadata.
    :returns: Dictionary mapping User ID (str) to the objects.User object.
    """
    
    log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock)
    log_func(f'____________________ get_instance_users({inst_url})')
    
    # 1. Get Role Map for lookup using the roles function
    roles_map = roles.get_instance_roles_by_id(inst_name, inst_url, inst_dev_token, lock, logs_array)
    
    # 2. Get raw user data using the private search helper
    inst_users_raw = _get_instance_users_search(
        inst_name, inst_url, inst_dev_token, lock, logs_array, print_response, sync_attrs
    )
    
    users_map: Dict[str, objects.User] = {}

    # 3. Process and enrich each user record
    for u_raw in inst_users_raw:
        # START for u_raw in inst_users_raw
        
        user_id = str(u_raw.get('id', ''))
        
        # Process Custom attributes into Dict[str, List[str]] format
        u_attrs_map: Dict[str, List[str]] = {}
        if "attributes" in u_raw:
            # START if "attributes" in u_raw
            u_attrs = u_raw['attributes']            
            for a in u_attrs:
                # START for a in u_attrs
                key = a.get("key")
                values = a.get("values", [])
                if key: u_attrs_map[key] = values
                # END for a in u_attrs
            # END if "attributes" in u_raw
        
        # Process Groups
        groups_list: List[str] = []
        if "groups" in u_raw:
            # START if "groups" in u_raw
            for g in u_raw['groups']:
                # START for g in u_raw['groups']
                if g.get("name"): groups_list.append(g["name"])
                # END for g in u_raw['groups']
            # END if "groups" in u_raw
        
        # 4. Create the User object
        user_obj = objects.User(
            id=user_id,
            email_address=u_raw.get('emailAddress', ''),
            name=u_raw.get('displayName'), # Owner base class name maps to displayName
            type='USER',
            user_name=u_raw.get('userName'),
            role_id=str(u_raw.get('roleId')),
            last_activity=u_raw.get('lastActivity'),
            groups=groups_list,
            attributes=u_attrs_map
        )
        
        # 5. Add to the return map
        users_map[user_id] = user_obj
        
        # END for u_raw in inst_users_raw
    
    log_func(f'____________________ END get_instance_users()')
 
    return users_map
# END def get_instance_users

def get_user_by_email (inst_url: str, inst_dev_token: str, user_email: str, log_func: LogFunc) -> Optional[objects.User]:
# =======================================================================
# RETRIEVES A SINGLE USER BY EMAIL ADDRESS
# =======================================================================
    # START def get_user_by_email
    """
    Stubs out functionality to retrieve a single user by their email address.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param user_email: The email address of the user.
    :param log_func: Pre-bound logging function.
    :returns: The objects.User object, or None if not found.
    """
    print(f"STUB: Getting user {user_email} from {inst_url}")
    return None
# END def get_user_by_email

def get_user_by_id (inst_url: str, inst_dev_token: str, user_id: str, log_func: LogFunc) -> Optional[objects.User]:
# =======================================================================
# RETRIEVES A SINGLE USER BY ID
# =======================================================================
    # START def get_user_by_id
    """
    Stubs out functionality to retrieve a single user by their ID.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param user_id: The string ID of the user.
    :param log_func: Pre-bound logging function.
    :returns: The objects.User object, or None if not found.
    """
    print(f"STUB: Getting user by ID {user_id} from {inst_url}")
    return None
# END def get_user_by_id

# =======================================================================
# USER ATTRIBUTES RETRIEVAL
# =======================================================================

def get_all_instance_user_attributes (
    inst_url: str, inst_dev_token: str, lock: threading.Lock, logs_array: List[List[Any]]
) -> AttrMap:
# =======================================================================
# FETCHES ALL USER ATTRIBUTES AND MAPS THEM BY KEY
# =======================================================================
    # START def get_all_instance_user_attributes
    """
    Fetches all instance user attributes and returns them mapped by attribute key.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :returns: Dictionary mapping attribute key (str) to attribute details.
    """
    
    log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock)
    log_func(f'____________________ get_all_instance_user_attributes({inst_url})')
    
    inst_attrs_map = {}
    
    # 1. Call the private API function to get raw attributes
    inst_attrs = _get_instance_attributes(inst_url, inst_dev_token, lock, logs_array)
    
    # 2. Map attributes by their full key
    for a in inst_attrs:
        # START for a in inst_attrs
        full_key = a['key']
        inst_attrs_map[full_key] = a
        # END for a in inst_attrs
    
    log_func('____________________ END get_all_instance_user_attributes()')

    return inst_attrs_map
# END def get_all_instance_user_attributes

def get_user_attribute_by_name (inst_url: str, inst_dev_token: str, attribute_name: str, log_func: LogFunc) -> Optional[Dict[str, Any]]:
# =======================================================================
# RETRIEVES A SINGLE USER ATTRIBUTE BY NAME
# =======================================================================
    # START def get_user_attribute_by_name
    """
    Stubs out functionality to retrieve a single user attribute by its display name.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param attribute_name: The display name of the attribute.
    :param log_func: Pre-bound logging function.
    :returns: The attribute dictionary, or None if not found.
    """
    print(f"STUB: Getting user attribute {attribute_name} from {inst_url}")
    return None
# END def get_user_attribute_by_name

def get_user_attribute_by_id (inst_url: str, inst_dev_token: str, attribute_id: str, log_func: LogFunc) -> Optional[Dict[str, Any]]:
# =======================================================================
# RETRIEVES A SINGLE USER ATTRIBUTE BY ID
# =======================================================================
    # START def get_user_attribute_by_id
    """
    Stubs out functionality to retrieve a single user attribute by its ID.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param attribute_id: The string ID of the attribute.
    :param log_func: Pre-bound logging function.
    :returns: The attribute dictionary, or None if not found.
    """
    print(f"STUB: Getting user attribute by ID {attribute_id} from {inst_url}")
    return None
# END def get_user_attribute_by_id


# =======================================================================
# USER MODIFICATION FUNCTIONS
# =======================================================================

def save_user (inst_url: str, inst_dev_token: str, user_obj: objects.User, log_func: LogFunc) -> Optional[str]:
# =======================================================================
# SAVES (CREATES OR UPDATES) A USER
# =======================================================================
    # START def save_user
    """
    Stubs out functionality to create or update a user.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param user_obj: The objects.User object (dataclass instance) to be saved.
    :param log_func: Pre-bound logging function.
    :returns: The string ID of the saved user, or None on failure.
    """
    print(f"STUB: Saving user {user_obj.email_address} to {inst_url}")
    return user_obj.id
# END def save_user

def save_user_attribute (inst_url: str, inst_dev_token: str, attribute_obj: Dict[str, Any], log_func: LogFunc) -> Optional[str]:
# =======================================================================
# SAVES (CREATES OR UPDATES) A USER ATTRIBUTE
# =======================================================================
    # START def save_user_attribute
    """
    Stubs out functionality to create or update a user attribute.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param attribute_obj: The Attribute object (dictionary) to be saved.
    :param log_func: Pre-bound logging function.
    :returns: The key (string) of the saved attribute, or None on failure.
    """
    print(f"STUB: Saving user attribute {attribute_obj.get('key')} to {inst_url}")
    return attribute_obj.get('key')
# END def save_user_attribute

def delete_user (inst_url: str, inst_dev_token: str, user_id: str, log_func: LogFunc) -> bool:
# =======================================================================
# DELETES A USER BY ID
# =======================================================================
    # START def delete_user
    """
    Stubs out functionality to delete a user.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param user_id: The string ID of the user to delete.
    :param log_func: Pre-bound logging function.
    :returns: True on success, False on failure.
    """
    print(f"STUB: Deleting user {user_id} from {inst_url}")
    return True
# END def delete_user


# =======================================================================
# PRIVATE API RETRIEVAL FUNCTIONS
# =======================================================================

def _get_user_email_map (
    user_id_map: Dict[str, objects.User], lock: threading.Lock, logs_array: List[List[Any]]
) -> Dict[str, objects.User]:
# =======================================================================
# PRIVATE: REMAPS USER DICTIONARIES KEYED BY EMAIL ADDRESS
# =======================================================================
    # START def _get_user_email_map
    """
    (PRIVATE) Takes a map of users keyed by ID and remaps them keyed by emailAddress.
    
    :param user_id_map: Dictionary of objects.User objects keyed by User ID.
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :returns: Dictionary mapping email address (str) to the objects.User object.
    """
    
    log_func = lambda msg: logs.log("N/A", msg, logs_array, lock) # Instance URL is not available here
    log_func('_______________ _get_user_email_map()')
    
    user_email_map: Dict[str, objects.User] = {}
    for user_id, user_details in user_id_map.items():
        # START for user_id, user_details in user_id_map.items()
        user_email_map[user_details.email_address] = user_details
        # END for user_id, user_details in user_id_map.items()

    log_func('_______________ END _get_user_email_map()')

    return user_email_map
# END def _get_user_email_map


def _get_instance_attributes (
    inst_url: str, inst_dev_token: str, lock: threading.Lock, logs_array: List[List[Any]]
) -> List[Dict[str, Any]]:
# =======================================================================
# PRIVATE: RETRIEVES A LIST OF RAW USER ATTRIBUTE METADATA KEYS
# =======================================================================
    # START def _get_instance_attributes
    """
    (PRIVATE) Retrieves a list of all raw user attribute metadata keys (properties) from a Domo instance.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :returns: A list of raw attribute metadata dictionaries.
    """
    
    log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock)
    log_func(f'_________________________ _get_instance_attributes({inst_url})')

    api_url = f'https://{inst_url}.domo.com/api/user/v1/properties/meta/keys?issuerTypes=idp,domo-defined,customer-defined'
    headers = helpers.get_http_headers(inst_dev_token)
    
    try:
        # START try
        # 1. Make API request
        attrs_res = requests.get(api_url, headers=headers)
        attrs_res.raise_for_status()
        inst_attrs = attrs_res.json()
        
        return inst_attrs
    # END try
    except requests.exceptions.RequestException as e:
        # START except requests.exceptions.RequestException as e
        log_func(f"ERROR fetching instance attributes: {e}")
        return []
        # END except requests.exceptions.RequestException as e
    
    log_func('_________________________ END _get_instance_attributes()')
# END def _get_instance_attributes


def _get_instance_users_search (
    inst_name: str, inst_url: str, inst_dev_token: str,
    lock: threading.Lock, logs_array: List[List[Any]], 
    print_response: PrintResponseFunc, sync_attrs: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
# =======================================================================
# PRIVATE: RETRIEVES ALL USERS VIA PAGINATED SEARCH API
# =======================================================================
    # START def _get_instance_users_search
    """
    (PRIVATE) Searches and retrieves all users from an instance, including custom attributes 
    from the provided SYNC_ATTRS map.
    
    :param inst_name: The display name of the instance (for context).
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :param print_response: Function to print raw API responses.
    :param sync_attrs: Dictionary mapping desired attribute keys to metadata.
    :returns: A list of raw user dictionaries.
    """
    
    log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock)
    log_func(f'_________________________ _get_instance_users_search({inst_url})')

    # --- Step 1: Determine attributes to request ---
    # Call the PUBLIC attribute getter
    inst_attrs_map = get_all_instance_user_attributes(inst_url, inst_dev_token, lock, logs_array)
    
    attrs = []
    # Build the list of attributes that exist in the instance or are Domo-defined defaults
    for attr_key, attr_details in sync_attrs.items():
        # START for attr_key, attr_details in sync_attrs.items()
        if attr_key in inst_attrs_map or attr_details.get("keyspace") == "domo-defined":
            # START if attr_key in inst_attrs_map or attr_details.get("keyspace") == "domo-defined"
            attrs.append(attr_key)
            # END if attr_key in inst_attrs_map or attr_details.get("keyspace") == "domo-defined"
        # END for attr_key, attr_details in sync_attrs.items()

    # --- Step 2: Paginate through users ---
    api_url = f'https://{inst_url}.domo.com/api/identity/v1/users/search'
    
    inst_user = []
    total = 100000
    offset = 0
    limit = 100
    
    while offset < total:
        # START while offset < total
        
        # Define the search body for the current page
        body = {
            "showCount": "true",
            "count": "false",
            "includeDeleted": "false",
            "includeSupport": "false",
            "limit": limit,
            "offset": offset,
            "sort": {
                "field": "displayName",
                "order": "ASC"
            },
            "filters": [],
            "attributes": attrs,
            "parts": ["GROUPS"]
        }
        # END body definition

        try:
            # START try
            users_res = requests.post(api_url, headers=helpers.get_http_headers(inst_dev_token), json=body)
            users_res.raise_for_status() 
            res_json = users_res.json()
            
            print_response(inst_url, "____________ GET USERS RESP ", users_res)
            
            # Update total count based on API response
            count = res_json.get("count", 0)
            total = count
            page_users = res_json.get("users", [])
            
            # Append users and increment offset
            inst_user.extend(page_users)
            offset = offset + limit
            
        # END try
        except requests.exceptions.RequestException as e:
            # START except requests.exceptions.RequestException as e
            log_func(f"ERROR fetching users page (offset {offset}): {e}")
            break
            # END except requests.exceptions.RequestException as e
    # END while offset < total
    
    log_func(f'_________________________ END _get_instance_users_search()')

    return inst_user
# END def _get_instance_users_search