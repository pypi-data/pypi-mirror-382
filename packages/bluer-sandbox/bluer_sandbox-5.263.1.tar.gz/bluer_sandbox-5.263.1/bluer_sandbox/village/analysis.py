from blueness import module

from bluer_sandbox import NAME
from bluer_sandbox.village.village import Village
from bluer_sandbox.logger import logger


NAME = module.name(__file__, NAME)


def analyze(
    object_name: str,
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.analyze: {object_name}")

    village = Village()
    if not village.load(
        object_name=object_name,
        verbose=verbose,
    ):
        return False

    logger.info("🪄")

    return True
