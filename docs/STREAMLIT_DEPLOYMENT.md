# Streamlit Community Cloud Deployment

HelixAgent includes a deployable Streamlit entry point at `streamlit_app.py`.

## Deploy

1. Open Streamlit Community Cloud.
2. Select **Create app**.
3. Choose the repository `CoreyLeath-code/HelixAgent`.
4. Select the `main` branch after this feature is merged.
5. Set the main file path to:

```text
streamlit_app.py
```

6. Choose a public app URL and deploy.

No secrets are required for the built-in fallback demonstration. Optional external tools can be configured later through Streamlit's secrets management.

## Runtime contract

The deployment uses:

- `runtime.txt` for Python 3.11
- `requirements.txt` for runtime dependencies
- `.streamlit/config.toml` for headless server and theme configuration
- `streamlit_app.py` as the application entry point

## Local validation

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open:

```text
http://localhost:8501
```

The Streamlit health endpoint is available at:

```text
http://localhost:8501/_stcore/health
```

## CI validation

The Enterprise CI workflow starts the Streamlit application in headless mode and verifies the health endpoint before the release-readiness contract can pass.

## Optional secrets

Add external API keys only through Streamlit Community Cloud's encrypted secrets interface. Never commit `.streamlit/secrets.toml` or plaintext credentials to the repository.
