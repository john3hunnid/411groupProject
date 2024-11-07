import unittest
from unittest.mock import MagicMock, patch
import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, update_meal_stats
@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of the BattleModel for each test"""
    return BattleModel()


"""Fixture for providing sample meals"""

@pytest.fixture
def sample_meal1():
    #the score should be: 58
    return Meal(1, "Cake", "desert",10, 'MED')

@pytest.fixture
def sample_meal2():
    #the score should be: 61
    return Meal(2, "BLT", "sandwich", 8, 'LOW')

@pytest.fixture
def sample_meal3():
    return Meal(3, "Pizza", "dinner", 7, 'HIGH')

@pytest.fixture
def sample_combatants():
    return[sample_meal1,sample_meal2]






####################################################
# Get combatant and Get Score Test Cases
####################################################

def test_get_battle_score(battle_model, sample_meal1):
    """testing the get_battle_score method"""
    expected_score=58.0
    returned_score=battle_model.get_battle_score(sample_meal1)
    assert expected_score==returned_score

def test_get_combatants(battle_model, sample_meal1):
    """testing the retrieval of the combatants"""
    battle_model.prep_combatant(sample_meal1)
    returned_combatants=battle_model.get_combatants()
    assert returned_combatants[0]==sample_meal1

####################################################
# Adding and Clearing combatants Test Cases
####################################################
def test_prep_combatants(battle_model,sample_meal1,sample_meal2):
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    assert battle_model.combatants[0]==sample_meal1
    assert battle_model.combatants[1]==sample_meal2
    assert len(battle_model.combatants)==2

def test_prepping_too_many(battle_model, sample_meal1,sample_meal2,sample_meal3):
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal3)

def test_clear_combatants(battle_model,sample_meal1):
    """add meals to the combatants list"""
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert 0 == len(battle_model.combatants)

####################################################
# Battle Test Cases
####################################################


@patch("meal_max.utils.random_utils.get_random")
@patch("meal_max.models.kitchen_model.update_meal_stats")
def battle_function(self, mock_update_meal_stats, mock_get_random):
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    mock_get_random.return_value = 0.5
    #meal 2 should be winner (delta=0.03)
    with patch.object(BattleModel, "get_battle_score", side_effect=[58, 61]):
        winner_meal = battle_model.battle()

    assert winner_meal==sample_meal2
    mock_update_meal_stats.assert_any_call(self.combatants[0].id, 'loss')
    mock_update_meal_stats.assert_any_call(self.combatants[1].id, 'win')
    self.assertIn(sample_meal2, self.battle_model.combatants)
    self.assertNotIn(sample_meal1, self.battle_model.combatants)