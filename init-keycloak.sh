#!/bin/bash

# Wait for Keycloak to be ready
echo "Waiting for Keycloak to be ready..."
while true; do
    if curl -s http://keycloak:8080/auth/health > /dev/null; then
        break
    fi
    sleep 5
done

# Get admin token
echo "Getting admin token..."
ADMIN_TOKEN=$(curl -s -X POST http://keycloak:8080/auth/realms/master/protocol/openid-connect/token \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=admin' \
    -d 'password=admin' \
    -d 'grant_type=password' \
    -d 'client_id=admin-cli' | jq -r '.access_token')

# Create realm
echo "Creating realm..."
curl -s -X POST http://keycloak:8080/auth/admin/realms \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "realm": "psycho-realm",
        "enabled": true,
        "sslRequired": "external",
        "loginTheme": "keycloak"
    }'

# Create client
echo "Creating client..."
curl -s -X POST http://keycloak:8080/auth/admin/realms/psycho-realm/clients \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "psycho-client",
        "enabled": true,
        "protocol": "openid-connect",
        "redirectUris": ["http://localhost:3000/*"],
        "webOrigins": ["http://localhost:3000"],
        "publicClient": true,
        "standardFlowEnabled": true,
        "directAccessGrantsEnabled": true
    }'

# Create initial test user
echo "Creating test user..."
curl -s -X POST http://keycloak:8080/auth/admin/realms/psycho-realm/users \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "test",
        "enabled": true,
        "emailVerified": true,
        "firstName": "Test",
        "lastName": "User",
        "credentials": [
            {
                "type": "password",
                "value": "test",
                "temporary": false
            }
        ]
    }'

echo "Keycloak initialization completed."
