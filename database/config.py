import os
from dotenv import load_dotenv

def load_config():
    app_env = os.getenv("APP_ENV", "local")
    # If on AWS, it expects the RDS envs you've already set in Task Definition
    if app_env == "aws":
        print("Running in AWS mode...")
    else:
        # Locally, it will use your Supabase or local postgres strings
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(project_root, ".env.local"))
        print("Running in local mode...")

load_config()
