# # from typing import Dict, Any, Optional
# # from langgraph.graph import StateGraph, END
# # from sub_agents.main_arch import AgentState
# # from classifier.intent_classifier import classify_intent
# # from classifier.priority_classifier import calculate_priority
# # from sub_agents.order_agent import OrderAgent
# # from sub_agents.return_refund_agent import ReturnRefundAgent
# # from sub_agents.payment_agent import PaymentAgent
# # from knowledgebase.KB_retriever import kb_retriever
# # from escalation.escalation_handler import compile_and_escalate

# # class RouterAgent:
# #     def __init__(self):
# #         self.order_agent = OrderAgent()
# #         self.refund_agent = ReturnRefundAgent()
# #         self.payment_agent = PaymentAgent()
# #         self.app = self._build_graph()

# #     def router_node(self, state: AgentState) -> AgentState:
# #         intent_res = classify_intent(state.user_message)
# #         priority_res = calculate_priority(state.user_message, user_tier=state.user_tier)
        
# #         state.intent = intent_res["intent"]
# #         state.confidence = intent_res["confidence"]
# #         state.entities = intent_res["entities"]
# #         state.sentiment = priority_res["sentiment"]
# #         state.priority = priority_res["priority"]
        
# #         if state.confidence < 0.70 or state.sentiment == "VERY_NEGATIVE":
# #             state.requires_escalation = True
# #             state.escalation_reason = "LOW_CONFIDENCE" if state.confidence < 0.70 else "HIGH_CUSTOMER_FRUSTRATION"
            
# #         return state

# #     def escalation_node(self, state: AgentState) -> AgentState:
# #         escalation_info = compile_and_escalate(
# #             ticket_id=state.ticket_id or 0,
# #             customer_id=state.customer_id or 0,
# #             user_message=state.user_message,
# #             sentiment=state.sentiment,
# #             urgency=state.priority,
# #             reason=state.escalation_reason or "MANUAL_ESCALATION"
# #         )
# #         state.sub_agent_output = (
# #             f"🚨 **Issue Escalated to Support Agent**\n\n"
# #             f"Your query has been assigned to a human support agent for immediate attention.\n"
# #             f"• Priority: **{state.priority}**\n"
# #             f"• Reason: {escalation_info['summary']}\n\n"
# #             f"An agent will join this conversation shortly."
# #         )
# #         return state

# #     def order_agent_node(self, state: AgentState) -> AgentState:
# #         return self.order_agent.execute(state)

# #     def refund_agent_node(self, state: AgentState) -> AgentState:
# #         return self.refund_agent.execute(state)

# #     def payment_agent_node(self, state: AgentState) -> AgentState:
# #         return self.payment_agent.execute(state)

# #     def kb_policy_node(self, state: AgentState) -> AgentState:
# #         snippets = kb_retriever.search(state.user_message, top_k=2)
# #         policy_info = "\n\n".join(f"• {s}" for s in snippets)
# #         state.sub_agent_output = (
# #             f"📖 **Store Policy Information**\n\n"
# #             f"Based on our support knowledge base:\n{policy_info}\n\n"
# #             f"If you need further specialized assistance, please let me know!"
# #         )
# #         return state

# #     def route_decision(self, state: AgentState) -> str:
# #         if state.requires_escalation:
# #             return "escalation_node"
        
# #         if state.intent == "ORDER_INQUIRY":
# #             return "order_agent_node"
# #         elif state.intent == "RETURN_REFUND":
# #             return "refund_agent_node"
# #         elif state.intent == "PAYMENT_ISSUE":
# #             return "payment_agent_node"
# #         else:
# #             return "kb_policy_node"

# #     def _build_graph(self):
# #         workflow = StateGraph(AgentState)
        
# #         workflow.add_node("router_node", self.router_node)
# #         workflow.add_node("escalation_node", self.escalation_node)
# #         workflow.add_node("order_agent_node", self.order_agent_node)
# #         workflow.add_node("refund_agent_node", self.refund_agent_node)
# #         workflow.add_node("payment_agent_node", self.payment_agent_node)
# #         workflow.add_node("kb_policy_node", self.kb_policy_node)
        
