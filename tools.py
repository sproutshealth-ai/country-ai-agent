"""
Tools for interacting with the REST Countries API
"""
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CountryAPITool:
    """Tool for fetching country information from REST Countries API"""

    BASE_URL = "https://restcountries.com/v3.1"

    @staticmethod
    def fetch_country_data(country_name: str) -> Dict[str, Any]:
        """
        Fetch country data from REST Countries API

        Args:
            country_name: Name of the country to search for

        Returns:
            Dictionary containing country data or error information
        """
        try:
            url = f"{CountryAPITool.BASE_URL}/name/{country_name}"
            logger.info(f"Fetching data for country: {country_name}")

            response = requests.get(url, timeout=10)

            if response.status_code == 404:
                return {
                    "success": False,
                    "error": "country_not_found",
                    "message": f"Country '{country_name}' not found"
                }

            response.raise_for_status()
            data = response.json()

            if not data or len(data) == 0:
                return {
                    "success": False,
                    "error": "no_data",
                    "message": f"No data available for '{country_name}'"
                }

            # Return the first match (most relevant)
            country = data[0]

            # Extract and structure the relevant information
            result = {
                "success": True,
                "data": {
                    "name": {
                        "common": country.get("name", {}).get("common", "N/A"),
                        "official": country.get("name", {}).get("official", "N/A")
                    },
                    "capital": country.get("capital", ["N/A"])[0] if country.get("capital") else "N/A",
                    "population": country.get("population", "N/A"),
                    "area": country.get("area", "N/A"),
                    "region": country.get("region", "N/A"),
                    "subregion": country.get("subregion", "N/A"),
                    "currencies": CountryAPITool._extract_currencies(country.get("currencies", {})),
                    "languages": CountryAPITool._extract_languages(country.get("languages", {})),
                    "timezones": country.get("timezones", ["N/A"]),
                    "borders": country.get("borders", []),
                    "flag": country.get("flag", ""),
                    "maps": country.get("maps", {}).get("googleMaps", "N/A"),
                    "continents": country.get("continents", ["N/A"])
                }
            }

            logger.info(f"Successfully fetched data for: {result['data']['name']['common']}")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching data for: {country_name}")
            return {
                "success": False,
                "error": "timeout",
                "message": "Request timed out. Please try again."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {country_name}: {str(e)}")
            return {
                "success": False,
                "error": "api_error",
                "message": f"Failed to fetch country data: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error for {country_name}: {str(e)}")
            return {
                "success": False,
                "error": "unknown_error",
                "message": f"An unexpected error occurred: {str(e)}"
            }

    @staticmethod
    def _extract_currencies(currencies: Dict) -> list:
        """Extract currency information from API response"""
        if not currencies:
            return []

        result = []
        for code, info in currencies.items():
            result.append({
                "code": code,
                "name": info.get("name", "N/A"),
                "symbol": info.get("symbol", "")
            })
        return result

    @staticmethod
    def _extract_languages(languages: Dict) -> list:
        """Extract language information from API response"""
        if not languages:
            return []

        return list(languages.values())
