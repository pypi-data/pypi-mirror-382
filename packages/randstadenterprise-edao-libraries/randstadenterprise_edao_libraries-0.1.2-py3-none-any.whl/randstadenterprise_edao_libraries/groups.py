# randstadenterprise_edao_libraries/groups.py
import requests
import logging 
import base64  
from typing import List, Dict, Any, Optional, Callable

from . import helpers # Provides get_http_headers
from . import logs    # Provides log function (for type hinting)
from . import objects # Import all dataclasses

# Define the type for the log function for clean type hinting
LogFunc = Callable[[str], None] 
# Define the type for the GroupMap retrieval function used in save_group_owners
GroupMapGetterFunc = Callable[[str, str, str], Dict[str, objects.Group]] 
# Define the type for the GroupDetails retrieval function
GroupDetailsGetterFunc = Callable[[str, str, str, str], Optional[objects.Group]]

# =======================================================================
# GROUP API RETRIEVAL FUNCTIONS
# =======================================================================

def get_all_instance_groups (
    inst_url: str, inst_dev_token: str, log_func: LogFunc
) -> Optional[Dict[str, objects.Group]]:
# =======================================================================
# FETCHES ALL GROUPS AND MAPS BY LOWERCASE NAME
# =======================================================================
    # START def get_all_instance_groups
    """
    Fetches all groups in an instance and returns them mapped by lowercase group name.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param log_func: Pre-bound logging function for this instance.
    :returns: A dictionary mapping lowercase group names to the objects.Group object, or None on critical failure.
    """
    
    log_func(f'__________ Calling get_all_instance_groups for {inst_url}')
    api_url = f'https://{inst_url}.domo.com/api/content/v2/groups'
    
    inst_groups_map: Dict[str, objects.Group] = {}
    
    try:
        # START try
        # 1. Fetch groups list
        resp = requests.get(api_url, headers=helpers.get_http_headers(inst_dev_token), timeout=30)
        resp.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        groups_json = resp.json()
        
        if isinstance(groups_json, list):
            # START if isinstance(groups_json, list)
            # 2. Map groups by lowercase name
            for group_entry in groups_json:
                # START for group_entry in groups_json
                if isinstance(group_entry, dict) and "name" in group_entry:
                    # START if isinstance(group_entry, dict) and "name" in group_entry
                    group_obj = objects.Group(
                        id=str(group_entry.get('id', '')),
                        name=group_entry.get('name', ''),
                        group_type=group_entry.get('groupType'),
                        description=group_entry.get('description'),
                        owners=[], # Owner/Member lists require separate processing
                        member_ids=[]
                    )
                    # Store group names as lowercase keys for consistent lookup
                    inst_groups_map[str(group_obj.name).lower()] = group_obj
                    # END if isinstance(group_entry, dict) and "name" in group_entry
            # END for group_entry in groups_json
            return inst_groups_map
        else:
            # START else
            log_func(f"WARN (Inst: {inst_url}): Expected list of groups, got {type(groups_json)}.")
            return {} 
            # END else
            
    # END try
    except requests.exceptions.RequestException as e:
        # START except requests.exceptions.RequestException as e
        log_func(f"ERROR (Inst: {inst_url}): RequestException in get_all_instance_groups: {type(e).__name__} - {e}")
        return None
        # END except requests.exceptions.RequestException as e
# END def get_all_instance_groups

def get_group_by_name (inst_url: str, inst_dev_token: str, group_name: str, log_func: LogFunc) -> Optional[objects.Group]:
# =======================================================================
# RETRIEVES A SINGLE GROUP BY NAME
# =======================================================================
    # START def get_group_by_name
    """
    Stubs out functionality to retrieve a single group by its name.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param group_name: The name of the group.
    :param log_func: Pre-bound logging function.
    :returns: The objects.Group object, or None if not found.
    """
    print(f"STUB: Getting group {group_name} from {inst_url}")
    return None
# END def get_group_by_name

# =======================================================================
# GROUP MODIFICATION FUNCTIONS (All Public)
# =======================================================================

