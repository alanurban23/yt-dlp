FROM python:3.12-alpine
WORKDIR /app
RUN apk add --no-cache ffmpeg python3 py3-pip \
    && pip install --no-cache-dir yt-dlp
COPY . .
ENTRYPOINT ["yt-dlp"]
