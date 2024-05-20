import pytest
from unittest.mock import MagicMock, patch
from src.controllers.recipecontroller import RecipeController
from src.util.dao import DAO
from src.static.diets import Diet
from src.util.calculator import calculate_readiness


# MockDAO
class MockDAO:
    def setUp(self):
        self.mock_dao = MagicMock(spec=DAO)

        self.controller = RecipeController(items_dao=self.mock_dao)
        
        self.mock_recipes = [
            {"name": "Salad", "diets": ["vegetarian"], "ingredients": {"lettuce": 2, "tomato": 5}},
            {"name": "Veal", "diets": ["non_vegetarian"], "ingredients": {"lettuce": 2, "tomato": 5}},
        ]
        
        self.controller.load_recipes = MagicMock(return_value=self.mock_recipes)
        self.controller.recipes = self.controller.load_recipes()

# Fixture
@pytest.fixture
def mock_dao():
    mock_dao_instance = MockDAO()
    mock_dao_instance.setUp()
    return mock_dao_instance

@pytest.mark.unit
@patch('src.util.calculator.calculate_readiness')
def test_get_recipe_full_readiness(mock_calculate_readiness, mock_dao):
    # Test case 1: Full readiness
    mock_calculate_readiness.side_effect = lambda recipe, available_items: 1.0 if recipe["name"] == "Salad" else 0.0
    
    mock_dao.controller.get_available_items = MagicMock(return_value={"lettuce": 2, "tomato": 5})
    
    selected_recipe_name = mock_dao.controller.get_recipe(diet=Diet.VEGETARIAN, take_best=True)
    assert selected_recipe_name == "Salad"

@pytest.mark.unit
@patch('src.util.calculator.calculate_readiness')
def test_get_recipe_incomplete_diet(mock_calculate_readiness, mock_dao):
    # Test case 2: Incomplete diet
    mock_calculate_readiness.side_effect = lambda recipe, available_items: 1.0 if recipe["name"] == "Salad" else 0.0
    
    mock_dao.controller.get_available_items = MagicMock(return_value={"lettuce": 2, "tomato": 5})
    
    selected_recipe_name = mock_dao.controller.get_recipe(diet=Diet.NON_VEGETARIAN, take_best=True)
    assert selected_recipe_name is None

@pytest.mark.unit
@patch('src.util.calculator.calculate_readiness')
def test_get_recipe_insufficient_ingredients(mock_calculate_readiness, mock_dao):
    # Test case 3: Insufficient ingredients
    mock_calculate_readiness.side_effect = lambda recipe, available_items: 0.0
    
    mock_dao.controller.get_available_items = MagicMock(return_value={"lettuce": 0, "tomato": 0})
    
    selected_recipe_name = mock_dao.controller.get_recipe(diet=Diet.VEGETARIAN, take_best=True)
    assert selected_recipe_name is None

@pytest.mark.unit
@patch('src.util.calculator.calculate_readiness')
def test_get_recipe_partial_readiness(mock_calculate_readiness, mock_dao):
    # Test case 4: Partial readiness
    mock_calculate_readiness.side_effect = lambda recipe, available_items: 0.5 if recipe["name"] == "Salad" else 0.0
    
    mock_dao.controller.get_available_items = MagicMock(return_value={"lettuce": 2, "tomato": 0})
    
    selected_recipe_name = mock_dao.controller.get_recipe(diet=Diet.VEGETARIAN, take_best=True)
    assert selected_recipe_name == "Salad"