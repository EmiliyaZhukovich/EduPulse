#!/bin/bash

# Import configuration
# First, start Keycloak to import the configuration
/opt/keycloak/bin/kc.sh import --file /opt/keycloak/init-config.json &

# Wait for the import to complete
sleep 10

# Now start Keycloak in development mode
/opt/keycloak/bin/kc.sh start-dev --http-port=8080

# Keep the container running (this is not needed anymore since start-dev is in foreground)
# wait
