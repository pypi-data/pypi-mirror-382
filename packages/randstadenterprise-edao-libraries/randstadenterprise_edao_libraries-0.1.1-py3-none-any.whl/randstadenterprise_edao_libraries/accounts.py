# randstadenterprise_edao_libraries/accounts.py
import requests
import threading
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from . import helpers # Provides get_http_headers
from . import logs # Provides log function (for type hinting)
from . import objects # Import all dataclasses

# Define custom types needed for function signatures
LogFunc = Callable[[str], None]

# =======================================================================
# CORE API RETRIEVAL FUNCTIONS
# =======================================================================

def get_all_instance_accounts (
    inst_name: str, inst_url: str, inst_dev_token: str,
    log_func: LogFunc
) -> Dict[str, objects.Account]:
# =======================================================================
# RETRIEVES, PROCESSES, AND MAPS ALL INTEGRATION ACCOUNTS
# =======================================================================
    # START def get_all_instance_accounts
    """
    Retrieves all integration accounts for an instance, processes them into 
    Account objects, and returns a map keyed by account ID.
    
    :param inst_name: The display name of the instance.
    :param inst_url: The URL prefix of the instance.
    :param inst_dev_token: The developer token for API access.
    :param log_func: Pre-bound logging function for this instance.
    :returns: Dictionary mapping Account ID (str) to the processed objects.Account object.
    """
    
    log_func(f'_______________ get_all_instance_accounts({inst_name}, {inst_url})')

    # 1. Fetch all paginated account data using the private helper
    all_inst_accts = _get_accounts_pages(
        inst_name, inst_url, inst_dev_token, log_func
    )
    
    all_inst_accts_map: Dict[str, objects.Account] = {}
    
    # 2. Iterate through accounts and process into structured records
    for inst_acct in all_inst_accts:
        # START for inst_acct in all_inst_accts
        
        account_id = str(inst_acct.get("databaseId"))
        
        # 3. Process owners into Owner objects
        owners_list: List[objects.Owner] = []
        owners = inst_acct.get("owners", [])
        
        for owner in owners:
            # START for owner in owners
            # Create a generic Owner object
            owners_list.append(objects.Owner(
                id=str(owner.get("id", "")),
                name=owner.get("displayName", ""),
                type=owner.get("type", "")
            ))
            # END for owner in owners
        
        # 4. Create the final Account object
        processed_account = objects.Account(
            id=account_id,
            name=inst_acct.get("name", ""),
            type=inst_acct.get("entityType", ""), # The Account object inherits 'type' from Owner
            display_name=inst_acct.get("displayName", ""),
            entity_type=inst_acct.get("entityType", ""),
            data_provider_type=inst_acct.get("dataProviderType", ""),
            valid=inst_acct.get("valid", ""),
            last_modified=inst_acct.get("lastModified", ""),
            owners=owners_list, 
            dataset_count=inst_acct.get("datasetCount"),
        )
        
        # 5. Add to the return map
        if account_id:
            # START if account_id
            all_inst_accts_map[account_id] = processed_account            
            # END if account_id

    # END for inst_acct in all_inst_accts
    
    log_func('_______________ END get_all_instance_accounts()')
    return all_inst_accts_map
# END def get_all_instance_accounts

def get_account_by_id (inst_name: str, inst_url: str, inst_dev_token: str, account_id: str, log_func: LogFunc) -> Optional[objects.Account]:
# =======================================================================
# RETRIEVES A SINGLE ACCOUNT BY ID
# =======================================================================
    # START def get_account_by_id
    """
    Stubs out functionality to retrieve a single integration account by its ID.
    
    :param inst_name: The display name of the instance.
    :param inst_url: The URL prefix of the instance.
    :param inst_dev_token: The developer token for API access.
    :param account_id: The string ID of the account.
    :param log_func: Pre-bound logging function.
    :returns: The objects.Account object, or None if not found.
    """
    print(f"STUB: Getting account {account_id} from {inst_url}")
    return None
# END def get_account_by_id

def save_account (inst_name: str, inst_url: str, inst_dev_token: str, account_obj: objects.Account, log_func: LogFunc) -> Optional[str]:
# =======================================================================
# CREATES OR UPDATES AN INTEGRATION ACCOUNT
# =======================================================================
    # START def save_account
    """
    Stubs out functionality to create or update an integration account.
    
    :param inst_name: The display name of the instance.
    :param inst_url: The URL prefix of the instance.
    :param inst_dev_token: The developer token for API access.
    :param account_obj: The objects.Account object (dataclass instance) to be saved.
    :param log_func: Pre-bound logging function.
    :returns: The string ID of the saved account, or None on failure.
    """
    print(f"STUB: Saving account {account_obj.name} to {inst_url}")
    return account_obj.id
# END def save_account

def delete_account (inst_name: str, inst_url: str, inst_dev_token: str, account_id: str, log_func: LogFunc) -> bool:
# =======================================================================
# DELETES AN INTEGRATION ACCOUNT BY ID
# =======================================================================
    # START def delete_account
    """
    Stubs out functionality to delete an integration account.
    
    :param inst_name: The display name of the instance.
    :param inst_url: The URL prefix of the instance.
    :param inst_dev_token: The developer token for API access.
    :param account_id: The string ID of the account to delete.
    :param log_func: Pre-bound logging function.
    :returns: True on success, False on failure.
    """
    print(f"STUB: Deleting account {account_id} from {inst_url}")
    return True
