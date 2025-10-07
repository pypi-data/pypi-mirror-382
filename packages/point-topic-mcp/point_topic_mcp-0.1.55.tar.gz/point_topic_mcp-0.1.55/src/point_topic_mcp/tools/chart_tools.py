"""Chart generation and access tools."""

from typing import Optional
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from dotenv import load_dotenv
import os

load_dotenv()

# Public chart tools (no credentials needed) - always available
def get_point_topic_public_chart_catalog(ctx: Optional[Context[ServerSession, None]] = None) -> str:
    """Get all available public charts from the Point Topic Charts API.
    
    Fetches the public chart catalog (no authentication required).
    
    Returns:
        JSON string containing public chart catalog with titles, parameters, and example URLs.
    """
    import requests
    import json
    response = requests.get("https://charts.point-topic.com/public")
    return json.dumps(response.json())


def get_point_topic_public_chart_csv(url: str, ctx: Optional[Context[ServerSession, None]] = None) -> str:
    """Get a specific public chart from Point Topic Charts API as CSV.
    
    Use this to fetch chart data for context when displaying charts.
    For iframe embedding, use URL without format parameter.
    
    Args:
        url: Chart URL WITHOUT the format parameter (e.g., no &format=png/csv).
    
    Returns: CSV string with chart data
    """
    import urllib.parse
    import requests

    # strip any existing format param and add format=csv
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    query.pop('format', None)
    query['format'] = 'csv'
    csv_url = urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query, doseq=True)))

    resp = requests.get(csv_url)
    if resp.status_code != 200:
        return f"Error: {resp.status_code} {resp.text}"
    
    return resp.text


# Authenticated chart tools (require API key) - TEMPORARILY DISABLED
# Uncomment the block below when the production issues are fixed

# Authenticated chart tools (require API key) - ONLY if API key present
# if has_chart_api_key:
#     # Track for status reporting
#     check_env_vars('chart_tools', ['CHART_API_KEY'])
#     def get_point_topic_chart_catalog(format_type: str = "json", ctx: Optional[Context[ServerSession, None]] = None) -> str:
#         """Get complete chart catalog with required parameters AND valid values.
        
#         CRITICAL: Check 'required_params' for EACH chart before generating URLs.
#         Most charts require 'period' - NOT optional if listed as required.
        
#         Catalog now includes valid period values for each chart.
#         Use the MOST RECENT period shown unless user specifies otherwise.
        
#         Args:
#             format_type: "json" (default) or "html"
            
#         Returns:
#             Chart metadata with required_params AND valid period values.
#         """
#         import requests
#         import os
        
#         api_key = os.getenv("CHART_API_KEY")
#         headers = {
#             "X-API-Key": api_key,
#             "User-Agent": "MCP-Server/1.0"
#         }
        
#         # Determine URL based on format
#         if format_type.lower() == "html":
#             url = "https://charts.point-topic.com/catalog?pretty=true"
#         else:
#             url = "https://charts.point-topic.com/catalog"
        
#         try:
#             response = requests.get(url, headers=headers, timeout=30.0)
            
#             if response.status_code == 401:
#                 return "Error: Invalid API key. Check CHART_API_KEY environment variable."
#             elif response.status_code != 200:
#                 return f"Error: API returned status {response.status_code}: {response.text}"
            
#             if format_type.lower() == "html":
#                 return f"HTML catalog retrieved successfully. View at: {url}"
#             else:
#                 return response.text
                
#         except requests.exceptions.Timeout:
#             return "Error: Request timed out after 30 seconds"
#         except Exception as e:
#             return f"Error fetching catalog: {str(e)}"
    
#     def get_point_topic_chart_csv(url: str, ctx: Optional[Context[ServerSession, None]] = None) -> str:
#         """Get chart data as CSV. URL must include ALL required parameters.
        
#         If you get "Missing required parameters" error, check catalog for required_params
#         and regenerate URL with all required parameters (especially 'period').
        
#         Args:
#             url: Full chart URL with all required params (without format param)
        
#         Returns: CSV data or error showing which required params are missing
#         """
#         import urllib.parse
#         import requests
#         import os

