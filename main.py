import os
import unittest

def list_tests():
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    test_files = [f for f in os.listdir(tests_dir) if f.startswith('test_') and f.endswith('.py')]
    return test_files

def run_test(test_file):
    test_name = test_file.replace('.py', '')
    suite = unittest.TestLoader().loadTestsFromName(f'tests.{test_name}')
    unittest.TextTestRunner().run(suite)

def main():
    test_files = list_tests()
    print("Available tests:")
    for idx, test_file in enumerate(test_files):
        print(f"{idx + 1}. {test_file}")
    
    try:
        choice = int(input("Select the test to run (number): ")) - 1
        if 0 <= choice < len(test_files):
            run_test(test_files[choice])
        else:
            print("Invalid choice. Exiting.")
    except ValueError:
        print("Invalid input. Exiting.")

if __name__ == "__main__":
    main()
