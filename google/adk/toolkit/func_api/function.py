"""
Mock implementation of Google's ADK function API.
"""

def function(func):
    """Decorator for functions that can be used by the agent.
    
    This is a mock implementation that simply returns the function.
    In a real implementation, this would register the function with the agent.
    """
    return func 