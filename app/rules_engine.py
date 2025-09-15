# CSV Rules Engine Integration - Dynamic Rule Loading
# This module loads your CSV files and creates intelligent routing logic

import pandas as pd
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

@dataclass
class EligibilityResult:
    service: str
    qualified: bool
    confidence: float
    reasoning: str
    next_questions: List[str]
    fallback_options: List[str]

class DynamicRulesEngine:
    """
    Loads CSV rules and creates intelligent routing logic.
    Minimizes hard-coding by using LLM to interpret criteria.
    """
    
    def __init__(self, csv_paths: Dict[str, str]):
        self.csv_paths = csv_paths
        self.initial_use_cases = None
        self.questions_db = None
        self.rpm_specific = None
        self.load_all_rules()
    
    def load_all_rules(self):
        """Load all CSV files into memory for fast access."""
        try:
            self.initial_use_cases = pd.read_csv(self.csv_paths['initial_use_cases'])
            self.questions_db = pd.read_csv(self.csv_paths['questions'])  
            self.rpm_specific = pd.read_csv(self.csv_paths['rpm_specific'])
            print("✅ All CSV rules loaded successfully")
        except Exception as e:
            print(f"❌ Error loading CSV files: {e}")
    
    def get_service_rules(self, service_name: str) -> List[Dict]:
        """Get all rules for a specific service."""
        if self.initial_use_cases is None:
            return []
        
        service_rules = self.initial_use_cases[
            self.initial_use_cases['Program'].str.contains(service_name, case=False, na=False)
        ]
        
        return service_rules.to_dict('records')
    
    def generate_assessment_questions(self) -> List[Dict]:
        """Generate questions to ask patients based on CSV question database."""
        if self.questions_db is None:
            return []
        
        questions = []
        for _, row in self.questions_db.iterrows():
            question_text = row.iloc[0]  # First column has questions
            data_type = row.get('Data Type', 'text')
            
            if pd.notna(question_text) and question_text.strip():
                questions.append({
                    'question': question_text.strip(),
                    'data_type': data_type,
                    'inclusion_criteria': row.get('Inclusion Criteria', ''),
                    'exclusion_criteria': row.get('Exclusion Criteria', ''),
                    'marketplace_route': row.get('Marketplace Route', ''),
                    'fallback': row.get('Fallback', row.get('Fallback ', ''))
                })
        
        return questions
    
    def evaluate_patient_against_rules(self, patient_responses: Dict, service: str) -> EligibilityResult:
        """
        Evaluate if patient qualifies for a service using CSV rules.
        Returns structured eligibility result.
        """
        service_rules = self.get_service_rules(service)
        
        if not service_rules:
            return EligibilityResult(
                service=service,
                qualified=False,
                confidence=0.0,
                reasoning=f"No rules found for service: {service}",
                next_questions=[],
                fallback_options=[]
            )
        
        total_confidence = 0.0
        qualifying_rules = []
        all_fallbacks = set()
        
        for rule in service_rules:
            inclusion = rule.get('Inclusion Criteria', '')
            exclusion = rule.get('Exclusion Criteria', '')
            
            # Calculate rule match confidence
            rule_confidence = self._evaluate_rule_match(
                patient_responses, inclusion, exclusion
            )
            
            if rule_confidence > 0.3:  # Threshold for qualification
                qualifying_rules.append(rule)
                total_confidence += rule_confidence
                
                fallback = rule.get('Fallback', '')
                if fallback:
                    all_fallbacks.add(fallback)
        
        # Average confidence across qualifying rules
        avg_confidence = total_confidence / len(service_rules) if service_rules else 0.0
        
        qualified = avg_confidence >= 0.5
        
        reasoning = self._generate_reasoning(qualifying_rules, patient_responses)
        next_questions = self._suggest_clarifying_questions(service_rules, patient_responses)
        
        return EligibilityResult(
            service=service,
            qualified=qualified,
            confidence=avg_confidence,
            reasoning=reasoning,
            next_questions=next_questions,
            fallback_options=list(all_fallbacks)
        )
    
    def _evaluate_rule_match(self, patient_responses: Dict, inclusion: str, exclusion: str) -> float:
        """
        Evaluate how well patient responses match inclusion/exclusion criteria.
        Returns confidence score 0.0-1.0.
        """
        confidence = 0.0
        
        # Parse inclusion criteria
        if inclusion and self._matches_criteria(patient_responses, inclusion, positive=True):
            confidence += 0.6
        
        # Parse exclusion criteria  
        if exclusion and self._matches_criteria(patient_responses, exclusion, positive=False):
            confidence -= 0.4
        
        # Ensure confidence stays in bounds
        return max(0.0, min(1.0, confidence))
    
    def _matches_criteria(self, responses: Dict, criteria: str, positive: bool = True) -> bool:
        """
        Check if patient responses match specific criteria.
        Uses keyword matching and pattern recognition.
        """
        if not criteria or not responses:
            return False
        
        # Handle case where criteria might be NaN or float
        if not isinstance(criteria, str):
            return False
            
        criteria_lower = criteria.lower()
        
        # Check for common health conditions
        health_conditions = [
            'diabetes', 'hypertension', 'copd', 'asthma', 'heart failure', 
            'kidney disease', 'ckd', 'chronic condition'
        ]
        
        for condition in health_conditions:
            if condition in criteria_lower:
                has_condition = any(
                    condition in str(response).lower() 
                    for response in responses.values()
                )
                if has_condition == positive:
                    return True
        
        # Check for age criteria
        age_match = re.search(r'age.*?(\d+)', criteria_lower)
        if age_match:
            criteria_age = int(age_match.group(1))
            patient_age = responses.get('age', 0)
            
            if 'older' in criteria_lower or '≥' in criteria or '>=' in criteria:
                return (patient_age >= criteria_age) == positive
            elif 'younger' in criteria_lower or '<' in criteria:
                return (patient_age < criteria_age) == positive
        
        # Check for recent hospitalization
        if 'hospital' in criteria_lower or 'admission' in criteria_lower:
            recent_hospital = responses.get('recent_hospitalization', False)
            return recent_hospital == positive
        
        # Check for insurance status
        if 'insurance' in criteria_lower or 'medicare' in criteria_lower:
            has_insurance = responses.get('has_insurance', False)
            return has_insurance == positive
        
        return False
    
    def _generate_reasoning(self, qualifying_rules: List[Dict], responses: Dict) -> str:
        """Generate human-readable reasoning for eligibility decision."""
        if not qualifying_rules:
            return "Patient does not meet eligibility criteria for this service."
        
        reasoning_parts = []
        for rule in qualifying_rules:
            inclusion = rule.get('Inclusion Criteria', '')
            if inclusion:
                reasoning_parts.append(f"✅ Meets criteria: {inclusion}")
        
        return " | ".join(reasoning_parts)
    
    def _suggest_clarifying_questions(self, rules: List[Dict], responses: Dict) -> List[str]:
        """Suggest questions to better assess eligibility."""
        suggested = []
        
        # If no age provided, ask for it
        if 'age' not in responses:
            suggested.append("What is your age?")
        
        # If chronic conditions unclear, ask specifically
        if 'chronic_conditions' not in responses:
            suggested.append("Do you have any chronic health conditions like diabetes, high blood pressure, or heart disease?")
        
        # If hospitalization history unclear
        if 'recent_hospitalization' not in responses:
            suggested.append("Have you been hospitalized in the past 6 months?")
        
        # If insurance status unclear
        if 'has_insurance' not in responses:
            suggested.append("Do you currently have health insurance?")
        
        return suggested[:2]  # Limit to 2 questions to avoid overwhelming

