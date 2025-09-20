# Fix 2: Improve age recognition in identify_missing_critical_data
# Replace the method in app/rules_engine.py

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
