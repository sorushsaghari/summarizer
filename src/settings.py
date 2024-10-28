# src/settings.py
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="MYAPP",
    settings_files=['settings.yaml', '.secrets.yaml'],
    environments=True,
    load_dotenv=True,
    env_switcher="ENV_FOR_DYNACONF",
    fresh_vars=['db_url'],  # Add any other keys you want to keep in lowercase
    # Add the following line to prevent uppercasing keys
    uppercase_keys=False
)
