from typing import Dict, Any
# No import needed for schemas — validation handled by validate_data()

def process_cv(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process CV data and prepare for rendering"""
    try:
        if not isinstance(data, dict):
            raise ValueError("CV data must be a dictionary")

        # Personal info
        if 'personal' in data:
            if 'birthdate' in data['personal']:
                data['personal']['formatted_birthdate'] = data['personal']['birthdate']

            if 'contact' in data['personal']:
                contact = data['personal']['contact']
                data['personal']['contact'] = {
                    'email': contact.get('email', ''),
                    'phone': contact.get('phone', ''),
                    'address': contact.get('address', '')
                }

        # Experience
        if 'experience' in data:
            data['experience'] = sorted(
                data['experience'],
                key=lambda x: x.get('end_date', '9999'),
                reverse=True
            )

        # Education
        if 'education' in data:
            data['education'] = sorted(
                data['education'],
                key=lambda x: x.get('end_date', '9999'),
                reverse=True
            )

        return data
    except Exception as e:
        raise ValueError(f"CV processing failed: {str(e)}")
