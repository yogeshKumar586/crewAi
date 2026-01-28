"""Main entry point for HR Bot Flow."""

#!/usr/bin/env python
import sys
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables - search for .env file in parent directories
dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)
    print(f"✅ Loaded .env from: {dotenv_path}")
else:
    # Fallback: try to find .env in project root
    current_dir = Path(__file__).resolve()
    for parent in current_dir.parents:
        env_file = parent / '.env'
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            print(f"✅ Loaded .env from: {env_file}")
            break

from aye_finance_hr_bot_v2.flows.hr_bot_flow import HRBotFlow


def run():
    """Run the HR Bot Flow with default user_id."""
    print("🤖 Starting HR Bot Flow...")
    print("📝 Using default user_id: '123'\n")
    
    # Create flow instance
    flow = HRBotFlow()
    
    # Run flow with inputs (including user_id)
    result = flow.kickoff(inputs={
        'user_id': '123',  # Default user for testing
        'employee_query': 'What is my salary?'
    })
    
    print("\n" + "="*50)
    print("📊 RESULT:")
    print("="*50)
    print(result)
    print("="*50)


def chat():
    """Interactive chat mode with MongoDB persistence."""
    print("🤖 HR Bot - Interactive Chat Mode")
    print("📝 Using default user_id: '123'")
    print("Type 'quit' to exit\n")
    
    # Create flow instance ONCE (reuse for entire session)
    flow = HRBotFlow()
    
    print("✅ Ready! Ask your HR questions...")
    print("💡 Your credentials will be saved to MongoDB after first query\n")
    
    while True:
        query = input("You: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            # Run flow with inputs (MongoDB will handle credential persistence)
            result = flow.kickoff(inputs={
                'user_id': '123',  # Default user for testing
                'employee_query': query
            })
            
            print(f"\n🤖 Bot: {result}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        chat()
    else:
        run()
