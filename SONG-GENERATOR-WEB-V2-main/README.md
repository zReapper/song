# SONG-GENERATOR-WEB-V2
Simple web UI and Telegram bot wrapper for a Notegpt-based AI music generator.

## Setup

1. Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the web UI

Start the Flask app:

```bash
export FLASK_APP=api/index.py
export FLASK_ENV=development
.venv/bin/flask run --host=0.0.0.0 --port=5001
```

## Notes

- The project calls external Notegpt endpoints and may require valid cookies in `NOTEGPT_COOKIES`.
- This is a development setup; for production use a proper WSGI server and secure secret handling.

## Deploying from GitHub to Heroku (web app)

1. Create a Heroku app and get an API key.
2. In your GitHub repository settings -> Secrets, add:
	- `HEROKU_API_KEY` (your Heroku API key)
	- `HEROKU_APP_NAME` (the Heroku app name)
3. Push to the `main` branch. You can use any CI or push to Heroku directly. Heroku will run the `web` process from the `Procfile`.

Notes:
- The `Procfile` runs `gunicorn api.index:app` so the Flask web UI is served as a web dyno.
- Set config vars on Heroku for any `NOTEGPT_COOKIES` if required by the external API.

