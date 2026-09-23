#!/usr/bin/env sh
# Serve the built game and open it in the default browser.
cd "$(dirname "$0")/dist" || exit 1
URL=http://localhost:8765/
( sleep 1; (command -v open >/dev/null && open "$URL") || (command -v xdg-open >/dev/null && xdg-open "$URL") ) &
exec python3 -m http.server 8765 --bind 127.0.0.1
