# GSA Quickstart

1. **Ensure Python 3.11 is installed**:

   - You can check your Python version by running:

   ```bash
   python3.11 --version
   ```

   - If Python 3.11 is not installed, you will need to install it first.

   ```bash
   brew install python@3.11
   ```

2. **Navigate to your project directory and Create the virtual environment**:

   - Run:

   ```bash
   python3.11 -m venv venv
   ```

3. **Activate the virtual environment**:

   - Run:

   ```bash
   source ./venv/bin/activate
   ```

4. **Install and use node 20.15.1**:

   - If you don't have nvm, you can install with `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash` and `source ~/.zshrc` (or `source ~/.bashrc` if you use bash):

   ```bash
   nvm install 20.15.1
   nvm use 20.15.1
   ```

5. **Install gitleaks**:

   - Install with homebrew, then start a new terminal:

   ```bash
   brew install gitleaks
   ```

6. **Run redis**:

   - Check for redis on the default `lsof -i:6379`, if it's there, make sure it's got the default creds, or kill it and run:

   ```bash
   docker run -d --name redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
   ```

7. **Install deps, build and run**:

   - Install, build and run with hot reloading:

   ```bash
   rm ./backend/data/webui.db && \
   pip install -r ./backend/requirements.txt && \
   rm -rf node_modules && \
   npm install && \
   npm run build && \
   ./backend/start.sh
   ```

   - You should see the pipelines server running at 9099, the static files should be compiled and the webui server should be running at http://0.0.0.0:8080.

8. **Set up pipelines to access models via API**:

- The first user to sign up to a new installation should get the admin role. Once you're in, navigate to the Admin Panel > Settings > Connections > OpenAI API section. Set the API URL to http://localhost:9099 and the API key to 0p3n-w3bu! and hit refresh to see if it connects.
- After completing these steps, the model specified in the pipeline should be available in the drop down at the upper left when you create a new conversation.
