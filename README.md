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
   python3.11 -m venv .env
   ```

3. **Activate the virtual environment**:

   - Run:

   ```bash
   source .env/bin/activate
   ```

4. **Install and use node 20.15.1**:

   - If you don't have nvm, you can install with `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash` and `source ~/.zshrc` (or `source ~/.bashrc` if you use bash):

   ```bash
   nvm install 20.15.1
   nvm use 20.15.1
   ```

5. **Install deps, build and run**:

   - Install, build and run with hot reloading:

   ```bash
   rm ./backend/data/webui.db && \
   pip install -r ./backend/requirements.txt && \
   npm install && \
   npm run build && \
   npm run dev & \
   ./backend/start.sh & \
   open http://localhost:5173
   ```

   - You should see the pipelines server running at 9099, the webui backend running at 8080 and you should be able to sign in at http://localhost:5173.

6. **Set up pipelines to access models via API**:

- The first user to sign up to a new installation should get the admin role. Once you're in, navigate to the Admin Panel > Settings > Connections > OpenAI API section. Set the API URL to http://localhost:9099 and the API key to 0p3n-w3bu! and hit refresh to see if it connects.
- After completing these steps, the model specified in the pipeline should be available in the drop down at the upper left when you create a new conversation.
