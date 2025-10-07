"""Chart generation and access tools."""

from typing import Optional
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from point_topic_mcp.core.utils import check_env_vars
from dotenv import load_dotenv
import os

load_dotenv()

# Determine which tools to register based on API key availability
has_chart_api_key = bool(os.getenv("CHART_API_KEY"))

# Public chart tools (no credentials needed) - ONLY if no API key
if not has_chart_api_key:
    def get_point_topic_public_chart_catalog(ctx: Optional[Context[ServerSession, None]] = None) -> str:
        """Get all available public charts from the Point Topic Charts API.
        
        Not needed if you have a CHART_API_KEY. This tool is only needed if you don't have a CHART_API_KEY.

        Fetches the public chart catalog (no authentication required).
        For complete catalog including private charts, use get_point_topic_chart_catalog (requires API key).
        
        Returns:
            JSON string containing public chart catalog with titles, parameters, and example URLs.
        """
        import requests
        import json
        response = requests.get("https://charts.point-topic.com/public")
        return json.dumps(response.json())


    def get_point_topic_public_chart_csv(url: str, ctx: Optional[Context[ServerSession, None]] = None) -> str:
        """Get a specific PUBLIC chart from Point Topic Charts API as CSV.
        
        Not needed if you have a CHART_API_KEY. This tool is only needed if you don't have a CHART_API_KEY.
        
        For private/authenticated charts, use get_point_topic_chart_csv (requires API key).
        
        When displaying charts to the user in an iframe, use this tool to see
        the chart contents and provide context. The user can only see charts if
        you embed them as iframes without the format parameter.
        
        Strategy: Embed the iframe first, then give some context about the chart
        with the info returned by this tool.
        
        Args:
            url: Chart URL WITHOUT the format parameter (e.g., no &format=png/csv).
        
        Returns: csv string with chart data
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


# Authenticated chart tools (require API key) - ONLY if API key present
if has_chart_api_key:
    # Track for status reporting
    check_env_vars('chart_tools', ['CHART_API_KEY'])
    def get_point_topic_chart_catalog(format_type: str = "json", ctx: Optional[Context[ServerSession, None]] = None) -> str:
        """Get the complete Point Topic chart catalog including all public and private charts.
        
        Requires API key authentication to access private charts.
        
        Args:
            format_type: Response format - "json" for API data or "html" for browser view
            
        Returns:
            Complete chart catalog with titles, required parameters, tags, and example URLs.
            JSON format includes: chart titles, required_params, available formats, tags, base_url, examples.
        
        Example response includes:
            - total_charts: count of all available charts
            - charts: dict with chart_path -> metadata (title, required_params, formats, tags)
            - base_url: https://charts.point-topic.com/chart
            - example_url: sample chart URL with parameters
        """
        import requests
        import os
        
        api_key = os.getenv("CHART_API_KEY")
        headers = {
            "X-API-Key": api_key,
            "User-Agent": "MCP-Server/1.0"
        }
        
        # Determine URL based on format
        if format_type.lower() == "html":
            url = "https://charts.point-topic.com/catalog?pretty=true"
        else:
            url = "https://charts.point-topic.com/catalog"
        
        try:
            response = requests.get(url, headers=headers, timeout=30.0)
            
            if response.status_code == 401:
                return "Error: Invalid API key. Check CHART_API_KEY environment variable."
            elif response.status_code != 200:
                return f"Error: API returned status {response.status_code}: {response.text}"
            
            if format_type.lower() == "html":
                return f"HTML catalog retrieved successfully. View at: {url}"
            else:
                return response.text
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out after 30 seconds"
        except Exception as e:
            return f"Error fetching catalog: {str(e)}"
    
    def get_point_topic_chart_csv(url: str, ctx: Optional[Context[ServerSession, None]] = None) -> str:
        """Get a specific chart (public or private) from Point Topic Charts API as CSV.
        
        Requires API key authentication. Use this for both public and private charts when you have credentials.
        For public charts without credentials, use get_point_topic_public_chart_csv.
        
        When displaying charts to the user in an iframe, use this tool to see
        the chart contents and provide context.
        
        Args:
            url: Chart URL WITHOUT the format parameter (e.g., no &format=png/csv).
        
        Returns: csv string with chart data
        """
        import urllib.parse
        import requests
        import os

        api_key = os.getenv("CHART_API_KEY")
        
        # strip any existing format param and add format=csv
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        query.pop('format', None)
        query['format'] = 'csv'
        csv_url = urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query, doseq=True)))

        headers = {
            "X-API-Key": api_key,
            "User-Agent": "MCP-Server/1.0"
        }
        
        resp = requests.get(csv_url, headers=headers, timeout=30.0)
        
        if resp.status_code == 401:
            return "Error: Invalid API key. Check CHART_API_KEY environment variable."
        elif resp.status_code != 200:
            return f"Error: {resp.status_code} {resp.text}"
        
        return resp.text
    
    def generate_authenticated_chart_url(
        project: str,
        chart_name: str,
        period: str = "",
        la_code: str = "",
        additional_params: dict = {},
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Generate signed URL for embedding private charts with iframe.
        
        Creates temporary token that expires after specified hours (default 24).
        Use this for charts that require authentication (non-public charts).
        
        For public charts, continue using get_point_topic_public_chart_catalog().
        
        Args:
            project: Chart project name (e.g., 'inca', 'ukplus')
            chart_name: Chart name (e.g., 'footprint_subs_openreach_altnet')
            period: Chart period parameter (e.g., '2024Q4') [optional]
            la_code: Local Authority code (e.g., 'E09000033') [optional]
            additional_params: Any other chart parameters as dict [optional]
        
        Returns:
            Iframe-ready URL with embedded token that expires in 24 hours.
            Embed like: <iframe src="RETURNED_URL" width="800" height="600"></iframe>
        
        Example:
            url = generate_authenticated_chart_url(
                "inca",
                "footprint_subs_openreach_altnet",
                period="2024Q4",
                la_code="E09000033"
            )
            # Returns: https://charts.point-topic.com/chart/inca/footprint_subs_openreach_altnet?period=2024Q4&la_code=E09000033&token=eyJhbGc...
        """
        import requests
        import json
        import os
        
        # Build params dict from individual parameters
        params = {}
        if period:
            params['period'] = period
        if la_code:
            params['la_code'] = la_code
        if additional_params:
            params.update(additional_params)
        
        # Get Chart API key from environment (we know it exists due to conditional registration)
        api_key = os.getenv("CHART_API_KEY")
        
        # Build request payload
        payload = {
            "charts": [{
                "project": project,
                "chart_name": chart_name,
                "params": params
            }],
            "expires_in_hours": 24
        }
        
        try:
            response = requests.post(
                "https://charts.point-topic.com/token/generate",
                headers={
                    "X-API-Key": api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            
            # Debug info for troubleshooting
            debug_info = f"\n\nDEBUG INFO:\n"
            debug_info += f"Request URL: https://charts.point-topic.com/token/generate\n"
            debug_info += f"Payload: {json.dumps(payload, indent=2)}\n"
            debug_info += f"Response Status: {response.status_code}\n"
            debug_info += f"Response Headers: {dict(response.headers)}\n"
            debug_info += f"Response Body: {response.text}\n"
            
            if response.status_code == 401:
                return "Error: Invalid Chart API key. Check CHART_API_KEY in environment." + debug_info
            
            if response.status_code != 200:
                return f"Error generating token: HTTP {response.status_code} - {response.text[:200]}" + debug_info
            
            result = response.json()
            return result["tokens"][0]["iframe_url"]
            
        except requests.exceptions.Timeout:
            return "Error: Request timed out while generating token"
        except requests.exceptions.RequestException as e:
            return f"Error: Network request failed - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
