from typing import Any, Dict, List


def get_response_item_ids(response: Any) -> List[str]:
    """get item ids from a response

    Args:
        response (Any): response object

    Returns:
        List[str]: all ids inside a list
    """
    return [item["id"] for item in response["items"]]
     
def get_regions(youtube: Any) -> Dict[str, str]:
    """retrieves content regions that the YouTube website supports
    
    cost = 1
    
    Args:
        youtube (Any): a resource object with methods for interacting with the service.

    Returns:
        Dict[str, str]: region id mapped with its name
    """
    request = youtube.i18nRegions().list(part="snippet")
    response = request.execute()
    return {region["id"]: region["snippet"]["name"] for region in response["items"]}
