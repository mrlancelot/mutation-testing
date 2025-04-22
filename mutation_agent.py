import os
import re
import subprocess
import sys
import platform
from typing import List, Dict, Tuple

# Check if running on Windows
IS_WINDOWS = platform.system() == 'Windows'

# Simple local implementations instead of Google ADK
class ActionInput:
    def __init__(self, content=None):
        self.content = content

class ActionResponse:
    def __init__(self, content=None):
        self.content = content

# Simple function decorator
def function(func):
    return func

class Agent:
    def __init__(self):
        pass
    
    def run(self):
        print("Running agent...")
        input_obj = ActionInput(content="Run full cycle")
        response = self.run_full_cycle(input_obj)
        print(response.content)

class MutationTestingAgent(Agent):
    """Agent for running mutation tests and improving test coverage."""
    
    def __init__(self):
        super().__init__()
        self.current_coverage = 0.0
        self.calculator_coverage = 0.0
        self.target_coverage = 100.0
        self.current_mutations_killed = 0
        self.total_mutations = 0
        self.failed_mutations = []
        
    @function
    def run_coverage(self, action_input: ActionInput) -> ActionResponse:
        """Run pytest with coverage."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--cov=.", "--cov-report=term"], 
                capture_output=True, 
                text=True,
                check=False
            )
            
            # Extract overall coverage percentage
            coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', result.stdout)
            if coverage_match:
                self.current_coverage = float(coverage_match.group(1))
                
                # Extract coverage for calculator.py specifically
                calculator_match = re.search(r'calculator\.py\s+(\d+)\s+(\d+)\s+(\d+)%', result.stdout)
                if calculator_match:
                    stmts = int(calculator_match.group(1))
                    miss = int(calculator_match.group(2))
                    self.calculator_coverage = float(calculator_match.group(3))
                    
                return ActionResponse(
                    content=f"Current test coverage: {self.current_coverage}%\nCalculator module coverage: {self.calculator_coverage}%\n{result.stdout}"
                )
            else:
                return ActionResponse(
                    content=f"Failed to extract coverage information.\n{result.stdout}\n{result.stderr}"
                )
        except Exception as e:
            return ActionResponse(content=f"Error running coverage: {str(e)}")
    
    @function
    def run_mutmut(self, action_input: ActionInput) -> ActionResponse:
        """Run mutmut to find mutations."""
        if IS_WINDOWS:
            return ActionResponse(
                content="Mutmut is not fully compatible with Windows due to missing 'resource' module. "
                        "Please consider using WSL or a Linux environment for mutation testing."
            )
            
        try:
            # First, run mutmut
            result = subprocess.run(
                [sys.executable, "-m", "mutmut", "run"], 
                capture_output=True, 
                text=True,
                check=False
            )
            
            # Parse the results
            mutations_match = re.search(r'(\d+) mutations were generated', result.stdout)
            killed_match = re.search(r'(\d+) of them were killed', result.stdout)
            
            if mutations_match and killed_match:
                self.total_mutations = int(mutations_match.group(1))
                self.current_mutations_killed = int(killed_match.group(1))
                
                return ActionResponse(
                    content=(
                        f"Mutation testing results:\n"
                        f"Total mutations: {self.total_mutations}\n"
                        f"Killed mutations: {self.current_mutations_killed}\n"
                        f"Mutation score: {self.current_mutations_killed/self.total_mutations*100:.2f}%\n\n"
                        f"{result.stdout}"
                    )
                )
            else:
                return ActionResponse(
                    content=f"Failed to extract mutation information.\n{result.stdout}\n{result.stderr}"
                )
        except Exception as e:
            return ActionResponse(content=f"Error running mutmut: {str(e)}")
    
    @function
    def find_surviving_mutations(self, action_input: ActionInput) -> ActionResponse:
        """Find and analyze surviving mutations."""
        if IS_WINDOWS:
            return ActionResponse(
                content="Mutmut is not fully compatible with Windows due to missing 'resource' module."
            )
            
        try:
            # Get list of surviving mutations
            result = subprocess.run(
                [sys.executable, "-m", "mutmut", "results"], 
                capture_output=True, 
                text=True,
                check=False
            )
            
            surviving_mutations = result.stdout.strip().split('\n')
            self.failed_mutations = surviving_mutations
            
            return ActionResponse(
                content=f"Found {len(surviving_mutations)} surviving mutations:\n{result.stdout}"
            )
        except Exception as e:
            return ActionResponse(content=f"Error finding surviving mutations: {str(e)}")
    
    @function
    def improve_tests(self, action_input: ActionInput) -> ActionResponse:
        """Improve tests based on surviving mutations."""
        if IS_WINDOWS:
            # On Windows, we'll use a more basic approach to improve tests
            # Analyze the calculator.py file directly and generate additional tests
            return self._improve_tests_windows()
            
        if not self.failed_mutations:
            return ActionResponse(content="No surviving mutations to fix.")
        
        improvements = []
        
        for mutation_id in self.failed_mutations[:5]:  # Process first 5 mutations
            try:
                # Show the mutation
                result = subprocess.run(
                    [sys.executable, "-m", "mutmut", "show", mutation_id], 
                    capture_output=True, 
                    text=True,
                    check=False
                )
                
                mutation_info = result.stdout
                
                # Extract file and line information
                file_match = re.search(r'--- (\w+\.py)', mutation_info)
                if not file_match:
                    continue
                    
                file_name = file_match.group(1)
                
                # Generate improved test for this mutation
                improved_test = self._generate_test_for_mutation(file_name, mutation_info)
                if improved_test:
                    improvements.append((file_name, improved_test))
            except Exception as e:
                continue
        
        # Apply improvements to test files
        for file_name, improved_test in improvements:
            test_file_name = f"test_{file_name}"
            
            # Check if test file exists
            if os.path.exists(test_file_name):
                with open(test_file_name, 'r') as f:
                    content = f.read()
                
                # Append the new test
                with open(test_file_name, 'a') as f:
                    f.write("\n\n" + improved_test)
            else:
                # Create a new test file
                with open(test_file_name, 'w') as f:
                    module_name = file_name.replace('.py', '')
                    f.write(f"import pytest\nfrom {module_name} import *\n\n{improved_test}")
        
        return ActionResponse(
            content=f"Improved {len(improvements)} tests based on surviving mutations."
        )
    
    def _improve_tests_windows(self) -> ActionResponse:
        """Windows-specific approach to improve tests by direct analysis."""
        improvements = []
        
        # Read calculator.py to identify functions
        try:
            with open('calculator.py', 'r') as f:
                calculator_code = f.read()
                
            # Find function definitions
            func_matches = re.finditer(r'def (\w+)\(([^)]*)\):', calculator_code)
            
            for match in func_matches:
                func_name = match.group(1)
                args = match.group(2)
                
                # Generate specific additional tests for each function
                improved_test = self._generate_windows_test(func_name, args)
                if improved_test:
                    improvements.append(('calculator.py', improved_test))
                    
            # Apply improvements to test files
            for file_name, improved_test in improvements:
                test_file_name = f"test_{file_name}"
                
                # Check if test file exists
                if os.path.exists(test_file_name):
                    with open(test_file_name, 'r') as f:
                        content = f.read()
                    
                    # Append the new test if it doesn't already exist
                    if improved_test not in content:
                        with open(test_file_name, 'a') as f:
                            f.write("\n\n" + improved_test)
                else:
                    # Create a new test file
                    with open(test_file_name, 'w') as f:
                        module_name = file_name.replace('.py', '')
                        f.write(f"import pytest\nfrom {module_name} import *\n\n{improved_test}")
            
            return ActionResponse(
                content=f"Improved {len(improvements)} tests based on direct code analysis."
            )
                
        except Exception as e:
            return ActionResponse(
                content=f"Error improving tests on Windows: {str(e)}"
            )
    
    def _generate_windows_test(self, func_name: str, args: str) -> str:
        """Generate additional tests for Windows where mutmut can't run."""
        args_list = [arg.strip().split(':')[0].split('=')[0].strip() for arg in args.split(',') if arg.strip()]
        
        if func_name == 'add':
            return """
def test_{0}_edge_cases():
    \"\"\"Edge cases for the add function.\"\"\"
    assert {0}(0, 0) == 0
    assert {0}(100, -100) == 0
    assert {0}(-1, -1) == -2
    assert {0}(10**6, 10**6) == 2 * 10**6
""".format(func_name)
        elif func_name == 'subtract':
            return """
def test_{0}_edge_cases():
    \"\"\"Edge cases for the subtract function.\"\"\"
    assert {0}(0, 0) == 0
    assert {0}(100, 100) == 0
    assert {0}(-1, -1) == 0
    assert {0}(-1, 1) == -2
    assert {0}(10**6, 10**6) == 0
""".format(func_name)
        elif func_name == 'multiply':
            return """
def test_{0}_edge_cases():
    \"\"\"Edge cases for the multiply function.\"\"\"
    assert {0}(0, 5) == 0
    assert {0}(5, 0) == 0
    assert {0}(1, 100) == 100
    assert {0}(-1, 10) == -10
    assert {0}(-2, -3) == 6
""".format(func_name)
        elif func_name == 'divide':
            return """
def test_{0}_edge_cases():
    \"\"\"Edge cases for the divide function.\"\"\"
    assert {0}(10, 2) == 5
    assert {0}(10, 3) == pytest.approx(3.333333, 0.01)
    assert {0}(-10, 2) == -5
    assert {0}(-10, -2) == 5
    assert {0}(0, 5) == 0
    
    with pytest.raises(ValueError):
        {0}(10, 0)
""".format(func_name)
        else:
            # Generic test for unknown functions
            return """
def test_{0}_additional():
    \"\"\"Additional tests for {0}.\"\"\"
    # Add more test cases here based on the function behavior
    pass
""".format(func_name)
    
    def _generate_test_for_mutation(self, file_name: str, mutation_info: str) -> str:
        """Generate a test for a specific mutation."""
        # Extract function name from mutation info
        func_match = re.search(r'def (\w+)\(', mutation_info)
        if not func_match:
            return ""
            
        func_name = func_match.group(1)
        
        # Extract the mutation details
        mutation_lines = mutation_info.split('\n')
        original_line = ""
        mutated_line = ""
        
        for i, line in enumerate(mutation_lines):
            if line.startswith('-'):
                original_line = line[1:].strip()
            elif line.startswith('+') and original_line:
                mutated_line = line[1:].strip()
                break
        
        if not original_line or not mutated_line:
            return ""
        
        # Generate a test case that would catch this mutation
        module_name = file_name.replace('.py', '')
        
        # Create a test based on the mutation type
        if "==" in original_line and "!=" in mutated_line:
            # Equality mutation
            return f"""
def test_{func_name}_equality_mutation():
    # Testing for mutation: {original_line} -> {mutated_line}
    from {module_name} import {func_name}
    # Test both cases for equality
    assert {func_name}(1, 1) == 2  # This would fail if == became !=
    assert {func_name}(2, 2) != 5  # This ensures correct inequality comparisons
"""
        elif "+" in original_line and "-" in mutated_line:
            # Arithmetic operator mutation
            return f"""
def test_{func_name}_arithmetic_mutation():
    # Testing for mutation: {original_line} -> {mutated_line}
    from {module_name} import {func_name}
    # Test cases that would catch +/- mutations
    assert {func_name}(5, 3) == 8  # This would fail if + became -
    assert {func_name}(5, 3) != 2  # This ensures it's not subtraction
"""
        else:
            # Generic test
            return f"""
def test_{func_name}_mutation_catch():
    # Testing for mutation: {original_line} -> {mutated_line}
    from {module_name} import {func_name}
    # Add more specific test cases to catch this mutation
    assert {func_name}(10, 20) == 30
    assert {func_name}(0, 0) == 0
    assert {func_name}(-5, 5) == 0
"""
    
    @function
    def run_full_cycle(self, action_input: ActionInput) -> ActionResponse:
        """Run a full cycle of coverage check, mutation testing, and test improvement."""
        # Run coverage check
        coverage_response = self.run_coverage(action_input)
        
        # Run mutation testing
        mutation_response = self.run_mutmut(action_input)
        
        # Find surviving mutations
        surviving_response = self.find_surviving_mutations(action_input)
        
        # Improve tests
        improvement_response = self.improve_tests(action_input)
        
        # Check if calculator module has 100% coverage
        if self.calculator_coverage >= self.target_coverage:
            if not IS_WINDOWS:
                # On non-Windows, also check mutation score
                if self.current_mutations_killed == self.total_mutations:
                    return ActionResponse(
                        content=(
                            f"SUCCESS! Achieved {self.calculator_coverage}% coverage for calculator module and killed "
                            f"all {self.total_mutations} mutations.\n\n"
                            f"Coverage details:\n{coverage_response.content}\n\n"
                            f"Mutation details:\n{mutation_response.content}"
                        )
                    )
            else:
                # On Windows, just check coverage
                return ActionResponse(
                    content=(
                        f"SUCCESS! Achieved {self.calculator_coverage}% coverage for calculator module.\n\n"
                        f"Coverage details:\n{coverage_response.content}\n\n"
                        f"Note: Full mutation testing is not available on Windows."
                    )
                )
                
        # In progress
        content_parts = [
            f"Progress: {self.current_coverage}% overall coverage, {self.calculator_coverage}% calculator module coverage"
        ]
        
        if not IS_WINDOWS:
            content_parts[0] += f", {self.current_mutations_killed}/{self.total_mutations} mutations killed"
            
        content_parts[0] += ".\n\n"
        content_parts.append(f"Coverage details:\n{coverage_response.content}\n\n")
        
        if not IS_WINDOWS:
            content_parts.append(f"Mutation details:\n{mutation_response.content}\n\n")
            
        content_parts.append(f"Improvements made:\n{improvement_response.content}\n\n")
        content_parts.append(f"Run again to continue improving test coverage.")
        
        return ActionResponse(content="".join(content_parts))

# Main entry point
if __name__ == "__main__":
    agent = MutationTestingAgent()
    agent.run() 