# Fix 1: Handle non-string missing data in get_next_assessment_questions
# Replace line 289 in app/rules_engine.py

# OLD CODE:
# if any(keyword in question_text for keyword in missing.split()):

# NEW CODE:
# if isinstance(missing, str) and any(keyword in question_text for keyword in missing.split()):
