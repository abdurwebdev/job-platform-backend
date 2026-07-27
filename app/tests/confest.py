import os

# app.config.config.Settings requires DATABASE_URL with no default. Route tests
# use dependency_overrides so they never touch a real DB, but importing
# app.routes.job_routes still imports app.config.config, which instantiates
# Settings() at module load time. Give it a harmless placeholder if the
# environment (or a local .env) hasn't already supplied one.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")