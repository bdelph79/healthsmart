# Alaska Telehealth Restriction Fix

## Problem
The system doesn't recognize Alaska as a restricted state for telehealth services, causing it to continue with standard assessment instead of explaining licensing limitations and offering alternatives.

## Root Cause
1. **Data Type Error**: `TypeError: sequence item 0: expected str instance, float found` in rules_engine_enhanced.py line 621
2. **Missing State Restriction Logic**: No check for restricted states before proceeding with telehealth assessment
3. **Agent Instructions**: Coordinator agent doesn't prioritize state restriction checks

## Fix Implementation

### 1. Fix Data Type Error (rules_engine_enhanced.py line 621)

**Current Code:**
```python
if result.fallback_options:
    response += f"Fallback Options: {', '.join(result.fallback_options)}\n"
```

**Fixed Code:**
```python
if result.fallback_options:
    fallback_str = ', '.join(str(option) for option in result.fallback_options)
    response += f"Fallback Options: {fallback_str}\n"
```

### 2. Add State Restriction Function (rules_engine_enhanced.py)

**Add this function:**
```python
def check_telehealth_state_restrictions(state: str) -> tuple[bool, str]:
    """Check if state has telehealth restrictions"""
    restricted_states = {
        'alaska', 'hawaii', 'montana', 'north dakota', 'south dakota', 
        'wyoming', 'vermont', 'delaware', 'rhode island'
    }
    
    state_lower = state.lower().strip()
    
    if state_lower in restricted_states:
        return False, f"Unfortunately, our telehealth providers are not currently licensed to practice in {state.title()}. This is due to state medical licensing requirements."
    
    return True, ""
```

### 3. Modify assess_service_specific_eligibility Function (rules_engine_enhanced.py)

**Add state check for telehealth:**
```python
def assess_service_specific_eligibility(service_type: str, patient_responses: str) -> str:
    # ... existing code ...
    
    # Add state check for telehealth
    if service_type.upper() == "TELEHEALTH":
        # Extract state from responses
        state_match = re.search(r'(?:live|living|reside|residing|state|location).*?(?:in|is|at)\s+([a-zA-Z\s]+)', 
                               patient_responses, re.IGNORECASE)
        if state_match:
            state = state_match.group(1).strip()
            is_licensed, restriction_msg = check_telehealth_state_restrictions(state)
            
            if not is_licensed:
                return f"""
🚫 Telehealth State Restriction

{restriction_msg}

Alternative Options:
• In-person care locator to find local providers
• Phone triage services for non-urgent care
• Remote Patient Monitoring (if you have chronic conditions)
• Insurance enrollment assistance
• Pharmacy savings programs

Would you like me to help you with any of these alternatives?
"""
```

### 4. Add State Detection Tool (smart_health_agent.py)

**Add this tool:**
```python
@tool
def check_telehealth_state_eligibility_tool(patient_responses: str) -> str:
    """Check if patient's state allows telehealth services"""
    restricted_states = {
        'alaska', 'hawaii', 'montana', 'north dakota', 'south dakota', 
        'wyoming', 'vermont', 'delaware', 'rhode island'
    }
    
    # Extract state from responses
    state_match = re.search(r'(?:live|living|reside|residing|state|location).*?(?:in|is|at)\s+([a-zA-Z\s]+)', 
                           patient_responses, re.IGNORECASE)
    
    if not state_match:
        return "No state information found in patient responses"
    
    state = state_match.group(1).strip().lower()
    
    if state in restricted_states:
        return f"RESTRICTED: {state.title()} is not a licensed state for our telehealth providers. Offer alternatives: in-person care locator, phone triage, RPM, or insurance enrollment."
    else:
        return f"LICENSED: {state.title()} is a licensed state. Continue with standard telehealth assessment."
```

### 5. Update Coordinator Agent Instructions (smart_health_agent.py)

**Modify the coordinator agent instruction:**
```python
coordinator_agent = Agent(
    name="HealthcareCoordinator",
    model="gemini-2.5-flash",
    instruction="""
    You are a healthcare navigation assistant helping patients find the right services.
    
    CRITICAL STATE RESTRICTION HANDLING:
    - For Telehealth requests, IMMEDIATELY check if patient lives in a restricted state
    - Restricted states: Alaska, Hawaii, Montana, North Dakota, South Dakota, Wyoming, Vermont, Delaware, Rhode Island
    - If patient is in restricted state, explain licensing limitations and offer alternatives
    - DO NOT continue with standard telehealth assessment for restricted states
    
    Your workflow:
    1. If the message starts with "FIRST_INTERACTION:", present available services
    2. For telehealth interest, check state restrictions FIRST using check_telehealth_state_eligibility_tool
    3. If state is restricted, explain limitations and offer alternatives
    4. If state is licensed, continue with standard assessment
    5. Use assess_service_specific_eligibility_tool for other services
    6. Route qualified patients to appropriate specialist agents
    
    # ... rest of existing instructions ...
    """,
    tools=[present_available_services, load_routing_rules,
           get_next_assessment_questions_tool, assess_service_specific_eligibility_tool,
           get_service_details, route_to_specialist, check_telehealth_state_eligibility_tool],  # Add new tool
    # ... rest of existing code ...
)
```

## Expected Behavior After Fix

### Test Case 4 - Alaska Scenario:

1. **"I need a virtual doctor visit"** 
   - Response: Presents available services

2. **"I live in Alaska"** 
   - Response: **"🚫 Telehealth State Restriction - Unfortunately, our telehealth providers are not currently licensed to practice in Alaska. This is due to state medical licensing requirements. Alternative Options: In-person care locator, Phone triage services, Remote Patient Monitoring, Insurance enrollment assistance, Pharmacy savings programs. Would you like me to help you with any of these alternatives?"**

3. **"What are my options?"** 
   - Response: **"Alternative Options: In-person care locator to find local providers, Phone triage services for non-urgent care, Remote Patient Monitoring (if you have chronic conditions), Insurance enrollment assistance, Pharmacy savings programs"**

## Files to Modify

1. `app/rules_engine_enhanced.py` - Fix data type error and add state restriction logic
2. `app/smart_health_agent.py` - Add state detection tool and update agent instructions

## Testing

After applying the fix, test with:
- Alaska (restricted state) - should show restriction message
- California (licensed state) - should continue with normal assessment
- Other restricted states - should show appropriate restriction messages

## Notes

- This fix prioritizes state restriction checks before any other telehealth assessment
- Provides clear alternatives for patients in restricted states
- Maintains professional tone while explaining limitations
- Ensures legal compliance with state licensing requirements