#         api_key = os.getenv("CHART_API_KEY")
        
#         # strip any existing format param and add format=csv
#         parsed = urllib.parse.urlparse(url)
#         query = urllib.parse.parse_qs(parsed.query)
#         query.pop('format', None)
#         query['format'] = 'csv'
#         csv_url = urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query, doseq=True)))

#         headers = {
#             "X-API-Key": api_key,
#             "User-Agent": "MCP-Server/1.0"
#         }
        
#         resp = requests.get(csv_url, headers=headers, timeout=30.0)
        
#         if resp.status_code == 401:
#             return "Error: Invalid API key. Check CHART_API_KEY environment variable."
#         elif resp.status_code != 200:
#             return f"Error: {resp.status_code} {resp.text}"
        
#         return resp.text
    
#     def generate_authenticated_chart_url(
#         project: str,
#         chart_name: str,
#         period: str = "",
#         la_code: str = "",
#         additional_params: dict = {},
#         ctx: Optional[Context[ServerSession, None]] = None
#     ) -> str:
#         """Generate signed chart URL. ALWAYS check catalog first for required_params and valid periods.
        
#         CRITICAL: Most charts require 'period' parameter. 
#         Catalog shows required_params AND valid period values - use most recent period.
        
#         Args:
#             project: Chart project (e.g., 'broadband_geography')
#             chart_name: Chart name (e.g., 'ward_build_progress')
#             period: Time period - REQUIRED for most charts (see catalog for valid values)
#             la_code: Local authority code (e.g., 'E09000033')
#             additional_params: Other params as dict
        
#         Returns:
#             Iframe-ready URL with token (expires in 24h)
        
#         Examples:
#             # Step 1: Check catalog for required_params and valid periods
#             get_point_topic_chart_catalog()
#             # Shows: required_params: ['period', 'la_code'], valid_periods: ['2024Q4', '2024Q3']
            
#             # Step 2: Generate URL with valid period from catalog
#             generate_authenticated_chart_url("broadband_geography", "ward_build_progress", 
#                                             period="2024Q4", la_code="E09000033")
#         """
#         import requests
#         import json
#         import os
        
#         # Build params dict from individual parameters
#         params = {}
#         if period:
#             params['period'] = period
#         if la_code:
#             params['la_code'] = la_code
#         if additional_params:
#             params.update(additional_params)
        
#         # Get Chart API key from environment (we know it exists due to conditional registration)
#         api_key = os.getenv("CHART_API_KEY")
        
#         # Build request payload
#         payload = {
#             "charts": [{
#                 "project": project,
#                 "chart_name": chart_name,
#                 "params": params
#             }],
#             "expires_in_hours": 24
#         }
        
#         try:
#             response = requests.post(
#                 "https://charts.point-topic.com/token/generate",
#                 headers={
#                     "X-API-Key": api_key,
#                     "Content-Type": "application/json"
#                 },
#                 json=payload,
#                 timeout=10
#             )
            
#             # Debug info for troubleshooting
#             debug_info = f"\n\nDEBUG INFO:\n"
#             debug_info += f"Request URL: https://charts.point-topic.com/token/generate\n"
#             debug_info += f"Payload: {json.dumps(payload, indent=2)}\n"
#             debug_info += f"Response Status: {response.status_code}\n"
#             debug_info += f"Response Headers: {dict(response.headers)}\n"
#             debug_info += f"Response Body: {response.text}\n"
            
#             if response.status_code == 401:
#                 return "Error: Invalid Chart API key. Check CHART_API_KEY in environment." + debug_info
            
#             if response.status_code != 200:
#                 return f"Error generating token: HTTP {response.status_code} - {response.text[:200]}" + debug_info
            
#             result = response.json()
#             return result["tokens"][0]["iframe_url"]
            
#         except requests.exceptions.Timeout:
#             return "Error: Request timed out while generating token"
#         except requests.exceptions.RequestException as e:
#             return f"Error: Network request failed - {str(e)}"
#         except Exception as e:
#             return f"Error: {str(e)}"