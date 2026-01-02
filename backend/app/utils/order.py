from app.extensions import db

def compact_order(query, order_field="order"):
    """
    Re-assigns sequential order values (1..N) for a scoped query.
    """
    items = query.order_by(getattr(query.column_description[0]['entity'], order_field).asc()).all()
    
    for index, item in enumerate(items, start=1):
        setattr(item, order_field, index)
        
    db.session.flush()