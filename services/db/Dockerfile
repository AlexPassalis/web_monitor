FROM postgres:17-alpine AS base
# Install only tzdata (for correct UTC handling) and locale support
RUN apk add --no-cache tzdata musl-locales musl-locales-lang
# Set timezone to UTC explicitly
ENV TZ=UTC
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

CMD ["postgres"]
