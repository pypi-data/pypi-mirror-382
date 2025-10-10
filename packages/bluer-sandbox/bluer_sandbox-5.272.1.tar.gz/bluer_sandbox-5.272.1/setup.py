from blueness.pypi import setup

from bluer_sandbox import NAME, VERSION, DESCRIPTION, REPO_NAME

setup(
    filename=__file__,
    repo_name=REPO_NAME,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    packages=[
        NAME,
        f"{NAME}.ai4k",
        f"{NAME}.help",
        f"{NAME}.help.offline_llm",
        f"{NAME}.interview",
        f"{NAME}.offline_llm",
        f"{NAME}.offline_llm.model",
        f"{NAME}.parser",
        f"{NAME}.raspbian",
        f"{NAME}.village",
    ],
    include_package_data=True,
    package_data={
        NAME: [
            "config.env",
            ".abcli/**/*.sh",
            "assets/*",
        ],
    },
    extras_require={
        "llama": ["llama-cpp-python"],
    },
)
