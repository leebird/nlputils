# Brat Visualization for Dependency Parse

## Initialization
- `sh init.sh`
- Change the line `var fontLoadTimeout = 5000` to `var fontLoadTimeout = 0` in brat/client/visualizer.js. This is to avoid waiting for useless fonts.

## Start the server
- `sh run.sh`
