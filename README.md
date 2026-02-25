# Enhanced Course Bot

A powerful Telegram bot designed to find course links across various platforms like Google Drive, Mega.nz, MediaFire, and more.

## Features

- **Multi-Platform Search**: Search for courses on Drive, Mega, Dropbox, OneDrive, and MediaFire.
- **Search History**: Keeps track of your previous searches.
- **Favorites**: Save your favorite course links for easy access.
- **Settings**: Customize your search experience.
- **Rate Limiting**: Integrated protection against spam.

## Local Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Ng-course-extractor-
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file or export them directly:
   ```bash
   export BOT_TOKEN="your_telegram_bot_token"
   export SERPAPI_KEY="your_serpapi_key"
   ```

5. **Run the bot**:
   ```bash
   python3 main.py
   ```

## Deployment on PythonAnywhere

### 1. Upload your code
- You can use `git clone` in a PythonAnywhere Bash console if your repo is public.
- Or use the "Files" tab to upload your files.

### 2. Set up a Virtual Environment
In a Bash console on PythonAnywhere:
```bash
mkvirtualenv --python=/usr/bin/python3.11 bot-env
pip install -r requirements.txt
```

### 3. Environment Variables
You need to set your API keys. A good way on PythonAnywhere is to add them to your `.bashrc` or use a `.env` file with `python-dotenv` (not included by default, but you can add it).

Alternatively, if running as a Task, you can set them in the command.

### 4. Running the Bot

#### Option A: Always-on Task (Recommended - Paid Feature)
1. Go to the **Tasks** tab.
2. In the "Always-on tasks" section, enter the following command:
   ```bash
   export BOT_TOKEN='your_token' SERPAPI_KEY='your_key'; /home/yourusername/.virtualenvs/bot-env/bin/python /home/yourusername/Ng-course-extractor-/main.py
   ```
3. Click **Create**.

#### Option B: Bash Console (Free - Not persistent)
1. Open a **Bash console**.
2. Activate your virtualenv: `workon bot-env`
3. Set variables and run:
   ```bash
   export BOT_TOKEN='your_token'
   export SERPAPI_KEY='your_key'
   python main.py
   ```
   *Note: The bot will stop if the console is closed or the server restarts.*

## Deployment on Render

### 1. Blueprint Deployment (Recommended)
1. Fork this repository to your GitHub account.
2. Go to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** and select **Blueprint**.
4. Connect your GitHub repository.
5. Render will automatically detect the `render.yaml` file.
6. Enter your `BOT_TOKEN` and `SERPAPI_KEY` in the environment variables section.
7. Click **Deploy**.

### 2. Manual Web Service Deployment
1. Create a new **Web Service**.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python main.py`
4. Add Environment Variables:
   - `RENDER`: `true`
   - `BOT_TOKEN`: `your_telegram_bot_token`
   - `SERPAPI_KEY`: `your_serpapi_key`
   - `PYTHON_VERSION`: `3.11.0` (or higher)

## Configuration

The bot configuration is managed in `bot/config.py`. It uses environment variables:
- `BOT_TOKEN`: Your Telegram Bot Token from @BotFather.
- `SERPAPI_KEY`: Your API key from [SerpApi](https://serpapi.com/) for search results.

## Project Structure

- `main.py`: Entry point.
- `bot/`: Source code directory.
  - `config.py`: Configuration and environment variables.
  - `database.py`: SQLite database management.
  - `handlers.py`: Command and message handlers.
  - `keyboards.py`: Inline keyboard definitions.
  - `search.py`: Search engine integration.
  - `utils.py`: Helper functions.
