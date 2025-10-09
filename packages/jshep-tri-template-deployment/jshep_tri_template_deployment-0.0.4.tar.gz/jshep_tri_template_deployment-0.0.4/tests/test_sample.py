from my_python_package import Greeter

def test_greet():
    """Tests the Greeter class."""
    greeter = Greeter()
    assert greeter.greet("World") == "Hello, World!"
    assert greeter.greet("Dev") == "Hello, Dev!"
