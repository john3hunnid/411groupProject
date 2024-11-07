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
    echo "prepping meal ($meal)..."
    response=$(curl -s -X GET "$BASE_URL/prep-combatant/$meal")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "combatant successfully prepped ($meal)."
    else
        echo "Failed to prep combatant ($meal)."
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
# Health checks
check_health
check_db

#battle model tests

prep_combatant 1 "Cake" "desert" 10 'MED'
prep_combatant 2 "BLT" "sandwich" 8 'LOW'

get_combatants
battle

clear_combatants

echo "All tests passed successfully"
