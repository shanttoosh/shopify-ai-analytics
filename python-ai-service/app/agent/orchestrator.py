"""
Agent Orchestrator - Main controller for the agentic workflow
Coordinates all steps: Intent → Planning → Generation → Execution → Processing → Explanation
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from app.llm.client import LLMClient
from app.agent.intent_classifier import IntentClassifier
from app.agent.query_planner import QueryPlanner
from app.agent.shopifyql_generator import ShopifyQLGenerator
from app.agent.query_executor import QueryExecutor
from app.agent.result_processor import ResultProcessor
from app.agent.explainer import Explainer


class AgentOrchestrator:
    """
    Main agent orchestrator implementing the 6-step workflow:
    1. Intent Classification
    2. Query Planning
    3. ShopifyQL Generation
    4. Query Execution
    5. Result Processing
    6. Natural Language Explanation
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
        # Initialize agent components
        self.intent_classifier = IntentClassifier(llm_client)
        self.query_planner = QueryPlanner(llm_client)
        self.shopifyql_generator = ShopifyQLGenerator(llm_client)
        self.query_executor = QueryExecutor()
        self.result_processor = ResultProcessor()
        self.explainer = Explainer(llm_client)
        
        self.reasoning_steps = []

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user question through the complete agentic workflow
        
        Args:
            request: {
                "store_id": str,
                "question": str,
                "access_token": Optional[str],
                "use_mock": bool
            }
            
        Returns:
            {
                "answer": str,
                "confidence": str,
                "shopify_query": str,
                "reasoning": List[str],
                "metadata": Dict
            }
        """
        self.reasoning_steps = []
        start_time = datetime.now()
        
        question = request["question"]
        store_id = request["store_id"]
        use_mock = request.get("use_mock", False)
        
        try:
            # Step 1: Intent Classification
            print("🎯 Step 1: Classifying intent...")
            intent_result = await self.intent_classifier.classify(question)
            self._add_reasoning(f"Classified as: {intent_result['intent']}")
            
            # Check if question is too ambiguous
            if intent_result.get("confidence") == "low":
                return self._handle_ambiguous_question(question, intent_result)
            
            # Step 2: Query Planning
            print("📋 Step 2: Planning query...")
            plan = await self.query_planner.plan(intent_result, question)
            self._add_reasoning(
                f"Need data from: {', '.join(plan['resources_needed'])}"
            )
            
            # Step 3: ShopifyQL Generation
            print("⚙️  Step 3: Generating ShopifyQL...")
            query_spec = await self.shopifyql_generator.generate(plan, intent_result)
            self._add_reasoning(f"Generated query plan")
            
            # Step 4: Query Execution
            print("🔍 Step 4: Executing queries...")
            raw_data = await self.query_executor.execute(
                query_spec=query_spec,
                store_id=store_id,
                access_token=request.get("access_token"),
                use_mock=use_mock
            )
            self._add_reasoning(
                f"Retrieved {raw_data.get('record_count', 0)} data points"
            )
            
            # Step 5: Result Processing
            print("📊 Step 5: Processing results...")
            processed = await self.result_processor.process(
                raw_data=raw_data,
                intent=intent_result,
                plan=plan
            )
            self._add_reasoning(f"Calculated metrics and insights")
            
            # Step 6: Natural Language Explanation
            print("💬 Step 6: Generating explanation...")
            explanation = await self.explainer.explain(
                question=question,
                intent=intent_result,
                data_summary=processed["summary"],
                calculations=processed["calculations"]
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Build final response
            return {
                "answer": explanation["answer"],
                "confidence": explanation["confidence"],
                "shopify_query": query_spec.get("shopifyql", "N/A"),
                "reasoning": self.reasoning_steps,
                "metadata": {
                    "execution_time": f"{execution_time:.2f}s",
                    "data_points_analyzed": raw_data.get("record_count", 0),
                    "intent": intent_result["intent"],
                    "confidence_reason": explanation.get("confidence_reason", "")
                }
            }
            
        except Exception as e:
            print(f"❌ Agent orchestration error: {str(e)}")
            # Return graceful error
            return {
                "answer": (
                    f"I encountered an issue processing your question: {str(e)}. "
                    "Please try rephrasing your question or contact support."
                ),
                "confidence": "low",
                "shopify_query": None,
                "reasoning": self.reasoning_steps + [f"Error: {str(e)}"],
                "metadata": {
                    "error": str(e),
                    "execution_time": "N/A"
                }
            }

    def _add_reasoning(self, step: str):
        """Add a reasoning step to the trail"""
        self.reasoning_steps.append(step)
        
    def _handle_ambiguous_question(
        self, 
        question: str, 
        intent_result: Dict
    ) -> Dict[str, Any]:
        """Handle questions that are too ambiguous to process"""
        clarifications = []
        
        if not intent_result.get("time_period"):
            clarifications.append("- What time period are you interested in?")
        if not intent_result.get("products"):
            clarifications.append("- Which products should I analyze?")
            
        clarification_text = "\n".join(clarifications) if clarifications else \
            "the specific metrics or products you're interested in"
        
        return {
            "answer": (
                f"I'd like to help, but I need a bit more information. "
                f"Could you clarify:\n{clarification_text}\n\n"
                f"For example: 'What were the top 5 selling products last month?'"
            ),
            "confidence": "low",
            "shopify_query": None,
            "reasoning": ["Question too ambiguous for confident analysis"],
            "metadata": {
                "requires_clarification": True
            }
        }
