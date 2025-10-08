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
    caption: Optional[str]
    source_table: Optional[str]
    file_path: str

# Initialize FastMCP Server
mcp = FastMCP("AL Parser Server")

# Configuration paths - supports shared folder via environment variable
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

AZURE_DEVOPS_REPO_URL = "https://schouw.visualstudio.com/Foodware%20365%20BC/_git/PageScripting"
AZURE_DEVOPS_BRANCH = "feature/MCPALFiles"
AZURE_DEVOPS_PAT = os.environ.get('AZURE_DEVOPS_PAT', '')

# Local paths in package directory
AL_FILES_PATH = os.path.join(str(Path.home()), "Downloads", "al_files")
YAML_TEMPLATES_PATH = os.path.join(PACKAGE_DIR, "Template.yml")

def check_git_available() -> bool:
    """Check if Git is available on the system"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=10)
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

def clone_azure_devops_repo(repo_url: str, branch: str, destination_path: str, pat: str = '') -> bool:
    """Clone Azure DevOps repository to destination path"""
    try:
        # Check if Git is available
        if not check_git_available():
            print("Git is not available on the system. Please install Git.")
            return False

        # Remove existing directory if it exists
        if os.path.exists(destination_path):
            print(f"Removing existing directory: {destination_path}")
            shutil.rmtree(destination_path)

        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        print(f"Cloning Azure DevOps repository to {destination_path}...")
        print(f"Repository: {repo_url}")
        print(f"Branch: {branch}")

        # Construct authenticated URL if PAT is provided
        clone_url = construct_git_url_with_auth(repo_url, pat)

        # Clone the repository
        cmd = ['git', 'clone', '--branch', branch, '--single-branch', clone_url, destination_path]
        
        # Hide the URL in output for security
        display_cmd = ['git', 'clone', '--branch', branch, '--single-branch', repo_url, destination_path]
        print(f"Running: {' '.join(display_cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
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
    print("Checking for AL files...")
    
    # Check for environment override
    env_path = os.environ.get('AISCRIPTGEN_AL_PATH')
    if env_path and os.path.exists(env_path):
        print(f"Using AL files from environment variable: {env_path}")
        return env_path
    
    # Try to clone from Azure DevOps if URL is provided
    if AZURE_DEVOPS_REPO_URL and AZURE_DEVOPS_REPO_URL.strip():
        print(f"Attempting to clone from Azure DevOps: {AZURE_DEVOPS_REPO_URL}")
        print(f"Branch: {AZURE_DEVOPS_BRANCH}")
        
        # Check if repository already exists and try to pull latest changes
        if os.path.exists(AL_FILES_PATH) and os.path.exists(os.path.join(AL_FILES_PATH, '.git')):
            print("Repository already exists, trying to pull latest changes...")
            if pull_latest_changes(AL_FILES_PATH, AZURE_DEVOPS_BRANCH):
                return AL_FILES_PATH
            else:
                print("Pull failed, will try to clone fresh...")
        
        # Clone the repository
        if clone_azure_devops_repo(AZURE_DEVOPS_REPO_URL, AZURE_DEVOPS_BRANCH, AL_FILES_PATH, AZURE_DEVOPS_PAT):
            return AL_FILES_PATH
        else:
            print("Azure DevOps clone failed, trying fallback options...")
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
    print(f"No AL files found. Created empty directory: {AL_FILES_PATH}")
    print("To use AL files, either:")
    print("1. Set AZURE_DEVOPS_REPO_URL environment variable to your Azure DevOps Git repository URL")
    print("2. Set AZURE_DEVOPS_BRANCH environment variable to specify the branch (default: main)")
    print("3. Set AZURE_DEVOPS_PAT environment variable for authentication (if private repo)")
    print("4. Set AISCRIPTGEN_AL_PATH environment variable to point to your AL files directory")
    print("5. Place AL files in the FoodFresh directory relative to the package")
    print("\nExample environment variable setup:")
    print("AZURE_DEVOPS_REPO_URL=https://dev.azure.com/yourorg/yourproject/_git/yourrepo")
    print("AZURE_DEVOPS_BRANCH=main")
    print("AZURE_DEVOPS_PAT=your_personal_access_token")
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
        ("exact", lambda name: ALExtractor.get_page_info(name)),
        ("fuzzy_match", lambda name: ALExtractor.get_page_info_fuzzy(name)),
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
        os.path.join(YAML_TEMPLATES_PATH, "Template.yml"),
        os.path.join(PACKAGE_DIR, "Template.yml"),
        os.path.join(PACKAGE_DIR, "..", "..", "Template.yml")
    ]
    
    template_structure = None
    template_source = None
    
    for template_path in template_locations:
        try:
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    template_structure = f.read()
                template_source = template_path
                break
        except Exception:
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
            "description": "This is the expected YAML structure template",
            "usage": "Use this structure as a reference when generating new YAML files",
            "custom_tags_preserved": False
        },
        "file_source": template_source
    }

@mcp.prompt("generate_yaml_scenario")
def generate_yaml_scenario(scenario: str, app_name: str) -> str:
    """Yaml Scenario Generator with Complete Field Analysis Instructions"""
    return f"""
    SCENARIO:
    {scenario}
    
    APP NAME:
    {app_name}

        # 🛠️ MPC-Powered YML Generator 

        ## 🎯 ROLE
        You are an **MCP-driven AL Object Analyzer and YML Generator** for Microsoft Dynamics 365 Business Central.  
        Your job is to:  
        1. Systematically analyze AL objects **using MCP tools only** (never assume).  
        2. Trace pages → actions → codeunits.
        3. Trace pages → source tables → fields → enums.
        4. Map the findings into **Business Central YML test files** following strict formatting rules.  
        5. Always validate before output.  

        You **must not guess** or invent object names, actions, or fields.  
        You **must not skip** any phase.  
        **Use tools read_yaml_template(), find_page_info_with_fields(), find_table_info_with_fields(), find_enum_info(), find_codeunit_info()**
        ---

        ## 🚦 EXECUTION PHASES

        ### 🔎 PHASE 1: Identify Pages
        - Parse the given scenario.  
        - **Output**: List of required **pages, subpages, and part pages**.  

        ---

        ### 📖 PHASE 2: Read Pages
        - Use MCP to read all identified pages.  
        - Read all the fields in each table.
        - Always include subform/part pages.  
        - **Before moving forward**: List all **actions** (with context).  
        - If there are multiple matches → choose the most relevant.
        ---

        ### 🔧 PHASE 2.1: Analyze Extensions
        - For each page from Phase 2, examine the returned `extensions` array.
        - **Focus on extensions from the specified APP NAME only**.
        - For extensions matching the app scenario:
          - Read the extension content thoroughly.
          - Identify additional fields, actions, and modifications.
          - Note any new controls, repeaters, or field groups.
        - **Priority**: Extension fields and actions take precedence over base page elements.
        ---

        ### ⚡ PHASE 3: Analyze Actions
        - For each action from Phase 2 **AND** extension actions from Phase 2.1:  
        - Inspect its **OnAction() trigger**.  
        - If it calls a **procedure/codeunit**, read that file via MCP.  
        - Trace dependencies.
        - **Important**: Include actions from relevant app extensions.

        ---

        ### 🗂️ PHASE 4: Read Source Tables
        - For each page/subpage:  
        - Identify **SourceTable**.  
        - Read both base table and its extensions.
        - **Focus on table extensions from the specified APP NAME**.
        - Extract:  
        - Field definitions (base + extensions)
        - Data types  
        - Enum fields (list them explicitly)
        - **Priority**: Extension fields are often the most relevant for the scenario.

        ---

        ### 🔢 PHASE 5: Read Enums
        - For each enum field from base objects **AND** extensions:  
        - Read enum file via MCP.  
        - Read enum extensions from the specified APP NAME.
        - Capture **all values with ordinal index**.
        - **Priority**: Extension enum values may be required for the scenario.

        ---

        ### ✅ PHASE 6: Validation
        - Confirm all details gathered:  
        - Base Pages ✔  
        - **App-specific Extensions ✔**
        - Actions (base + extensions) ✔  
        - Codeunits/procedures ✔  
        - Tables (base + extensions) ✔  
        - Enums (base + extensions) ✔  
        - **Verify extension fields from the specified APP NAME are included**.
        - If missing → read additional AL files.  

        ---

        ### 📏 PHASE 7: YML Rules
        Strict mapping between AL → YML:

        | AL Field Type | YML Format | Example |
        |---------------|------------|---------|
        | Text[N]       | `"quoted string"` | `"Demo Customer"` |
        | Code[N]       | `"quoted string"` | `"ITEM001"` |
        | Integer       | `numeric_value` | `10` |
        | Decimal       | `numeric_value.decimal` | `99.95` |
        | Boolean       | `true` / `false` | `true` |
        | Date          | `YYYY-MM-DD` | `2024-01-15` |
        | Enum          | `ordinal_index` | `2` |
        | Option        | `"option_text"` | `"Released"` |

        **Critical Rules**:  
        - **Strictly** Generate the yml for the given scenario only.
        - Always *check before creating any record* (e.g., Item, Vendor, Customer, etc.).
        - Always use **exact action names** from `action(ActionName)`.  
        - Never assume input values.  
        - Exclude `automationId` for confirmation dialogs.  
        - Validate field mappings before generating YML.  
        - Use the data given in Scenario.
        - Generate the YML for the steps only mentioned in the scenario.
        - Never use the value mentioned in the YAML Template.
        - While validating an integer use equals only to validate the exact match.
        - **MANDATORY**: Read extension files from the specified APP NAME.
        - **PRIORITY**: Extension fields and actions from the target app take precedence over base objects.
        - Make sure to use the correct fields for the given scenario from the extensions matching the APP NAME.
        - When analyzing returned data, check `extensions` array and filter by `app_name` field.
        - If a field is inside a repeater, represent it in YAML as `- repeater(<repeater_name>)` in the appropriate location.
        - If a field is non editable, just validate that field value in the YAML.
        - **Extension Analysis**: Always examine extension content for app-specific customizations.
        ---

        ### 📝 PHASE 8: Generate YML
        - Fetch YML base template with `read_yaml_template()` MCP Tool.  
        - Map analyzed objects into template.  
        - Add a `wait` step after every `invoke`.  

        **Final Output**:  
        A complete YML file with:  
        - Exact action names  
        - Correct field formatting  
        - Validated enum/option values  
        - Full compliance with AL analysis  

        ---

        ✨ **Remember**: You are a **Business Central MCP-YML Generator**. You must always follow this workflow in strict order and never skip or assume.  

    """


def main():
    """Main function to run the MCP server."""
    # Ensure AL files are available (download if necessary)
    al_files_path = ensure_al_files()
    cache_file = os.path.join(PACKAGE_DIR, "al_cache.json")
    
    # Build cache if needed
    if needs_rebuild(al_files_path, cache_file):
        build_cache(al_files_path, cache_file)
    
    mcp.run()


if __name__ == "__main__":
    main()