# Tool functions for the ADK agents
def load_dynamic_rules() -> str:
    """Tool to load CSV rules and return summary."""
    from config import CSV_PATHS
    csv_paths = CSV_PATHS
    
    rules_engine = DynamicRulesEngine(csv_paths)
    
    # Get service counts
    service_counts = {}
    if rules_engine.initial_use_cases is not None:
        service_counts = rules_engine.initial_use_cases['Program'].value_counts().to_dict()
    
    questions_count = len(rules_engine.generate_assessment_questions())
    
    summary = f"""
    📋 Dynamic Rules Engine Loaded:
    
    Services Available:
    {json.dumps(service_counts, indent=2)}
    
    Total Assessment Questions: {questions_count}
    
    Ready to process patient routing decisions!
    """
    
    return summary

def assess_eligibility_dynamically(patient_data: str) -> str:
    """Tool to assess patient eligibility using CSV rules."""
    try:
        # Parse patient data (expecting JSON string)
        patient_responses = json.loads(patient_data)
    except:
        return "❌ Error: Patient data must be in JSON format"
    
    from config import CSV_PATHS
    csv_paths = CSV_PATHS
    
    rules_engine = DynamicRulesEngine(csv_paths)
    
    # Evaluate each service
    services = ["Remote Patient Monitoring", "Telehealth", "Insurance"]
    results = []
    
    for service in services:
        result = rules_engine.evaluate_patient_against_rules(patient_responses, service)
        
        status = "✅ QUALIFIED" if result.qualified else "❌ NOT QUALIFIED"
        confidence_pct = f"{result.confidence:.0%}"
        
        results.append(f"""
        🏥 {service}:
        Status: {status} (Confidence: {confidence_pct})
        Reasoning: {result.reasoning}
        Fallback Options: {', '.join(result.fallback_options) if result.fallback_options else 'None'}
        """)
    
    return "\n".join(results)

def get_next_assessment_questions(current_responses: str) -> str:
    """Tool to get the next questions to ask based on current responses."""
    from config import CSV_PATHS
    csv_paths = CSV_PATHS
    
    rules_engine = DynamicRulesEngine(csv_paths)
    assessment_questions = rules_engine.generate_assessment_questions()
    
    # Return first 3 most relevant questions
    priority_questions = [
        q['question'] for q in assessment_questions[:3] 
        if q['question']
    ]
    
    return "Next questions to ask:\n" + "\n".join(f"• {q}" for q in priority_questions)

# Example usage
if __name__ == "__main__":
    # Test the rules engine
    print(load_dynamic_rules())
    
    # Test patient assessment
    sample_patient = {
        "age": 67,
        "chronic_conditions": "diabetes, hypertension", 
        "recent_hospitalization": True,
        "has_insurance": True,
        "tech_comfortable": True
    }
    
    print(assess_eligibility_dynamically(json.dumps(sample_patient)))