from loguru import logger


def wrote_content(path: str):
    logger.info(f"wrote some content to {path}")


def softlink_created(source: str, destination: str):
    logger.info(f"created a soft link {destination} -> {source}")


def file_copied(source: str, destination: str):
    logger.info(f"copied {source} file to {destination}")


def directory_copied(source: str, destination: str):
    logger.info(f"copied {source} directory to {destination}")