# #         workflow.set_entry_point("router_node")
        
# #         workflow.add_conditional_edges(
# #             "router_node",
# #             self.route_decision,
# #             {
# #                 "escalation_node": "escalation_node",
# #                 "order_agent_node": "order_agent_node",
# #                 "refund_agent_node": "refund_agent_node",
# #                 "payment_agent_node": "payment_agent_node",
# #                 "kb_policy_node": "kb_policy_node"
# #             }
# #         )
        
# #         workflow.add_edge("escalation_node", END)
# #         workflow.add_edge("order_agent_node", END)
# #         workflow.add_edge("refund_agent_node", END)
# #         workflow.add_edge("payment_agent_node", END)
# #         workflow.add_edge("kb_policy_node", END)
        
# #         return workflow.compile()

# #     def route_message(
# #         self,
# #         user_message: str,
# #         ticket_id: Optional[int] = None,
# #         customer_id: Optional[int] = None,
# #         user_tier: str = "STANDARD",
# #         conversation_history: Optional[list] = None
# #     ) -> Dict[str, Any]:
# #         initial_state = AgentState(
# #             ticket_id=ticket_id,
# #             customer_id=customer_id,
# #             user_message=user_message,
# #             user_tier=user_tier,
# #             conversation_history=conversation_history or []
# #         )
# #         result = self.app.invoke(initial_state)
        
# #         if isinstance(result, dict):
# #             final_state = AgentState(**result)
# #         else:
# #             final_state = result

# #         # Non-escalated tickets are considered autonomously RESOLVED by the AI agent;
# #         # only escalated tickets remain open for a human agent to work.
# #         status = "ESCALATED" if final_state.requires_escalation else "RESOLVED"

# #         return {
# #             "response": final_state.sub_agent_output or "No response generated",
# #             "intent": final_state.intent,
# #             "confidence": final_state.confidence,
# #             "priority": final_state.priority,
# #             "sentiment": final_state.sentiment,
# #             "status": status,
# #             "escalated": final_state.requires_escalation,
# #             "escalation_reason": final_state.escalation_reason
# #         }

# # router_agent = RouterAgent()





# from typing import Dict, Any, Optional
# from langgraph.graph import StateGraph, END
# from sub_agents.main_arch import AgentState
# from classifier.unified_classifier import analyze_user_request
# from sub_agents.order_agent import OrderAgent
# from sub_agents.return_refund_agent import ReturnRefundAgent
# from sub_agents.payment_agent import PaymentAgent
# from knowledgebase.KB_retriever import kb_retriever
# from escalation.escalation_handler import compile_and_escalate

# class RouterAgent:
#     def __init__(self):
#         self.order_agent = OrderAgent()
#         self.refund_agent = ReturnRefundAgent()
#         self.payment_agent = PaymentAgent()
#         self.app = self._build_graph()

#     def router_node(self, state: AgentState) -> AgentState:
#         # Single-pass LLM call for Classification, Extraction, and Priority
#         analysis = analyze_user_request(
#             user_message=state.user_message,
#             user_tier=state.user_tier,
#             conversation_history=state.conversation_history
#         )
        
#         state.intent = analysis.primary_intent
#         state.confidence = analysis.confidence
#         # Handle dict transformation for Pydantic v2 compatibility
#         state.entities = analysis.entities.model_dump() if hasattr(analysis.entities, 'model_dump') else analysis.entities.dict()
#         state.sentiment = analysis.sentiment
#         state.priority = analysis.priority
        
#         # Override to human escalation if model flagged it OR confidence is too low
#         if analysis.requires_escalation or state.confidence < 0.70:
#             state.requires_escalation = True
#             state.escalation_reason = analysis.escalation_reason or ("LOW_CONFIDENCE" if state.confidence < 0.70 else "HIGH_CUSTOMER_FRUSTRATION")
            
#         return state

