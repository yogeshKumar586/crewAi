"""Main entry point for HR Bot Flow."""

#!/usr/bin/env python
import sys
from aye_finance_hr_bot_v2.flows.hr_bot_flow import HRBotFlow


def run():
    """Run the HR Bot Flow."""
    print("🤖 Starting HR Bot Flow...")
    
    # Create flow instance
    flow = HRBotFlow()
    
    # Set inputs in state
    flow.state['employee_query'] = 'What is my salary?'
    flow.state['employee_id'] = 'EMP12345'
    flow.state['employee_email'] = 'john@ayefinance.com'
    
    # Run flow
    result = flow.kickoff()
    
    print("\n" + "="*50)
    print("📊 RESULT:")
    print("="*50)
    print(result)
    print("="*50)


def chat():
    """Interactive chat mode."""
    print("🤖 HR Bot - Interactive Chat Mode")
    print("Type 'quit' to exit\n")
    
    flow = HRBotFlow()
    
    # Get employee info once
    employee_id = input("Enter your Employee ID (e.g., EMP12345): ").strip()
    employee_email = input("Enter your Email (e.g., john@ayefinance.com): ").strip()
    
    print("\n✅ Ready! Ask your HR questions...\n")
    
    while True:
        query = input("You: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            # Set inputs in state
            flow.state['employee_query'] = query
            flow.state['employee_id'] = employee_id
            flow.state['employee_email'] = employee_email
            
            result = flow.kickoff()
            print(f"\n🤖 Bot: {result}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        chat()
    else:
        run()
