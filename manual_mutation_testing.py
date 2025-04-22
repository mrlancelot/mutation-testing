import os
import sys
import re
import tempfile
import subprocess
import shutil
from pathlib import Path

# Mutation types to apply
MUTATIONS = {
    # Arithmetic mutations
    r'\+': '-',             # + to -
    r'-(?![>])': '+',       # - to + (avoid matching ->)
    r'\*\*': '*',           # ** to *
    r'\*(?!\*)': '/',       # * to / (avoid matching **)
    r'/': '*',              # / to *
    r'%': '/',              # % to /
    
    # Comparison mutations
    r'==': '!=',            # == to !=
    r'!=': '==',            # != to ==
    r'>': '<=',             # > to <=
    r'<': '>=',             # < to >=
    r'>=': '<',             # >= to <
    r'<=': '>',             # <= to >
    
    # Boolean mutations
    r' and ': ' or ',       # and to or
    r' or ': ' and ',       # or to and
    r'not ': '',            # not to nothing
    
    # Return value mutations
    r'return (.+)': r'return True',   # return x to return True
    r'return True': 'return False',   # return True to return False
    r'return False': 'return True',   # return False to return True
    
    # Exception mutations
    r'raise (.+)': r'pass',  # raise to pass
    
    # Value mutations
    r'\b0\b': '1',          # 0 to 1
    r'\b1\b': '0',          # 1 to 0
    r'\bTrue\b': 'False',   # True to False
    r'\bFalse\b': 'True',   # False to True
    r'\bNone\b': 'True',    # None to True
}

def backup_file(filepath):
    """Create a backup of the file."""
    backup_path = f"{filepath}.bak"
    shutil.copy(filepath, backup_path)
    return backup_path

def restore_file(backup_path, filepath):
    """Restore the file from backup."""
    shutil.copy(backup_path, filepath)
    os.remove(backup_path)

def apply_mutation(filepath, pattern, replacement, line_index):
    """Apply a mutation to a file at a specific line."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    original_line = lines[line_index]
    
    # Apply the mutation
    if re.search(pattern, original_line):
        lines[line_index] = re.sub(pattern, replacement, original_line, count=1)
        with open(filepath, 'w') as f:
            f.writelines(lines)
        return True, original_line, lines[line_index]
    return False, original_line, original_line

def run_tests():
    """Run pytest and return True if all tests pass."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.returncode == 0

def analyze_mutations(file_to_mutate="calculator.py", test_file="test_calculator.py"):
    """Test each possible mutation in the code."""
    total_mutations = 0
    surviving_mutations = []
    
    # Create a backup of the original file
    backup_path = backup_file(file_to_mutate)
    
    try:
        # Get the lines from the file
        with open(file_to_mutate, 'r') as f:
            lines = f.readlines()
        
        # Try each mutation pattern on each line
        print(f"Analyzing mutations in {file_to_mutate}...")
        
        for line_index, line in enumerate(lines):
            for pattern, replacement in MUTATIONS.items():
                # Skip comments and docstrings
                if line.strip().startswith("#") or line.strip().startswith('"""'):
                    continue
                
                # Apply the mutation
                applied, original, mutated = apply_mutation(
                    file_to_mutate, pattern, replacement, line_index
                )
                
                if applied:
                    total_mutations += 1
                    mutation_desc = f"Line {line_index+1}: {original.strip()} -> {mutated.strip()}"
                    print(f"Testing mutation {total_mutations}: {mutation_desc}", end=" ... ")
                    
                    # Check if the tests catch this mutation
                    if run_tests():
                        # Tests pass despite the mutation - this is a surviving mutation
                        surviving_mutations.append({
                            "line": line_index + 1,
                            "original": original.strip(),
                            "mutated": mutated.strip(),
                            "file": file_to_mutate,
                            "pattern": pattern,
                            "replacement": replacement
                        })
                        print("SURVIVED (not caught by tests)")
                    else:
                        print("killed (caught by tests)")
                    
                    # Restore the file after each mutation test
                    restore_file(backup_path, file_to_mutate)
                    backup_path = backup_file(file_to_mutate)
    
    finally:
        # Ensure we restore the original file
        try:
            restore_file(backup_path, file_to_mutate)
        except:
            pass
    
    # Print summary
    print("\n" + "="*50)
    print(f"Mutation testing summary for {file_to_mutate}:")
    print(f"Total mutations: {total_mutations}")
    print(f"Surviving mutations: {len(surviving_mutations)}")
    print(f"Mutation score: {((total_mutations - len(surviving_mutations)) / total_mutations * 100) if total_mutations else 0:.2f}%")
    
    if surviving_mutations:
        print("\nSurviving mutations that need additional test cases:")
        for i, mutation in enumerate(surviving_mutations, 1):
            print(f"{i}. Line {mutation['line']}: {mutation['original']} -> {mutation['mutated']}")
    
    return surviving_mutations

