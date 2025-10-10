from dataclasses import dataclass
from typing import Dict, Optional, List, Any
from difflib import SequenceMatcher
from .alparser import ALCache
import os 
@dataclass
class PageInfo:
    name: str
    page_id: Optional[int]
    caption: Optional[str]
    source_table: Optional[str]
    file_path: str
    app_name: Optional[str] = None

# Configuration paths
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# Global cache data
cache_data: Optional[ALCache] = None

def get_al_cache() -> ALCache:
    """Get AL cache instance, initializing only if needed"""
    global cache_data
    if cache_data is None:
        # Use the same cache path as server.py - in the project root
        cache_file = os.path.join(PACKAGE_DIR, "..", "..", "al_cache.json")
        cache_data = ALCache(cache_file)
    return cache_data

class ALExtractor:
    @staticmethod
    def get_page_info(page_name: str) -> Optional[PageInfo]:
        """Get exact page info by name from both pages and page extensions"""
        cache = get_al_cache()
        # Search in base pages first
        for page in cache.page:
            if page["name"].lower() == page_name.lower():
                return PageInfo(
                    name=page["name"],
                    page_id=page.get("id"),
                    caption=page.get("caption"),
                    source_table=page.get("source_table"),
                    file_path=page["location"],
                    app_name=page.get("app_name")
                )
        
        # Search in page extensions
        for pageext in cache.pageext:
            if pageext["name"].lower() == page_name.lower():
                return PageInfo(
                    name=pageext["name"],
                    page_id=pageext.get("id"),
                    caption=pageext.get("caption"),
                    source_table=pageext.get("source_table"),  # May be None for extensions
                    file_path=pageext["location"],
                    app_name=pageext.get("app_name")
                )
        
        return None

    @staticmethod
    def get_page_info_fuzzy(page_name: str, threshold: float = 0.6) -> Optional[PageInfo]:
        """Get page info using fuzzy matching from both pages and page extensions"""
        cache = get_al_cache()
        best_match = None
        best_ratio = 0.0
        
        # Search in base pages
        for page in cache.page:
            name_ratio = SequenceMatcher(None, page_name.lower(), page["name"].lower()).ratio()
            caption_ratio = 0.0
            if page.get("caption"):
                caption_ratio = SequenceMatcher(None, page_name.lower(), page["caption"].lower()).ratio()
            
            ratio = max(name_ratio, caption_ratio)
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = page
        
        # Search in page extensions
        for pageext in cache.pageext:
            name_ratio = SequenceMatcher(None, page_name.lower(), pageext["name"].lower()).ratio()
            caption_ratio = 0.0
            if pageext.get("caption"):
                caption_ratio = SequenceMatcher(None, page_name.lower(), pageext["caption"].lower()).ratio()
            
            ratio = max(name_ratio, caption_ratio)
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = pageext
        
        if best_match:
            return PageInfo(
                name=best_match["name"],
                app_name=best_match.get("app_name"),
                page_id=best_match.get("id"),
                caption=best_match.get("caption"),
                source_table=best_match.get("source_table"),
                file_path=best_match["location"]
            )
        
        return None

    @staticmethod
    def get_comprehensive_page_suggestions(page_name: str, limit: int = 10) -> List[str]:
        """Get comprehensive page suggestions from both pages and page extensions"""
        cache = get_al_cache()
        suggestions = []
        
        # Search in base pages
        for page in cache.page:
            name_ratio = SequenceMatcher(None, page_name.lower(), page["name"].lower()).ratio()
            caption_ratio = 0.0
            if page.get("caption"):
                caption_ratio = SequenceMatcher(None, page_name.lower(), page["caption"].lower()).ratio()
            
            ratio = max(name_ratio, caption_ratio)
            if ratio > 0.3:
                suggestions.append((page["name"], ratio))
        
        # Search in page extensions
        for pageext in cache.pageext:
            name_ratio = SequenceMatcher(None, page_name.lower(), pageext["name"].lower()).ratio()
            caption_ratio = 0.0
            if pageext.get("caption"):
                caption_ratio = SequenceMatcher(None, page_name.lower(), pageext["caption"].lower()).ratio()
            
            ratio = max(name_ratio, caption_ratio)
            if ratio > 0.3:
                suggestions.append((pageext["name"], ratio))
        
        # Sort by ratio and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in suggestions[:limit]]
    

    @staticmethod
    def get_table_info(table_name: str) -> Optional[PageInfo]:
        """Get exact table info by name from both tables and table extensions"""
        cache = get_al_cache()

        # Search in base tables first
        for table in cache.table:
            if table["name"].lower() == table_name.lower():
                return PageInfo(
                    name=table["name"],
                    app_name=table.get("app_name"),
                    page_id=table.get("id"),
                    caption=table.get("caption"),
                    source_table=table.get("source_table"),
                    file_path=table["location"]
                )

        # Search in table extensions
        for tableext in cache.tableext:
            if tableext["name"].lower() == table_name.lower():
                return PageInfo(
                    name=tableext["name"],
                    app_name=tableext.get("app_name"),
                    page_id=tableext.get("id"),
                    caption=tableext.get("caption"),
                    source_table=tableext.get("source_table"),  # May be None for extensions
                    file_path=tableext["location"]
                )
        
        return None

    @staticmethod
    def get_table_info_fuzzy(table_name: str, threshold: float = 0.6) -> Optional[PageInfo]:
        """Get table info using fuzzy matching from both tables and table extensions"""
        cache = get_al_cache()
        
        best_match = None
        best_ratio = 0.0
        
        # Search in base tables
        for table in cache.table:
            name_ratio = SequenceMatcher(None, table_name.lower(), table["name"].lower()).ratio()
            caption_ratio = 0.0
            if table.get("caption"):
                caption_ratio = SequenceMatcher(None, table_name.lower(), table["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = table

        # Search in table extensions
        for tableext in cache.tableext:
            name_ratio = SequenceMatcher(None, table_name.lower(), tableext["name"].lower()).ratio()
            caption_ratio = 0.0
            if tableext.get("caption"):
                caption_ratio = SequenceMatcher(None, table_name.lower(), tableext["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = tableext

        if best_match:
            return PageInfo(
                name=best_match["name"],
                app_name=best_match.get("app_name"),
                page_id=best_match.get("id"),
                caption=best_match.get("caption"),
                source_table=best_match.get("source_table"),
                file_path=best_match["location"]
            )
        
        return None

    @staticmethod
    def get_comprehensive_table_suggestions(table_name: str, limit: int = 10) -> List[str]:
        """Get comprehensive table suggestions from both tables and table extensions"""
        cache = get_al_cache()
        suggestions = []

        # Search in base tables
        for table in cache.table:
            name_ratio = SequenceMatcher(None, table_name.lower(), table["name"].lower()).ratio()
            caption_ratio = 0.0
            if table.get("caption"):
                caption_ratio = SequenceMatcher(None, table_name.lower(), table["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > 0.3:
                suggestions.append((table["name"], ratio))

        # Search in table extensions
        for tableext in cache.tableext:
            name_ratio = SequenceMatcher(None, table_name.lower(), tableext["name"].lower()).ratio()
            caption_ratio = 0.0
            if tableext.get("caption"):
                caption_ratio = SequenceMatcher(None, table_name.lower(), tableext["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > 0.3:
                suggestions.append((tableext["name"], ratio))

        # Sort by ratio and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in suggestions[:limit]]

    @staticmethod
    def get_enum_info(enum_name: str) -> Optional[PageInfo]:
        """Get exact enum info by name from both enums and enum extensions"""
        cache = get_al_cache()

        # Search in base enums first
        for enum in cache.enum:
            if enum["name"].lower() == enum_name.lower():
                return PageInfo(
                    name=enum["name"],
                    app_name=enum.get("app_name"),
                    page_id=enum.get("id"),
                    caption=enum.get("caption"),
                    source_table=enum.get("source_table"),
                    file_path=enum["location"]
                )

        # Search in enum extensions
        for enumext in cache.enumext:
            if enumext["name"].lower() == enum_name.lower():
                return PageInfo(
                    name=enumext["name"],
                    app_name=enumext.get("app_name"),
                    page_id=enumext.get("id"),
                    caption=enumext.get("caption"),
                    source_table=enumext.get("source_table"),  # May be None for extensions
                    file_path=enumext["location"]
                )
        
        return None

    @staticmethod
    def get_enum_info_fuzzy(enum_name: str, threshold: float = 0.6) -> Optional[PageInfo]:
        """Get enum info using fuzzy matching from both enums and enum extensions"""
        cache = get_al_cache()
        
        best_match = None
        best_ratio = 0.0
        
        # Search in base enums
        for enum in cache.enum:
            name_ratio = SequenceMatcher(None, enum_name.lower(), enum["name"].lower()).ratio()
            caption_ratio = 0.0
            if enum.get("caption"):
                caption_ratio = SequenceMatcher(None, enum_name.lower(), enum["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = enum

        # Search in enum extensions
        for enumext in cache.enumext:
            name_ratio = SequenceMatcher(None, enum_name.lower(), enumext["name"].lower()).ratio()
            caption_ratio = 0.0
            if enumext.get("caption"):
                caption_ratio = SequenceMatcher(None, enum_name.lower(), enumext["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = enumext

        if best_match:
            return PageInfo(
                name=best_match["name"],
                app_name=best_match.get("app_name"),
                page_id=best_match.get("id"),
                caption=best_match.get("caption"),
                source_table=best_match.get("source_table"),
                file_path=best_match["location"]
            )
        
        return None

    @staticmethod
    def get_comprehensive_enum_suggestions(enum_name: str, limit: int = 10) -> List[str]:
        """Get comprehensive enum suggestions from both enums and enum extensions"""
        cache = get_al_cache()
        suggestions = []

        # Search in base enums
        for enum in cache.enum:
            name_ratio = SequenceMatcher(None, enum_name.lower(), enum["name"].lower()).ratio()
            caption_ratio = 0.0
            if enum.get("caption"):
                caption_ratio = SequenceMatcher(None, enum_name.lower(), enum["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > 0.3:
                suggestions.append((enum["name"], ratio))

        # Search in enum extensions
        for enumext in cache.enumext:
            name_ratio = SequenceMatcher(None, enum_name.lower(), enumext["name"].lower()).ratio()
            caption_ratio = 0.0
            if enumext.get("caption"):
                caption_ratio = SequenceMatcher(None, enum_name.lower(), enumext["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > 0.3:
                suggestions.append((enumext["name"], ratio))

        # Sort by ratio and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in suggestions[:limit]]
    
    @staticmethod
    def get_codeunit_info(codeunit_name: str) -> Optional[PageInfo]:
        """Get exact codeunit info by name from both codeunits"""
        cache = get_al_cache()

        # Search in base codeunits first
        for codeunit in cache.codeunit:
            if codeunit["name"].lower() == codeunit_name.lower():
                return PageInfo(
                    name=codeunit["name"],
                    app_name=codeunit.get("app_name"),
                    page_id=codeunit.get("id"),
                    caption=codeunit.get("caption"),
                    source_table=codeunit.get("source_table"),
                    file_path=codeunit["location"]
                )
        
        return None

    @staticmethod
    def get_codeunit_info_fuzzy(codeunit_name: str, threshold: float = 0.6) -> Optional[PageInfo]:
        """Get codeunit info using fuzzy matching from both codeunits"""
        cache = get_al_cache()
        
        best_match = None
        best_ratio = 0.0

        # Search in base codeunits
        for codeunit in cache.codeunit:
            name_ratio = SequenceMatcher(None, codeunit_name.lower(), codeunit["name"].lower()).ratio()
            caption_ratio = 0.0
            if codeunit.get("caption"):
                caption_ratio = SequenceMatcher(None, codeunit_name.lower(), codeunit["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = codeunit

        if best_match:
            return PageInfo(
                name=best_match["name"],
                app_name=best_match.get("app_name"),
                page_id=best_match.get("id"),
                caption=best_match.get("caption"),
                source_table=best_match.get("source_table"),
                file_path=best_match["location"]
            )
        
        return None

    @staticmethod
    def get_comprehensive_codeunit_suggestions(codeunit_name: str, limit: int = 10) -> List[str]:
        """Get comprehensive codeunit suggestions from both codeunits"""
        cache = get_al_cache()
        suggestions = []

        # Search in base codeunits
        for codeunit in cache.codeunit:
            name_ratio = SequenceMatcher(None, codeunit_name.lower(), codeunit["name"].lower()).ratio()
            caption_ratio = 0.0
            if codeunit.get("caption"):
                caption_ratio = SequenceMatcher(None, codeunit_name.lower(), codeunit["caption"].lower()).ratio()

            ratio = max(name_ratio, caption_ratio)
            if ratio > 0.3:
                suggestions.append((codeunit["name"], ratio))

        # Sort by ratio and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in suggestions[:limit]]