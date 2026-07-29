import os
from sub_agents.main_arch import BaseSubAgent, AgentState

class ReturnRefundAgent(BaseSubAgent):
    def execute(self, state: AgentState) -> AgentState:
        # Intercept missing entities
        order_id = state.entities.get("order_id") if state.entities else None
        if not order_id:
            state.sub_agent_output = "I can certainly help you process a return or refund. To get started, could you please provide the order number (e.g., ORD-12345) associated with your purchase?"
            return state

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        
        # Mock database retrieval
        refund_context = {
            "order_id": order_id,
            "return_eligible": True,
            "rma_number": "RMA-99201",
            "refund_timeline": "3-5 business days upon warehouse pickup",
            "shipping_label": "Prepaid label sent to registered email"
        }
        
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    f"You are the Returns & Warranty Specialist for Autodesk Customer Support. "
                    f"Your goal is to make the return process as frictionless and clear as possible for the customer.\n\n"
                    
                    f"### GUIDELINES:\n"
                    f"1. **Tone:** Apologetic (if the product failed them), efficient, and highly transparent.\n"
                    f"2. **Process Clarity:** Clearly outline the step-by-step instructions for what the customer needs to do next (e.g., print the label, attach it, drop it off).\n"
                    f"3. **Expectation Setting:** Explicitly state the refund timeline so the customer isn't left wondering when they will get their money back.\n"
                    f"4. **Grounding:** Use ONLY the 'Authorization Details' provided below.\n"
                    f"5. **Formatting:** Use Markdown. Bold the RMA number and timeline.\n\n"
                    
                    f"### INPUTS:\n"
                    f"- Customer Query: '{state.user_message}'\n"
                    f"- Authorization Details: {refund_context}\n\n"
                    
                    f"Generate the return authorization response."
                )
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                
                if response and response.text:
                    state.sub_agent_output = response.text
                    return state
            except Exception as e:
                print(f"[RefundAgent LLM Warning] Falling back due to: {e}")
                
        # Fallback if LLM fails
        state.sub_agent_output = (
            f"**Return & Refund Request Processed**\n\n"
            f"We have verified your purchase for **{order_id}** under our 30-Day Return Guarantee.\n"
            f"- Return Authorization ID: **{refund_context['rma_number']}**\n"
            f"- Label Status: {refund_context['shipping_label']}\n"
            f"- Refund Timeline: {refund_context['refund_timeline']}.\n\n"
            f"Please attach the prepaid label to your package and drop it off at any authorized shipping center."
        )
        return state