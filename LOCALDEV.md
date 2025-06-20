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

3. **Install and use node 20.18.1**:

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

   - Set up pgvector postgres container:

   ```bash
   docker run --name pgvector_postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -p 5432:5432 pgvector/pgvector:pg15
   ```

   - Set up Redis:

   ```bash
   docker run -d -p 6379:6379 redis
   ```

   - Set up .env file:

     - Create a .env file in the project root
     - Contact dev team members for the shared .env values sheet.

   - Initial install/setup (run whenever starting fresh)

   ```bash
   pip install -r ./backend/requirements.txt && \
   cat z-root-public.pem >> $(python -c "import certifi; print(certifi.where())") && \
   npm install --verbose && \
   npx husky init && \
   cp pre-commit .husky/pre-commit && \
   ```

   - Build and run with hot reloading:

   ```bash
   ./dev.sh
   ```

   - The first user to sign up to a new installation should get the admin role. You can also predefine user roles in the .env file. Github auth checks that email domain is in ['gsa.gov'], but you can easily modify it at `backend/apps/webui/routers/auths.py:233`. Eventually we'll need to make github for local dev only for compliance reasons.
   - After the first install, you can just run `./dev.sh`. First app startup will take a minute even after it says `Uvicorn running on http://0.0.0.0:8080`, once you see the ascii art, all of the features should be available. You may see a 500 the first time and need to refresh. You can run a front end dev server that hot reloads via `npm run dev` but connecting it to the backend and getting auth redirects with live servers working is unresolved due to the frontend and back running on different ports. We probably need to mock auth locally.
   - ollama is not required for the app to run, but it is assumed, you can ignore the 500s if its not running. If you want to use it, you can install it with `brew install ollama`. You can then run `ollama serve` to start the server. You can then add a model to ollama with `ollama run mistral`.

6. **Set up pipelines to access models via API**:

   - Once you're in, you should see the four default models available in the chat. If not, check that the pipelines server is running on 9099 and in the UI click on your user in the lower left > Admin Panel > Settings > Connections > OpenAI API section. Set the API URL to [<http://localhost:9099](http://localhost:9099>) and the API key to 0p3n-w3bu! and hit refresh to see if it connects to the pipeline server.
   - After completing these steps, the models specified in the pipeline settings should be available in the drop down at the upper left when you create a new conversation.

7. **Testing stateless deployment with docker swarm**:

   - We can use docker swarm with the base docker-compose.yaml to spin up a cluster of replicas.

   - Build the app container from the base `Dockerfile`:

   ```bash
   docker build --progress=plain -t gsai-container -f Dockerfile .
   ```

   - Initialize a node:

   ```bash
   docker swarm init
   ```

   - Deploy the stack. Make sure to deploy with app `replicas: 1` in the `docker-compose.yaml` the first time to avoid parallel migration conflicts in your fresh db:

   ```bash
   docker stack deploy --detach=false -c docker-compose.yaml gsai-cluster
   # NOTE: the command will exit successfully after 'verify: Service ... converged' at which point, the app should be accessible at http://localhost:8080
   ```

   - To take down the container stack:

   ```bash
   docker stack rm gsai-cluster # takes 10-20 seconds to clean up
   ```

   - To take down the node:

   ```bash
   docker swarm leave --force
   ```

   - _NOTE_: a reasonable development cycle might look like pointing your IDE at the app volume (devcontainer style) and redeploying the stack after modifying the app volume. It might be a little tricky to share the volume properly, so that you can alternately bring up the single container and the swarm to test single or parallel behavior.

8. **Install autogen for commit and pr messages**:

   - Install the auto tool in your local bin:

   ```bash
   sudo ln -s $(pwd)/auto /usr/local/bin/auto
   ```

   - Create a commit or a pr (into main) with an autogenerated message:

   ```bash
   git add .
   auto commit
   auto pr
   ```

## Deploying to FCS

Development and production deployments are running on FCS. FCS maintains its own Github private repo that mirrors the public repo. To deploy new code FCS:

1. **Ensure you have access to FCS**

- You will need to ask someone on the team for access.

2. **Clone the code from the private FCS repository**

- From a computer that can access FCS clone the `gsai-core-chat` repo. You will need to run the script from this repo, which will build a new new branch with code from the public repo

3. **Execute pullpublic.sh**

- From the root of the `gsai-core-chat` repo run

  ```bash
  ./pullpublic.sh main
  ```

  to create a new pranch from the public main branch. This will output the result of some git commands ending in the creation of a new git branch in your local repository. If succesful, it will report something like the following indicating the creating of a new feature branch:

  ```
  Your branch is up to date with 'origin/development'.
  HEAD is now at 2f30a7c99 Merge pull request #54 from mcaas-gsai/feature/trigger-build
  Switched to a new branch 'feature/main-1741271146'
  bdc6b4be9c9b3b02437dda4981e417b87f39f42e	refs/heads/main
  HEAD is now at bdc6b4be9 Merge pull request #318 from GSA-TTS/user/issue272-homepage
  ```

4. **Push this branch and make PR**

- Push this like any other branch to the private FCS repo and make a pull request into development.

5. **Merge**

- Merging to development will start the CI/CD process to build and deploy the project. This will take a little while

6. **Ensure ENVs are in place**

- If your new code requires environmental variables, you will need to add them to the helm charts in FCS. You will need access to the gsai-flux-config repo. The chat-helmrelease.yaml file contains environmental variable at the end. If you need to add or change any, follow examples at the end of the file. Changes here will take a few minutes as the cluster redeploys pods.
