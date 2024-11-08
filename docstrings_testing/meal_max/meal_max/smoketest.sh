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
# Meal Functions
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating meal ($meal, $cuisine, $price, $difficulty)..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal created successfully: $meal"
  else
    echo "Failed to create meal: $meal"
    echo "$response"
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    echo "$response"
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1
  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    echo "$response"
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1
  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    echo "$response"
    exit 1
  fi
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
############################################################
#
# Leaderboard
#
############################################################
get_leaderboard() {
  sort_by=${1:-wins}
  echo "Getting leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_by")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    echo "$response"
    exit 1
  fi
}



# Health checks
check_health
check_db

#clear the catalog
clear_catalog

# Create meals
create_meal "Pasta" "Italian" 12.50 "MED"
create_meal "Burger" "American" 8.99 "LOW"

#Battle tests
#prep_combatant "Pasta"
#prep_combatant "Burger"
#get_combatants
#battle

# Retrieve meals
get_meal_by_id 1
get_meal_by_name "Burger"
get_meal_by_name "Pasta"

# Delete a meal
delete_meal_by_id 2


# Get leaderboard
get_leaderboard "wins"
clear_combatants

echo "All tests passed successfully!"

