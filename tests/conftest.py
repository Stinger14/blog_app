import os
import tempfile
import pytest

from blog.models import Article

@pytest.fixture(autouse=True)
def database():
    """
    This function is responsible for creating a new database before
    each test and removes it afterwards using a fixture.
    """
    _, file_name = tempfile.mkstemp()
    os.environ['DATABASE_NAME'] = file_name
    Article.create_table(database_name=file_name)
    yield
    os.unlink(file_name)