# END def delete_account

# =======================================================================
# PRIVATE PAGINATION HELPERS
# =======================================================================

def _get_accounts_pages (
    inst_name: str, inst_url: str, inst_dev_tok: str, log_func: LogFunc
) -> List[Dict[str, Any]]:
# =======================================================================
# PRIVATE: PAGINATES AND RETRIEVES ALL INTEGRATION ACCOUNTS
# =======================================================================
    # START def _get_accounts_pages
    """
    (PRIVATE) Handles pagination logic to retrieve all integration accounts from an instance
    using the search API.
    
    :param inst_name: The display name of the instance (for context).
    :param inst_url: The URL prefix of the instance.
    :param inst_dev_tok: The developer token.
    :param log_func: Pre-bound logging function.
    :returns: A list of all raw integration account dictionaries.
    """
    
    log_func(f"__________ _get_accounts_pages: {str(inst_url)}")        
    
    accounts_array: List[Dict[str, Any]] = []
    
    page_size = 100
    offset = 0
    total_accounts = 0
    # Initialize high to ensure loop runs at least once
    total_count = page_size + page_size 

    while total_accounts < total_count:
        # START while total_accounts < total_count

        log_func(f"_______________ page_size: {str(page_size)} | offset: {str(offset)}")        
        
        # 1. Call the page search API helper
        accounts_page_result = _get_accounts_page_search(
            inst_name, inst_url, inst_dev_tok, page_size, offset, log_func
        )

        if accounts_page_result is not None:
            # START if accounts_page_result is not None
            
            search_objects = accounts_page_result.get("searchObjects", [])
            # Update the total expected count from the API response
            total_count = accounts_page_result.get("totalResultCount", total_count)
            
            log_func(f"____________________ total_count: {str(total_count)}")        
            accounts_array.extend(search_objects)

            current_page_size = len(search_objects)
            total_accounts += current_page_size
            offset = offset + page_size
            
            # Safety break if an empty page is returned unexpectedly
            if current_page_size == 0 and total_accounts < total_count:
                # START if current_page_size == 0 and total_accounts < total_count
                log_func("WARN: Empty page returned, but total count not reached. Breaking loop.")
                break
                # END if current_page_size == 0 and total_accounts < total_count
        else:
            # START else
            log_func(f"__________ NO INTEGRATION ACCOUNTS FOUND {str(inst_url)} | page_size: {str(page_size)} | offset: {str(offset)}")
            break
            # END else
        # END if accounts_page_result is not None

    # END while total_accounts < total_count

    log_func(f"__________ END _get_accounts_pages: {str(inst_url)}")
    
    return accounts_array
# END def _get_accounts_pages    
                                    
def _get_accounts_page_search (
    inst_name: str, inst_url: str, inst_dev_token: str, page_size: int, offset: int, log_func: LogFunc
) -> Optional[Dict[str, Any]]:
# =======================================================================
# PRIVATE: CALLS THE INTEGRATION ACCOUNTS SEARCH API FOR A SINGLE PAGE
# =======================================================================
    # START def _get_accounts_page_search
    """
    (PRIVATE) Executes the Domo search API query for integration accounts on a single page.
    
    :param inst_name: The display name of the instance (for context).
    :param inst_url: The URL prefix of the instance.
    :param inst_dev_token: The developer token.
    :param page_size: The requested number of results.
    :param offset: The starting offset for the search.
    :param log_func: Pre-bound logging function.
    :returns: The raw JSON response dictionary, or None on API failure.
    """

    log_func(f'_______________ _get_accounts_page_search({inst_name}, {inst_url}, ..., {str(page_size)}, {str(offset)})')
         
    api_url = f'https://{inst_url}.domo.com/api/search/v1/query'
    
    # 1. Define the request body for the search API
    body = {
                "count": page_size,
                "offset": offset,
                "combineResults": "true",
                "query": "**",
                "filters": [],
                "facetValuesToInclude": [
                    "DATAPROVIDERNAME",
                    "OWNED_BY_ID",
                    "VALID",
                    "USED",
                    "LAST_MODIFIED_DATE"
                ],
                "queryProfile": "GLOBAL",
                "entityList": [
                    [
                        "account"
                    ]
                ],
                "sort": {
                    "fieldSorts": [
                        {
                            "field": "display_name_sort",
                            "sortOrder": "ASC"
                        }
                    ]
                }
            }

    # 2. Use the helpers function to get headers and make the API call
    headers = helpers.get_http_headers(inst_dev_token)
    resp = requests.post(api_url, headers=headers, json=body)

    results = None
    
    if resp.status_code == 200:
        # START if resp.status_code == 200
        # Success: Return the raw JSON result
        results = resp.json()
    else:
        # START else
        # Failure: Log the error details
        log_func(f"_______________ _get_accounts_page_search response error {str(resp.status_code)}: {resp.text}")   
        # END else
    # END if resp.status_code == 200
    
    log_func('_______________ END _get_accounts_page_search()')

    return results
# END def _get_accounts_page_search