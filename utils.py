import os

TRUE_VALUES = ["true", "1"]


def env_var_is_true(env_var_name):
    return (
        env_var_name in os.environ and os.environ[env_var_name].lower() in TRUE_VALUES
    )


timeout_amount = float(os.environ.get("REQUEST_TIMEOUT", "5"))
