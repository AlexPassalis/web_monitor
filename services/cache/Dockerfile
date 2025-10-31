FROM valkey/valkey:9-alpine AS base

COPY valkey.conf /etc/valkey/valkey.conf

CMD ["valkey-server", "/etc/valkey/valkey.conf"]
