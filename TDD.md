# Test Driven Development(TDD) with Flask 

## Approach
I'll use a simplified version of the CQRS pattern called *command and query pattern*. We're combining CQRS and CRUD.
The .dict() method that will be shown is provided by the BaseModel from pydantic, which all of our models inherit from. 

---

## How Should I Test My Software?

Software developers tend to be very opinionated about testing. Because of this, they have differing opinions about how important testing is and ideas on how to go about doing it. That said, let's look at three guidelines that (hopefully) most agree with that will help you write valuable tests:

    1.  Tests should tell you the expected behavior of the unit under test. Therefore, it's advisable to keep them short and to the point. The GIVEN, WHEN, THEN structure can help with this:

        - GIVEN: what are the initial conditions for the test?
        - WHEN: what is occurring that needs to be tested?
        - THEN: what is the expected response?

    So you should prepare your environment for testing, execute the behavior, and, at the end, check that output meets expectations.

    2. Each piece of behavior should be tested once -- and only once. Testing the same behavior more than once does not mean that your software is more likely to work. On the other hand, you need to maintain tests too. If you make a small change to your code base and then twenty tests break, how do you know which functionality is broken? When only a single test fails, it's much easier to find the bug.

    3. Each test must be independent from other tests. Otherwise, you'll have hard time maintaining and running the test suite.

### Requirements:
    - pytest
    - Flask
    - "pydantic[email]"
    - jsonschema

### Commands:
- ```(venv)$ python -m pytest tests```
- ```(venv)$ python -m pytest tests --cov=blog```
- ```(venv)$ python -m pytest tests -m 'e2e'```
- ```(venv)$ python -m pytest tests -m 'not e2e'```
- ```(venv)$ python blog/init_db.py```
- ```(venv)$ FLASK_APP=blog/app.py python -m flask run```

---

## Fixtures
To clear the database after each test and create a new one before each test we can use pytest fixtures. These are functions decorated with a @pytest.fixture decorator. They are usually located inside conftest.py but they can be added to the actual test files as well. These functions are executed by default before each test.

[**Note: Fixtures are added to the conftest.py**]

One option is to use their returned values inside your tests. For example:

```import random
import pytest


@pytest.fixture
def random_name():
    names = ['John', 'Jane', 'Marry']
    return random.choice(names)


def test_fixture_usage(random_name):
    assert random_name
```

So, to use the value returned from the fixture inside the test you just need to add the name of the fixture function as a parameter to the test function.

Another option is to perform a side effect, like creating a database or mocking a module.

You can also run part of a fixture before and part after a test using yield instead of return. For example:
```
@pytest.fixture
def some_fixture():
    # do something before your test
    yield # test runs here
    # do something after your test
```
---

## Coverage

It\'s a pytest plugin for coverage called *pytest-cov*. Install it with:

```(venv)$ pip install pytest-cov```

---

## Testing Pyramid

We started with unit tests (to test the commands and queries) followed by integration tests (to test the API endpoints), and finished with e2e tests. In simple applications, as in this example, you may end up with a similar number of unit and integration tests. The more the complexity grows the more pyramid-like shape you should see. That's where the "test pyramid" term comes from.


```Unit Tests -> Integration Tests -> End-to-End Tests```

Using the Test Pyramid as a guide, you typically want:
- 50% of your tests in your test suite to be unit tests.
- 30% to be integration tests.
- 20% to be e2e tests.

## Definitions:

- Unit test - tests a single unit of code.
- Integration tests - tests that multiple units work together.
- e2e - tests the whole application against a live production-like server.

The higher up you go in the pyramid, the more brittle and less predictable your tests are. What's more, e2e tests are by far the slowest to run so even though they can bring confidence that your application is doing what's expected of it, you shouldn't have nearly as many of them as unit or integration tests.

### What is a Unit?

It's pretty straightforward what integration and e2e tests look like. There's much more discussion about unit tests since you first have to define what a "unit" actually is. Most testing tutorials show a unit test example that tests a single function or method. Production code is never that simple.

First things first, before defining what a unit is, let's look at what the point of testing is in general and what should be tested.

### Why Test?

We write tests to:
    1. Ensure our code works as expected.
    2. protect out software against regressions.

Nonetheless, when feedback cycles are too long, developers tend to start to think more about the types of tests to write since time is a major constraint in software development. That's why we want to have more unit tests than other types of tests. We want to find and fix the defect as fast as possible.

### What to Test?

