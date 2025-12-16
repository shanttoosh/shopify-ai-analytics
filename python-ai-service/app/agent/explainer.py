"""
Explainer - Step 6 of agent workflow
Converts technical data into business-friendly natural language
"""

import json
from typing import Dict, Any
from app.llm.client import LLMClient
from app.llm.prompts import EXPLAINER_SYSTEM, EXPLAINER_PROMPT


class Explainer:
    """
    Generates natural language explanations from analytical results
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def explain(
        self,
        question: str,
        intent: Dict[str, Any],
        data_summary: Dict[str, Any],
        calculations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a business-friendly explanation
        
        Returns:
            {
                "answer": str,
                "insights": List[str],
                "confidence": "low|medium|high",
                "confidence_reason": str
            }
        """
        
        # Format data for the prompt
        data_summary_str = json.dumps(data_summary, indent=2)
        calculations_str = json.dumps(calculations, indent=2)
        
        prompt = EXPLAINER_PROMPT.format(
            question=question,
            intent=intent.get("intent", ""),
            data_summary=data_summary_str,
            calculations=calculations_str
        )
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=EXPLAINER_SYSTEM,
                temperature=0.7  # Higher temperature for more natural language
            )
            
            # Parse JSON response
            result = self._parse_json_response(response)
            
            # Validate
            result.setdefault("answer", "Unable to generate explanation")
            result.setdefault("insights", [])
            result.setdefault("confidence", "medium")
            result.setdefault("confidence_reason", "Standard analysis")
            
            return result
            
        except Exception as e:
            print(f"Explanation generation error: {e}")
            # Fallback to template-based explanation
            return self._fallback_explanation(intent, data_summary, calculations)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse explanation as JSON")

    def _fallback_explanation(
        self,
        intent: Dict[str, Any],
        data_summary: Dict[str, Any],
        calculations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate template-based explanation as fallback"""
        
        intent_type = intent.get("intent", "")
        
        # Template-based explanations
        if intent_type == "inventory_projection":
            daily_rate = data_summary.get("daily_sales_rate", 0)
            projected_need = calculations.get("projected_units_needed", 0)
            shortage = calculations.get("shortage", 0)
            
            if shortage > 0:
                answer = (
                    f"Based on your recent sales data, you sell approximately "
                    f"{daily_rate} units per day. To meet demand for the upcoming period, "
                    f"you'll need about {projected_need} units. You should reorder "
                    f"at least {shortage} units to avoid stockouts."
                )
            else:
                answer = (
                    f"Based on your sales rate of {daily_rate} units per day, "
                    f"your current inventory should be sufficient for the upcoming period."
                )
            
            confidence = "medium"
            
        elif intent_type in ["sales_analysis", "top_products"]:
            total_orders = data_summary.get("total_orders", 0)
            total_revenue = data_summary.get("total_revenue", 0)
            top_products = data_summary.get("top_products", [])
            
            if top_products:
                top_names = ", ".join([p["product"] for p in top_products[:3]])
                answer = (
                    f"Based on {total_orders} orders totaling ${total_revenue}, "
                    f"your top selling products are: {top_names}."
                )
            else:
                answer = f"Analyzed {total_orders} orders totaling ${total_revenue}."
            
            confidence = "high" if total_orders > 10 else "medium"
            
        elif intent_type == "customer_behavior":
            repeat_customers = data_summary.get("repeat_customers", 0)
            repeat_rate = data_summary.get("repeat_rate", 0)
            
            answer = (
                f"You have {repeat_customers} repeat customers, representing "
                f"{repeat_rate}% of your customer base."
            )
            confidence = "medium"
            
        else:
            answer = "I've analyzed your data and found the requested information."
            confidence = "low"
        
        return {
            "answer": answer,
            "insights": [],
            "confidence": confidence,
            "confidence_reason": "Template-based explanation used as fallback"
        }
