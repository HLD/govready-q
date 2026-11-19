#!/bin/sh

if [[ -d "node_modules" ]]; then
  rm -rf node_modules
fi

if [[ -d "static" ]]; then
  rm -rf static
fi

mkdir -p static

# Use the npm bundled with the Node.js LTS base image, and install exactly what
# package-lock.json specifies.
npm ci --prefer-offline --no-audit --progress=false

echo "[ + ] Starting Webpack"
npm --max-old-space-size=2048 run dev