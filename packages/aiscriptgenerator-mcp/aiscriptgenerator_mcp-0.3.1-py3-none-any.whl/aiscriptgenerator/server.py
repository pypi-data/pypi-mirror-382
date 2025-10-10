#!/usr/bin/env python3
"""
MCP Server for AL Parser - finds pages and fields for Business Central scenarios
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP
from .alparser import build_cache, needs_rebuild, ALCache
from .extract_al import ALExtractor
import os
import shutil
import subprocess
from pathlib import Path

@dataclass
class PageInfo:
    name: str
    page_id: Optional[int]
    app_name: Optional[str]
    caption: Optional[str]
    source_table: Optional[str]
    file_path: str

# Initialize FastMCP Server
mcp = FastMCP("AL Parser Server")

# Configuration paths - supports shared folder via environment variable
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

AZURE_DEVOPS_REPO_URL = "https://schouw.visualstudio.com/Foodware%20365%20BC/_git/PageScripting"
AZURE_DEVOPS_BRANCH = "feature/MCPALFiles"
# Removed PAT support - using Azure CLI authentication only

# Local paths in package directory
AL_FILES_PATH = os.path.join(str(Path.home()), "Downloads", "al_files")
YAML_TEMPLATES_PATH = os.path.join(PACKAGE_DIR, "..", "..")

def check_git_available() -> bool:
    """Check if Git is available on the system"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=10, shell=True)
        return result.returncode == 0
    except Exception:
        return False

def construct_git_url_with_auth(repo_url: str, pat: str = '') -> str:
    """Construct Git URL with authentication if PAT is provided"""
    if not pat:
        return repo_url
    
    # Handle Azure DevOps URLs
    if 'dev.azure.com' in repo_url:
        return repo_url.replace('https://', f'https://{pat}@')
    elif 'visualstudio.com' in repo_url:
        # Handle legacy Azure DevOps URLs
        return repo_url.replace('https://', f'https://{pat}@')
    else:
        # Generic Git URL with PAT
        return repo_url.replace('https://', f'https://{pat}@')

# def clone_azure_devops_repo(repo_url: str, branch: str, destination_path: str, pat: str = '') -> bool:
#     """Clone Azure DevOps repository to destination path"""
#     try:
#         # Check if Git is available
#         if not check_git_available():
#             print("Git is not available on the system. Please install Git.")
#             return False

#         # Remove existing directory if it exists
#         if os.path.exists(destination_path):
#             print(f"Removing existing directory: {destination_path}")
#             shutil.rmtree(destination_path)

#         # Create parent directory if it doesn't exist
#         os.makedirs(os.path.dirname(destination_path), exist_ok=True)

#         print(f"Cloning Azure DevOps repository to {destination_path}...")
#         print(f"Repository: {repo_url}")
#         print(f"Branch: {branch}")

#         # Construct authenticated URL if PAT is provided
#         clone_url = construct_git_url_with_auth(repo_url, pat)

#         # Clone the repository
#         cmd = ['git', 'clone', '--branch', branch, '--single-branch', clone_url, destination_path]
        
#         # Hide the URL in output for security
#         display_cmd = ['git', 'clone', '--branch', branch, '--single-branch', repo_url, destination_path]
#         print(f"Running: {' '.join(display_cmd)}")

#         result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
#         if result.returncode == 0:
#             print("Repository cloned successfully!")
            
#             # Check if we got AL files
#             al_files_count = 0
#             for root, dirs, files in os.walk(destination_path):
#                 for file in files:
#                     if file.lower().endswith('.al'):
#                         al_files_count += 1
            
#             print(f"Found {al_files_count} AL files in the repository")
#             return al_files_count > 0
#         else:
#             print(f"Git clone failed with error: {result.stderr}")
#             return False

#     except subprocess.TimeoutExpired:
#         print("Git clone operation timed out (5 minutes)")
#         return False
#     except Exception as e:
#         print(f"Error cloning repository: {str(e)}")
#         return False

def check_az_login() -> tuple[bool, str]:
    """Check if user is logged in via Azure CLI and get access token"""
    try:
        # Check if Azure CLI is available
        result = subprocess.run(['az', '--version'], capture_output=True, text=True, timeout=10, shell=True)
        if result.returncode != 0:
            return False, "Azure CLI not installed. Please install: winget install Microsoft.AzureCLI"
        
        # Check if user is logged in
        result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True, timeout=30, shell=True)
        if result.returncode != 0:
            # Check if we should attempt auto-login (via environment variable)
            auto_login = os.environ.get('MCP_AUTO_LOGIN', '').lower() in ('true', '1', 'yes')
            print(f"🔧 MCP_AUTO_LOGIN setting: {os.environ.get('MCP_AUTO_LOGIN', 'Not set')} (auto_login: {auto_login})")
            
            if auto_login:
                print("🔐 Azure CLI not authenticated. Attempting automatic login...")
                try:
                    print("⏳ Running 'az login'... (this may take up to 2 minutes)")
                    login_result = subprocess.run(['az', 'login'], timeout=120, shell=True)
                    print(f"🔍 Login result return code: {login_result.returncode}")
                    
                    if login_result.returncode == 0:
                        print("✅ Azure CLI login successful!")
                        # Verify login worked by checking account again
                        print("🔍 Verifying login by checking account...")
                        verify_result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True, timeout=30, shell=True)
                        if verify_result.returncode != 0:
                            print(f"❌ Login verification failed: {verify_result.stderr}")
                            return False, "Login appeared successful but account verification failed"
                        print("✅ Login verification successful!")
                        # Continue to get token below
                    else:
                        return False, "Azure CLI login failed. Please run 'az login' manually."
                except subprocess.TimeoutExpired:
                    print("⏰ Azure CLI login timed out after 2 minutes")
                    return False, "Azure CLI login timed out. Please run 'az login' manually."
                except Exception as e:
                    print(f"💥 Exception during automatic login: {str(e)}")
                    return False, f"Error during automatic login: {str(e)}"
            else:
                return False, "Not logged in to Azure CLI. Run 'az login' first or set MCP_AUTO_LOGIN=true"
        
        # Get access token for Azure DevOps
        result = subprocess.run([
            'az', 'account', 'get-access-token', 
            '--resource', '499b84ac-1321-427f-aa17-267ca6975798'  # Azure DevOps resource ID
        ], capture_output=True, text=True, timeout=30, shell=True)
        
        if result.returncode == 0:
            import json
            token_data = json.loads(result.stdout)
            return True, token_data['accessToken']
        else:
            return False, f"Failed to get Azure DevOps token: {result.stderr}"
            
    except Exception as e:
        return False, f"Error checking Azure CLI: {str(e)}"

