"""
Intent Classifier - Step 1 of agent workflow
Classifies user questions into analytics categories
"""

import json
from typing import Dict, Any
from app.llm.client import LLMClient
from app.llm.prompts import INTENT_CLASSIFIER_SYSTEM, INTENT_CLASSIFIER_PROMPT


class IntentClassifier:
    """
    Classifies natural language questions into analytical intents
    
    Categories:
    - inventory_projection
    - inventory_status
    - sales_analysis
    - top_products
    - customer_behavior
    - customer_retention
    - reorder_recommendations
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def classify(self, question: str) -> Dict[str, Any]:
        """
        Classify the user's question and extract parameters
        
        Returns:
            {
                "intent": str,
                "time_period": str,
                "products": str,
                "metrics": List[str],
                "confidence": "low|medium|high"
            }
        """
        prompt = INTENT_CLASSIFIER_PROMPT.format(question=question)
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=INTENT_CLASSIFIER_SYSTEM,
                temperature=0.1  # Very low temperature for consistent classification
            )
            
            # Parse JSON response
            result = self._parse_json_response(response)
            
            # Validate and return
            return self._validate_intent(result)
            
        except Exception as e:
            print(f"Intent classification error: {e}")
            # Return a reasonable default based on question keywords instead of always "low"
            question_lower = question.lower()
            
            # Simple keyword-based fallback
            if any(word in question_lower for word in ['top', 'best', 'selling', 'popular']):
                intent = "top_products"
                confidence = "medium"
            elif any(word in question_lower for word in ['reorder', 'need', 'inventory', 'stock']):
                intent = "inventory_projection"
                confidence = "medium"
            elif any(word in question_lower for word in ['customer', 'repeat', 'loyal']):
                intent = "customer_behavior"
                confidence = "medium"
            else:
                intent = "general_query"
                confidence = "low"
            
            return {
                "intent": intent,
                "time_period": "recent",
                "products": "all",
                "metrics": ["general"],
                "confidence": confidence
            }

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response, handling markdown code blocks"""
        try:
            # Remove markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response was: {response}")
            raise ValueError("Failed to parse LLM response as JSON")

    def _validate_intent(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate intent classification result"""
        valid_intents = [
            "inventory_projection",
            "inventory_status",
            "sales_analysis",
            "top_products",
            "customer_behavior",
            "customer_retention",
            "reorder_recommendations",
            "general_query"
        ]
        
        # Ensure intent is valid
        if result.get("intent") not in valid_intents:
            result["intent"] = "general_query"
            result["confidence"] = "low"
        
        # Ensure required fields exist
        result.setdefault("time_period", "recent")
        result.setdefault("products", "all")
        result.setdefault("metrics", ["general"])
        result.setdefault("confidence", "medium")
        
        return result
