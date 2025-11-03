# Streamlit Cloud Deployment Guide

## Setting Up Secrets in Streamlit Cloud

When deploying to Streamlit Cloud, you need to add your secrets through the Streamlit Cloud UI:

1. Go to your app's dashboard on [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. Click on **Settings** (⚙️ icon)
4. Go to the **Secrets** section
5. Copy and paste the following (update values as needed):

```toml
# Database Configuration
DB_HOST = "your-database-host"
DB_DATABASE = "cloudburst_management"
DB_USER = "your-db-username"
DB_PASSWORD = "your-db-password"
DB_PORT = 3306

# Mapbox Configuration
MAPBOX_TOKEN = "your-mapbox-token"

# OpenAI Configuration
OPENAI_API_KEY = "your-openai-api-key"
```

6. Click **Save**

## Important Notes

### Database Host
- **Local Development**: Use `localhost`
- **Streamlit Cloud**: You need a publicly accessible database server
  - Options: AWS RDS, Google Cloud SQL, Azure Database, PlanetScale, etc.
  - Update `DB_HOST` to your cloud database endpoint

### Local Development
- Keep your `.env` file for local development
- Never commit `.env` or `.streamlit/secrets.toml` to git
- Both files are already in `.gitignore`

### Configuration Hierarchy
The app will automatically:
1. Try to load from Streamlit secrets (when deployed)
2. Fall back to `.env` file (when running locally)

## Testing Locally with Streamlit Secrets
If you want to test the Streamlit secrets functionality locally:
- The `.streamlit/secrets.toml` file is already created
- Run: `streamlit run app.py`
- It will use the secrets.toml file

## Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DB_HOST | Database server hostname | `localhost` or `your-db.example.com` |
| DB_DATABASE | Database name | `cloudburst_management` |
| DB_USER | Database username | `root` |
| DB_PASSWORD | Database password | `your_password` |
| DB_PORT | Database port | `3306` |
| MAPBOX_TOKEN | Mapbox API token | `pk.eyJ1...` |
| OPENAI_API_KEY | OpenAI API key | `sk-proj-...` |
