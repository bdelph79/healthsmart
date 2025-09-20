# Fix 3: Improve age parsing in _matches_criteria
# Replace the age checking section in app/rules_engine.py

# OLD CODE:
# patient_age = responses.get('age', 0)

# NEW CODE:
# patient_age = self._get_patient_age(responses)

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