def create_group (
    src_group: Dict[str, Any], dest_inst_url: str, dest_inst_devtok: str, log_func: LogFunc
) -> Optional[objects.Group]:
# =======================================================================
# PUBLIC: CREATES A NEW GROUP VIA API
# =======================================================================
    # START def create_group
    """
    Creates a new group in the destination instance.
    
    :param src_group: The source group dictionary providing name, description, and type.
    :param dest_inst_url: URL prefix of the destination instance.
    :param dest_inst_devtok: Developer token for the destination instance.
    :param log_func: Pre-bound logging function.
    :returns: The objects.Group object if successful, None otherwise.
    """
    logging.info(f"API Call: Creating group '{src_group['name']}' in {dest_inst_url}")
    
    body = {
        "name": src_group["name"],
        "description": src_group.get("description", ""),
        "type": src_group.get("groupType", "open") # Default to 'open' if not specified
    }
    api_url = f"https://{dest_inst_url}.domo.com/api/content/v2/groups"
    
    resp = requests.post(api_url, headers=helpers.get_http_headers(dest_inst_devtok), json=body)

    if resp.status_code in [200, 201]:
        # START if resp.status_code in [200, 201]
        logging.info(f"Successfully created group '{src_group['name']}'.")
        raw_group = resp.json()
        
        # Convert raw response to object.Group
        return objects.Group(
            id=str(raw_group.get('id', '')),
            name=raw_group.get('name', ''),
            group_type=raw_group.get('groupType'),
            description=raw_group.get('description'),
        )
    else:
        # START else
        logging.error(f"Failed to create group. Status: {resp.status_code}, Reason: {resp.text}")
        return None
        # END else
        # END if resp.status_code in [200, 201]
# END def create_group

def save_group (inst_url: str, inst_dev_token: str, group_obj: objects.Group, log_func: LogFunc) -> Optional[str]:
# =======================================================================
# SAVES (CREATES OR UPDATES) A GROUP
# =======================================================================
    # START def save_group
    """
    Stubs out functionality to create or update a group.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param group_obj: The objects.Group object (dataclass instance) to be saved.
    :param log_func: Pre-bound logging function.
    :returns: The string ID of the saved group, or None on failure.
    """
    print(f"STUB: Saving group {group_obj.name} to {inst_url}")
    return group_obj.id
# END def save_group

def delete_group (inst_url: str, inst_dev_token: str, group_id: str, log_func: LogFunc) -> bool:
# =======================================================================
# DELETES A GROUP BY ID
# =======================================================================
    # START def delete_group
    """
    Stubs out functionality to delete a group.
    
    :param inst_url: The Domo instance URL prefix.
    :param inst_dev_token: The developer token.
    :param group_id: The string ID of the group to delete.
    :param log_func: Pre-bound logging function.
    :returns: True on success, False on failure.
    """
    print(f"STUB: Deleting group {group_id} from {inst_url}")
    return True
# END def delete_group


def save_group_attributes (
    src_group: Dict[str, Any], dest_inst_url: str, dest_inst_devtok: str, dest_group: Dict[str, Any], 
    log_func: LogFunc
) -> None:
# =======================================================================
# PUBLIC: UPDATES GROUP NAME, DESC, AND DYNAMIC DEFINITION
# =======================================================================
    # START def save_group_attributes
    """
    Updates a group's attributes (name, description, dynamic definition) in the destination instance.
    
    :param src_group: Source group details for attributes.
    :param dest_inst_url: URL prefix of the destination instance.
    :param dest_inst_devtok: Developer token for the destination instance.
    :param dest_group: Current destination group details (needed for 'groupId').
    :param log_func: Pre-bound logging function.
    :returns: None
    """
    logging.info(f"API Call: Saving attributes for group '{dest_group['name']}' in {dest_inst_url}")
    
    # 1. Build the base body for the PUT request
    body = [{
        "groupId": dest_group["groupId"],
        "name": src_group["name"],
        "description": src_group.get("description", ""),
        "type": src_group.get("groupType", "open"),
    }]
    
    # 2. Add dynamic definition only if it exists in the source
    if "permissions" in src_group and src_group.get("groupType") == "dynamic":
        # START if "permissions" in src_group and src_group.get("groupType") == "dynamic"
        permissions = src_group["permissions"].copy()
        # Remove owner data as it's handled separately
        permissions.pop("owners", None)
        permissions.pop("isCurrentUserOwner", None)
        body[0]["dynamicDefinition"] = permissions
        # END if "permissions" in src_group and src_group.get("groupType") == "dynamic"

    api_url = f"https://{dest_inst_url}.domo.com/api/content/v2/groups"
    resp = requests.put(api_url, headers=helpers.get_http_headers(dest_inst_devtok), json=body)

    if resp.status_code not in [200, 201]:
        # START if resp.status_code not in [200, 201]
        logging.error(f"Failed to save group attributes. Status: {resp.status_code}, Reason: {resp.text}")
        # END if resp.status_code not in [200, 201]
