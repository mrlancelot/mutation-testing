# Mutation Testing Agent

This project demonstrates an agent-based approach to mutation testing using mutmut.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the mutation testing agent:
```
python mutation_agent.py
```

## Project Structure

- `calculator.py` - Sample module to test
- `test_calculator.py` - Tests for the calculator module
- `mutation_agent.py` - Agent for mutation testing
- `requirements.txt` - Project dependencies

## How It Works

The agent will:
1. Run tests with coverage analysis
2. Perform mutation testing with mutmut
3. Analyze surviving mutations
4. Automatically add new tests to catch mutations
5. Repeat until 100% coverage and all mutations are killed

## Commands

- Run tests with coverage: `pytest --cov=. --cov-report=term`
- Run mutation tests: `mutmut run`
- Show mutation results: `mutmut results`
- Show specific mutation: `mutmut show <id>` 