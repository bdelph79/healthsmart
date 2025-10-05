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
    
    def assess_service_specific_eligibility(self, service_type: str, context: Dict) -> EligibilityResult:
        """Assess eligibility for specific service using CSV rules."""
        # Normalize service type
        service_mapping = {
            'rpm': 'Remote Patient Monitoring',
            'remote patient monitoring': 'Remote Patient Monitoring',
            'telehealth': 'Telehealth',
            'virtual primary care': 'Telehealth',
            'insurance': 'Insurance',
            'insurance enrollment': 'Insurance'
        }
        
        normalized_service = service_mapping.get(service_type.lower(), service_type)
        
        return self.evaluate_patient_against_rules(context, normalized_service)
    
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
            patient_age = self._get_patient_age(responses)
            
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
    
    def _get_patient_age(self, responses: Dict) -> int:
        """Get patient age from various possible fields."""
        # Try direct age field first
        if 'age' in responses and responses['age'] is not None and responses['age'] != '':
            try:
                return int(responses['age'])
            except (ValueError, TypeError):
                pass
        
        # Try birth year fields
        birth_year_fields = ['birth_year', 'year_of_birth', 'birthyear']
        for field in birth_year_fields:
            if field in responses and responses[field] is not None and responses[field] != '':
                try:
                    birth_year = int(responses[field])
                    current_year = 2024  # Could be made configurable
                    age = current_year - birth_year
                    if 0 <= age <= 150:  # Reasonable age range
                        return age
                except (ValueError, TypeError):
                    continue
        
        return 0  # Default if no valid age found
    
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
        if not self._has_age_info(responses):
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
        
        return suggested[:1]  # Limit to 1 question to avoid overwhelming
    
    def _has_age_info(self, context: Dict) -> bool:
        """Check if age information is available in any form."""
        # Check for direct age field
        if 'age' in context and context['age'] is not None and context['age'] != '':
            return True
        
        # Check for birth year fields
        birth_year_fields = ['birth_year', 'year_of_birth', 'birthyear']
        for field in birth_year_fields:
            if field in context and context[field] is not None and context[field] != '':
                return True
        
        return False
    
    def identify_missing_critical_data(self, context: Dict) -> List[str]:
        """Identify what critical data is missing from patient context."""
        missing = []
        
        # Critical data points for all services
        critical_fields = {
            'age': 'age',
            'chronic_conditions': 'chronic health conditions',
            'recent_hospitalization': 'recent hospitalization history',
            'has_insurance': 'insurance status',
            'tech_comfortable': 'technology comfort level',
            'state': 'state of residence',
            'household_income': 'household income'
        }
        
        # Check if age is provided (including birth year)
        has_age = self._has_age_info(context)
        
        for field, description in critical_fields.items():
            if field == 'age':
                if not has_age:
                    missing.append(description)
            elif field not in context or context[field] is None or context[field] == '':
                missing.append(description)
        
        return missing
    
    def get_next_assessment_questions(self, context: Dict, service_type: str = None) -> List[str]:
        """Generate next questions based on current context and missing data."""
        # Get all available questions
        all_questions = self.generate_assessment_questions()
        
        # Identify missing critical data
        missing_data = self.identify_missing_critical_data(context)
        
        # Filter questions based on missing information and service type
        relevant_questions = []
        
        for question in all_questions:
            question_text = question['question'].lower()
            
            # Check if question addresses missing data
            is_relevant = False
            for missing in missing_data:
                if isinstance(missing, str) and any(keyword in question_text for keyword in missing.split()):
                    is_relevant = True
                    break
            
            # Service-specific relevance
            if service_type:
                service_keywords = {
                    'rpm': ['chronic', 'diabetes', 'hypertension', 'copd', 'heart', 'device', 'monitor'],
                    'telehealth': ['state', 'device', 'video', 'virtual', 'appointment'],
                    'insurance': ['income', 'ssn', 'enrollment', 'medicare', 'marketplace']
                }
                
                if service_type.lower() in service_keywords:
                    if any(keyword in question_text for keyword in service_keywords[service_type.lower()]):
                        is_relevant = True
            
            if is_relevant:
                relevant_questions.append(question['question'])
        
        # If no specific missing data, return general priority questions
        if not relevant_questions:
            priority_questions = [
                "What is your age?",
                "Do you have any chronic health conditions?",
                "Do you currently have health insurance?"
            ]
            return priority_questions[:1]
        
        return relevant_questions[:1]  # Limit to 1 question
    
    def filter_questions_by_priority(self, questions: List[Dict], missing_data: List[str]) -> List[str]:
        """Filter questions by priority based on missing critical data."""
        priority_questions = []
        
        # High priority questions for critical missing data
        high_priority_keywords = ['age', 'chronic', 'insurance', 'hospital']
        
        for question in questions:
            question_text = question['question'].lower()
            
            # Check if question addresses high priority missing data
            if any(keyword in question_text for keyword in high_priority_keywords):
                if any(isinstance(missing, str) and missing in question_text for missing in missing_data):
                    priority_questions.append(question['question'])
        
        # If we have high priority questions, return them
        if priority_questions:
            return priority_questions[:1]
        
        # Otherwise return general questions
        return [q['question'] for q in questions[:1]]

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

def get_next_assessment_questions(current_responses: str, service_type: str = None) -> str:
    """Tool to get the next questions to ask based on current responses and service type."""
    from config import CSV_PATHS
    csv_paths = CSV_PATHS
    
    rules_engine = DynamicRulesEngine(csv_paths)
    
    # Parse current responses
    try:
        responses = json.loads(current_responses) if current_responses else {}
    except:
        responses = {}
    
    # Get next questions based on missing data and service type
    next_questions = rules_engine.get_next_assessment_questions(responses, service_type)
    
    if not next_questions:
        return "✅ All necessary information has been collected. Let me assess your eligibility..."
    
    return "Next questions to ask:\n" + "\n".join(f"• {q}" for q in next_questions)

def assess_service_specific_eligibility(service_type: str, patient_responses: str) -> str:
    """Tool to assess eligibility for a specific service using CSV rules."""
    from config import CSV_PATHS
    csv_paths = CSV_PATHS
    
    rules_engine = DynamicRulesEngine(csv_paths)
    
    # Parse patient responses
    try:
        responses = json.loads(patient_responses) if patient_responses else {}
    except:
        return "❌ Error: Patient responses must be in JSON format"
    
    # Assess eligibility for specific service
    result = rules_engine.assess_service_specific_eligibility(service_type, responses)
    
    status = "✅ QUALIFIED" if result.qualified else "❌ NOT QUALIFIED"
    confidence_pct = f"{result.confidence:.0%}"
    
    response = f"""
    🏥 {result.service} Assessment:
    Status: {status} (Confidence: {confidence_pct})
    Reasoning: {result.reasoning}
    """
    
    if result.fallback_options:
        response += f"Fallback Options: {', '.join(result.fallback_options)}\n"
    
    if result.next_questions:
        response += f"Next Questions: {'; '.join(result.next_questions)}"
    
    return response

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

