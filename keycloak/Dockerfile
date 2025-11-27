# Build stage
FROM quay.io/keycloak/keycloak:26.1.2 AS builder

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

# Configure a database vendor
ENV KC_DB=postgres

WORKDIR /opt/keycloak

# Build optimized version
RUN /opt/keycloak/bin/kc.sh build

# Final stage
FROM quay.io/keycloak/keycloak:26.1.2

COPY --from=builder /opt/keycloak/ /opt/keycloak/
COPY init-config.json /opt/keycloak/data/import/realm-export.json

ENV KC_DB=postgres
ENV KC_HTTP_RELATIVE_PATH=/auth

USER root
RUN chown keycloak:keycloak /opt/keycloak -R

USER keycloak

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
CMD ["start-dev", "--import-realm", "--http-port=8080"]
