"""Seed clean demo sales orders for the order-to-cash assistant demo.

All pre-seeded orders (SO00001-SO00008) already have PGI_DONE deliveries and
CLEARED invoices, so the picking->settlement chain would skip every stage on
them. This script creates fresh OPEN orders (SO00101+) with items but WITHOUT
deliveries / invoices, so the assistant demo executes every step for real.

Idempotent: skips ids that already exist. Safe to re-run before each demo.

Run: D:/Anaconda/python.exe seed_demo_orders.py
"""

from datetime import date, timedelta
from decimal import Decimal

from app.core.database import SessionLocal
from app.models.sales import SalesOrder, SalesOrderItem

# (so_id, customer, plant, payment_terms, [(material, qty, unit, price, plant)])
DEMO_ORDERS = [
    ("SO00107", "BP00001", "PL01", "NET30", [
        ("MAT0002", 20, "PC", Decimal("170.20"), "PL02"),
        ("MAT0006", 30, "BARREL", Decimal("304.00"), "PL01"),
    ]),
    ("SO00108", "BP00002", "PL02", "NET30", [
        ("MAT0013", 60, "BOX", Decimal("78.20"), "PL02"),
        ("MAT0004", 40, "SET", Decimal("1254.40"), "PL01"),
    ]),
    ("SO00109", "BP00003", "PL03", "NET30", [
        ("MAT0012", 12, "SET", Decimal("2327.50"), "PL01"),
    ]),
]


def main():
    db = SessionLocal()
    try:
        for so_id, customer, plant, terms, items in DEMO_ORDERS:
            if db.query(SalesOrder).filter(SalesOrder.sales_order_id == so_id).first():
                print(f"{so_id} already exists, skipped")
                continue
            net_value = sum(Decimal(qty) * price for _, qty, _, price, _ in items)
            so = SalesOrder(
                sales_order_id=so_id,
                order_type="OR",
                status="OPEN",
                customer_id=customer,
                sold_to_party=customer,
                ship_to_party=None,
                requested_delivery_date=date.today() + timedelta(days=7),
                payment_terms=terms,
                incoterms="FOB",
                delivering_plant=plant,
                currency="CNY",
                net_value=net_value,
            )
            db.add(so)
            for idx, (mat, qty, unit, price, item_plant) in enumerate(items, start=1):
                db.add(SalesOrderItem(
                    so_item_id=f"SI{so_id[2:]}{idx:03d}",
                    sales_order_id=so_id,
                    item_no=idx * 10,
                    material_id=mat,
                    item_category="TAN",
                    order_quantity=Decimal(qty),
                    confirmed_quantity=Decimal(qty),
                    sales_unit=unit,
                    plant=item_plant,
                    unit_price=price,
                    discount=Decimal("0.00"),
                    net_price=Decimal(qty) * price,
                    availability_status="AVAILABLE",
                ))
            print(f"{so_id} created (net {net_value})")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
