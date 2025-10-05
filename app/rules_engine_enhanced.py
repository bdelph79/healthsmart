# JSON Rules Engine Integration - Enhanced Version
# This module loads your JSON rule files and creates intelligent routing logic

import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class EligibilityResult:
    service: str
    qualified: bool
    confidence: float
    reasoning: str
    next_questions: List[str]
    fallback_options: List[str]
    missing_criteria: List[str] = None
    decision_trail: List[Dict[str, Any]] = None

class JSONRulesEngine:
    """
    Enhanced rules engine that loads JSON rule files instead of CSV.
    Provides more sophisticated rule evaluation and question generation.
    """
    
    def __init__(self, rules_dir: str = "rules"):
        self.rules_dir = Path(rules_dir)
        self.rules = {}
        self.assessment_questions = {}
        self.load_all_rules()
    
    def load_all_rules(self):
        """Load all JSON rule files into memory for fast access."""
        try:
            # Load specific rule files
            rule_files = {
                "rpm": "rpm_eligibility.json",
                "telehealth": "telehealth_eligibility.json", 
                "insurance": "insurance_enrollment.json",
                "emergency": "emergency_screening.json",
                "pharmacy": "pharmacy_savings.json",
                "wellness": "wellness_programs.json",
                "assessment": "assessment_questions.json"
            }
            
            for service, filename in rule_files.items():
                file_path = self.rules_dir / filename
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        rule_data = json.load(f)
                        self.rules[service] = rule_data
                        print(f"✅ Loaded {service} rules from {filename}")
                else:
                    print(f"⚠️ Warning: {filename} not found, using fallback logic")
            
            # Load assessment questions if available
            if "assessment" in self.rules:
                self.assessment_questions = self.rules["assessment"]
                
            print("✅ All JSON rules loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading JSON rule files: {e}")
            # Fallback to basic rules if JSON files not available
            self._load_fallback_rules()
    
    def _load_fallback_rules(self):
        """Fallback rules if JSON files are not available."""
        self.rules = {
            "rpm": {
                "requirements": {
                    "chronic_conditions": {"required": True, "question": "Do you have any chronic health conditions?"},
                    "insurance_coverage": {"required": True, "question": "Do you have health insurance?"},
                    "device_access": {"required": True, "question": "Do you have a smartphone or tablet?"},
                    "consent_monitoring": {"required": True, "question": "Are you comfortable sharing health data?"}
                },
                "fallback_options": ["Wellness education", "Preventive care", "Pharmacy savings"]
            }
        }
    
    def evaluate_patient_against_rules(self, patient_responses: Dict, service: str) -> EligibilityResult:
        """
        Enhanced evaluation using JSON rules instead of CSV.
        """
        # Normalize service name
        service_key = self._normalize_service_name(service)
        
        if service_key not in self.rules:
            return EligibilityResult(
                service=service,
                qualified=False,
                confidence=0.0,
                reasoning=f"No rules found for service: {service}",
                next_questions=[],
                fallback_options=[],
                missing_criteria=["service_definition"]
            )
        
        rule = self.rules[service_key]
        
        # Special handling for each service type
        if service_key == "rpm":
            return self._evaluate_rpm_eligibility_json(patient_responses, rule)
        elif service_key == "telehealth":
            return self._evaluate_telehealth_eligibility_json(patient_responses, rule)
        elif service_key == "insurance":
            return self._evaluate_insurance_eligibility_json(patient_responses, rule)
        elif service_key == "emergency":
            return self._evaluate_emergency_screening_json(patient_responses, rule)
        else:
            return self._evaluate_generic_eligibility_json(patient_responses, service, rule)
    
    def _normalize_service_name(self, service: str) -> str:
        """Normalize service names to match JSON file keys."""
        service_lower = service.lower()
        if "remote patient monitoring" in service_lower or "rpm" in service_lower:
            return "rpm"
        elif "telehealth" in service_lower or "virtual" in service_lower:
            return "telehealth"
        elif "insurance" in service_lower:
            return "insurance"
        elif "emergency" in service_lower:
            return "emergency"
        elif "pharmacy" in service_lower:
            return "pharmacy"
        elif "wellness" in service_lower:
            return "wellness"
        else:
            return "rpm"  # Default fallback
    
    def _evaluate_rpm_eligibility_json(self, patient_responses: Dict, rule: Dict) -> EligibilityResult:
        """Enhanced RPM eligibility evaluation using JSON rules."""
        
        requirements = rule.get("requirements", {})
        decision_trail = []
        missing_criteria = []
        met_requirements = []
        
        # Check each requirement
        for req_name, req_config in requirements.items():
            if req_config.get("required", False):
                is_met = self._check_requirement(patient_responses, req_name, req_config, decision_trail)
                
                if is_met:
                    met_requirements.append(req_name)
                else:
                    missing_criteria.append(req_name)
        
        # Check exclusion criteria if present
        exclusions = rule.get("exclusion_criteria", {})
        excluded = self._check_exclusions(patient_responses, exclusions, decision_trail)
        
        # Calculate qualification
        total_requirements = len([r for r in requirements.values() if r.get("required", False)])
        met_count = len(met_requirements)
        
        qualified = (met_count == total_requirements) and not excluded
        confidence = met_count / total_requirements if total_requirements > 0 else 0.0
        
        # Generate reasoning
        if excluded:
            reasoning = "❌ Excluded due to emergency symptoms or other exclusion criteria"
        elif missing_criteria:
            reasoning = f"Missing {len(missing_criteria)} required criteria: {', '.join(missing_criteria)}"
        else:
            reasoning = f"✅ Meets all {total_requirements} requirements for RPM"
        
        # Get next questions
        next_questions = self._generate_next_questions_json(patient_responses, requirements, missing_criteria)
        
        # Get fallback options
        fallback_options = rule.get("fallback_options", [])
        
        return EligibilityResult(
            service="Remote Patient Monitoring (RPM)",
            qualified=qualified,
            confidence=confidence,
            reasoning=reasoning,
            next_questions=next_questions,
            fallback_options=fallback_options,
            missing_criteria=missing_criteria,
            decision_trail=decision_trail
        )
    
    def _evaluate_telehealth_eligibility_json(self, patient_responses: Dict, rule: Dict) -> EligibilityResult:
        """Telehealth eligibility evaluation using JSON rules."""
        
        requirements = rule.get("requirements", {})
        exclusions = rule.get("exclusion_criteria", {})
        
        decision_trail = []
        missing_criteria = []
        met_requirements = []
        
        # Check requirements
        for req_name, req_config in requirements.items():
            if req_config.get("required", False):
                is_met = self._check_requirement(patient_responses, req_name, req_config, decision_trail)
                
                if is_met:
                    met_requirements.append(req_name)
                else:
                    missing_criteria.append(req_name)
        
        # Check exclusions
        excluded = self._check_exclusions(patient_responses, exclusions, decision_trail)
        
        # Calculate results
        total_requirements = len([r for r in requirements.values() if r.get("required", False)])
        met_count = len(met_requirements)
        
        qualified = (met_count >= total_requirements) and not excluded
        confidence = met_count / total_requirements if total_requirements > 0 else 1.0
        
        reasoning = self._generate_reasoning(met_requirements, missing_criteria, excluded, "Telehealth")
        next_questions = self._generate_next_questions_json(patient_responses, requirements, missing_criteria)
        fallback_options = rule.get("fallback_options", [])
        
        return EligibilityResult(
            service="Telehealth / Virtual Primary Care",
            qualified=qualified,
            confidence=confidence,
            reasoning=reasoning,
            next_questions=next_questions,
            fallback_options=fallback_options,
            missing_criteria=missing_criteria,
            decision_trail=decision_trail
        )
    
    def _evaluate_insurance_eligibility_json(self, patient_responses: Dict, rule: Dict) -> EligibilityResult:
        """Insurance enrollment eligibility evaluation using JSON rules."""
        
        requirements = rule.get("requirements", {})
        enrollment_periods = rule.get("enrollment_periods", {})
        
        decision_trail = []
        missing_criteria = []
        met_requirements = []
        
        # Check basic requirements
        for req_name, req_config in requirements.items():
            if req_config.get("required", False):
                is_met = self._check_requirement(patient_responses, req_name, req_config, decision_trail)
                
                if is_met:
                    met_requirements.append(req_name)
                else:
                    missing_criteria.append(req_name)
        
        # Check enrollment period eligibility
        enrollment_eligible = self._check_enrollment_period(patient_responses, enrollment_periods, decision_trail)
        
        # Calculate results
        total_requirements = len([r for r in requirements.values() if r.get("required", False)])
        met_count = len(met_requirements)
        
        # Need both requirements AND enrollment period
        qualified = (met_count >= total_requirements) and enrollment_eligible
        confidence = (met_count / total_requirements * 0.7 + (0.3 if enrollment_eligible else 0)) if total_requirements > 0 else 0.0
        
        reasoning = self._generate_insurance_reasoning(met_requirements, missing_criteria, enrollment_eligible)
        next_questions = self._generate_next_questions_json(patient_responses, requirements, missing_criteria)
        fallback_options = rule.get("fallback_options", [])
        
        return EligibilityResult(
            service="Insurance Enrollment",
            qualified=qualified,
            confidence=confidence,
            reasoning=reasoning,
            next_questions=next_questions,
            fallback_options=fallback_options,
            missing_criteria=missing_criteria,
            decision_trail=decision_trail
        )
    
    def _evaluate_emergency_screening_json(self, patient_responses: Dict, rule: Dict) -> EligibilityResult:
        """Emergency screening using JSON rules."""
        
        critical_symptoms = rule.get("critical_emergency_symptoms", {})
        urgent_symptoms = rule.get("urgent_but_not_emergency", {})
        
        decision_trail = []
        
        # Check for critical emergency symptoms
        emergency_found = False
        emergency_action = None
        
        for category, symptom_data in critical_symptoms.items():
            symptoms = symptom_data.get("symptoms", [])
            if self._check_symptoms_present(patient_responses, symptoms):
                emergency_found = True
                emergency_action = symptom_data.get("action")
                decision_trail.append({
                    "category": category,
                    "action": emergency_action,
                    "message": symptom_data.get("message")
                })
                break
        
        if emergency_found:
            return EligibilityResult(
                service="Emergency Screening",
                qualified=True,  # Qualified for emergency intervention
                confidence=1.0,
                reasoning="🚨 Emergency symptoms detected - immediate medical attention required",
                next_questions=[],
                fallback_options=[],
                missing_criteria=[],
                decision_trail=decision_trail
            )
        
        # Check for urgent but non-emergency symptoms
        urgent_found = False
        for category, symptom_data in urgent_symptoms.items():
            symptoms = symptom_data.get("symptoms", [])
            if self._check_symptoms_present(patient_responses, symptoms):
                urgent_found = True
                decision_trail.append({
                    "category": category,
                    "action": symptom_data.get("action"),
                    "timeframe": symptom_data.get("timeframe")
                })
                break
        
        if urgent_found:
            return EligibilityResult(
                service="Emergency Screening",
                qualified=True,  # Qualified for urgent care
                confidence=0.8,
                reasoning="⚠️ Urgent symptoms detected - seek medical care within hours",
                next_questions=[],
                fallback_options=["Urgent care", "Telehealth consultation"],
                missing_criteria=[],
                decision_trail=decision_trail
            )
        
        # No emergency or urgent symptoms
        return EligibilityResult(
            service="Emergency Screening",
            qualified=False,  # No emergency care needed
            confidence=0.9,
            reasoning="✅ No emergency symptoms detected - routine care appropriate",
            next_questions=["What specific health concerns would you like help with?"],
            fallback_options=["Telehealth", "Primary care appointment", "Wellness programs"],
            missing_criteria=[],
            decision_trail=decision_trail
        )
    
    def _evaluate_generic_eligibility_json(self, patient_responses: Dict, service: str, rule: Dict) -> EligibilityResult:
        """Generic eligibility evaluation for any service using JSON rules."""
        
        requirements = rule.get("requirements", {})
        decision_trail = []
        missing_criteria = []
        met_requirements = []
        
        for req_name, req_config in requirements.items():
            if req_config.get("required", False):
                is_met = self._check_requirement(patient_responses, req_name, req_config, decision_trail)
                
                if is_met:
                    met_requirements.append(req_name)
                else:
                    missing_criteria.append(req_name)
        
        total_requirements = len([r for r in requirements.values() if r.get("required", False)])
        met_count = len(met_requirements)
        
        qualified = met_count >= total_requirements
        confidence = met_count / total_requirements if total_requirements > 0 else 1.0
        
        reasoning = self._generate_reasoning(met_requirements, missing_criteria, False, service)
        next_questions = self._generate_next_questions_json(patient_responses, requirements, missing_criteria)
        fallback_options = rule.get("fallback_options", [])
        
        return EligibilityResult(
            service=service,
            qualified=qualified,
            confidence=confidence,
            reasoning=reasoning,
            next_questions=next_questions,
            fallback_options=fallback_options,
            missing_criteria=missing_criteria,
            decision_trail=decision_trail
        )
    
    def _check_requirement(self, patient_responses: Dict, req_name: str, req_config: Dict, decision_trail: List) -> bool:
        """Check if a specific requirement is met."""
        
        patient_value = patient_responses.get(req_name)
        req_type = req_config.get("type", "boolean")
        
        decision_entry = {
            "requirement": req_name,
            "expected_type": req_type,
            "patient_value": patient_value,
            "met": False
        }
        
        if req_type == "boolean":
            is_met = bool(patient_value)
        elif req_type == "contains_any":
            values = req_config.get("values", [])
            is_met = patient_value and any(
                val.lower() in str(patient_value).lower() 
                for val in values
            )
        elif req_type == "number":
            min_val = req_config.get("min_value")
            max_val = req_config.get("max_value")
            try:
                num_val = float(patient_value) if patient_value else 0
                is_met = True
                if min_val and num_val < min_val:
                    is_met = False
                if max_val and num_val > max_val:
                    is_met = False
            except (ValueError, TypeError):
                is_met = False
        else:
            # Default to checking if value exists
            is_met = patient_value is not None and patient_value != ""
        
        decision_entry["met"] = is_met
        decision_trail.append(decision_entry)
        
        return is_met
    
    def _check_exclusions(self, patient_responses: Dict, exclusions: Dict, decision_trail: List) -> bool:
        """Check if patient meets any exclusion criteria."""
        
        for exclusion_name, exclusion_config in exclusions.items():
            symptoms = exclusion_config.get("symptoms", [])
            if self._check_symptoms_present(patient_responses, symptoms):
                decision_trail.append({
                    "exclusion": exclusion_name,
                    "action": exclusion_config.get("action"),
                    "message": exclusion_config.get("message")
                })
                return True
        
        return False
    
    def _check_symptoms_present(self, patient_responses: Dict, symptoms: List[str]) -> bool:
        """Check if any of the specified symptoms are present in patient responses."""
        
        # Check all response values for symptom keywords
        all_responses = " ".join(str(v).lower() for v in patient_responses.values() if v)
        
        return any(symptom.lower() in all_responses for symptom in symptoms)
    
    def _check_enrollment_period(self, patient_responses: Dict, enrollment_periods: Dict, decision_trail: List) -> bool:
        """Check if patient is eligible for insurance enrollment period."""
        
        # Check for open enrollment (always eligible during this period)
        # In real implementation, would check current date
        
        # Check for Special Enrollment Period qualifying events
        sep_events = enrollment_periods.get("special_enrollment", {}).get("qualifying_events", [])
        
        all_responses = " ".join(str(v).lower() for v in patient_responses.values() if v)
        
        for event in sep_events:
            if event.lower() in all_responses:
                decision_trail.append({
                    "enrollment_eligibility": "SEP_qualified",
                    "qualifying_event": event
                })
                return True
        
        # Could add logic to check if currently in open enrollment period
        # For now, assume they qualify
        decision_trail.append({
            "enrollment_eligibility": "assumed_eligible",
            "reason": "General enrollment assistance available"
        })
        return True
    
    def _generate_reasoning(self, met_requirements: List, missing_criteria: List, excluded: bool, service: str) -> str:
        """Generate human-readable reasoning."""
        
        if excluded:
            return f"❌ Excluded from {service} due to safety or clinical criteria"
        elif missing_criteria:
            return f"Missing {len(missing_criteria)} required criteria: {', '.join(missing_criteria)}"
        else:
            return f"✅ Meets all requirements for {service}"
    
    def _generate_insurance_reasoning(self, met_requirements: List, missing_criteria: List, enrollment_eligible: bool) -> str:
        """Generate insurance-specific reasoning."""
        
        if missing_criteria and not enrollment_eligible:
            return f"Missing requirements: {', '.join(missing_criteria)} AND not in enrollment period"
        elif missing_criteria:
            return f"Missing {len(missing_criteria)} required criteria: {', '.join(missing_criteria)}"
        elif not enrollment_eligible:
            return "Not currently in open enrollment period and no qualifying life events detected"
        else:
            return "✅ Meets all requirements and eligible for enrollment"
    
    def _generate_next_questions_json(self, patient_responses: Dict, requirements: Dict, missing_criteria: List) -> List[str]:
        """Generate next questions based on missing criteria from JSON rules with options."""

        questions = []

        for missing in missing_criteria[:1]:  # Limit to 1 question
            req_config = requirements.get(missing, {})
            question_text = req_config.get("question")

            if question_text:
                # Check if this question has options we should include
                formatted_question = self._format_question_with_options(question_text, req_config, missing)
                questions.append(formatted_question)

        return questions

    def _format_question_with_options(self, question_text: str, req_config: Dict, req_name: str) -> str:
        """Format question with available options for better user experience."""

        # Special handling for chronic conditions
        if "chronic" in req_name.lower() or "conditions" in req_name.lower():
            values = req_config.get("values", [])
            if values:
                # Format chronic conditions nicely
                conditions_list = [
                    "Type 1 or Type 2 Diabetes",
                    "High Blood Pressure (Hypertension)",
                    "COPD (Chronic Obstructive Pulmonary Disease)",
                    "Heart Failure or other heart conditions",
                    "Chronic Kidney Disease",
                    "Asthma",
                    "Other chronic condition"
                ]
                return f"{question_text}\n" + "\n".join(f"• {cond}" for cond in conditions_list)

        # Special handling for insurance
        if "insurance" in req_name.lower():
            insurance_options = [
                "Medicare (Part A, Part B, or both)",
                "Medicaid",
                "Private insurance (through employer)",
                "Private insurance (self-purchased)",
                "Other government program",
                "No, I don't have insurance"
            ]
            return f"{question_text}\n" + "\n".join(f"• {opt}" for opt in insurance_options)

        # For other questions with values list
        values = req_config.get("values", [])
        if values and len(values) > 2:  # Only add list if there are multiple options
            return f"{question_text}\n" + "\n".join(f"• {val}" for val in values[:7])  # Limit to 7 options

        # Return question as-is if no options available
        return question_text
    
    def get_next_assessment_questions(self, context: Dict, service_type: Optional[str] = None) -> List[str]:
        """Enhanced question generation using JSON assessment database."""
        
        # Use assessment questions from JSON if available
        if "assessment" in self.rules:
            return self._get_questions_from_json_db(context, service_type)
        
        # Fallback to simple rule-based questions
        return self._get_fallback_questions(context, service_type)
    
    def _get_questions_from_json_db(self, context: Dict, service_type: str) -> List[str]:
        """Get questions from JSON assessment database with improved tracking."""
        
        assessment_rules = self.rules.get("assessment", {})
        question_categories = assessment_rules.get("question_categories", {})
        
        # Get service-specific flow if available
        flow_logic = assessment_rules.get("question_flow_logic", {})
        service_specific = flow_logic.get("service_specific", {})
        
        service_key = self._normalize_service_name(service_type) if service_type else None
        
        # Track asked questions to prevent repetition
        asked_questions = context.get("_asked_questions", [])
        
        if service_key and service_key in service_specific:
            required_questions = service_specific[service_key].get("required_questions", [])
            
            # Find first unanswered required question that hasn't been asked
            for question_id in required_questions:
                if (question_id not in context or not context[question_id]) and question_id not in asked_questions:
                    # Find the actual question text
                    question_text = self._find_question_by_id(question_categories, question_id)
                    if question_text:
                        # Mark this question as asked
                        if "_asked_questions" not in context:
                            context["_asked_questions"] = []
                        context["_asked_questions"].append(question_id)
                        return [question_text]
        
        # Default priority questions - check if already asked
        priority_categories = ["emergency_symptoms", "chronic_conditions", "insurance_status", "age"]
        
        for category in priority_categories:
            if category in question_categories:
                questions = question_categories[category].get("questions", [])
                for q in questions:
                    question_id = q.get("id")
                    if (question_id not in context or not context[question_id]) and question_id not in asked_questions:
                        # Mark this question as asked
                        if "_asked_questions" not in context:
                            context["_asked_questions"] = []
                        context["_asked_questions"].append(question_id)
                        return [q.get("text")]
        
        return ["How can I help you with your healthcare needs today?"]
    
    def _find_question_by_id(self, question_categories: Dict, question_id: str) -> Optional[str]:
        """Find question text by ID in question categories."""
        
        for category, category_data in question_categories.items():
            questions = category_data.get("questions", [])
            for q in questions:
                if q.get("id") == question_id:
                    return q.get("text")
        return None
    
    def _get_fallback_questions(self, context: Dict, service_type: str) -> List[str]:
        """Fallback questions if JSON assessment not available."""
        
        if service_type and "rpm" in service_type.lower():
            if "chronic_conditions" not in context:
                return ["Do you have any chronic health conditions like diabetes, high blood pressure, or heart disease?"]
            elif "insurance_coverage" not in context:
                return ["Do you currently have health insurance coverage?"]
            elif "device_access" not in context:
                return ["Do you have access to a smartphone, tablet, or Wi-Fi at home?"]
            elif "consent_monitoring" not in context:
                return ["Are you comfortable with sharing your health data for remote monitoring?"]
        elif service_type and "wellness" in service_type.lower():
            if "age" not in context:
                return ["What is your age?"]
            elif "care_goals" not in context:
                return ["What are your main healthcare goals? (e.g., lose weight, prevent diabetes, reduce stress)"]
            elif "lifestyle_factors" not in context:
                return ["Which of these describes your current lifestyle? (e.g., sedentary, unhealthy diet, high stress)"]
            elif "chronic_conditions" not in context:
                return ["Do you have any chronic health conditions or risk factors?"]
        
        # Generic fallback questions
        return ["What is your age?", "Do you have any chronic health conditions?", "Do you currently have health insurance?"][:1]

