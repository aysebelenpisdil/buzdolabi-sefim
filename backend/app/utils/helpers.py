import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def parse_ingredient_list(ingredients_str: str) -> List[str]:
    """
    Helper to safely parse the python-style list string provided in the data
    """
    try:
        # Replace single quotes with double quotes for valid JSON
        # assuming the data format is consistent ['a', 'b']
        valid_json = ingredients_str.replace("'", '"')
        return json.loads(valid_json)
    except Exception as e:
        logger.warning("Failed to parse ingredient list: %s, error: %s", ingredients_str[:100], e)
        return []


def get_ingredient_image_url(name: str) -> str:
    """
    Assuming images are in public/images/ingredients/
    Using simple logic to match filename.
    """
    return f"images/ingredients/{name.lower()}.jpeg"


def get_recipe_image_url(image_name: str) -> str:
    """
    Get recipe image URL
    """
    return f"images/recipies/{image_name}.jpg"

