#!/usr/bin/env python3
"""
Nintendo Museum Booking Assistant MCP Server

A Model Context Protocol server for managing Nintendo Museum booking assistant configuration.
Provides tools for date management and IFTTT webhook configuration.
"""

import asyncio
import json
from typing import Any, Dict, List
from fastmcp import FastMCP
from .config_manager import ConfigManager
from .validators import is_date_in_past, extract_ifttt_key


# Initialize MCP server
mcp = FastMCP("Nintendo Museum Config Manager")

# Global config manager instance
config_manager = ConfigManager()


@mcp.tool()
def get_config_status() -> Dict[str, Any]:
    """
    Get current configuration status including target dates and webhook setup.
    
    Returns:
        Dictionary with current config status
    """
    success, error, status = config_manager.get_config_status()
    
    if not success:
        return {
            "success": False,
            "error": error,
            "status": None
        }
    
    # Add helpful information
    if status["target_dates"]:
        past_dates = [date for date in status["target_dates"] if is_date_in_past(date)]
        status["past_dates_count"] = len(past_dates)
        status["future_dates_count"] = status["target_dates_count"] - len(past_dates)
        if past_dates:
            status["past_dates"] = past_dates
    
    if status["webhook_url"] and status["webhook_configured"]:
        key = extract_ifttt_key(status["webhook_url"])
        status["ifttt_key_preview"] = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
    
    return {
        "success": True,
        "error": None,
        "status": status
    }


@mcp.tool()
def list_target_dates() -> Dict[str, Any]:
    """
    List all currently configured target dates.
    
    Returns:
        Dictionary with current target dates
    """
    success, error, dates = config_manager.get_target_dates()
    
    if not success:
        return {
            "success": False,
            "error": error,
            "dates": []
        }
    
    # Add helpful information about dates
    result = {
        "success": True,
        "error": None,
        "dates": dates,
        "count": len(dates)
    }
    
    if dates:
        past_dates = [date for date in dates if is_date_in_past(date)]
        result["past_dates"] = past_dates
        result["future_dates"] = [date for date in dates if not is_date_in_past(date)]
        result["past_dates_count"] = len(past_dates)
        result["future_dates_count"] = len(result["future_dates"])
    
    return result


@mcp.tool()
def add_target_dates(dates: List[str]) -> Dict[str, Any]:
    """
    Add new target dates to the configuration. Dates are automatically deduplicated and sorted.
    
    Args:
        dates: List of dates in YYYY-MM-DD format to add
        
    Returns:
        Dictionary with operation result and final dates list
    """
    if not dates:
        return {
            "success": False,
            "error": "No dates provided",
            "added_dates": [],
            "final_dates": []
        }
    
    # Get current dates for comparison
    current_success, current_error, current_dates = config_manager.get_target_dates()
    if not current_success:
        return {
            "success": False,
            "error": f"Failed to read current dates: {current_error}",
            "added_dates": [],
            "final_dates": []
        }
    
    success, error, final_dates = config_manager.add_target_dates(dates)
    
    if not success:
        return {
            "success": False,
            "error": error,
            "added_dates": [],
            "final_dates": current_dates
        }
    
    # Calculate which dates were actually added (new ones)
    added_dates = [date for date in final_dates if date not in current_dates]
    
    result = {
        "success": True,
        "error": None,
        "added_dates": added_dates,
        "final_dates": final_dates,
        "added_count": len(added_dates),
        "total_count": len(final_dates)
    }
    
    # Add warnings for past dates
    past_added = [date for date in added_dates if is_date_in_past(date)]
    if past_added:
        result["warning"] = f"Added {len(past_added)} past date(s): {', '.join(past_added)}"
    
    return result


@mcp.tool()
def remove_target_dates(dates: List[str]) -> Dict[str, Any]:
    """
    Remove specific target dates from the configuration.
    
    Args:
        dates: List of dates in YYYY-MM-DD format to remove
        
    Returns:
        Dictionary with operation result and remaining dates list
    """
    if not dates:
        return {
            "success": False,
            "error": "No dates provided",
            "removed_dates": [],
            "final_dates": []
        }
    
    # Get current dates for comparison
    current_success, current_error, current_dates = config_manager.get_target_dates()
    if not current_success:
        return {
            "success": False,
            "error": f"Failed to read current dates: {current_error}",
            "removed_dates": [],
            "final_dates": []
        }
    
    success, error, remaining_dates = config_manager.remove_target_dates(dates)
    
    if not success:
        return {
            "success": False,
            "error": error,
            "removed_dates": [],
            "final_dates": current_dates
        }
    
    # Calculate which dates were actually removed
    removed_dates = [date for date in current_dates if date not in remaining_dates]
    not_found_dates = [date for date in dates if date not in current_dates]
    
    result = {
        "success": True,
        "error": None,
        "removed_dates": removed_dates,
        "final_dates": remaining_dates,
        "removed_count": len(removed_dates),
        "total_count": len(remaining_dates)
    }
    
    if not_found_dates:
        result["warning"] = f"Dates not found (not removed): {', '.join(not_found_dates)}"
    
    return result