# END def save_group_attributes
        

def save_group_owners (
    dest_inst_url: str, dest_inst_devtok: str, dest_group: Dict[str, Any], dest_group_owners_list: List[str],
    get_group_map_func: GroupMapGetterFunc, get_group_details_func: GroupDetailsGetterFunc, 
    dest_inst_name: str, log_func: LogFunc
) -> None:
# =======================================================================
# PUBLIC: ADDS/REMOVES OWNERS TO MATCH DEFINED LIST
# =======================================================================
    # START def save_group_owners
    """
    Ensures the destination group's owners match the hardcoded list 
    by performing ADD and REMOVE operations.
    
    :param dest_inst_url: URL prefix of the destination instance.
    :param dest_inst_devtok: Developer token.
    :param dest_group: Current destination group details.
    :param dest_group_owners_list: The list of desired owner names (strings).
    :param get_group_map_func: Function to retrieve group map (for owner ID lookup).
    :param get_group_details_func: Function to retrieve full group details (for owner refresh).
    :param dest_inst_name: Name of the destination instance.
    :param log_func: Pre-bound logging function.
    :returns: None
    """
    logging.info(f"Configuring owners for group '{dest_group['name']}' to match the defined list.")

    # 1. Get the group map again to find IDs of desired owners
    dest_group_map = get_group_map_func(dest_inst_name, dest_inst_url, dest_inst_devtok)
    current_owners = {owner["displayName"]: owner for owner in dest_group.get("owners", [])}
    logging.debug(f"Current owners are: {list(current_owners.keys())}")

    # Step 1: Determine which owners to ADD.
    add_owners = []
    for owner_name in dest_group_owners_list:
        # START for owner_name in dest_group_owners_list
        if owner_name not in current_owners:
            # START if owner_name not in current_owners
            owner_to_add = dest_group_map.get(owner_name)
            if owner_to_add:
                # START if owner_to_add
                # Assuming the GroupMapGetterFunc returns dicts with 'groupId' or objects.Group objects
                owner_id = owner_to_add.id if isinstance(owner_to_add, objects.Group) else owner_to_add.get('groupId')
                
                # Use the ID from the dest_group_map (assuming it contains groupId)
                add_owners.append({"type": "GROUP", "id": owner_id})
            else:
                # START else
                logging.warning(f"Desired owner group '{owner_name}' does not exist in '{dest_inst_name}' and cannot be added.")
                # END else
            # END if owner_to_add
        # END if owner_name not in current_owners
        # END for owner_name in dest_group_owners_list

    # 2a. Execute ADD API call
    if add_owners:
        # START if add_owners
        logging.info(f"Step 1: Adding {len(add_owners)} new owner(s).")
        api_url = f"https://{dest_inst_url}.domo.com/api/content/v2/groups/access"
        add_body = [{"groupId": dest_group["groupId"], "addOwners": add_owners, "removeOwners": []}]
        add_resp = requests.put(api_url, headers=helpers.get_http_headers(dest_inst_devtok), json=add_body)
        if add_resp.status_code not in [200, 201]:
            # START if add_resp.status_code not in [200, 201]
            logging.error(f"Failed to add owners. Status: {add_resp.status_code}, Reason: {add_resp.text}")
            return # Stop if adding fails.
            # END if add_resp.status_code not in [200, 201]
    else:
        # START else
        logging.info("Step 1: No new owners to add.")
        # END else
    # END if add_owners

    # Step 2: Determine which owners to REMOVE.
    # 2b. Refresh the group details to get the most current owner list
    # The return type of get_group_details_func is assumed to be objects.Group
    refreshed_group = get_group_details_func(dest_inst_name, dest_inst_url, dest_inst_devtok, dest_group["name"])
    if not refreshed_group: return # Safety check
    
    # NOTE: The dest_group dictionary passed to this function must contain the 'owners' field from a previous API call, 
    # not just the dataclass. For now, we rely on the helper functions to retrieve the raw dict.
    
    # We assume 'owners' key in the raw dict structure for simplicity here
    refreshed_owners = {owner["displayName"]: owner for owner in refreshed_group.get("owners", [])}

    # Identify owners currently on the group that are NOT in the desired list
    remove_owners = [
        {"type": owner["type"], "id": owner["id"]}
        for name, owner in refreshed_owners.items()
        if name not in dest_group_owners_list
    ]

    # 3a. Execute REMOVE API call
    if remove_owners:
        # START if remove_owners
        logging.info(f"Step 2: Removing {len(remove_owners)} outdated owner(s).")
        api_url = f"https://{dest_inst_url}.domo.com/api/content/v2/groups/access"
        remove_body = [{"groupId": dest_group["groupId"], "addOwners": [], "removeOwners": remove_owners}]
        remove_resp = requests.put(api_url, headers=helpers.get_http_headers(dest_inst_devtok), json=remove_body)
        if remove_resp.status_code not in [200, 201]:
            # START if remove_resp.status_code not in [200, 201]
            logging.error(f"Failed to remove outdated owners. Status: {remove_resp.status_code}, Reason: {remove_resp.text}")
            # END if remove_resp.status_code not in [200, 201]
    else:
        # START else
        logging.info("Step 2: No outdated owners to remove.")
        # END else
    # END if remove_owners
