#!/usr/bin/env bash
set -eu
BIN="$HOME/bin"
WS="/mnt/c/Program Files/Wireshark"
mkdir -p "$BIN"

for tool in tshark capinfos dumpcap; do
  cat > "$BIN/$tool" <<EOF
#!/usr/bin/env bash
exec "$WS/${tool}.exe" "\$@"
EOF
  chmod +x "$BIN/$tool"
done

MARKER='# Lab5 Wireshark wrappers in ~/bin'
BASHRC="$HOME/.bashrc"
if ! grep -qF "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" <<'EOF'

# Lab5 Wireshark wrappers in ~/bin
export PATH="$HOME/bin:$PATH"
EOF
  echo "appended ~/bin to ~/.bashrc PATH"
else
  echo "~/bin PATH already in ~/.bashrc"
fi

# remove old function-based helpers if present (keep PATH line if wrappers marker exists)
# leave as-is; wrappers take precedence when ~/bin is first

export PATH="$BIN:$PATH"
hash -
command -v tshark
command -v capinfos
tshark -v 2>&1 | head -n 1
capinfos -h 2>&1 | head -n 1
echo OK
