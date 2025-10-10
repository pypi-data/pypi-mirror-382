import re
import sys
import io
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Regex for AL object definitions
AL_OBJECT_REGEX = re.compile(
    r'^(table|tableextension|page|pageextension|enum|enumextension|report|reportextension|codeunit)'   # type
    r'(?:\s+(\d+))?'                                    # optional ID
    r'\s+(?:"([^"]+)"|([\w\.]+))'                       # name, quoted or unquoted
    r'(?:\s+extends\s+(?:"([^"]+)"|([\w\.]+)))?',       # optional extends, quoted or unquoted
    re.IGNORECASE | re.MULTILINE
)


# Regex for Caption
CAPTION_REGEX = re.compile(r'Caption\s*=\s*([\'"])(.*?)\1;', re.IGNORECASE)

# Regex for SourceTable (page/pageextension)
SOURCE_TABLE_REGEX = re.compile(r'SourceTable\s*=\s*("?[\w\s\.\-]+"?);', re.IGNORECASE)


def parse_al_file(file_path: str) -> List[Dict[str, Any]]:
    """Extract AL object definitions with optimized parsing."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return []

    # Early exit if no AL objects found
    if not AL_OBJECT_REGEX.search(content):
        return []

    # Extract AppName from file path - get value after "Aptean_Aptean" and before "for"
    app_name = "Base"  # Default value
    path_str = str(file_path)
    # Look for pattern like "Aptean_Aptean [AppName] for" and capture everything between them
    app_name_match = re.search(r'Aptean_Aptean\s+(.+?)\s+for', path_str, re.IGNORECASE)
    if app_name_match:
        app_name = app_name_match.group(1).strip()

    objects = []
    # Pre-compile searches for better performance
    obj_type_lower_cache = {}
    
    for match in AL_OBJECT_REGEX.finditer(content):
        obj_type = match.group(1)
        obj_id = match.group(2)
        obj_name = match.group(3) or match.group(4)
        extends = match.group(5) or match.group(6)

        # Cache lowercased type
        if obj_type not in obj_type_lower_cache:
            obj_type_lower_cache[obj_type] = obj_type.lower()
        obj_type_lower = obj_type_lower_cache[obj_type]

        # Only search for caption within a reasonable range after the match
        caption = None
        caption_search_end = min(match.end() + 1000, len(content))  # Limit search range
        caption_match = CAPTION_REGEX.search(content, match.end(), caption_search_end)
        if caption_match:
            caption = caption_match.group(2)

        # Only search for SourceTable if it's a page type
        source_table = None
        if obj_type_lower in ("page", "pageextension"):
            st_search_end = min(match.end() + 500, len(content))  # Limit search range
            st_match = SOURCE_TABLE_REGEX.search(content, match.end(), st_search_end)
            if st_match:
                source_table = st_match.group(1).strip('"')

        objects.append({
            "type": obj_type_lower,
            "app_name": app_name,
            "id": int(obj_id) if obj_id and obj_id.isdigit() else None,
            "name": obj_name.strip().strip('"'),
            "caption": caption,
            "source_table": source_table,
            "extends": extends,
            "location": str(file_path)
        })
    return objects



def build_cache(al_dir: str, cache_file: str = "al_cache.json") -> None:
    """Build cache file with optimized parallel parsing."""
    allowed_suffixes = (".page.al", ".pageext.al", ".table.al", ".tableext.al", ".enum.al",".enumext.al","report.al","reportext.al","codeunit.al")

    print(f"Scanning for AL files in {al_dir}...")
    al_files = [str(p) for p in Path(al_dir).rglob("*.al") if p.name.lower().endswith(allowed_suffixes)]
    print(f"Found {len(al_files)} AL files to scan...")

    if not al_files:
        print(" No matching AL files found.")
        return

    # Optimize worker count for I/O bound tasks
    max_workers = min(32, (os.cpu_count() or 4) * 2)
    print(f" Using {max_workers} parallel workers")

    all_objects: List[Dict[str, Any]] = []
    processed_count = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        futures = {executor.submit(parse_al_file, f): f for f in al_files}
        
        # Process results as they complete with progress updates
        for future in as_completed(futures):
            try:
                result = future.result()
                all_objects.extend(result)
                processed_count += 1
                
                # Show progress every 100 files
                if processed_count % 100 == 0:
                    print(f" Processed {processed_count}/{len(al_files)} files...")
                    
            except Exception as e:
                print(f" Error parsing {futures[future]}: {e}")

    print(f" Completed processing {processed_count} files")

    # Save cache with proper formatting
    print(f" Writing cache to {cache_file}...")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(all_objects, f, indent=2, ensure_ascii=False)

    print(f"Cache built with {len(all_objects)} objects → {cache_file}")


def needs_rebuild(al_dir: str, cache_file: str) -> bool:
    cache_path = Path(cache_file)
    if not cache_path.exists():
        return True

    cache_mtime = cache_path.stat().st_mtime
    allowed_suffixes = (".page.al", ".pageext.al", ".table.al", ".tableext.al", ".enum.al", ".enumext.al","report.al","reportext.al","codeunit.al")

    # Quick check: get current files
    al_dir_path = Path(al_dir)
    if not al_dir_path.exists():
        return True

    current_files = {str(p) for p in al_dir_path.rglob("*.al") if p.name.lower().endswith(allowed_suffixes)}

    # Fast check: if no AL files exist but cache does, rebuild
    if not current_files:
        return True

    try:
        # Only load cache locations for faster comparison
        with open(cache_file, "r", encoding="utf-8") as f:
            cached_objects = json.load(f)
        cached_files = {obj["location"] for obj in cached_objects}
    except Exception:
        return True  # corrupted cache, force rebuild

    # Quick file count check first
    if len(cached_files) != len(current_files):
        return True

    # Check for missing/deleted files
    if not cached_files.issubset(current_files):
        return True

    # Check if any current file is newer than cache (optimized with early exit)
    for p in current_files:
        try:
            if Path(p).stat().st_mtime > cache_mtime:
                return True
        except (FileNotFoundError, OSError):
            # File was deleted or became inaccessible, rebuild needed
            return True

    return False

class ALCache:
    """Manages parsed AL objects with categorized lists (without affecting al_cache.json)."""

    def __init__(self, cache_file: str = "al_cache.json"):
        self.cache_file = cache_file

        # categorized storage
        self.page: List[Dict[str, Any]] = []
        self.pageext: List[Dict[str, Any]] = []
        self.table: List[Dict[str, Any]] = []
        self.tableext: List[Dict[str, Any]] = []
        self.enum: List[Dict[str, Any]] = []
        self.enumext: List[Dict[str, Any]] = []
        self.report: List[Dict[str, Any]] = []
        self.reportext: List[Dict[str, Any]] = []
        self.codeunit: List[Dict[str, Any]] = []

        self.load_cache()

    def load_cache(self) -> None:
        """Load objects from al_cache.json into respective categories."""
        if not Path(self.cache_file).exists():
            raise FileNotFoundError(f"{self.cache_file} not found. Run build_cache first.")

        with open(self.cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for obj in data:
            t = obj.get("type")
            if t == "page":
                self.page.append(obj)
            elif t == "pageextension":
                self.pageext.append(obj)
            elif t == "table":
                self.table.append(obj)
            elif t == "tableextension":
                self.tableext.append(obj)
            elif t == "enum":
                self.enum.append(obj)
            elif t == "enumextension":
                self.enumext.append(obj)
            elif t == "report":
                self.report.append(obj)
            elif t == "reportextension":
                self.reportext.append(obj)
            elif t == "codeunit":
                self.codeunit.append(obj)