def get_auth_token() -> str:
    """Get authentication token - Azure CLI only"""
    print("🔑 Checking Azure CLI authentication...")
    
    # Try Azure CLI authentication
    az_success, az_token = check_az_login()
    if az_success:
        print("✅ Azure CLI authentication successful")
        return az_token
    else:
        print(f"❌ Azure CLI authentication failed: {az_token}")
        auto_login_enabled = os.environ.get('MCP_AUTO_LOGIN', '').lower() in ('true', '1', 'yes')
        if auto_login_enabled:
            print("🔄 MCP_AUTO_LOGIN is enabled but authentication still failed")
        else:
            print("💡 To enable automatic login, set environment variable: MCP_AUTO_LOGIN=true")
        print("   Or manually run: az login")
        return ""

def clone_azure_devops_repo(repo_url: str, branch: str, destination_path: str) -> bool:
    """Clone Azure DevOps repository to destination path using Azure CLI authentication only"""
    print(f"🔄 Starting repository clone process...")
    print(f"📍 Repository: {repo_url}")
    print(f"🌿 Branch: {branch}")
    print(f"📂 Destination: {destination_path}")
    
    try:
        # Check if Git is available
        print("🔍 Checking Git availability...")
        if not check_git_available():
            print("❌ Git is not available on the system. Please install Git.")
            return False
        print("✅ Git is available")

        # Get authentication token (Azure CLI only)
        auth_token = get_auth_token()
        if not auth_token:
            print("❌ Could not obtain Azure CLI authentication token")
            return False
        print("✅ Authentication token obtained")

        # Remove existing directory if it exists
        if os.path.exists(destination_path):
            print(f"Removing existing directory: {destination_path}")
            shutil.rmtree(destination_path)

        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        print(f"Cloning Azure DevOps repository to {destination_path}...")
        print(f"Repository: {repo_url}")
        print(f"Branch: {branch}")

        # Construct authenticated URL
        clone_url = construct_git_url_with_auth(repo_url, auth_token)

        # Clone the repository with Windows long path support
        cmd = [
            'git', 'clone', 
            '--config', 'core.longpaths=true',
            '--config', 'core.autocrlf=false',
            '--branch', branch, 
            '--single-branch', 
            clone_url, 
            destination_path
        ]
        
        # Hide the URL in output for security
        display_cmd = ['git', 'clone', '--branch', branch, '--single-branch', repo_url, destination_path]
        print(f"Running: {' '.join(display_cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
        
        if result.returncode == 0:
            print("Repository cloned successfully!")
            
            # Check if we got AL files
            al_files_count = 0
            for root, dirs, files in os.walk(destination_path):
                for file in files:
                    if file.lower().endswith('.al'):
                        al_files_count += 1
            
            print(f"Found {al_files_count} AL files in the repository")
            return al_files_count > 0
        else:
            print(f"Git clone failed with error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("Git clone operation timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"Error cloning repository: {str(e)}")
        return False

def pull_latest_changes(repo_path: str, branch: str) -> bool:
    """Pull latest changes from the repository if it already exists"""
    try:
        if not os.path.exists(os.path.join(repo_path, '.git')):
            return False
        
        print(f"Pulling latest changes from branch {branch}...")
        
        # Change to the repository directory and pull
        cmd = ['git', '-C', repo_path, 'pull', 'origin', branch]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
        
        if result.returncode == 0:
            print("Repository updated successfully!")
            return True
        else:
            print(f"Git pull failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error pulling changes: {str(e)}")
        return False

def ensure_al_files() -> str:
    """Ensure AL files are available, clone from Azure DevOps if necessary"""
    print("🔍 Checking for AL files...")
    
    # Check for environment override
    env_path = os.environ.get('AISCRIPTGEN_AL_PATH')
    print(f"🌍 Environment path (AISCRIPTGEN_AL_PATH): {env_path}")
    if env_path and os.path.exists(env_path):
        print(f"✅ Using AL files from environment variable: {env_path}")
        return env_path
    
    # Debug: Show current configuration
    print(f"🔧 Azure DevOps Repository URL: {AZURE_DEVOPS_REPO_URL}")
    print(f"🔧 Azure DevOps Branch: {AZURE_DEVOPS_BRANCH}")
    print(f"🔧 Target AL Files Path: {AL_FILES_PATH}")
    print(f"🔧 MCP_AUTO_LOGIN: {os.environ.get('MCP_AUTO_LOGIN', 'Not set')}")
    
    # Try to clone from Azure DevOps if URL is provided - Azure CLI only
    if AZURE_DEVOPS_REPO_URL and AZURE_DEVOPS_REPO_URL.strip():
        print(f"🚀 Attempting to clone from Azure DevOps using Azure CLI authentication...")
        print(f"📍 Repository: {AZURE_DEVOPS_REPO_URL}")
        print(f"🌿 Branch: {AZURE_DEVOPS_BRANCH}")
        
        # Check if repository already exists and try to pull latest changes
        if os.path.exists(AL_FILES_PATH) and os.path.exists(os.path.join(AL_FILES_PATH, '.git')):
            print("Repository already exists, trying to pull latest changes...")
            if pull_latest_changes(AL_FILES_PATH, AZURE_DEVOPS_BRANCH):
                return AL_FILES_PATH
            else:
                print("Pull failed, will try to clone fresh...")
        
        # Clone the repository using Azure CLI authentication only
        if clone_azure_devops_repo(AZURE_DEVOPS_REPO_URL, AZURE_DEVOPS_BRANCH, AL_FILES_PATH):
            return AL_FILES_PATH
        else:
            print("Azure DevOps clone failed with Azure CLI authentication")
            print("Please ensure you are logged in with 'az login' and have proper permissions")
    else:
        print("No Azure DevOps repository URL provided in AZURE_DEVOPS_REPO_URL environment variable")
    
    # Fall back to local directory if it exists
    local_foodfresh = os.path.join(PACKAGE_DIR, "..", "..", "FoodFresh")
    if os.path.exists(local_foodfresh):
        print(f"Using local FoodFresh directory: {local_foodfresh}")
        return local_foodfresh
    
    # Check if there are any AL files already in the target directory
    if os.path.exists(AL_FILES_PATH):
        al_files = []
        for root, dirs, files in os.walk(AL_FILES_PATH):
            al_files.extend([f for f in files if f.lower().endswith('.al')])
        if al_files:
            print(f"Found {len(al_files)} AL files in existing directory: {AL_FILES_PATH}")
            return AL_FILES_PATH
    
    # Create empty directory as last resort
    os.makedirs(AL_FILES_PATH, exist_ok=True)
    return AL_FILES_PATH

# Global cache data
cache_data: Optional[ALCache] = None

def get_al_cache() -> ALCache:
    """Get AL cache instance, initializing only if needed"""
    global cache_data
    if cache_data is None:
        cache_file = os.path.join(PACKAGE_DIR, "al_cache.json")
        cache_data = ALCache(cache_file)
    return cache_data

@mcp.tool()
def find_page_info_with_fields(page_name: str) -> Dict[str, Any]:
    """Find information about AL pages with fields, actions, repeaters."""
    cache = get_al_cache()  # Your ALCache instance

    # Search strategies
    search_strategies = [
        ("exact", lambda name: ALExtractor.get_page_info(cache,name)),
        ("fuzzy_match", lambda name: ALExtractor.get_page_info_fuzzy(cache,name)),
    ]

    search_method_used = None
    page_info = None

    for strategy_name, strategy_func in search_strategies:
        try:
            page_info = strategy_func(page_name)
            if page_info:
                search_method_used = strategy_name
                break
        except Exception:
            continue

    if not page_info:
        all_suggestions = ALExtractor.get_comprehensive_page_suggestions(cache, page_name)
        return {
            "error": f"Page '{page_name}' not found",
            "search_suggestions": all_suggestions,
            "search_methods_tried": [s[0] for s in search_strategies]
        }

    # Extract base page content
    try:
        with open(page_info.file_path, 'r', encoding='utf-8') as f:
            al_file_content = f.read()
    except Exception as e:
        return {"error": f"Could not read file {page_info.file_path}: {str(e)}"}
    
    # Find related extensions
    related_extensions = []
    for ext in cache.pageext:
        if ext.get("extends") and ext["extends"].lower() == page_info.name.lower():
            try:
                with open(ext["location"], 'r', encoding='utf-8') as f:
                    ext_content = f.read()
                related_extensions.append({
                    "name": ext.get("name"),
                    "id": ext.get("id"),
                    "app_name": ext.get("app_name"),
                    "location": ext.get("location"),
                    "content": ext_content
                })
            except Exception:
                continue
                    
    return {
        "base_page": {
            "name": page_info.name,
            "app_name": page_info.app_name,
            "id": page_info.page_id,
            "caption": page_info.caption,
            "source_table": page_info.source_table,
            "location": page_info.file_path,
            "content": al_file_content
        },
        "extensions": related_extensions
    }



@mcp.tool()
def find_table_info_with_fields(table_name: str) -> Dict[str, Any]:
    """Find information about AL tables with fields, including extensions."""
    cache = get_al_cache()  # Your ALCache instance

    # Search strategies
    search_strategies = [
        ("exact", lambda name: ALExtractor.get_table_info(name)),
        ("fuzzy_match", lambda name: ALExtractor.get_table_info_fuzzy(name)),
    ]

    table_info = None

    for strategy_name, strategy_func in search_strategies:
        try:
            table_info = strategy_func(table_name)
            if table_info:
                search_method_used = strategy_name
                break
        except Exception:
            continue

    if not table_info:
        all_suggestions = ALExtractor.get_comprehensive_table_suggestions(cache, table_name)
        return {
            "error": f"Table '{table_name}' not found",
            "search_suggestions": all_suggestions,
            "search_methods_tried": [s[0] for s in search_strategies]
        }

    # Extract base table content
    try:
        with open(table_info.file_path, 'r', encoding='utf-8') as f:
            al_file_content = f.read()
    except Exception as e:
        return {"error": f"Could not read file {table_info.file_path}: {str(e)}"}
    
    # Find related extensions
    related_extensions = []
    for ext in cache.tableext:
        if ext.get("extends") and ext["extends"].lower() == table_info.name.lower():
            try:
                with open(ext["location"], 'r', encoding='utf-8') as f:
                    ext_content = f.read()
                related_extensions.append({
                    "name": ext.get("name"),
                    "id": ext.get("id"),
                    "app_name": ext.get("app_name"),
                    "location": ext.get("location"),
                    "content": ext_content
                })
            except Exception:
                continue
                
    return {
        "base_table": {
            "name": table_info.name,
            "app_name": table_info.app_name,
            "id": table_info.table_id if hasattr(table_info, 'table_id') else None,
            "location": table_info.file_path,
            "content": al_file_content
        },
        "extensions": related_extensions
    }

@mcp.tool()
def find_enum_info(enum_name: str) -> Dict[str, Any]:
    """Find information about AL enums with fields, including extensions."""
    cache = get_al_cache()  # Your ALCache instance

    # Search strategies
    search_strategies = [
        ("exact", lambda name: ALExtractor.get_enum_info(name)),
        ("fuzzy_match", lambda name: ALExtractor.get_enum_info_fuzzy(name)),
    ]

    enum_info = None

    for strategy_name, strategy_func in search_strategies:
        try:
            enum_info = strategy_func(enum_name)
            if enum_info:
                search_method_used = strategy_name
                break
        except Exception:
            continue

    if not enum_info:
        all_suggestions = ALExtractor.get_comprehensive_enum_suggestions(cache, enum_name)
        return {
            "error": f"Enum '{enum_name}' not found",
            "search_suggestions": all_suggestions,
            "search_methods_tried": [s[0] for s in search_strategies]
        }

    # Extract base enum content
    try:
        with open(enum_info.file_path, 'r', encoding='utf-8') as f:
            al_file_content = f.read()
    except Exception as e:
        return {"error": f"Could not read file {enum_info.file_path}: {str(e)}"}

    # Find related extensions
    related_extensions = []
    for ext in cache.enumext:
        if ext.get("extends") and ext["extends"].lower() == enum_info.name.lower():
            try:
                with open(ext["location"], 'r', encoding='utf-8') as f:
                    ext_content = f.read()
                related_extensions.append({
                    "name": ext.get("name"),
                    "id": ext.get("id"),
                    "app_name": ext.get("app_name"),
                    "location": ext.get("location"),
                    "content": ext_content
                })
            except Exception:
                continue
                
    return {
        "base_enum": {
            "name": enum_info.name,
            "app_name": enum_info.app_name,
            "id": enum_info.enum_id if hasattr(enum_info, 'enum_id') else None,
            "location": enum_info.file_path,
            "content": al_file_content
        },
        "extensions": related_extensions
    }


@mcp.tool()
def find_codeunit_info(codeunit_name: str) -> Dict[str, Any]:
    """Find information about AL codeunits with fields, including extensions."""
    cache = get_al_cache()  # Your ALCache instance

    # Search strategies
    search_strategies = [
        ("exact", lambda name: ALExtractor.get_codeunit_info(name)),
        ("fuzzy_match", lambda name: ALExtractor.get_codeunit_info_fuzzy(name)),
    ]

    codeunit_info = None

    for strategy_name, strategy_func in search_strategies:
        try:
            codeunit_info = strategy_func(codeunit_name)
            if codeunit_info:
                search_method_used = strategy_name
                break
        except Exception:
            continue

    if not codeunit_info:
        all_suggestions = ALExtractor.get_comprehensive_codeunit_suggestions(cache, codeunit_name)
        return {
            "error": f"Codeunit '{codeunit_name}' not found",
            "search_suggestions": all_suggestions,
            "search_methods_tried": [s[0] for s in search_strategies]
        }

    # Extract base codeunit content
    try:
        with open(codeunit_info.file_path, 'r', encoding='utf-8') as f:
            al_file_content = f.read()
    except Exception as e:
        return {"error": f"Could not read file {codeunit_info.file_path}: {str(e)}"}

    return {
        "base_codeunit": {
            "name": codeunit_info.name,
            "app_name": codeunit_info.app_name,
            "id": codeunit_info.codeunit_id if hasattr(codeunit_info, 'codeunit_id') else None,
            "location": codeunit_info.file_path,
            "content": al_file_content
        }
    }

@mcp.tool()
def read_yaml_template() -> Dict[str, Any]:
    """
    Reads a YAML template file and returns the structure as a reference.
    Fixes 'tag:yaml.org,2002:value' by treating it as a plain string.
    """
    # Try to find template file in multiple locations
    template_locations = [
        os.path.join(YAML_TEMPLATES_PATH, "Template.yml"),  # Project root
        os.path.join(PACKAGE_DIR, "Template.yml"),          # In package directory
        os.path.join(PACKAGE_DIR, "..", "..", "Template.yml") # Project root (alternative)
    ]
    
    template_structure = None
    template_source = None
    
    for template_path in template_locations:
        try:
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    template_structure = f.read()
                template_source = template_path
                print(f"✅ Found template file: {template_path}")
                break
            else:
                print(f"❌ Template not found at: {template_path}")
        except Exception as e:
            print(f"⚠️ Error reading template at {template_path}: {str(e)}")
            continue
    
    if not template_structure:
        # Return a basic template structure if no file found
        template_structure = """# Basic YAML Template Structure
testSuite: 
  - testFunction:
      name: "Test Function Name"
      steps:
        - actionType: "Open"
          objectType: "Page"
          objectId: "PageName"
        - actionType: "Set"
          control: "FieldName"
          value: "FieldValue"
        - actionType: "Invoke"
          control: "ActionName"
"""
        template_source = "built-in default"
    
    return {
        "yaml_template_structure": template_structure,
        "structure_info": {
            "description": "Business Central YAML test template structure",
            "usage": "Use this structure as a reference when generating new YAML test files",
            "template_found": template_source is not None,
            "search_locations": template_locations
        },
        "file_source": template_source if template_source else "built-in default"
    }

@mcp.prompt("generate_yaml_scenario")
def generate_yaml_scenario(scenario: str, app_name: str) -> str:
    """Yaml Scenario Generator with Complete Field Analysis Instructions"""
    return f"""
    SCENARIO:
    {scenario}
    
    # 🛠️ **MPC-Powered YML Generator (Read-Only Base + Extension Mode)**

    ## 🎯 ROLE
    You are an **MCP-driven AL Object Analyzer and YML Generator** for **Microsoft Dynamics 365 Business Central**.  

    Your responsibilities:  
    1. Systematically analyze AL objects using **MCP tools only** — never assume.  
    2. For each **base object** (Page, Table, Enum, etc.), also **read the corresponding APP-level extension(s)** from the specified **APP NAME**.  
    3. Trace relationships:
    - Pages → Actions → Codeunits  
    - Pages → Source Tables → Fields → Enums  
    4. Use analyzed data to create accurate, validated **YAML test files**.  
    5. Validate all references before YAML generation.  

    🚫 **Never assume, merge, or skip any step.**  
    🧩 **Use only these MCP tools:**  
    `find_page_info_with_fields()`, `find_table_info_with_fields()`, `find_enum_info()`, `find_codeunit_info()`, `read_yaml_template()`

    ---

    ## ⚙️ EXECUTION FLOW

    ### 🔍 **PHASE 1 — Identify Pages**
    - Parse the given scenario to determine all relevant **Pages**.  
    - **Output:** List of all required **base Pages** and **subpages** (including parts, factboxes, and subforms).  

    ---

    ### 📄 **PHASE 2 — Read Pages**
    For each identified Page:
    1. Use `find_page_info_with_fields()` to read the **base Page**.  
    2. From the response, check for an `extensions` array.  
    3. For every Page extension related to the **target APP NAME**:
    - Read the **Page Extension** separately using the same MCP tool.  
    - Note any additional fields, actions, or control modifications for later reference.  
    4. **Do not merge** extension data into the base Page — just record it as a separate reference.

    ---

    ### ⚙️ **PHASE 2.1 — App Page Extension Analysis**
    - For each Page analyzed:
    - Read all matching **Page Extensions** from the **APP NAME**.  
    - Document extension-specific:
        - Fields  
        - Actions  
        - Groups / Repeaters  

    **List the identified field names from page and it's extensions.**
    ---

    ### ⚡ **PHASE 3 — Action and Codeunit Analysis**
    - For each **Action** from both:
    - Base Page  
    - APP-level Page Extension  
    - Inspect its **OnAction() trigger**.  
    - If it calls a **procedure or codeunit**, read that object using `find_codeunit_info()`.  
    - Trace procedure logic and note any dependencies or validations.  

    ---

    ### 🗂️ **PHASE 4 — Read Source Tables**
    For each Page (and Subpage):
    1. Identify the **SourceTable**.  
    2. Use `find_table_info_with_fields()` to read the **base Table**.  
    3. Check for and read all **Table Extensions** belonging to the **APP NAME**.  
    4. Record both **base Table fields** and **extension fields** separately for comparison.  
    5. Do **not** merge extension data into the base Table; treat as parallel objects.

    ---

    ### 🧩 **PHASE 4.1 — Table Extension Analysis**
    - For each Table analyzed:
    - Read every **Table Extension** from the target **APP NAME**.  
    - Note all custom fields, validations, or triggers.  
    - Keep extension data separate — only reference it where the scenario requires it.

    ---

    ### 🔢 **PHASE 5 — Enum Analysis**
    - For every Enum field discovered in Tables or Pages:
    1. Use `find_enum_info()` to read the **base Enum**.  
    2. Read all **Enum Extensions** from the target APP NAME.  
    3. Record the ordinal index and captions for both sets (base and extension).  
    4. Treat base and app Enum definitions as separate data sources — do not merge.

    ---

    ### ✅ **PHASE 6 — Validation**
    Before generating YAML, verify:
    - ✅ All base Pages, Tables, and Enums were successfully read.  
    - ✅ All corresponding APP-level Extensions (Pages, Tables, Enums) were read.  
    - ✅ All Actions and Codeunits were analyzed.  
    - ✅ Scenario requirements are fully supported.  
    - If any base or app extension object is missing → re-fetch via MCP before YAML generation.

    ---

    ### 📏 **PHASE 7 — YAML Mapping Rules**

    | AL Type | YAML Format | Example |
    |----------|-------------|----------|
    | Text[N], Code[N] | `"quoted string"` | `"ITEM001"` |
    | Integer | `numeric_value` | `10` |
    | Decimal | `numeric_value.decimal` | `99.95` |
    | Boolean | `true` / `false` | `true` |
    | Date | `YYYY-MM-DD` | `2024-01-15` |
    | Enum | `ordinal_index` | `2` |
    | Option | `"option_text"` | `"Released"` |

    **Strict YAML Rules:**
    - Generate YAML **only** for the steps described in the scenario.  
    - Never assume or reuse template values.  
    - Always check record existence before creation (e.g., Item, Vendor, Customer).  
    - Use **exact action names** from AL definition.  
    - Add `wait` after every `invoke`.  
    - Use `equals` for integer validations.  
    - Represent repeater data as:
    ```yaml
    - repeater(<repeater_name>)
    ```
    - Validate non-editable fields (no data entry).  
    - Exclude `automationId` for confirmation dialogs.  
    - Ensure **fields and actions from app extensions** are used where relevant.
    - use field name from page not from table (field(field_name;Rec.Reference_name))

    ---

    ### 🧠 **PHASE 8 — YAML Generation**
    1. Load the YAML base template via `read_yaml_template()`.  
    2. Map analyzed base and extension objects separately into scenario-relevant steps.  
    3. Include actions, validations, and field updates based on scenario flow.  
    4. Insert `wait` after every `invoke`.  
    5. Validate YAML against all rules and ensure structural correctness.

    ---

    ### 🧩 **QUALITY CONTROL RULES**
    - Always read **both base and APP-level extension objects**, even if extension fields aren’t used.  
    - Keep base and extension data **separate** — never merged.  
    - Validate every object’s presence and correctness before YAML generation.  
    - Maintain strict YAML formatting and step order.  
    - Never output partial or assumed data.

    ---

    ✅ **FINAL OUTPUT:**  
    A verified, scenario-specific **YAML test file**, based on:  
    - Base Pages, Tables, Enums, and Codeunits  
    - Corresponding App-level Extensions (read independently)  
    - Accurate field, action, and enum mappings  
    - Fully validated MCP-based analysis  

    """

@mcp.prompt("generate_test_scenario")
def generate_test_scenario(workitem: int) -> str:
    # Implementation for generating test scenario
    return f"""Work Item ID: {workitem} """ + """
    
    # DevOps Work Item Test Scenario Generator (Business Central Functional Testing)

        ## Project Overview  
        **PROJECT**: Microsoft Dynamics 365 Business Central Functional Requirements Testing  
        **PURPOSE**: Generate comprehensive **Test Scenarios** from DevOps work items following BaseScripts.csv format  
        **OUTPUT**: Functional QA-ready scenarios aligned with Business Central workflows  

        ---

        ## Step 1: DevOps Work Item Analysis  

        Before generating test scenarios, analyze the DevOps work item thoroughly:  

        - Fetch the work item using:  
        mcp_ado_wit_get_work_item(id=[{workitem}], project="[PROJECT_NAME]", expand="all")  

        - Extract comprehensive details:  
        • Title (System.Title)  
        • Description (System.Description)  
        • Acceptance Criteria (Microsoft.VSTS.Common.AcceptanceCriteria)  
        • Attachments & linked documents  
        • Linked Work Items (dependencies/bugs/enhancements)  

        ### REQUIRED OUTPUT:  
        Produce a **comprehensive business analysis** of:  
        1. **Business Objective** → Functional requirement and business purpose  
        2. **Business Central Context** → Which BC modules/areas are impacted (Purchase, Sales, Warehouse, Finance, Manufacturing)  
        3. **Functional Requirements** → Key business flows and processes that need validation  
        4. **Dependencies & Prerequisites** → Any linked requirements, bugs, or setup dependencies  

        Keep this **functional QA focused** and aligned with Business Central terminology.  

        ---

        ## Step 2: Test Scenario Generation (Structured Format Alignment)

        ### Test Scenario Standards  
        - **All scenarios must align with Business Central functional flows**  
        - **Follow the strict 3-column format: Title, Action, Expected Result**  
        - **Generate multiple scenarios per work item** (positive, negative, edge cases)  
        - **Ensure functional QA readiness** with clear preconditions and measurable outcomes  

        ---

        ## 📑 Test Scenario Schema (Strict Adherence Required)
        The output must follow the exact 3-column format with these columns:

        ### Core Structure (3-Column Format):
        1. **Title**  
        - Business Central process-focused scenario title  
        - **CRITICAL**: Only populate title for the **first row** of each scenario  
        - **Leave title BLANK** for all subsequent action steps within the same scenario  
        - Examples: "Vendor creation", "Customer creation", "Item creation 1"  

        2. **Action**  
        - **Individual step-by-step actions** - ONE action per row  
        - Each action numbered sequentially (1., 2., 3., etc.)  
        - Precise Business Central UI/Process terminology  
        - Individual navigation steps, field entries, button clicks  
        - Each action step gets its own row with corresponding expected result  

        3. **Expected Result**  
        - **Specific expected outcome for each individual action step**  
        - Must include immediate system response for that step:  
            - Page opens (*System displays the Vendors page*)  
            - Dialog appearances (*Select a template for a new vendor dialog is shown*)  
            - Field acceptance (*System accepts and saves Name = Base Vendor*)  
            - Navigation confirmations (*New - Vendor Card page opens with template defaults*)  

        ### Extended Format (8-Column Format) for Comprehensive Testing:
        When generating comprehensive test scenarios, include additional columns:

        4. **Test Case ID**  
        - Unique identifier: TC[XX]_[MODULE]_[FUNCTION]  
        - Examples: TC01_PURCHASE_VENDOR_SETUP, TC02_SALES_ORDER_CREATION  

        5. **Pre-Conditions**  
        - Clearly defined setup requirements  
        - Master data prerequisites  
        - System configuration requirements  
        - User permissions and access requirements  

        6. **Priority**  
        - High: Critical business processes, core functionality  
        - Medium: Important workflows, moderate business impact  
        - Low: Edge cases, nice-to-have features  

        7. **Module/Area**  
        - Business Central functional areas: Purchase, Sales, Warehouse, Finance, Manufacturing, Planning  
        - Align with BC module structure  

        8. **Business Central Version / Feature Reference**  
        - BC version compatibility  
        - Specific feature or enhancement reference  
        - Related work item or requirement ID  

        ---

        ### Business Central Test Data Standards  
        **Use existing master data if available in workspace, otherwise use these standards:**

        - **Vendors**: Base Vendor, Primary Supplier, Secondary Supplier  
        - **Customers**: Base Customer, Primary Customer, Secondary Customer  
        - **Items**: 
        - Raw Material (with Item Tracking Code = "lotall", Lot Nos. = "LOT")  
        - BaseProductionItem (with Item Tracking Code = "lotall", Lot Nos. = "lot")  
        - Base Item 1, Base Item 2  
        - **Locations**: 
        - Aptean DIR (Direct location with Warehouse Employees and Inventory Posting Setup)  
        - TRANSIT (Aptean Transit, Use As In-Transit = true, with Warehouse Employees and Inventory Posting Setup)  
        - Apt WSWR (Warehouse location with Receive/Shipment/Bins, Warehouse Employees, Inventory Posting Setup)  
        - APT INV (Inventory location with Put-away/Pick/Bins, Warehouse Employees, Inventory Posting Setup)  
        - Apt WINV (Full warehouse with all features, Warehouse Employees, Inventory Posting Setup)  
        - **Bins**: REC, SHIP, DRY, COOL (must be created as part of location setup)  
        - **Inventory Posting Group**: RESALE (must be configured for all locations and items)  
        - **Item Tracking Codes**: lotall, LOT, lot  
        - **Warehouse Employees**: Current user must be added as warehouse employee for all locations  
        - **Dates**: Use current system date and logical business dates  

        ### **CRITICAL: Complete Base Functionality Patterns**

        **Location Creation Complete Pattern (ALL steps must be included):**
        1. Navigate to Locations page  
        2. Click "New" to create location  
        3. Enter Code and Name  
        4. Configure location-specific settings (bins, receive/shipment flags, etc.)  
        5. **Open "Warehouse Employees" from Location Card**  
        6. **Add current user as warehouse employee**  
        7. **Close Warehouse Employees page**  
        8. **Open "Inventory Posting Setup" from Location Card**  
        9. **Add Invt. Posting Group Code = RESALE**  
        10. **If Inventory Account is empty, use "Suggest Accounts" to populate it**  
        11. **Save and close Inventory Posting Setup page**  
        12. Save and close Location Card  
        13. Close Locations page  

        **Item Creation Complete Pattern (ALL steps must be included):**
        1. Navigate to Items page  
        2. Click "New" to create item  
        3. Select Item Template (when dialog appears)  
        4. Enter Description and item details  
        5. **Set Base Unit of Measure (e.g., KG)**  
        6. **Set Inventory Posting Group = RESALE**  
        7. Set Item Tracking Code (when applicable)  
        8. Set Lot Numbers series (when applicable)  
        9. Save and close Item Card  
        10. Verify item appears in items list  
        11. Close Items page  

        **Vendor/Customer Creation Complete Pattern (ALL steps must be included):**
        1. Navigate to respective page  
        2. Click "New"  
        3. **Select template when dialog appears**  
        4. **Confirm template selection**  
        5. Enter all required details (No., Name, etc.)  
        6. Save and close card  
        7. **Verify record appears in respective list**  
        8. Close page  

        ---

        ## 📝 Test Scenario Generation Rules

        1. **Complete End-to-End Scenarios (Not Chunked)**  
        - **CRITICAL**: Generate complete, full scenarios from start to finish  
        - **Avoid scenario chunking** - each scenario must be self-contained and complete  
        - **One complete business process per scenario** (e.g., complete vendor creation including all setup steps)  
        - **Include ALL necessary setup steps** within each scenario (don't split into separate setup scenarios)  

        2. **Mandatory Base Functionality Coverage**  
        **CRITICAL**: Do NOT miss any base functionalities from BaseScripts.csv patterns:  
        
        **For Location Creation scenarios, ALWAYS include:**
        - Warehouse Employees setup (Add current user as warehouse employee)  
        - Inventory Posting Setup (Add Invt. Posting Group Code = RESALE)  
        - Account suggestion ("Use Suggest Accounts to populate if Inventory Account is empty")  
        - Proper bin setup for warehouse locations (REC, SHIP, DRY, COOL)  
        - Location-specific settings (Require Receive, Require Shipment, Bin Mandatory, etc.)  
        
        **For Item Creation scenarios, ALWAYS include:**
        - Base Unit of Measure setup  
        - Inventory Posting Group assignment  
        - Item Tracking Code setup (when applicable)  
        - Lot Numbers series setup (when applicable)  
        
        **For Master Data scenarios, ALWAYS include:**
        - Complete template selection process  
        - All required field configurations  
        - Proper save and validation steps  
        - Verification that records appear in respective lists  

        3. **Functional QA Alignment**  
        - All scenarios must be **functional QA ready**  
        - Clearly defined preconditions and setup  
        - Step-by-step actions in Business Central UI/Process terms  
        - Measurable and verifiable expected outcomes  
        - Avoid ambiguity in steps and results  

        4. **Business Central Context Requirements**  
        All scenarios must align with Business Central functional flows:  
        - **Purchase Order creation and posting**  
        - **Sales Order and shipment processing**  
        - **Warehouse operations** (Put-away, Pick, Movement)  
        - **Item tracking and lot/serial management**  
        - **Production and planning scenarios**  
        - **Financial posting and validation**  

        5. **Structured Format Compliance**  
        - **CRITICAL**: Each individual action step gets its own row  
        - **Title field populated only for first row** of each scenario  
        - **All subsequent rows have blank titles** but continue the action sequence  
        - **Each action has its corresponding immediate expected result**  
        - **One Action Per Row Format** - never compress multiple actions  

        6. **Scenario Coverage Types**  
        For each work item, generate scenarios covering:  
        - **Happy Path**: Successful business flows  
        - **Negative Scenarios**: Validation errors, business rule violations  
        - **Edge Cases**: Boundary conditions, exceptional scenarios  
        - **Integration Tests**: Cross-module business processes  

        7. **Professional QA Documentation Style**  
        - Use precise, functional terms from Business Central  
        - Maintain clarity for manual execution or automation  
        - Structure scenarios for reusability  
        - Ensure end-to-end business coverage  

        8. **Complete Setup Requirements**  
        - **Every scenario must be complete and self-contained**  
        - **Include ALL setup steps within the scenario** (don't separate into different scenarios)  
        - **Follow complete setup patterns** for consistency  
        - **Ensure all prerequisites are covered** within the same scenario execution  

        ---



        ## 📊 Test Scenario Output Format (Structured 3-Column Format)

        ### Standard Format (3-Column Structure - COMPLETE SCENARIOS):
        | Title | Action | Expected Result |
        |-------|--------|-----------------|
        | Warehouse location creation | 1. Navigate to "Locations" page. | System displays the Locations page. |
        | | 2. Click "New" to add a location. | New - Location Card page opens. |
        | | 3. Enter Code = Apt WSWR on the Location Card. | System accepts and saves Code = Apt WSWR |
        | | 4. Enter Name = Apt WSWR on the Location Card. | System accepts and saves Name = Apt WSWR. |
        | | 5. Open "Bins" from the Location Card. | |
        | | 6. Add bin with Code = REC. | Bins REC is Created |
        | | 7. Add bin with Code = SHIP. | Bins SHIP is Created |
        | | 8. Add bin with Code = DRY. | Bins DRY is Created |
        | | 9. Add bin with Code = COOL. | Bins COOL is Created |
        | | 10. Close the Bins page. | |
        | | 11. Set "Require Receive" to true on the Location Card. | |
        | | 12. Set "Require Shipment" to true on the Location Card. | |
        | | 13. Set "Bin Mandatory" to true on the Location Card. | Require Receive, "Require Shipment", and "Bin Mandatory" are set to true. |
        | | 14. Set "Receipt Bin Code" to REC. | |
        | | 15. Set "Shipment Bin Code" to SHIP. | Receipt Bin Code is set to REC and "Shipment Bin Code" is set to SHIP. |
        | | 16. Open "Warehouse Employees" from the Location Card. | |
        | | 17. Add the current user as a warehouse employee. | User is added as a warehouse employee for the location. |
        | | 20. Open "Inventory Posting Setup" from the Location Card. | |
        | | 22. Add Invt. Posting Group Code = RESALE in Inventory Posting Setup. | |
        | | 23. If Inventory Account is empty, use "Suggest Accounts" to populate it. | |
        | | 24. Save and close the Inventory Posting Setup page. | |
        | | 25. Close the Location Card. | All pages close without error and the location is available for warehouse transactions. |
        | | 26. Close the Locations page. | |

        **CRITICAL NOTICE**: The above example shows a **COMPLETE** scenario that includes ALL necessary setup steps (Bins, Warehouse Employees, Inventory Posting Setup). This is the pattern that must be followed - **NOT chunked scenarios**.

        ### Extended Format (For Comprehensive Test Documentation):
        | Test Case ID | Test Scenario Title | Pre-Conditions | Test Steps | Expected Results | Priority | Module/Area | BC Version/Feature Reference |
        |--------------|-------------------|-----------------|------------|-----------------|----------|-------------|----------------------------|
        | TC01_SETUP_VENDOR | Setup Master Data - Vendor Creation | 1. User has Purchase module access<br>2. Vendor template configured<br>3. Business Central environment ready | 1. Navigate to "Vendors" page<br>2. Click "New" to add a vendor<br>3. Select Vendor Template<br>4. Enter vendor details<br>5. Save vendor record | 1. Vendors page opens successfully<br>2. New vendor card opens<br>3. Template applied correctly<br>4. Vendor details accepted<br>5. Vendor created and available | High | Purchase | BC 24.0 Master Data |

        ---

        ## 📦 Final Output Requirements

        ### CSV File Structure Options  
        **Option 1: Standard Format (3-Column)**  
        - Save as: `[WorkItemID]_TestScenarios.csv`  
        - Columns: Title, Action, Expected Result  
        - Format: Exactly match 3-column structure  

        **Option 2: Comprehensive Format (8-Column)**  
        - Save as: `[WorkItemID]_Comprehensive_TestScenarios.csv`  
        - Columns: Test Case ID, Test Scenario Title, Pre-Conditions, Test Steps, Expected Results, Priority, Module/Area, BC Version/Feature Reference  

        - Location: `$env:USERPROFILE\Downloads`  

        ### Quality Standards  
        1. **Each scenario must be completely self-contained and follow complete setup patterns**  
        2. **NO SCENARIO CHUNKING** - scenarios must be complete from start to finish  
        3. **ALL base functionalities must be included** (Warehouse Employees, Inventory Posting Setup, etc.)  
        4. **Title populated only for first row of each scenario**  
        5. **Actions must be numbered and sequential with ALL required steps**  
        6. **Expected results must be specific and immediate for each action**  
        7. **Business Central terminology must be precise and functional**  
        8. **Complete setup within each scenario** (don't split setup across multiple scenarios)  

        ### Scenario Coverage Validation  
        Ensure scenarios cover:  
        - **Complete Setup and Master Data scenarios** (following complete patterns)  
        - **Core business process flows** (primary functionality with all setup included)  
        - **Exception handling** (error validation)  
        - **Integration points** (cross-module workflows)  
        - **End-to-end business validation** (complete user journeys)  

        ### **CRITICAL ANTI-PATTERN WARNINGS:**
        ❌ **DO NOT** create chunked scenarios like "Vendor creation - Albaik", "Customer creation - Super Almere" as separate incomplete scenarios  
        ❌ **DO NOT** miss Warehouse Employees setup in location scenarios  
        ❌ **DO NOT** miss Inventory Posting Setup in location scenarios  
        ❌ **DO NOT** miss Base Unit of Measure setup in item scenarios  
        ❌ **DO NOT** miss template selection steps in master data scenarios  

        ✅ **DO** create complete scenarios that include ALL setup steps from established patterns  
        ✅ **DO** follow the complete location creation pattern with bins, warehouse employees, and inventory posting setup  
        ✅ **DO** follow the complete item creation pattern with UoM, inventory posting group, and tracking setup  
        ✅ **DO** ensure each scenario is executable from start to finish without dependencies  

        ---

        ## Step 3: CSV File Generation  

        ## 💻 PowerShell Script (CSV Generator - Structured Format)
        ```powershell
        # PowerShell: Generate TestScenarios CSV following structured format

        param(
            [string]$WorkItemId = "WI0000",
            [string]$WorkItemTitle = "Sample Work Item",
            [string]$DownloadsPath = "$env:USERPROFILE\Downloads",
            [string]$Format = "Standard" # Options: "Standard" or "Comprehensive"
        )

        if ($Format -eq "Standard") {
            $csvPath = Join-Path $DownloadsPath "$($WorkItemId)_TestScenarios.csv"
            
            # Example scenarios following structured format exactly - COMPLETE SCENARIOS
            $scenarios = @(
                [PSCustomObject]@{
                    "Title" = "Warehouse location creation"
                    "Action" = '1. Navigate to "Locations" page.'
                    "Expected Result" = "System displays the Locations page."
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '2. Click "New" to add a location.'
                    "Expected Result" = "New - Location Card page opens."
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "3. Enter Code = Apt WSWR on the Location Card."
                    "Expected Result" = "System accepts and saves Code = Apt WSWR"
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "4. Enter Name = Apt WSWR on the Location Card."
                    "Expected Result" = "System accepts and saves Name = Apt WSWR."
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '5. Open "Bins" from the Location Card.'
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "6. Add bin with Code = REC."
                    "Expected Result" = "Bins REC is Created"
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "7. Add bin with Code = SHIP."
                    "Expected Result" = "Bins SHIP is Created"
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "8. Add bin with Code = DRY."
                    "Expected Result" = "Bins DRY is Created"
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "9. Add bin with Code = COOL."
                    "Expected Result" = "Bins COOL is Created"
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "10. Close the Bins page."
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '11. Set "Require Receive" to true on the Location Card.'
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '12. Set "Require Shipment" to true on the Location Card.'
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '13. Set "Bin Mandatory" to true on the Location Card.'
                    "Expected Result" = 'Require Receive, "Require Shipment", and "Bin Mandatory" are set to true.'
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '14. Set "Receipt Bin Code" to REC.'
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '15. Set "Shipment Bin Code" to SHIP.'
                    "Expected Result" = 'Receipt Bin Code is set to REC and "Shipment Bin Code" is set to SHIP.'
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '16. Open "Warehouse Employees" from the Location Card.'
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "17. Add the current user as a warehouse employee."
                    "Expected Result" = "User is added as a warehouse employee for the location."
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "18. Close the Warehouse Employees page."
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '19. Open "Inventory Posting Setup" from the Location Card.'
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "20. Add Invt. Posting Group Code = RESALE in Inventory Posting Setup."
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = '21. If Inventory Account is empty, use "Suggest Accounts" to populate it.'
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "22. Save and close the Inventory Posting Setup page."
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "23. Close the Location Card."
                    "Expected Result" = "All pages close without error and the location is available for warehouse transactions."
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = "24. Close the Locations page."
                    "Expected Result" = ""
                },
                [PSCustomObject]@{
                    "Title" = ""
                    "Action" = ""
                    "Expected Result" = ""
                }
            )
        } else {
            $csvPath = Join-Path $DownloadsPath "$($WorkItemId)_Comprehensive_TestScenarios.csv"
            
            # Example scenarios with comprehensive format
            $scenarios = @(
                [PSCustomObject]@{
                    "Test Case ID" = "TC01_SETUP_VENDOR"
                    "Test Scenario Title" = "Setup Master Data - Vendor Creation"
                    "Pre-Conditions" = "1. User has Purchase module access`n2. Vendor template configured`n3. Business Central environment ready"
                    "Test Steps" = '1. Navigate to "Vendors" page`n2. Click "New" to add vendor`n3. Select Vendor Template`n4. Enter vendor details`n5. Save vendor record'
                    "Expected Results" = "1. Vendors page opens successfully`n2. New vendor card opens`n3. Template applied correctly`n4. Vendor details accepted`n5. Vendor created and available"
                    "Priority" = "High"
                    "Module/Area" = "Purchase"
                    "BC Version/Feature Reference" = "BC 24.0 Master Data Management"
                },
                [PSCustomObject]@{
                    "Test Case ID" = "TC02_PO_CREATE"
                    "Test Scenario Title" = "Create Purchase Order with Item Tracking"
                    "Pre-Conditions" = "1. Vendor Base Vendor exists`n2. Item Raw Material with lot tracking`n3. Location configured`n4. User has PO creation permissions"
                    "Test Steps" = '1. Navigate to "Purchase Orders" page`n2. Create new Purchase Order`n3. Select Vendor Base Vendor`n4. Add item line with tracking`n5. Release order'
                    "Expected Results" = "1. Purchase Orders page opens`n2. New PO created`n3. Vendor details populate`n4. Item tracking enabled`n5. Order released successfully"
                    "Priority" = "High"
                    "Module/Area" = "Purchase"
                    "BC Version/Feature Reference" = "BC 24.0 Item Tracking"
                }
            )
        }

        # Export to CSV with proper formatting
        $scenarios | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

        Write-Host "✅ Test Scenarios CSV created following $Format format: $csvPath"
        Write-Host "📋 Generated $($scenarios.Count) test scenario rows aligned with Business Central flows"

        # Display summary
        Write-Host "`n📊 Test Scenario Summary:"
        if ($Format -eq "Standard") {
            $scenarios | Where-Object { $_."Title" -ne "" } | ForEach-Object { Write-Host "  - $($_.'Title')" }
        } else {
            $scenarios | ForEach-Object { Write-Host "  - $($_.'Test Case ID'): $($_.'Test Scenario Title')" }
        }
        ```

        ## Notes  
        - **Strictly follows structured 3-column format** with exact formatting and **COMPLETE SCENARIOS**  
        - **Two output formats available**: Standard (3-column) or Comprehensive (8-column)  
        - **One action per row format** with title populated only for first row  
        - **COMPLETE SCENARIOS ONLY** - no chunking or incomplete scenarios  
        - **ALL base functionalities included** (Warehouse Employees, Inventory Posting Setup, etc.)  
        - **Business Central terminology** aligned with functional QA requirements  
        - **Complete setup scenarios** following established patterns  
        - **Functional QA ready** with clear actions and expected results  
        - **Professional documentation style** suitable for manual execution or automation  
        - **End-to-end comprehensive coverage** with complete scenarios from start to finish  

        ### **FINAL CRITICAL REMINDER:**
        🚫 **NEVER create chunked scenarios** like incomplete examples  
        ✅ **ALWAYS create complete scenarios** like the established patterns  
        ✅ **ALWAYS include ALL setup steps** (Warehouse Employees, Inventory Posting Setup, Bins, UoM, etc.)  
        ✅ **ALWAYS follow complete end-to-end patterns**  

        The generated scenarios must be **executable from start to finish** without dependencies on other scenarios.  

"""


def main():
    """Main function to run the MCP server."""
    print("🚀 Starting AI Script Generator MCP Server...")
    
    # Ensure AL files are available (download if necessary)
    print("📁 Ensuring AL files are available...")
    al_files_path = ensure_al_files()
    print(f"📂 AL files path: {al_files_path}")
    
    # Check if we actually have AL files
    if os.path.exists(al_files_path):
        al_files = list(Path(al_files_path).rglob("*.al"))
        print(f"📄 Found {len(al_files)} AL files in directory")
        if len(al_files) == 0:
            print("⚠️  Warning: No AL files found. Repository may not have cloned properly.")
    else:
        print("❌ AL files directory does not exist!")
    
    cache_file = os.path.join(PACKAGE_DIR, "al_cache.json")
    print(f"🗄️  Cache file: {cache_file}")

    # Build cache if needed
    if needs_rebuild(al_files_path, cache_file):
        print("🔄 Building/rebuilding cache...")
        build_cache(al_files_path, cache_file)
    else:
        print("✅ Cache is up to date")
    
    print("🟢 Starting MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
