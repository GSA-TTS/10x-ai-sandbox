# GSA Quickstart

1. **Ensure Python 3.11 is installed**:

   - You can check your Python3.11.x version by running:

   ```bash
   python3.11 --version
   ```

   - If Python 3.11 is not installed, you will need to install it first.

   ```bash
   brew install python@3.11
   ```

2. **Create the virtual environment (or however you prefer)**:

   - Run:

   ```bash
   python3.11 -m venv venv
   source ./venv/bin/activate
   ```

3. **Install and use node 20.15.1**:

   - If you don't have nvm, you can install with `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash` and `source ~/.zshrc` (or `source ~/.bashrc` if you use bash):

   ```bash
   nvm install 20.18.1
   nvm use 20.18.1
   ```

4. **Install gitleaks**:

   - Install with homebrew, then start a new terminal:

   ```bash
   brew install gitleaks
   ```

5. **Install deps, build and run**:

   - Make sure you've got the .env file set up, then install, build and run with hot reloading:

   ```bash
   rm ./backend/data/webui.db || true && \
   pip install -r ./backend/requirements.txt && \
   rm -rf node_modules || true && \
   npm install --verbose && \
   npx husky init && \
   cp pre-commit .husky/pre-commit && \
   npm run build && \
   ./backend/start.sh
   ```

   - The first user to sign up to a new installation should get the admin role. You can also predefine user roles in the .env file. Github auth checks that email domain is in ['gsa.gov'], but you can easily modify it at `backend/apps/webui/routers/auths.py:233`. Eventually we'll need to make github for local dev only for compliance reasons.
   - After the first install, you can just run `./backend/start.sh`. First app startup will take a minute even after it says `Uvicorn running on http://0.0.0.0:8080`, once you see the ascii art, all of the features should be available. You may see a 500 the first time and need to refresh. You can run a front end dev server that hot reloads via `npm run dev` but connecting it to the backend and getting auth redirects with live servers working is unresolved due to the frontend and back running on different ports. We probably need to mock auth locally.
   - ollama is not required for the app to run, but it is assumed, you can ignore the 500s if its not running. If you want to use it, you can install it with `brew install ollama`. You can then run `ollama serve` to start the server. You can then add a model to ollama with `ollama run mistral`.

6. **Set up pipelines to access models via API**:

- Once you're in, you should see the four default models available in the chat. If not, check that the pipelines server is running on 9099 and in the UI click on your user in the lower left > Admin Panel > Settings > Connections > OpenAI API section. Set the API URL to [<http://localhost:9099](http://localhost:9099>) and the API key to 0p3n-w3bu! and hit refresh to see if it connects to the pipeline server.
- After completing these steps, the models specified in the pipeline settings should be available in the drop down at the upper left when you create a new conversation.

7. **Local e2e testing**:

- The cypress tests in the open-webui repo are out of date and need some love. Here's how to get started. Make sure you've run `npm install` locally and then install cypress locally:

`npx cypress install`

- You can remove the local backend db and run the backend and Ollama however you want, as long as they're available at `:8080` and `:11434` respectively. Here's how to run them via docker:

```
OPEN_WEBUI_PORT=8080 rm ./backend/data/webui.db || true && \
            docker compose \
            --file docker-compose.yaml \
            --file docker-compose.api.yaml \
            up --detach --build
```

- If you have Ollama installed and running locally with at least one model, you can just run:

`rm ./backend/data/webui.db || true && ./backend/start.sh`

- Once the app is available at 8080 and Ollama is available at 11434, you can run cypress with the helper script:

`npm run cy:open`
