import json
import requests
import logging
import time
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
try:
    from .config import config
except ImportError:
    from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Load the environment variables from the .env file
load_dotenv()


def get_law_interpretations(
    query: str, display: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Calls the National Law Information Center API to get a list of legal interpretations.
    Includes retry logic and timeout handling.

    Args:
        query: The search query string for legal interpretations.
        display: Number of results to display (default: from config).

    Returns:
        A dictionary containing the JSON response from the API, or None if an error occurs.
    """
    logger.info(f"Searching for legal interpretations with query: '{query}'")

    # Get parameters from config
    params = config.get_law_api_params(query, display)

    # Retry logic with exponential backoff
    for attempt in range(config.MAX_RETRIES):
        try:
            logger.debug(f"API request attempt {attempt + 1}/{config.MAX_RETRIES}")

            # Make the GET request to the API with timeout
            response = requests.get(
                config.LAW_SEARCH_URL, params=params, timeout=config.REQUEST_TIMEOUT
            )

            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            logger.info(f"Successfully retrieved results for query: '{query}'")
            return response.json()

        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout on attempt {attempt + 1}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.RETRY_DELAY * (attempt + 1))
                continue
            logger.error("Max retries reached due to timeout")
            return None

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logger.error(f"HTTP error occurred: {status_code} - {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed on attempt {attempt + 1}: {e}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.RETRY_DELAY * (attempt + 1))
                continue
            logger.error("Max retries reached")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None

    return None


def parse_interpretation_list(
    json_data: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Parses the raw JSON data from the list API to extract key legal interpretation information.
    This version correctly handles both 'lawSearch' and 'CgmExpc' nesting.

    Args:
        json_data: The dictionary object loaded from the API's JSON response.

    Returns:
        A list of dictionaries, where each dictionary contains key information for one interpretation.
    """
    if not json_data:
        logger.error("JSON data is empty or None")
        return []

    interpretation_items = []

    # Check for the 'lawSearch' nesting (previous structure)
    if "lawSearch" in json_data and "moelCgmExpc" in json_data["lawSearch"]:
        interpretation_items = json_data["lawSearch"]["moelCgmExpc"]
    # Check for the 'CgmExpc' nesting (new structure)
    elif "CgmExpc" in json_data and "cgmExpc" in json_data["CgmExpc"]:
        interpretation_items = json_data["CgmExpc"]["cgmExpc"]
    else:
        logger.error("Unexpected JSON data structure")
        return []

    # Check if the found list is a list
    if not isinstance(interpretation_items, list):
        # If it's a single dictionary (e.g., only one result), put it in a list to handle it uniformly
        if isinstance(interpretation_items, dict):
            interpretation_items = [interpretation_items]
        else:
            logger.error("The final field is not a list or dict")
            return []

    interpretation_list = []

    for item in interpretation_items:
        # Extract the key fields from each interpretation item
        # Build the full URL for the legal interpretation
        interpretation_link = None
        if item.get("법령해석상세링크"):
            base_url = "http://www.law.go.kr"
            link_path = item.get("법령해석상세링크")
            interpretation_link = base_url + link_path
        
        parsed_item = {
            "case_number": item.get("안건번호"),
            "case_name": item.get("안건명"),
            "interpretation_id": item.get("법령해석일련번호"),
            "inquiry_org": item.get("질의기관명"),
            "reply_date": item.get("해석일자"),
            "link": interpretation_link,
        }
        interpretation_list.append(parsed_item)

    logger.info(f"Parsed {len(interpretation_list)} interpretations")
    return interpretation_list


def get_full_interpretation_text(interpretation_id: str) -> Optional[Dict[str, Any]]:
    """
    Calls the National Law Information Center API to get the full text of a legal interpretation.
    Includes retry logic and timeout handling.

    Args:
        interpretation_id: The ID number of the legal interpretation (e.g., '21822').

    Returns:
        A dictionary containing the JSON response from the API, or None if an error occurs.
    """
    logger.info(f"Retrieving full text for interpretation ID: {interpretation_id}")

    # Get parameters from config
    params = config.get_law_service_params(interpretation_id)

    # Retry logic with exponential backoff
    for attempt in range(config.MAX_RETRIES):
        try:
            logger.debug(f"API request attempt {attempt + 1}/{config.MAX_RETRIES}")

            response = requests.get(
                config.LAW_SERVICE_URL, params=params, timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            logger.info(f"Successfully retrieved full text for ID: {interpretation_id}")
            return response.json()

        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout on attempt {attempt + 1}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.RETRY_DELAY * (attempt + 1))
                continue
            logger.error("Max retries reached due to timeout")
            return None

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logger.error(f"HTTP error occurred: {status_code} - {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed on attempt {attempt + 1}: {e}")
            if attempt < config.MAX_RETRIES - 1:
                time.sleep(config.RETRY_DELAY * (attempt + 1))
                continue
            logger.error("Max retries reached")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None

    return None


def parse_full_text(json_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parses the raw JSON data from the full-text API to extract key information.

    Args:
        json_data: The dictionary object loaded from the full-text API's JSON response.

    Returns:
        A dictionary containing the parsed legal text and metadata.
    """
    if not json_data or "CgmExpcService" not in json_data:
        logger.error(
            "Invalid JSON data structure for full text or 'CgmExpcService' key not found"
        )
        return {}

    service_data = json_data["CgmExpcService"]

    # Extract the core content and metadata
    parsed_data = {
        "text": f"질의요지: {service_data.get('질의요지', '')}\n\n회답: {service_data.get('회답', '')}",
        "metadata": {
            "title": service_data.get("안건명"),
            "interpretation_id": service_data.get("법령해석일련번호"),
            "reply_date": service_data.get("해석일자"),
        },
    }

    logger.debug(f"Parsed full text for: {parsed_data['metadata']['title']}")
    return parsed_data


if __name__ == "__main__":
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        exit(1)

    test_query = "퇴직"
    logger.info(f"Searching for legal interpretations related to '{test_query}'...")

    raw_list_data = get_law_interpretations(test_query)

    if raw_list_data:
        print("\n--- Raw List JSON Data ---")
        print(json.dumps(raw_list_data, indent=4, ensure_ascii=False))
        print("---------------------")

        logger.info("Successfully received raw list data. Now parsing...")
        parsed_list = parse_interpretation_list(raw_list_data)

        if parsed_list:
            first_interpretation_id = parsed_list[0]["interpretation_id"]
            logger.info(
                f"Found interpretation ID '{first_interpretation_id}'. Now retrieving full text..."
            )

            full_text_data = get_full_interpretation_text(first_interpretation_id)

            if full_text_data:
                logger.info("Successfully retrieved raw full text data. Now parsing...")
                parsed_full_text = parse_full_text(full_text_data)
                print("\nSuccessfully parsed full text data:")
                print(json.dumps(parsed_full_text, indent=4, ensure_ascii=False))
            else:
                logger.error("Failed to retrieve full text data from the API")
        else:
            logger.warning("Could not parse the received list data")
    else:
        logger.error("Failed to retrieve list data from the API")