#     def escalation_node(self, state: AgentState) -> AgentState:
#         escalation_info = compile_and_escalate(
#             ticket_id=state.ticket_id or 0,
#             customer_id=state.customer_id or 0,
#             user_message=state.user_message,
#             sentiment=state.sentiment,
#             urgency=state.priority,
#             reason=state.escalation_reason or "MANUAL_ESCALATION"
#         )
#         state.sub_agent_output = (
#             f"**Issue Escalated to Support Agent**\n\n"
#             f"Your query has been assigned to a human support agent for immediate attention.\n"
#             f"- Priority: **{state.priority}**\n"
#             f"- Reason: {escalation_info['summary']}\n\n"
#             f"An agent will join this conversation shortly."
#         )
#         return state

#     def order_agent_node(self, state: AgentState) -> AgentState:
#         return self.order_agent.execute(state)

#     def refund_agent_node(self, state: AgentState) -> AgentState:
#         return self.refund_agent.execute(state)

#     def payment_agent_node(self, state: AgentState) -> AgentState:
#         return self.payment_agent.execute(state)

#     def kb_policy_node(self, state: AgentState) -> AgentState:
#         snippets = kb_retriever.search(state.user_message, top_k=2)
#         policy_info = "\n\n".join(f"- {s}" for s in snippets)
#         state.sub_agent_output = (
#             f"**Store Policy Information**\n\n"
#             f"Based on our support knowledge base:\n{policy_info}\n\n"
#             f"If you need further specialized assistance, please let me know!"
#         )
#         return state

#     def route_decision(self, state: AgentState) -> str:
#         if state.requires_escalation:
#             return "escalation_node"
            
#         if state.intent == "ORDER_INQUIRY":
#             return "order_agent_node"
#         elif state.intent == "RETURN_REFUND":
#             return "refund_agent_node"
#         elif state.intent == "PAYMENT_ISSUE":
#             return "payment_agent_node"
#         elif state.intent == "POLICY_QUESTION":
#             return "kb_policy_node"
#         elif state.intent == "TECHNICAL_SUPPORT":
#             # If you build a Tech Agent later, route it there. For now, escalate tech issues.
#             state.requires_escalation = True
#             state.escalation_reason = "TECHNICAL_SUPPORT_REQUIRED"
#             return "escalation_node"
#         else:
#             # Fallback for "OTHER" or highly ambiguous queries
#             state.requires_escalation = True
#             state.escalation_reason = "AMBIGUOUS_QUERY_ESCALATION"
#             return "escalation_node"

#     def _build_graph(self):
#         workflow = StateGraph(AgentState)
        
#         workflow.add_node("router_node", self.router_node)
#         workflow.add_node("escalation_node", self.escalation_node)
#         workflow.add_node("order_agent_node", self.order_agent_node)
#         workflow.add_node("refund_agent_node", self.refund_agent_node)
#         workflow.add_node("payment_agent_node", self.payment_agent_node)
#         workflow.add_node("kb_policy_node", self.kb_policy_node)
        
#         workflow.set_entry_point("router_node")
        
#         workflow.add_conditional_edges(
#             "router_node",
#             self.route_decision,
#             {
#                 "escalation_node": "escalation_node",
#                 "order_agent_node": "order_agent_node",
#                 "refund_agent_node": "refund_agent_node",
#                 "payment_agent_node": "payment_agent_node",
#                 "kb_policy_node": "kb_policy_node"
#             }
#         )
        
#         workflow.add_edge("escalation_node", END)
#         workflow.add_edge("order_agent_node", END)
#         workflow.add_edge("refund_agent_node", END)
#         workflow.add_edge("payment_agent_node", END)
#         workflow.add_edge("kb_policy_node", END)
        
#         return workflow.compile()

#     def route_message(
#         self,
#         user_message: str,
#         ticket_id: Optional[int] = None,
#         customer_id: Optional[int] = None,
#         user_tier: str = "STANDARD",
#         conversation_history: Optional[list] = None
#     ) -> Dict[str, Any]:
#         initial_state = AgentState(
#             ticket_id=ticket_id,
#             customer_id=customer_id,
#             user_message=user_message,
#             user_tier=user_tier,
#             conversation_history=conversation_history or []
#         )
#         result = self.app.invoke(initial_state)
        
#         if isinstance(result, dict):
#             final_state = AgentState(**result)
#         else:
#             final_state = result

