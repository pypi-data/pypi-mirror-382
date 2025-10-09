from bluer_options.env import load_config, load_env, get_env

load_env(__name__)
load_config(__name__)


ARVANCLOUD_PRIVATE_KEY = get_env("ARVANCLOUD_PRIVATE_KEY")

BLUER_VILLAGE_OBJECT = get_env("BLUER_VILLAGE_OBJECT")
BLUER_VILLAGE_TEST_OBJECT = get_env("BLUER_VILLAGE_TEST_OBJECT")
