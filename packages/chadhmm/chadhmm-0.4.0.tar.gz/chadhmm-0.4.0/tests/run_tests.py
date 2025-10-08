from unittest import TestLoader, TextTestRunner

if __name__ == "__main__":
    test_loader = TestLoader()
    test_suite = test_loader.discover("tests", pattern="test_*.py")

    runner = TextTestRunner()
    runner.run(test_suite)