Now that you know why we should test, we now must look at what we should test.

We should test the behavior of our software. (And, yes: This still applies to TDD, not just BDD.) This is because you shouldn't have to change your tests every time there's a change to the code base.

Thinking back to the blog_app application. From a testing perspective, we don't care where the articles are stored. It could be a text file, some other relational database, or a key/value store -- it doesn't matter. Again, our app had the following requirements:

    - articles can be created.
    - articles can be fetched.
    - articles can be listed.

As long as those requirements don't change, a change to the storage medium shouldn't break our tests. Similarly, we know that as long as those tests pass, we know our software meets those requirements -- so it's working.

### So what is a Unit then?

Each function/method is technically a unit, but we still shouldn't test every single one of them. Instead, focus your energy on testing the functions and methods that are publicly exposed from a module/package.

In our case, these were the execute methods. We don't expect to call the Article model directly from the Flask API, so don't focus much (if any) energy on testing it. To be more precise, in our case, the "units", that should be tested, are the execute methods from the commands and queries. If some method is not intended to be directly called from other parts of our software or an end user, it's probably implementation detail. Consequently, our tests are resistant to refactoring to the implementation details, which is one of the qualities of great tests.

On the other hand, if you make a breaking change inside Article the tests will fail. And that's exactly what we want. In that situation, we can either revert the breaking change or adapt to it inside our command or query.

Because there's one thing that we're striving for: Passing tests means working software.

### When Should You Use Mocks?

We didn't use any mocks in our tests, because we didn't need them. Mocking methods or classes inside your modules or packages produces tests that are not resistant to refactoring because they are coupled to the implementation details. Such tests break often and are costly to maintain. On the other hand, it makes sense to mock external resources when speed is an issue (calls to external APIs, sending emails, long-running async processes, etc.).

For example, we could test the ```Article``` model separately and mock it inside our tests for ```CreateArticleCommand``` like so:

```
def test_create_article(monkeypatch):
    """
    GIVEN CreateArticleCommand with valid properties author, title and content
    WHEN the execute method is called
    THEN a new Article must exist in the database with same attributes
    """
    article = Article(
        author='john@doe.com',
        title='New Article',
        content='Super awesome article'
    )
    monkeypatch.setattr(
        Article,
        'save',
        lambda self: article
    )
    cmd = CreateArticleCommand(
        author='john@doe.com',
        title='New Article',
        content='Super awesome article'
    )

    db_article = cmd.execute()

    assert db_article.id == article.id
    assert db_article.author == article.author
    assert db_article.title == article.title
    assert db_article.content == article.content
```

That's perfectly fine to do, but we now have more tests to maintain -- e.g. all the tests from before plus all the new tests for the methods in Article. Besides that, the only thing that is now tested by test_create_article is that an article returned from save is the same as the one returned by execute. When we break something inside Article this test will still pass because we mocked it. And that's something we want to avoid: We want to test software behavior to ensure that it works as expected. In this case, behavior is broken but our test won't show that.

---

## Conclusion

You can use the same ideas with Domain-driven design (DDD), Behavior-driven design (BDD), and many other approaches. Keep in mind that tests should be treated the same as any other code: They are a liability and not an asset. Write tests to protect your software against the bugs but don't let it burn your time.

---

## Takeaways


1. There's no single right way to test your software. Nonetheless, it's easier to test logic when it's not coupled with your database. You can use the Active Record pattern with commands and queries (CQRS) to help with this.

2. Focus on the business value of your code.

3. Don't test methods just to say they're tested. You need working software not tested methods. TDD is just a tool to deliver better software faster and more reliable. Similar can be said for code coverage: Try to keep it high but don't add tests just to have 100% coverage.

4. A test is valuable only when it protects you against regressions, allows you to refactor, and provides you fast feedback. Therefore, you should strive for your tests to resemble a pyramid shape (50% unit, 30% integration, 20% e2e). Although, in simple applications, it may look more like a house (40% unit, 40% integration, 20% e2e), which is fine.

5. The faster you notice regressions, the faster you can intercept and correct them. The faster you correct them, the shorter the development cycle. To speed up feedback, you can use pytest markers to exclude e2e and other slow tests during development. You can run them less frequently.

6. Use mocks only when necessary (like for third-party HTTP APIs). They make your test setup more complicated and your tests overall less resistant to refactoring. Plus, they can result in false positives.

7. Once again, your tests are a liability not an asset; they should cover your software's behavior but don't over test.