# Updated tool functions to use JSON rules engine
def load_dynamic_rules() -> str:
    """Tool to load JSON rules and return summary."""
    rules_engine = JSONRulesEngine("rules")
    
    service_counts = {}
    for service, rule_data in rules_engine.rules.items():
        service_counts[service] = rule_data.get("version", "1.0")
    
    summary = f"""
    📋 Enhanced JSON Rules Engine Loaded:
    
    Services Available:
    {json.dumps(service_counts, indent=2)}
    
    Ready to process patient routing decisions with improved JSON-based logic!
    """
    
    return summary

def assess_eligibility_dynamically(patient_data: str) -> str:
    """Tool to assess patient eligibility using JSON rules."""
    try:
        patient_responses = json.loads(patient_data) if isinstance(patient_data, str) else patient_data
    except:
        return "❌ Error: Patient data must be in JSON format"
    
    rules_engine = JSONRulesEngine("rules")
    
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

def get_next_assessment_questions(current_responses: str, service_type: Optional[str] = None) -> str:
    """Tool to get next questions using JSON rules."""
    rules_engine = JSONRulesEngine("rules")
    
    try:
        responses = json.loads(current_responses) if current_responses else {}
    except:
        responses = {}
    
    next_questions = rules_engine.get_next_assessment_questions(responses, service_type)
    
    if not next_questions:
        return "✅ All necessary information has been collected. Let me assess your eligibility..."
    
    return "Next questions to ask:\n" + "\n".join(f"• {q}" for q in next_questions)

def assess_service_specific_eligibility(service_type: str, patient_responses: str) -> str:
    """Tool to assess eligibility for specific service using JSON rules."""
    rules_engine = JSONRulesEngine("rules")
    
    try:
        responses = json.loads(patient_responses) if patient_responses else {}
    except:
        return "❌ Error: Patient responses must be in JSON format"
    
    result = rules_engine.evaluate_patient_against_rules(responses, service_type)
    
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
