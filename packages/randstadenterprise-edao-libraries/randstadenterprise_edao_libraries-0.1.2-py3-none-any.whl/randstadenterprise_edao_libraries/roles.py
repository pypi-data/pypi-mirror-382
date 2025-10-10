# randstadenterprise_edao_libraries/roles.py
import requests
import threading
from typing import List, Dict, Any, Optional, Callable

from . import helpers # Provides get_http_headers
from . import logs    # Provides log function (for type hinting)
from . import objects # Import all dataclasses

# Define the type for the log function
LogFunc = Callable[[str], None] 

# =======================================================================
# ROLE GRANTS (AUTHORITIES) RETRIEVAL
# =======================================================================

def get_instance_role_grants (
    inst_url: str, inst_dev_token: str, log_func: LogFunc
) -> Dict[str, objects.RoleGrant]:
# =======================================================================
# FETCHES ALL AUTHORITIES AND MAPS THEM TO ROLE IDS
# =======================================================================
    # START def get_instance_role_grants
    """
    Fetches all authorities (role grants) in an instance and maps them to their respective Role IDs.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param log_func: Pre-bound logging function.
    :returns: Dictionary mapping Role ID (str) to the objects.RoleGrant object.
    """

    log_func(f'_______________ get_instance_role_grants({inst_url})')

    api_url = f'https://{inst_url}.domo.com/api/authorization/v1/authorities'
    headers = helpers.get_http_headers(inst_dev_token)
    
    role_grants_map: Dict[str, objects.RoleGrant] = {}
    
    try:
        # START try
        # 1. Fetch all authorities
        role_grants_res = requests.get(api_url, headers=headers)
        role_grants_res.raise_for_status()
        instance_role_grants = role_grants_res.json()
        
        # 2. Iterate through authorities and map to all associated Role IDs
        for rg in instance_role_grants:
            # START for rg in instance_role_grants
            role_ids = [str(r_id) for r_id in rg.get('roleIds', [])]
            authority_name = rg['authority']
            
            # Create a RoleGrant object
            role_grant_obj = objects.RoleGrant(
                authority=authority_name,
                role_ids=role_ids,
                description=rg.get('description')
            )
            
            # Map the RoleGrant object by its authority name (key)
            role_grants_map[authority_name] = role_grant_obj
            # END for rg in instance_role_grants
        
    # END try
    except requests.exceptions.RequestException as e:
        # START except requests.exceptions.RequestException as e
        log_func(f"ERROR fetching role grants: {type(e).__name__} - {e}")
        return {} 
        # END except requests.exceptions.RequestException as e

    log_func('_______________ END get_instance_role_grants()')
    return role_grants_map
    
# END def get_instance_role_grants

# =======================================================================
# PRIVATE ROLE RETRIEVAL (CORE API CALL)
# =======================================================================

def _get_instance_roles (
    inst_url: str, inst_dev_token: str, log_func: LogFunc
) -> List[objects.Role]:
# =======================================================================
# PRIVATE: FETCHES ALL ROLES AND ENRICHES THEM WITH GRANTS
# =======================================================================
    # START def _get_instance_roles
    """
    (PRIVATE) Fetches all roles, then enriches each role object with its corresponding authorities (role grants).
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param log_func: Pre-bound logging function.
    :returns: A list of objects.Role objects.
    """

    log_func(f'_______________ _get_instance_roles({inst_url})')

    api_url = f'https://{inst_url}.domo.com/api/authorization/v1/roles'
    headers = helpers.get_http_headers(inst_dev_token)

    try:
        # START try (Roles API Call)
        # 1. Fetch all roles
        roles_res = requests.get(api_url, headers=headers)
        roles_res.raise_for_status() 
        inst_roles_raw = roles_res.json()
    # END try (Roles API Call)
    except requests.exceptions.RequestException as e:
        # START except requests.exceptions.RequestException as e
        log_func(f"ERROR fetching roles: {type(e).__name__} - {e}")
        return []
        # END except requests.exceptions.RequestException as e

    # --- Enrich Roles with Grants ---
    # 2. Get the role grants map (mapped by authority name: 'EDIT_DASHBOARD')
    role_grants_map_by_authority = get_instance_role_grants(inst_url, inst_dev_token, log_func)
    
    # 3. Join roles with their grants and convert to Role objects
    inst_roles: List[objects.Role] = []
    
    for r_raw in inst_roles_raw:
        # START for r_raw in inst_roles_raw
        r_id = str(r_raw['id'])
        r_grants: Dict[str, objects.RoleGrant] = {}
        
        # Build the grants map for this specific role
        for auth_name, grant_obj in role_grants_map_by_authority.items():
            # START for auth_name, grant_obj in role_grants_map_by_authority.items()
            if r_id in grant_obj.role_ids:
                # START if r_id in grant_obj.role_ids
                r_grants[auth_name] = grant_obj
                # END if r_id in grant_obj.role_ids
            # END for auth_name, grant_obj in role_grants_map_by_authority.items()
            
        # Create the Role object
        role_obj = objects.Role(
            id=r_id,
            name=r_raw.get('name', ''),
            description=r_raw.get('description'),
            is_default=r_raw.get('isDefault'),
            grants=r_grants
        )
        inst_roles.append(role_obj)
        # END for r_raw in inst_roles_raw

    log_func('_______________ END _get_instance_roles()')
    return inst_roles
    
