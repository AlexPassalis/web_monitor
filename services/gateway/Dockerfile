FROM nginx:1.27.4-alpine AS base
# Install curl for the healthcheck
RUN apk add --no-cache curl

FROM base AS dev
COPY nginx-development.conf /etc/nginx/nginx.conf

FROM base AS prod
COPY frontend/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
