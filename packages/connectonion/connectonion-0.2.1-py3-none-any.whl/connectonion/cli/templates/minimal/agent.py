#!/usr/bin/env python3
"""Minimal ConnectOnion agent example."""

import os
from dotenv import load_dotenv
from connectonion import Agent, llm_do

# Load environment variables from .env file
load_dotenv()


def hello_world(name: str = "World") -> str:
    """Simple greeting function.
    
    Args:
        name: Name to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}! Welcome to ConnectOnion."


def main():
    """Run the minimal agent."""
    # Create agent with a simple tool
    agent = Agent(
        name="minimal-agent",
        tools=[hello_world],
        model=os.getenv("MODEL", "co/o4-mini")
    )
    
    # Example interaction
    response = agent.input("Say hello to the user")
    print(response)
    
    # You can also use llm_do directly for simple queries
    simple_response = llm_do("What is ConnectOnion?")
    print(simple_response)


if __name__ == "__main__":
    main()