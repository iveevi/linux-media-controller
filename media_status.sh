#!/bin/bash

# Files
CACHE_FILE="/tmp/spotify_status_cache.txt"
IMAGE_FILE="$HOME/.cache/media_album_cover"

# Get media player to query
if [ -z "$1" ]; then
    PLAYER="spotify"
else
    PLAYER="$1"
fi

# Get playing status
status=$(playerctl -p $PLAYER status 2> /dev/null)

# Check if spotify is even running
if [ ! "$status" ]; then
	echo ":$PLAYER is not running::0:0"
	exit 0
fi

# Get icon for status
case $status in
    "Playing")
	icon=" "
	;;
    "Paused")
	icon="喇 "
	;;
    "Stopped")
	icon="[x]"
	;;
    *)
	echo "Unknown status"
	exit 1
	;;
esac

# Get artist, title, and album
artist=$(playerctl -p $PLAYER metadata artist 2> /dev/null)
title=$(playerctl -p $PLAYER metadata title 2> /dev/null)
album=$(playerctl -p $PLAYER metadata album 2> /dev/null)

if [ "$title" = "Advertisement" ]; then
	artist="Spotify"
	album="Advertisement"
fi

if [ "$title" = "Spotify" ]; then
	title="Advertisement"
	artist="Spotify"
	album="Advertisement"
fi

# Get song length and current position
length=$(playerctl -p $PLAYER metadata --format "{{ duration(mpris:length) }}" 2> /dev/null)
position=$(playerctl -p $PLAYER metadata --format "{{ duration(position) }}" 2> /dev/null)

# Convert to seconds
length_min=$(echo $length | cut -d ':' -f 1)
length_sec=$(echo $length | cut -d ':' -f 2)
length_sec=$((10#$length_sec + (10#$length_min * 60)))

position_min=$(echo $position | cut -d ':' -f 1)
position_sec=$(echo $position | cut -d ':' -f 2)
position_sec=$((10#$position_sec + (10#$position_min * 60)))

# Get album conver url
album_cover=$(playerctl -p $PLAYER metadata --format "{{ mpris:artUrl }}" 2> /dev/null)

# Read url from cache file if it exists
if [ -f "$CACHE_FILE" ]; then
	cached=$(cat $CACHE_FILE)
fi

# If not cached, download it
if [ ! "$cached" ] || [ "$cached" != "$album_cover" ] || [ ! -f "$IMAGE_FILE" ]; then
	eval "wget -O $IMAGE_FILE $album_cover > /dev/null 2>&1"
fi

# Write to cache file (so that we don't have to keep getting the album cover)
echo "$album_cover" > $CACHE_FILE

# Final message data
msg="$artist:$title:$album:$length_sec:$position_sec"
echo $msg
