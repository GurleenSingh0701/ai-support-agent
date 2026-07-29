import os
from sub_agents.main_arch import BaseSubAgent, AgentState

class OrderAgent(BaseSubAgent):
    def execute(self, state: AgentState) -> AgentState:
        # Intercept missing entities before asking the LLM to hallucinate
        order_id = state.entities.get("order_id") if state.entities else None
        if not order_id:
            state.sub_agent_output = "I would be happy to check the status of your order! Could you please provide your order number (e.g., ORD-12345) so I can look it up for you?"
            return state

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        
        # Mock database retrieval
        order_context = {
            "order_id": order_id,
            "status": "In Transit",
            "carrier": "FedEx Express",
            "tracking_number": f"FX-{str(order_id)[-5:]}",
            "estimated_delivery": "Tomorrow by 5:00 PM"
        }
        
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    f"You are the Logistics & Order Support Specialist for Autodesk Customer Support. "
                    f"Your role is to clearly and warmly communicate shipment statuses to customers.\n\n"
                    
                    f"### GUIDELINES:\n"
                    f"1. **Tone:** Professional, reassuring, and helpful. Mirror the customer's energy—if they are anxious, be comforting.\n"
                    f"2. **Grounding:** Use ONLY the data provided in the 'Order Record' below. Do not invent tracking numbers, carrier names, or delivery dates.\n"
                    f"3. **Formatting:** Use clean Markdown. Bold the Order ID, Tracking Number, and Estimated Delivery for easy reading.\n"
                    f"4. **Actionable:** Always provide a logical next step (e.g., 'You can use this tracking number on the carrier's website').\n\n"
                    
                    f"### INPUTS:\n"
                    f"- Customer Message: '{state.user_message}'\n"
                    f"- Order Record: {order_context}\n\n"
                    
                    f"Generate a direct response to the customer."
                )
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                
                if response and response.text:
                    state.sub_agent_output = response.text
                    return state
            except Exception as e:
                print(f"[OrderAgent LLM Warning] Falling back to structured response due to: {e}")
                
        # Fallback if LLM fails
        state.sub_agent_output = (
            f"**Order Status Update**\n\n"
            f"Your order **{order_id}** is currently **{order_context['status']}** via {order_context['carrier']}.\n"
            f"- Estimated Delivery: {order_context['estimated_delivery']}\n"
            f"- Tracking Number: {order_context['tracking_number']}\n\n"
            f"Is there anything else regarding this shipment I can assist you with?"
        )
        return state