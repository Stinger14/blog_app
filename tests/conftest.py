import os
import tempfile
import pytest

from blog.models import Article

@pytest.fixture(autouse=True)
def database():
    """
    This function is responsible for creating a new database before
    each test and removes it afterwards using a fixture.

    The autouse flag is set to True so that it's automatically used 
    by default before (and after) each test in the test suite. 
    Since we're using a database for all tests it makes sense 
    to use this flag. That way you don't have to explicitly add 
    the fixture name to every test as a parameter.

    """
    _, file_name = tempfile.mkstemp()
    os.environ['DATABASE_NAME'] = file_name
    Article.create_table(database_name=file_name)
    yield
    os.unlink(file_name)
