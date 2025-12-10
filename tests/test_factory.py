from flaskr import create_app

# There’s not much to test about the factory itself. Most of the code will be executed for each test already, so if something fails the other tests will notice. The only behavior that can change is passing test config. If config is not passed, there should be some default configuration, otherwise the configuration should be overridden.
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

# Pytest uses fixtures by matching their function names with the names of arguments in the test functions. For example, the test_hello function takes a (client) argument.
def test_hello(client):
    # Pytest matches the argument with the client fixture function, calls it, and passes the returned value to the test function.
    response = client.get('/hello')
    # the test checks that the response data matches
    assert response.data == b'Hello, World!'