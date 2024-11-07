import pytest
from unittest.mock import patch, MagicMock
from meal_max.models.kitchen_model import (
    Meal, create_meal, clear_meals, delete_meal,
    get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats
)
import sqlite3


@pytest.fixture
def sample_meal():
    """Fixture to create a sample Meal instance."""
    return Meal(id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty='MED')


def test_meal_initialization(sample_meal):
    """Test the initialization and validation of the Meal class."""
    assert sample_meal.id == 1
    assert sample_meal.meal == "Pasta"
    assert sample_meal.cuisine == "Italian"
    assert sample_meal.price == 10.0
    assert sample_meal.difficulty == "MED"


def test_meal_invalid_price():
    """Test that an error is raised if the price is negative."""
    with pytest.raises(ValueError, match="Price must be a positive value."):
        Meal(id=2, meal="Burger", cuisine="American", price=-5.0, difficulty="LOW")


def test_meal_invalid_difficulty():
    """Test that an error is raised if the difficulty is not valid."""
    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'."):
        Meal(id=3, meal="Salad", cuisine="Vegetarian", price=8.0, difficulty="EASY")


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_create_meal(mock_get_db_connection):
    """Test the create_meal function with valid data."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    create_meal("Soup", "Asian", 15.0, "HIGH")

    mock_conn.cursor().execute.assert_called_once_with(
        "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)",
        ("Soup", "Asian", 15.0, "HIGH")
    )
    mock_conn.commit.assert_called_once()


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_create_meal_invalid_difficulty(mock_get_db_connection):
    """Test create_meal with an invalid difficulty level."""
    with pytest.raises(ValueError, match="Invalid difficulty level: INVALID. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal("Pizza", "Italian", 20.0, "INVALID")


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_clear_meals(mock_get_db_connection):
    """Test the clear_meals function."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    clear_meals()

    mock_conn.cursor().executescript.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_delete_meal(mock_get_db_connection):
    """Test the delete_meal function for marking a meal as deleted."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchone.return_value = (0,)

    delete_meal(1)
    mock_conn.cursor().execute.assert_any_call("UPDATE meals SET deleted = TRUE WHERE id = ?", (1,))
    mock_conn.commit.assert_called_once()


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_delete_nonexistent_meal(mock_get_db_connection):
    """Test delete_meal raises an error if the meal ID does not exist."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_get_leaderboard(mock_get_db_connection):
    """Test the get_leaderboard function."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchall.return_value = [
        (1, "Soup", "Asian", 15.0, "HIGH", 5, 3, 0.6),
        (2, "Salad", "Vegetarian", 10.0, "LOW", 10, 7, 0.7)
    ]

    leaderboard = get_leaderboard("win_pct")
    assert len(leaderboard) == 2
    assert leaderboard[0]["meal"] == "Soup"
    assert leaderboard[1]["win_pct"] == 70.0


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_get_meal_by_id(mock_get_db_connection):
    """Test the get_meal_by_id function with a valid ID."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchone.return_value = (1, "Pizza", "Italian", 20.0, "MED", False)

    meal = get_meal_by_id(1)
    assert meal.id == 1
    assert meal.meal == "Pizza"


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_get_meal_by_id_not_found(mock_get_db_connection):
    """Test get_meal_by_id raises an error if the meal ID does not exist."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        get_meal_by_id(1)


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_update_meal_stats(mock_get_db_connection):
    """Test the update_meal_stats function for a winning result."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchone.return_value = (0,)

    update_meal_stats(1, "win")
    mock_conn.cursor().execute.assert_any_call("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,))
    mock_conn.commit.assert_called_once()


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_update_meal_stats_invalid_result(mock_get_db_connection):
    """Test update_meal_stats raises an error with an invalid result."""
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(1, "draw")

@patch("meal_max.models.kitchen_model.get_db_connection")
def test_get_meal_by_name(mock_get_db_connection):
    """Test the get_meal_by_name function with a valid meal name."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchone.return_value = (1, "Pasta", "Italian", 12.0, "MED", False)

    meal = get_meal_by_name("Pasta")
    assert meal.id == 1
    assert meal.meal == "Pasta"
    assert meal.cuisine == "Italian"
    assert meal.price == 12.0
    assert meal.difficulty == "MED"


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_get_meal_by_name_not_found(mock_get_db_connection):
    """Test get_meal_by_name raises an error if the meal name does not exist."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with name Pasta not found"):
        get_meal_by_name("Pasta")


@patch("meal_max.models.kitchen_model.get_db_connection")
def test_get_meal_by_name_deleted(mock_get_db_connection):
    """Test get_meal_by_name raises an error if the meal is marked as deleted."""
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor().fetchone.return_value = (1, "Pasta", "Italian", 12.0, "MED", True)

    with pytest.raises(ValueError, match="Meal with name Pasta has been deleted"):
        get_meal_by_name("Pasta")

