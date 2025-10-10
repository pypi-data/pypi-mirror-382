# objects.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import datetime

# =======================================================================
# ABSTRACT OWNER BASE CLASS
# =======================================================================

@dataclass
class Owner:
    # START class Owner
    """Abstract base class representing an entity (User or Group) that can own an object."""
    id: str
    name: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None) # 'USER' or 'GROUP'
# END class Owner

# =======================================================================
# INSTANCE CONFIGURATION OBJECTS
# =======================================================================

@dataclass
class Instance:
    # START class Instance
    """Represents a single Domo instance configuration record loaded from a control dataset."""
    
    # Core Identification
    Instance_Name: str
    Instance_URL: str
    Developer_Token: str
    
    # Secondary Identification and Attributes
    Developer_Token_User: Optional[str] = field(default=None)
    Instance_Abbreviation: Optional[str] = field(default=None)
    Client_Name: Optional[str] = field(default=None)
    Client_ID: Optional[str] = field(default=None)
    Client_Secret: Optional[str] = field(default=None)
    Environment: Optional[str] = field(default=None)
    Region: Optional[str] = field(default=None)
    Type: Optional[str] = field(default=None)
    Level: Optional[str] = field(default=None)
    Description: Optional[str] = field(default=None)
    Instance_Color: Optional[str] = field(default=None)
    Old_Instance: Optional[str] = field(default=None)

    # Sync and Status Flags
    Sync_Datasets_Owners: Optional[str] = field(default=None)
    Sync_User_Landing_Page: Optional[str] = field(default=None)
    Include_in_User_Activity: Optional[str] = field(default=None)
    Show_In_SSO_Portal: Optional[str] = field(default=None)
    Sync_Default_Roles: Optional[str] = field(default=None)
    Sync_Users: Optional[str] = field(default=None)
    Sync_Default_Groups: Optional[str] = field(default=None)
    
    # Dates and Ordering
    Load_Data_Date: Optional[str] = field(default=None)
    Build_Cards_Date: Optional[str] = field(default=None)
    Go_Live_Date: Optional[str] = field(default=None)
    Order: Optional[int] = field(default=None)
    
    # Login Configuration
    Randstad_Login: Optional[str] = field(default=None)
    Login_Type: Optional[str] = field(default=None)
    Client_Login: Optional[str] = field(default=None)
# END class Instance

# =======================================================================
# DOMO OBJECTS
# =======================================================================

@dataclass
class RoleGrant:
    # START class RoleGrant
    """Represents a single authority (permission) granted to a role."""
    authority: str
    role_ids: List[str] = field(default_factory=list)
    description: Optional[str] = field(default=None)
# END class RoleGrant

@dataclass
class Role:
    # START class Role
    """Represents a Domo Role, including its ID, name, and associated grants."""
    id: str
    name: str
    description: Optional[str] = field(default=None)
    is_default: Optional[bool] = field(default=None)
    # grants should be mapped by authority name for easy lookup
    grants: Dict[str, RoleGrant] = field(default_factory=dict)
# END class Role

@dataclass
class Account(Owner): # Account inherits from Owner
    # START class Account
    """Represents a Domo Integration Account (Data Source Credentials)."""
    # Inherits: id, name, type
    display_name: Optional[str] = field(default=None)
    entity_type: Optional[str] = field(default=None)
    data_provider_type: Optional[str] = field(default=None)
    valid: Optional[bool] = field(default=None)
    last_modified: Optional[str] = field(default=None)
    owners: List[Owner] = field(default_factory=list) # List of Owner objects
    dataset_count: Optional[int] = field(default=None)
# END class Account

@dataclass
class Group(Owner): # Group inherits from Owner
    # START class Group
    """Represents a Domo Group."""
    # Inherits: id, name, type
    group_type: Optional[str] = field(default=None) # e.g., 'open', 'closed', 'dynamic'
    description: Optional[str] = field(default=None)
    owners: List[Owner] = field(default_factory=list) # List of Owner objects
    member_ids: List[str] = field(default_factory=list)
# END class Group

@dataclass
class Dataset:
    # START class Dataset
    """Represents a Domo DataSet."""
    id: str
    name: str
    data_provider_name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    row_count: Optional[int] = field(default=None)
    column_count: Optional[int] = field(default=None)
    owners: List[Owner] = field(default_factory=list) # List of Owner objects
# END class Dataset

@dataclass
class User(Owner): # User inherits from Owner
    # START class User
    """Represents a Domo User."""
    # Inherits: id, name, type
    email_address: str
    user_name: Optional[str] = field(default=None)
    role_id: Optional[str] = field(default=None)
    last_activity: Optional[str] = field(default=None)
    groups: List[str] = field(default_factory=list) # List of group IDs
    attributes: Dict[str, List[str]] = field(default_factory=dict) # Key -> List of values
# END class User