def generate_test_case(mutation):
    """Generate a test case to catch a specific mutation."""
    file = mutation["file"]
    line = mutation["line"]
    original = mutation["original"]
    mutated = mutation["mutated"]
    pattern = mutation["pattern"]
    replacement = mutation["replacement"]
    
    # Extract the function name from the file
    with open(file, 'r') as f:
        lines = f.readlines()
    
    # Find the function containing this line
    func_name = None
    for i in range(line-1, -1, -1):
        if i < len(lines) and re.match(r'def (\w+)\(', lines[i]):
            func_match = re.match(r'def (\w+)\(', lines[i])
            if func_match:
                func_name = func_match.group(1)
                break
    
    if not func_name:
        return None
    
    # Generate test name
    test_name = f"test_{func_name}_mutation_{len(os.listdir())}"
    
    # Generate test based on the mutation type
    if '+' in pattern and '-' in replacement:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Test that addition doesn't become subtraction
    assert {func_name}(5, 3) == 8
    assert {func_name}(5, 3) != 2
"""
    elif '-' in pattern and '+' in replacement:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Test that subtraction doesn't become addition
    assert {func_name}(5, 3) == 2
    assert {func_name}(5, 3) != 8
"""
    elif '*' in pattern and '/' in replacement:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Test that multiplication doesn't become division
    assert {func_name}(10, 2) == 20
    assert {func_name}(10, 2) != 5
"""
    elif '/' in pattern and '*' in replacement:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Test that division doesn't become multiplication
    assert {func_name}(10, 2) == 5
    assert {func_name}(10, 2) != 20
"""
    elif '%' in pattern:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Test that modulo doesn't become division
    assert {func_name}(10, 3) == 1
    assert {func_name}(10, 3) != 3.33
"""
    elif '==' in pattern and '!=' in replacement:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Test that equality check doesn't become inequality
    assert {func_name}(5, 5) == True
    assert {func_name}(5, 6) == False
"""
    elif '!=' in pattern and '===' in replacement:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Test that inequality check doesn't become equality
    assert {func_name}(5, 6) == True
    assert {func_name}(5, 5) == False
"""
    elif 'raise' in pattern:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Test that exception is properly raised
    with pytest.raises(ValueError):
        {func_name}(10, 0)
"""
    else:
        return f"""
def {test_name}():
    \"\"\"Test to catch mutation: {original} -> {mutated}\"\"\"
    # Add a specific test for this mutation
    # Original: {original}
    # Mutated: {mutated}
    pass
"""

def add_test_cases_to_file(test_file, test_cases):
    """Add generated test cases to the test file."""
    with open(test_file, 'a') as f:
        f.write("\n# Automatically generated tests for catching mutations\n")
        for test_case in test_cases:
            if test_case:
                f.write(test_case)
        f.write("\n")

if __name__ == "__main__":
    print("Starting manual mutation testing...")
    file_to_mutate = "calculator.py"
    test_file = "test_calculator.py"
    
    # Run mutation analysis
    surviving_mutations = analyze_mutations(file_to_mutate, test_file)
    
    # Generate and add test cases for surviving mutations
    if surviving_mutations:
        test_cases = [generate_test_case(mutation) for mutation in surviving_mutations]
        add_test_cases_to_file(test_file, test_cases)
        print(f"\nAdded {len([tc for tc in test_cases if tc])} new test cases to {test_file}")
    else:
        print("\nNo surviving mutations found. Your tests are robust!") 