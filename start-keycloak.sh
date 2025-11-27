#!/bin/bash

# Start Keycloak in the background
/opt/keycloak/bin/kc.sh start-dev --http-port=8080 &

# Wait for Keycloak to start
sleep 30

# Run initialization script
sh /opt/keycloak/init-keycloak.sh

# Keep the container running
wait
