#!/usr/bin/env python3
import subprocess
import re
import time
import sys

def extract_coverage(output):
    """Extract coverage percentage from output."""
    # Try to extract calculator module coverage
    calc_match = re.search(r'(\d+(?:\.\d+)?)% calculator module coverage', output)
    if calc_match:
        return float(calc_match.group(1))
        
    # Fall back to overall progress
    progress_match = re.search(r'Progress: (\d+(?:\.\d+)?)%', output)
    if progress_match:
        return float(progress_match.group(1))
        
    return 0.0

def extract_mutations(output):
    """Extract mutation information from output."""
    match = re.search(r'(\d+)/(\d+) mutations killed', output)
    if match:
        killed = int(match.group(1))
        total = int(match.group(2))
        return killed, total
    return 0, 0

def main():
    """Run the mutation agent until 100% coverage is achieved."""
    max_iterations = 10
    iteration = 1
    coverage = 0.0
    killed_mutations = 0
    total_mutations = 0
    
    print("Starting mutation testing agent loop")
    print("======================================")
    
    while iteration <= max_iterations:
        print(f"\nIteration {iteration}/{max_iterations}")
        print("---------------------------")
        
        # Run the agent
        result = subprocess.run(
            [sys.executable, "mutation_agent.py"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        # Extract progress information
        prev_coverage = coverage
        coverage = extract_coverage(result.stdout)
        prev_killed = killed_mutations
        killed_mutations, total_mutations = extract_mutations(result.stdout)
        
        # Check for success
        if "SUCCESS!" in result.stdout or coverage >= 100.0:
            print("\nSuccess! Achieved 100% coverage for calculator module.")
            return 0
        
        # Check for progress
        if coverage <= prev_coverage and killed_mutations <= prev_killed and iteration > 1:
            print("\nNo progress made in this iteration.")
        
        iteration += 1
        time.sleep(1)  # Small delay between iterations
    
    print("\nMaximum iterations reached without achieving 100% coverage.")
    print(f"Final coverage: {coverage}%")
    print(f"Final mutation score: {killed_mutations}/{total_mutations}")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 