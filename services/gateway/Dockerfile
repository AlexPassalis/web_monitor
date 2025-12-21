FROM nginx:1.27.4-alpine AS base
# Install curl for the healthcheck
RUN apk add --no-cache curl

COPY nginx-development.conf /etc/nginx/nginx.conf
COPY certs/ /etc/nginx/certs/
