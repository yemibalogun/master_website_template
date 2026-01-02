from app.extensions import db

def compact_order(query, order_field="order"):
    model = query.column_descriptions[0]["entity"]
    items = query.order_by(getattr(model, order_field).asc()).all()

    for idx, item in enumerate(items, start=1):
        setattr(item, order_field, idx)

    db.session.flush()