# END def save_group_owners

def save_group_image (
    src_inst_url: str, src_inst_devtok: str, src_group: Dict[str, Any], 
    dest_inst_url: str, dest_inst_devtok: str, dest_group: Dict[str, Any],
    log_func: LogFunc
) -> None:
# =======================================================================
# PUBLIC: COPIES GROUP AVATAR IMAGE
# =======================================================================
    # START def save_group_image
    """
    Copies the group's avatar/image from the source to the destination 
    instance using base64 encoding.
    
    :param src_inst_url: URL prefix of the source instance.
    :param src_inst_devtok: Developer token for the source instance.
    :param src_group: Source group details (needed for 'groupId').
    :param dest_inst_url: URL prefix of the destination instance.
    :param dest_inst_devtok: Developer token for the destination instance.
    :param dest_group: Destination group details (needed for 'groupId').
    :param log_func: Pre-bound logging function.
    :returns: None
    """
    logging.info(f"API Call: Saving image for group '{dest_group['name']}' in {dest_inst_url}")
    
    # 1. Retrieve the image from the source instance
    src_img_url = f"https://{src_inst_url}.domo.com/api/content/v1/avatar/GROUP/{src_group['groupId']}"
    src_img_resp = requests.get(src_img_url, headers=helpers.get_http_headers(src_inst_devtok))

    if src_img_resp.status_code != 200:
        # START if src_img_resp.status_code != 200
        logging.warning(f"Could not retrieve source group image. Status: {src_img_resp.status_code}")
        return
        # END if src_img_resp.status_code != 200

    # 2. Encode image to base64 data URL
    base64_str = base64.b64encode(src_img_resp.content).decode('utf-8')
    data_url = f"data:image/png;base64,{base64_str}"
    
    # 3. Upload the image to the destination instance
    dest_url = f"https://{dest_inst_url}.domo.com/api/content/v1/avatar/GROUP/{dest_group['groupId']}"
    body = {"encodedImage": data_url}

    dest_img_resp = requests.post(dest_url, json=body, headers=helpers.get_http_headers(dest_inst_devtok))
    if dest_img_resp.status_code not in [200, 201, 204]:
        # START if dest_img_resp.status_code not in [200, 201, 204]
        logging.error(f"Failed to save group image. Status: {dest_img_resp.status_code}, Reason: {dest_img_resp.text}")
        # END if dest_img_resp.status_code not in [200, 201, 204]
# END def save_group_image