import logging

import pytest


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s:%(filename)s:%(lineno)d %(message)s",
    )
