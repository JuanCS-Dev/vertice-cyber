import unittest
import sys
import os

# Runner Entrypoint
if __name__ == "__main__":
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(0 if result.wasSuccessful() else 1)
