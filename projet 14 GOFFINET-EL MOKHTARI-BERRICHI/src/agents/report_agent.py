from typing import Dict, Any
# No import needed for schemas — validation handled by validate_data()

def process_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process report data and prepare for rendering"""
    try:
        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Report data must be a dictionary")
        
        # Process report metadata
        if 'metadata' in data:
            # Format dates
            if 'date' in data['metadata']:
                data['metadata']['formatted_date'] = data['metadata']['date']
            
            # Format version
            if 'version' in data['metadata']:
                data['metadata']['version_string'] = f"v{data['metadata']['version']}"
        
        # Process report content
        if 'content' in data:
            # Process sections
            if 'sections' in data['content']:
                for section in data['content']['sections']:
                    if 'title' in section:
                        # Format section title
                        section['formatted_title'] = f"=== {section['title'].upper()} ==="
                    
                    if 'items' in section and isinstance(section['items'], list):
                        # Add item counts
                        section['item_count'] = len(section['items'])
        
        # Process authors information
        if 'authors' in data:
            # Format author names
            formatted_authors = []
            for author in data['authors']:
                if isinstance(author, dict):
                    name_parts = []
                    if 'first_name' in author:
                        name_parts.append(author['first_name'])
                    if 'last_name' in author:
                        name_parts.append(author['last_name'])
                    if name_parts:
                        formatted_authors.append(' '.join(name_parts))
            
            data['formatted_authors'] = ', '.join(formatted_authors)
        
        # Format numeric values
        if 'financials' in data:
            for key, value in data['financials'].items():
                if isinstance(value, (int, float)):
                    data['financials'][key] = f"{value:,.2f} €"
        
        return data
    except Exception as e:
        raise ValueError(f"Report processing failed: {str(e)}")