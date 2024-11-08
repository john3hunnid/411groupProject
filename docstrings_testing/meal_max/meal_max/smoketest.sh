#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}
clear_catalog() {
  echo "Clearing the playlist..."
  curl -s -X DELETE "$BASE_URL/clear-catalog" | grep -q '"status": "success"'
}
##########################################################
#
# Battle Model 
#
##########################################################

get_combatants(){
    echo "Getting all combatants"
    response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get Combatants."
    exit 1
  fi
}

clear_combatants(){
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi

}

prep_combatant(){
    meal=$1
    echo "prepping meal: ($meal)..."
    response=$(curl -s -X POST "$BASE_URL/prep-combatant"\
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "combatant successfully prepped ($meal)."
    else
        echo "Failed to prep combatant ($meal)"
        exit 1
    fi
}

battle(){
  echo "starting battle...."
  response=$(curl -s -X GET "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Winner:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to battle."
    exit 1
  fi

}
##########################################################
#
# Meal Functions
#
##########################################################

create_meal() {
  echo "Creating meal: Pasta..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" \
    -H "Content-Type: application/json" \
    -d '{"meal": "Pasta", "cuisine": "Italian", "price": 10.0, "difficulty": "MED"}')
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal created successfully."
  else
    echo "Failed to create meal."
    exit 1
  fi
}

# Function to clear the meal catalog
clear_catalog() {
  echo "Clearing the meal catalog..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Catalog cleared successfully."
  else
    echo "Failed to clear catalog."
    exit 1
  fi
}

# Function to delete a meal by ID
delete_meal() {
  echo "Deleting meal by ID: 1..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/1")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal."
    exit 1
  fi
}

# Function to get a meal by ID
get_meal_by_id() {
  echo "Retrieving meal by ID: 1..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/1")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID."
  else
    echo "Failed to retrieve meal by ID."
    exit 1
  fi
}

# Function to get a meal by name
get_meal_by_name() {
  echo "Retrieving meal by name: Pasta..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/Pasta")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
  else
    echo "Failed to retrieve meal by name."
    exit 1
  fi
}

# Function to get the leaderboard
get_leaderboard() {
  echo "Retrieving leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

#clear the catalog
clear_catalog

#battle model tests
clear_combatants

prep_combatant  "Cake" 
prep_combatant "BLT"

get_combatants
battle

clear_combatants
# Meal functions
clear_catalog
create_meal
get_meal_by_id
get_meal_by_name
delete_meal
get_leaderboard

echo "All tests passed successfully"
