import ast
import sys
import astunparse
import os
import openai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

FILENAME = 'tests.py'

def extract_functions(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    functions = [(node.name, astunparse.unparse(node).strip()) for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    function_code_list = []
    for function_name, function_code in functions:
        function_code_list.append(function_code)
        
    return function_code_list

def test_file_init(py_file):
    path = Path(FILENAME)
    if path.is_file() == 0:
        with open(path, 'w') as file:
            file.write(f'import unittest\nfrom {py_file[:-3]} import *\n')
            
def generate_tests(funcs):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    tests = []
    for func in funcs:
        prompt = f"Assuming I have the setup complete for a python unittest and have the library imported, generate a Python unittest class for the following function: '{func}', and return only the class."
        response = openai.Completion.create(
            model = 'text-davinci-003',
            prompt = prompt,
            max_tokens = 1024,
            temperature = 0.5
        )
        tests.append(response['choices'][0]['text'])
    for item in tests:
        print(item)
    return tests
        
def generate_test_file(tests):
    test_main = "\nif __name__ == '__main__':\n    unittest.main(testRunner=unittest.TextTestRunner(), verbosity=2)"
    
    for item in tests:
        with open(FILENAME, 'a') as file:
            file.write(item)
        
    with open(FILENAME, 'a') as file:
        file.write(test_main)

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_functions.py <python_file>")
        return
    
    file_path = sys.argv[1]
    functions_list = extract_functions(file_path)
    
    test_list = generate_tests(functions_list)
    test_file_init(file_path)
    generate_test_file(test_list)
    
if __name__ == '__main__':
    main()