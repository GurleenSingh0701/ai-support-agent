import os
from sub_agents.main_arch import BaseSubAgent, AgentState

class PaymentAgent(BaseSubAgent):
    def execute(self, state: AgentState) -> AgentState:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        
        # Mock database retrieval
        payment_context = {
            "status": "Verified / Settled",
            "hold_period": "24-48 hours",
            "support_note": "No duplicate settled charges detected. Second charge is likely a temporary authorization hold."
        }
        
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    f"You are the Billing & Payment Audit Specialist for Autodesk Customer Support. "
                    f"Financial inquiries cause high anxiety, so your role is to provide extreme clarity, transparency, and reassurance.\n\n"
                    
                    f"### GUIDELINES:\n"
                    f"1. **Tone:** Empathetic, highly professional, and reassuring. Validate their concern immediately.\n"
                    f"2. **Explanation:** Clearly explain the difference between a 'settled charge' and a 'temporary authorization hold' (which dissolves automatically).\n"
                    f"3. **Security:** Never ask for full credit card numbers, passwords, or sensitive PII.\n"
                    f"4. **Grounding:** Base your audit entirely on the 'Audit Record' provided below.\n"
                    f"5. **Formatting:** Use Markdown bullet points to break down complex financial concepts.\n\n"
                    
                    f"### INPUTS:\n"
                    f"- Customer Query: '{state.user_message}'\n"
                    f"- Audit Record: {payment_context}\n\n"
                    
                    f"Generate a clear, reassuring response to the customer."
                )
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                
                if response and response.text:
                    state.sub_agent_output = response.text
                    return state
            except Exception as e:
                print(f"[PaymentAgent LLM Warning] Falling back due to: {e}")
                
        # Fallback if LLM fails
        state.sub_agent_output = (
            f"**Billing & Payment Audit**\n\n"
            f"We have audited your recent billing transaction details.\n"
            f"- Payment Status: {payment_context['status']}\n"
            f"- A temporary authorization hold will automatically dissolve within {payment_context['hold_period']}.\n\n"
            f"If you continue to see a duplicate charge after 48 hours, please reply so we can investigate further."
        )
        return state