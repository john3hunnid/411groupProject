from contextlib import contextmanager
import re
import sqlite3
import pytest
from unittest.mock import MagicMock, patch

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_meal_by_id,
    get_meal_by_name,
    get_leaderboard,
    update_meal_stats
)

######################################################
# Fixtures and Helpers
######################################################

def normalize_whitespace(sql_query: str) -> str:
    """Helper function to normalize whitespace in SQL queries for comparison."""
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
# Create and Delete Meal Tests
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the catalog."""

    # Call the function to create a new meal
    create_meal(meal="Pasta", cuisine="Italian", price=10.0, difficulty="MED")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Check the arguments
    expected_arguments = ("Pasta", "Italian", 10.0, "MED")
    actual_arguments = mock_cursor.execute.call_args[0][1]
    assert actual_arguments == expected_arguments

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty."""

    with pytest.raises(ValueError, match="Invalid difficulty level: INVALID. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Pizza", cuisine="Italian", price=12.0, difficulty="INVALID")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal by meal ID."""

    mock_cursor.fetchone.return_value = ([False])
    delete_meal(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql
    assert actual_update_sql == expected_update_sql

    expected_select_args = (1,)
    expected_update_args = (1,)
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args
    assert actual_update_args == expected_update_args

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meal catalog."""
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="CREATE TABLE meals"))

    clear_meals()

    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()

######################################################
# Get Meal Tests
######################################################

def test_get_meal_by_id(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "MED", False)

    result = get_meal_by_id(1)
    expected_result = Meal(1, "Pasta", "Italian", 10.0, "MED")

    assert result == expected_result

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query
    expected_arguments = (1,)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    assert actual_arguments == expected_arguments

def test_get_meal_by_name(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "MED", False)

    result = get_meal_by_name("Pasta")
    expected_result = Meal(1, "Pasta", "Italian", 10.0, "MED")

    assert result == expected_result

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query
    expected_arguments = ("Pasta",)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    assert actual_arguments == expected_arguments

def test_get_leaderboard(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 10.0, "MED", 5, 3, 0.6),
        (2, "Pizza", "Italian", 12.0, "LOW", 10, 7, 0.7)
    ]

    leaderboard = get_leaderboard("win_pct")
    assert len(leaderboard) == 2
    assert leaderboard[0]["meal"] == "Pasta"
    assert leaderboard[1]["win_pct"] == 70.0

def test_update_meal_stats(mock_cursor):
    mock_cursor.fetchone.return_value = [False]

    update_meal_stats(1, "win")

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query
    expected_arguments = (1,)
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_arguments == expected_arguments

def test_update_meal_stats_invalid_result():
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(1, "draw")

def test_get_meal_by_id_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with name Pasta not found"):
        get_meal_by_name("Pasta")

def test_get_meal_by_name_deleted(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 12.0, "MED", True)

    with pytest.raises(ValueError, match="Meal with name Pasta has been deleted"):
        get_meal_by_name("Pasta")

def test_delete_meal_already_deleted(mock_cursor):
    mock_cursor.fetchone.return_value = [True]

    with pytest.raises(ValueError, match="Meal with ID 999 has already been deleted"):
        delete_meal(999)


