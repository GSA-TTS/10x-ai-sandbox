# Add Node.js and Python paths
export PATH="$HOME/deps/1/node/bin:$HOME/deps/0/bin:$PATH"

# Set the library path for Python
export LD_LIBRARY_PATH="$HOME/deps/0/lib:$LD_LIBRARY_PATH"

# Echo the paths to verify when you SSH in
echo "PATH is set to: $PATH"
echo "LD_LIBRARY_PATH is set to: $LD_LIBRARY_PATH"