# END def _get_instance_roles

# =======================================================================
# MAPPING FUNCTIONS (Public)
# =======================================================================

def get_instance_roles (
    inst_name: str, inst_url: str, inst_dev_token: str, 
    lock: threading.Lock, logs_array: List[List[Any]]
) -> Dict[str, objects.Role]:
# =======================================================================
# RETRIEVES ALL ROLES AND MAPS THEM BY ROLE NAME
# =======================================================================
    # START def get_instance_roles
    """
    Fetches all roles and maps them by Role Name.
    
    :param inst_name: The instance name (for logging context).
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :returns: Dictionary mapping Role Name (str) to the objects.Role object.
    """

    log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock)
    log_func(f'_______________ get_instance_roles({inst_name}, {inst_url})')

    # 1. Get the enriched list of roles using the private helper
    inst_roles = _get_instance_roles(inst_url, inst_dev_token, log_func)
    
    # 2. Map roles by name
    roles_map = {r.name: r for r in inst_roles if r.name}

    log_func('_______________ END get_instance_roles()')
    return roles_map
        
# END def get_instance_roles


def get_role_by_name (inst_url: str, inst_dev_token: str, role_name: str, log_func: LogFunc) -> Optional[objects.Role]:
# =======================================================================
# RETRIEVES A SINGLE ROLE BY NAME
# =======================================================================
    # START def get_role_by_name
    """
    Stubs out functionality to retrieve a single role by its name.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param role_name: The name of the role.
    :param log_func: Pre-bound logging function.
    :returns: The objects.Role object, or None if not found.
    """
    print(f"STUB: Getting role {role_name} from {inst_url}")
    return None
# END def get_role_by_name

def get_role_by_id (inst_url: str, inst_dev_token: str, role_id: str, log_func: LogFunc) -> Optional[objects.Role]:
# =======================================================================
# RETRIEVES A SINGLE ROLE BY ID
# =======================================================================
    # START def get_role_by_id
    """
    Stubs out functionality to retrieve a single role by its ID.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param role_id: The string ID of the role.
    :param log_func: Pre-bound logging function.
    :returns: The objects.Role object, or None if not found.
    """
    print(f"STUB: Getting role by ID {role_id} from {inst_url}")
    return None
# END def get_role_by_id


def get_instance_roles_by_id (
    inst_name: str, inst_url: str, inst_dev_token: str, 
    lock: threading.Lock, logs_array: List[List[Any]]
) -> Dict[str, objects.Role]:
# =======================================================================
# RETRIEVES ALL ROLES AND MAPS THEM BY ROLE ID
# =======================================================================
    # START def get_instance_roles_by_id
    """
    Fetches all roles and maps them by Role ID (string).
    
    :param inst_name: The instance name (for logging context).
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param lock: The threading.Lock object (for logging).
    :param logs_array: The shared log array.
    :returns: Dictionary mapping Role ID (str) to the objects.Role object.
    """

    log_func = lambda msg: logs.log(inst_url, msg, logs_array, lock)
    log_func(f'_______________ get_instance_roles_by_id({inst_name}, {inst_url})')

    # 1. Get the enriched list of roles using the private helper
    inst_roles = _get_instance_roles(inst_url, inst_dev_token, log_func)
    
    # 2. Map roles by ID (must be converted to string key)
    roles_map = {r.id: r for r in inst_roles if r.id}

    log_func('_______________ END get_instance_roles_by_id()')
    return roles_map
        
# END def get_instance_roles_by_id

def save_role (inst_url: str, inst_dev_token: str, role_obj: objects.Role, log_func: LogFunc) -> Optional[str]:
# =======================================================================
# SAVES (CREATES OR UPDATES) A ROLE
# =======================================================================
    # START def save_role
    """
    Stubs out functionality to create or update a role.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param role_obj: The objects.Role object (dataclass instance) to be saved.
    :param log_func: Pre-bound logging function.
    :returns: The string ID of the saved role, or None on failure.
    """
    print(f"STUB: Saving role {role_obj.name} to {inst_url}")
    return role_obj.id
# END def save_role

def delete_role (inst_url: str, inst_dev_token: str, role_id: str, log_func: LogFunc) -> bool:
# =======================================================================
# DELETES A ROLE BY ID
# =======================================================================
    # START def delete_role
    """
    Stubs out functionality to delete a role.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param role_id: The string ID of the role to delete.
    :param log_func: Pre-bound logging function.
    :returns: True on success, False on failure.
    """
    print(f"STUB: Deleting role {role_id} from {inst_url}")
    return True
# END def delete_role