#         status = "ESCALATED" if final_state.requires_escalation else "RESOLVED"
#         return {
#             "response": final_state.sub_agent_output or "No response generated.",
#             "intent": final_state.intent,
#             "confidence": final_state.confidence,
#             "priority": final_state.priority,
#             "sentiment": final_state.sentiment,
#             "status": status,
#             "escalated": final_state.requires_escalation,
#             "escalation_reason": final_state.escalation_reason
#         }

# router_agent = RouterAgent()


import os
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from sub_agents.main_arch import AgentState
from classifier.unified_classifier import analyze_user_request
from sub_agents.order_agent import OrderAgent
from sub_agents.return_refund_agent import ReturnRefundAgent
from sub_agents.payment_agent import PaymentAgent
from knowledgebase.KB_retriever import kb_retriever
from escalation.escalation_handler import compile_and_escalate

class RouterAgent:
    def __init__(self):
        self.order_agent = OrderAgent()
        self.refund_agent = ReturnRefundAgent()
        self.payment_agent = PaymentAgent()
        self.app = self._build_graph()

    def router_node(self, state: AgentState) -> AgentState:
        # Single-pass LLM call for Classification, Extraction, and Priority
        analysis = analyze_user_request(
            user_message=state.user_message,
            user_tier=state.user_tier,
            conversation_history=state.conversation_history
        )
        
        state.intent = analysis.primary_intent
        state.confidence = analysis.confidence
        # Handle dict transformation for Pydantic v2 compatibility
        state.entities = analysis.entities.model_dump() if hasattr(analysis.entities, 'model_dump') else analysis.entities.dict()
        state.sentiment = analysis.sentiment
        state.priority = analysis.priority
        
        # Override to human escalation if model flagged it OR confidence is too low
        if analysis.requires_escalation or state.confidence < 0.70:
            state.requires_escalation = True
            state.escalation_reason = analysis.escalation_reason or ("LOW_CONFIDENCE" if state.confidence < 0.70 else "HIGH_CUSTOMER_FRUSTRATION")
            
        return state

    def escalation_node(self, state: AgentState) -> AgentState:
        escalation_info = compile_and_escalate(
            ticket_id=state.ticket_id or 0,
            customer_id=state.customer_id or 0,
            user_message=state.user_message,
            sentiment=state.sentiment,
            urgency=state.priority,
            reason=state.escalation_reason or "MANUAL_ESCALATION"
        )
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    f"You are the Support Handoff Coordinator for Autodesk Customer Support. "
                    f"You are transferring a customer to a human agent.\n\n"
                    f"### GUIDELINES:\n"
                    f"1. **Tone:** Empathetic, calm, and professional. If the escalation reason is frustration, apologize for the inconvenience.\n"
                    f"2. **Information:** Inform them that a human agent has been alerted and will join the chat shortly.\n"
                    f"3. **Context:** Acknowledge their specific issue briefly so they know they were heard.\n\n"
                    f"### INPUTS:\n"
                    f"- Customer Message: '{state.user_message}'\n"
                    f"- Priority Level: {state.priority}\n"
                    f"- Escalation Reason: {state.escalation_reason}\n\n"
                    f"Write a brief, comforting handoff message."
                )
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    state.sub_agent_output = response.text
                    return state
            except Exception as e:
                print(f"[Escalation Node LLM Warning] Falling back to static response: {e}")

        # Fallback static response
        state.sub_agent_output = (
            f"**Issue Escalated to Support Agent**\n\n"
            f"Your query has been assigned to a human support agent for immediate attention.\n"
            f"- Priority: **{state.priority}**\n"
            f"- Reason: {escalation_info['summary']}\n\n"
            f"An agent will join this conversation shortly."
        )
        return state

    def order_agent_node(self, state: AgentState) -> AgentState:
        return self.order_agent.execute(state)

    def refund_agent_node(self, state: AgentState) -> AgentState:
        return self.refund_agent.execute(state)

    def payment_agent_node(self, state: AgentState) -> AgentState:
        return self.payment_agent.execute(state)

    def kb_policy_node(self, state: AgentState) -> AgentState:
        snippets = kb_retriever.search(state.user_message, top_k=2)
        policy_context = "\n".join(f"- {s}" for s in snippets)
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    f"You are the Knowledge Base Assistant for Autodesk Customer Support. "
                    f"Your job is to answer policy questions clearly using ONLY the provided documentation snippets.\n\n"
                    f"### GUIDELINES:\n"
                    f"1. **Tone:** Helpful, precise, and polite.\n"
                    f"2. **Grounding:** Base your answer strictly on the 'Retrieved Policy Context'. Do not invent or assume policies outside of this text.\n"
                    f"3. **Synthesis:** Do not just copy-paste the bullet points. Synthesize them into a direct, conversational answer to the user's specific question.\n\n"
                    f"### INPUTS:\n"
                    f"- Customer Question: '{state.user_message}'\n"
                    f"- Retrieved Policy Context:\n{policy_context}\n\n"
                    f"Write a clear and helpful response."
                )
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    state.sub_agent_output = response.text
                    return state
            except Exception as e:
                print(f"[KB Policy Node LLM Warning] Falling back to static response: {e}")

        # Fallback static response
        state.sub_agent_output = (
            f"**Store Policy Information**\n\n"
            f"Based on our support knowledge base:\n{policy_context}\n\n"
            f"If you need further specialized assistance, please let me know!"
        )
        return state

    def route_decision(self, state: AgentState) -> str:
        if state.requires_escalation:
            return "escalation_node"
        
        if state.intent == "ORDER_INQUIRY":
            return "order_agent_node"
        elif state.intent == "RETURN_REFUND":
            return "refund_agent_node"
        elif state.intent == "PAYMENT_ISSUE":
            return "payment_agent_node"
        elif state.intent == "POLICY_QUESTION":
            return "kb_policy_node"
        elif state.intent == "TECHNICAL_SUPPORT":
            # Direct routing to human for tech issues since no agent exists yet
            state.requires_escalation = True
            state.escalation_reason = "TECHNICAL_SUPPORT_REQUIRED"
            return "escalation_node"
        else:
            # Fallback for "OTHER" or highly ambiguous queries
            state.requires_escalation = True
            state.escalation_reason = "AMBIGUOUS_QUERY_ESCALATION"
            return "escalation_node"

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("router_node", self.router_node)
        workflow.add_node("escalation_node", self.escalation_node)
        workflow.add_node("order_agent_node", self.order_agent_node)
        workflow.add_node("refund_agent_node", self.refund_agent_node)
        workflow.add_node("payment_agent_node", self.payment_agent_node)
        workflow.add_node("kb_policy_node", self.kb_policy_node)
        
        workflow.set_entry_point("router_node")
        
        workflow.add_conditional_edges(
            "router_node",
            self.route_decision,
            {
                "escalation_node": "escalation_node",
                "order_agent_node": "order_agent_node",
                "refund_agent_node": "refund_agent_node",
                "payment_agent_node": "payment_agent_node",
                "kb_policy_node": "kb_policy_node"
            }
        )
        
        workflow.add_edge("escalation_node", END)
        workflow.add_edge("order_agent_node", END)
        workflow.add_edge("refund_agent_node", END)
        workflow.add_edge("payment_agent_node", END)
        workflow.add_edge("kb_policy_node", END)
        
        return workflow.compile()

    def route_message(
        self,
        user_message: str,
        ticket_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        user_tier: str = "STANDARD",
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        initial_state = AgentState(
            ticket_id=ticket_id,
            customer_id=customer_id,
            user_message=user_message,
            user_tier=user_tier,
            conversation_history=conversation_history or []
        )
        result = self.app.invoke(initial_state)
        
        if isinstance(result, dict):
            final_state = AgentState(**result)
        else:
            final_state = result

        status = "ESCALATED" if final_state.requires_escalation else "RESOLVED"
        return {
            "response": final_state.sub_agent_output or "No response generated.",
            "intent": final_state.intent,
            "confidence": final_state.confidence,
            "priority": final_state.priority,
            "sentiment": final_state.sentiment,
            "status": status,
            "escalated": final_state.requires_escalation,
            "escalation_reason": final_state.escalation_reason
        }

router_agent = RouterAgent()