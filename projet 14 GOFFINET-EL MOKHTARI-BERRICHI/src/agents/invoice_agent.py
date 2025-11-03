from typing import Dict, Any
# No import needed for schemas — validation handled by validate_data()

def process_invoice(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process invoice data and prepare for rendering"""
    try:
        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Invoice data must be a dictionary")
        
        # Process invoice metadata
        if 'invoice' in data:
            # Format dates
            if 'date' in data['invoice']:
                data['invoice']['formatted_date'] = data['invoice']['date']
            
            # Format currency
            if 'total' in data['invoice']:
                data['invoice']['formatted_total'] = f"{data['invoice']['total']:.2f} €"
        
        # Process items list
        if 'items' in data:
            # Calculate line totals
            for item in data['items']:
                if 'quantity' in item and 'unit_price' in item:
                    item['line_total'] = item['quantity'] * item['unit_price']
            
            # Calculate totals
            subtotal = sum(item.get('line_total', 0) for item in data['items'])
            tax_rate = data.get('tax_rate', 0.20)  # Default 20% tax
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount
            
            data['totals'] = {
                'subtotal': subtotal,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'total': total,
                'formatted_total': f"{total:.2f} €"
            }
        
        return data
    except Exception as e:
        raise ValueError(f"Invoice processing failed: {str(e)}")
