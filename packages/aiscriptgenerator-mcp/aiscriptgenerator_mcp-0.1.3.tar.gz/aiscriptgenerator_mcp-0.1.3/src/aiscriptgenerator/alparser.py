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
    """Extract AL object definitions with a single caption string and source table for pages."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()


    objects = []
    for match in AL_OBJECT_REGEX.finditer(content):
        obj_type = match.group(1)
        obj_id = match.group(2)
        obj_name = match.group(3) or match.group(4)
        extends = match.group(5) or match.group(6)


        caption: Optional[str] = None
        caption_match: Optional[re.Match] = CAPTION_REGEX.search(content, match.end())
        if caption_match:
            caption = caption_match.group(2)
        else:
            caption = None

        # 🔹 New: parse SourceTable if it's a page or pageextension
        source_table = None
        if obj_type.lower() in ("page", "pageextension"):
            st_match = SOURCE_TABLE_REGEX.search(content, match.end())
            if st_match:
                source_table = st_match.group(1).strip('"')

        objects.append({
            "type": obj_type.lower(),
            "id": int(obj_id) if obj_id and obj_id.isdigit() else None,
            "name": obj_name.strip().strip('"'),
            "caption": caption,
            "source_table": source_table,
            "extends": extends,
            "location": str(file_path)
        })
    return objects



def build_cache(al_dir: str, cache_file: str = "al_cache.json") -> None:
    """Build cache file with parallel parsing (auto-detect CPU cores)."""
    allowed_suffixes = (".page.al", ".pageext.al", ".table.al", ".tableext.al", ".enum.al",".enumext.al","report.al","reportext.al","codeunit.al")

    al_files = [str(p) for p in Path(al_dir).rglob("*.al") if p.name.lower().endswith(allowed_suffixes)]

    max_workers = os.cpu_count() or 4

    all_objects: List[Dict[str, Any]] = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(parse_al_file, f): f for f in al_files}
        for future in as_completed(futures):
            result = future.result()
            all_objects.extend(result)
        
    # Save cache (complete list)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(all_objects, f, indent=2, ensure_ascii=False)


def needs_rebuild(al_dir: str, cache_file: str) -> bool:
    if not Path(cache_file).exists():
        return True

    cache_mtime = Path(cache_file).stat().st_mtime
    allowed_suffixes = (".page.al", ".pageext.al", ".table.al", ".tableext.al", ".enum.al", ".enumext.al","report.al","reportext.al","codeunit.al")

    current_files = {str(p) for p in Path(al_dir).rglob("*.al") if p.name.lower().endswith(allowed_suffixes)}

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            cached_objects = json.load(f)
        cached_files = {obj["location"] for obj in cached_objects}
    except Exception:
        return True  # corrupted cache, force rebuild

    # 🔹 Check for missing/deleted files
    if not cached_files.issubset(current_files):
        return True

    # 🔹 Check if any file is newer than cache
    for p in current_files:
        try:
            if Path(p).stat().st_mtime > cache_mtime:
                return True
        except FileNotFoundError:
            continue

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




