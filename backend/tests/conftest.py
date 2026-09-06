import pytest
from scripts.seed import seed

@pytest.fixture(scope="session",autouse=True)
def seeded():
    seed()
