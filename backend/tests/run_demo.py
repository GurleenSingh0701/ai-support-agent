import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from router.router_agent import router_agent

PRESET_QUERIES = [
    ("1", "Order Status Inquiry", "Where is my package for order #ORD-99823?"),
    ("2", "Return & Refund Approval", "I want to return my item #ORD-55412 because it doesn't fit."),
    ("3", "Payment & Billing Audit", "I see a duplicate charge on my credit card statement for my subscription."),
    ("4", "Store Policy Question", "What is your 30-day return policy and warranty guarantee?"),
    ("5", "High Frustration Escalation", "THIS SERVICE IS A COMPLETE SCAM! I DEMAND A FULL REFUND RIGHT NOW OR I WILL SUE!"),
]

def format_result(query: str, res: dict):
    print("\n" + "=" * 70)
    print(f" 📥 CUSTOMER QUERY : \"{query}\"")
    print("=" * 70)
    print(f" 🎯 Classified Intent : {res['intent']} (Confidence: {res['confidence']:.2f})")
    print(f" 📊 Sentiment Triage  : {res['sentiment']} (Urgency/Priority: {res['priority']})")
    print(f" 🚦 System Status     : {res['status']}")
    
    if res['escalated']:
        print(f" 🚨 ESCALATION EVENT  : Escalated due to [{res.get('escalation_reason', 'N/A')}]")
        print(" 📢 Pub/Sub Notice    : Broadcast payload sent to Redis 'agent_queue'")
    else:
        print(f" 🤖 LangGraph Node    : Multi-agent routing completed successfully")
        
    print("-" * 70)
    print(" 💬 GENERATED RESPONSE:")
    print(res['response'])
    print("=" * 70 + "\n")

def run_interactive():
    print("\n" + "*" * 70)
    print(" 🚀 AUTODESK MULTI-AGENT ROUTER DEMO TEST RUNNER")
    print("*" * 70)
    
    while True:
        print("\nSelect an option:")
        for code, label, q in PRESET_QUERIES:
            print(f" [{code}] {label:30} -> \"{q[:45]}...\"")
        print(" [C] Enter Custom Query")
        print(" [Q] Quit")
        
        choice = input("\nEnter choice (1-5, C, Q): ").strip().upper()
        
        if choice == "Q":
            print("Exiting demo runner. Goodbye!")
            break
            
        selected_query = None
        for code, label, q in PRESET_QUERIES:
            if choice == code:
                selected_query = q
                break
                
        if choice == "C":
            selected_query = input("\nType your custom message: ").strip()
            
        if not selected_query:
            print("Invalid choice. Please try again.")
            continue
            
        res = router_agent.route_message(selected_query)
        format_result(selected_query, res)

if __name__ == "__main__":
    run_interactive()