@mcp.tool()
def clear_all_target_dates() -> Dict[str, Any]:
    """
    Clear all target dates from the configuration.
    
    Returns:
        Dictionary with operation result
    """
    # Get current dates count for reporting
    current_success, current_error, current_dates = config_manager.get_target_dates()
    current_count = len(current_dates) if current_success else 0
    
    success, error = config_manager.clear_target_dates()
    
    return {
        "success": success,
        "error": error,
        "cleared_count": current_count if success else 0,
        "final_dates": [],
        "total_count": 0
    }


@mcp.tool()
def set_target_dates(dates: List[str]) -> Dict[str, Any]:
    """
    Replace all target dates with the provided list. Dates are automatically deduplicated and sorted.
    
    Args:
        dates: List of dates in YYYY-MM-DD format to set
        
    Returns:
        Dictionary with operation result and final dates list
    """
    success, error = config_manager.set_target_dates(dates)
    
    if not success:
        return {
            "success": False,
            "error": error,
            "final_dates": [],
            "total_count": 0
        }
    
    result = {
        "success": True,
        "error": None,
        "final_dates": dates,
        "total_count": len(dates)
    }
    
    # Add warnings for past dates
    if dates:
        past_dates = [date for date in dates if is_date_in_past(date)]
        if past_dates:
            result["warning"] = f"Set {len(past_dates)} past date(s): {', '.join(past_dates)}"
    
    return result


@mcp.tool()
def get_ifttt_webhook_status() -> Dict[str, Any]:
    """
    Get current IFTTT webhook configuration status.
    
    Returns:
        Dictionary with webhook status information
    """
    success, error, url = config_manager.get_ifttt_webhook_url()
    
    if not success:
        return {
            "success": False,
            "error": error,
            "configured": False,
            "url": "",
            "key_preview": ""
        }
    
    configured = bool(url and 'YOUR_IFTTT_KEY' not in url)
    key_preview = ""
    
    if configured:
        key = extract_ifttt_key(url)
        key_preview = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
    
    return {
        "success": True,
        "error": None,
        "configured": configured,
        "url": url,
        "key_preview": key_preview
    }


@mcp.tool()
def set_ifttt_webhook_url(url: str) -> Dict[str, Any]:
    """
    Set the IFTTT webhook URL in the configuration.
    
    Args:
        url: The complete IFTTT webhook URL
        
    Returns:
        Dictionary with operation result
    """
    success, error = config_manager.set_ifttt_webhook_url(url)
    
    if not success:
        return {
            "success": False,
            "error": error,
            "configured": False,
            "key_preview": ""
        }
    
    key = extract_ifttt_key(url)
    key_preview = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
    
    return {
        "success": True,
        "error": None,
        "configured": True,
        "key_preview": key_preview,
        "message": "IFTTT webhook URL updated successfully"
    }


@mcp.tool()
def set_ifttt_webhook_key(key: str) -> Dict[str, Any]:
    """
    Set the IFTTT webhook key (will construct the full URL automatically).
    
    Args:
        key: The IFTTT webhook key
        
    Returns:
        Dictionary with operation result
    """
    if not key.strip():
        return {
            "success": False,
            "error": "IFTTT key cannot be empty",
            "configured": False,
            "key_preview": ""
        }
    
    # Construct full webhook URL
    url = f"https://maker.ifttt.com/trigger/nintendo_museum_available/with/key/{key.strip()}"
    
    success, error = config_manager.set_ifttt_webhook_url(url)
    
    if not success:
        return {
            "success": False,
            "error": error,
            "configured": False,
            "key_preview": ""
        }
    
    key_preview = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
    
    return {
        "success": True,
        "error": None,
        "configured": True,
        "key_preview": key_preview,
        "message": f"IFTTT webhook key set successfully (key: {key_preview})"
    }


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with mcp.server.run_stdio() as streams:
        await mcp.server.run(
            streams[0], streams[1], mcp.create_initialization_options()
        )


if __name__ == "__main__":
    print("Starting Nintendo Museum Config Manager MCP Server...")
    asyncio.run(main())
