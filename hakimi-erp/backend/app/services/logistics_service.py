from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from app.models.logistics import Delivery, DeliveryItem, GoodsIssue, PickRecord
from app.models.sales import SalesOrder, SalesOrderItem
from app.models.customer import BusinessPartner
from app.models.material import Material
from app.models.finance import Invoice
from app.schemas.logistics import DeliveryCreate, Delivery as DeliverySchema, DeliveryListItem
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal

class LogisticsService:
    @staticmethod
    def _get_delivery_model(db: Session, delivery_id: str) -> Optional[Delivery]:
        return (
            db.query(Delivery)
            .options(
                joinedload(Delivery.items).joinedload(DeliveryItem.material),
                joinedload(Delivery.items).joinedload(DeliveryItem.goods_issues),
                joinedload(Delivery.items).joinedload(DeliveryItem.pick_records),
            )
            .filter(Delivery.delivery_id == delivery_id)
            .first()
        )

    # --- Delivery Listing with filters ---
    @staticmethod
    def get_deliveries(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        delivery_no: Optional[str] = None,
        sales_order_no: Optional[str] = None,
        customer_name: Optional[str] = None,
        status: Optional[str] = None
    ):
        query = db.query(Delivery).options(
            joinedload(Delivery.ship_to),
            joinedload(Delivery.items)
        )

        if delivery_no:
            query = query.filter(Delivery.delivery_id.like(f"%{delivery_no}%"))
        if sales_order_no:
            query = query.filter(Delivery.sales_order_id.like(f"%{sales_order_no}%"))
        if customer_name:
            query = query.join(BusinessPartner, Delivery.ship_to_party == BusinessPartner.bp_id)
            query = query.filter(
                or_(
                    BusinessPartner.bp_name.like(f"%{customer_name}%"),
                    BusinessPartner.search_term.like(f"%{customer_name}%")
                )
            )
        reverse_map = {
            "Creating": "OPEN", "Picking": "PICKING",
            "Picked": "SHIPPED", "Shipped": "SHIPPED", "In Transit": "IN_TRANSIT",
            "Completed": "PGI_DONE", "Cancelled": "CANCELLED"
        }
        if status:
            db_status = reverse_map.get(status, status)
            query = query.filter(Delivery.delivery_status == db_status)
        else:
            query = query.filter(Delivery.delivery_status != "CANCELLED")

        total = query.count()
        deliveries = query.order_by(Delivery.delivery_id.desc()).offset(skip).limit(limit).all()

        result = []
        for d in deliveries:
            total_qty = sum(
                (item.delivery_quantity or Decimal(0))
                for item in d.items
            )
            delivered_qty = sum((item.picked_quantity or Decimal(0)) for item in d.items)
            bp_name = d.ship_to.bp_name if d.ship_to else d.ship_to_party
            invoice_id = db.query(Invoice.invoice_id).filter(
                Invoice.delivery_id == d.delivery_id
            ).scalar()
            result.append(DeliveryListItem(
                delivery_id=d.delivery_id,
                sales_order_id=d.sales_order_id,
                delivery_type=d.delivery_type,
                delivery_status=d.delivery_status,
                ship_to_party=d.ship_to_party,
                ship_to_party_name=bp_name,
                planned_delivery_date=d.planned_delivery_date,
                planned_gi_date=d.planned_gi_date,
                actual_gi_date=d.actual_gi_date,
                picking_date=d.picking_date,
                shipping_point=d.shipping_point,
                total_quantity=total_qty,
                delivered_quantity=delivered_qty,
                invoice_id=invoice_id,
            ))

        return result, total

    # --- Delivery Detail ---
    @staticmethod
    def get_delivery_detail(db: Session, delivery_id: str) -> Optional[DeliverySchema]:
        delivery = (
            db.query(Delivery)
            .options(
                joinedload(Delivery.ship_to),
                joinedload(Delivery.items)
                .joinedload(DeliveryItem.material),
                joinedload(Delivery.items)
                .joinedload(DeliveryItem.goods_issues),
                joinedload(Delivery.items)
                .joinedload(DeliveryItem.pick_records),
            )
            .filter(Delivery.delivery_id == delivery_id)
            .first()
        )
        if not delivery:
            return None

        bp = delivery.ship_to
        bp_name = bp.bp_name if bp else delivery.ship_to_party
        bp_address = ""
        if bp:
            parts = [bp.street or "", bp.house_number or "", bp.city or "", bp.district or ""]
            bp_address = ", ".join(p for p in parts if p)

        items = []
        total_qty = Decimal(0)
        delivered_qty = Decimal(0)
        for item in delivery.items:
            mat = item.material
            mat_name = mat.material_name if mat else item.material_id
            base_uom = mat.base_unit if mat else ""
            total_qty += (item.delivery_quantity or Decimal(0))
            delivered_qty += (item.picked_quantity or Decimal(0))
            items.append({
                "delivery_item_id": item.delivery_item_id,
                "delivery_id": item.delivery_id,
                "item_no": item.item_no,
                "so_item_id": item.so_item_id,
                "material_id": item.material_id,
                "material_name": mat_name,
                "base_unit": base_uom,
                "order_quantity": float(item.order_quantity or 0),
                "delivery_quantity": float(item.delivery_quantity or 0),
                "picked_quantity": float(item.picked_quantity or 0),
                "sales_unit": item.sales_unit,
                "plant": item.plant,
                "storage_location": item.storage_location,
                "item_description": item.item_description,
                "item_status": item.item_status or "OPEN",
            })

        return {
            "delivery_id": delivery.delivery_id,
            "sales_order_id": delivery.sales_order_id,
            "delivery_type": delivery.delivery_type,
            "delivery_status": delivery.delivery_status,
            "ship_to_party": delivery.ship_to_party,
            "ship_to_party_name": bp_name,
            "ship_to_address": bp_address,
            "planned_delivery_date": delivery.planned_delivery_date,
            "planned_gi_date": delivery.planned_gi_date,
            "actual_gi_date": delivery.actual_gi_date,
            "picking_date": delivery.picking_date,
            "shipping_point": delivery.shipping_point,
            "carrier": delivery.carrier,
            "driver_name": delivery.driver_name,
            "route": delivery.route,
            "tracking_no": delivery.tracking_no,
            "items": items,
            "total_quantity": float(total_qty),
            "delivered_quantity": float(delivered_qty),
        }

    @staticmethod
    def get_delivery(db: Session, delivery_id: str) -> Optional[Delivery]:
        return db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()

    # --- Create Delivery ---
    @staticmethod
    def create_delivery(db: Session, data: DeliveryCreate) -> dict:
        if data.sales_order_id:
            existing = db.query(Delivery).filter(
                Delivery.sales_order_id == data.sales_order_id,
                Delivery.delivery_status != "CANCELLED",
            ).first()
            if existing:
                raise Exception(f"Delivery already exists for sales order {data.sales_order_id}: {existing.delivery_id}")

        db_delivery = Delivery(
            delivery_id=data.delivery_id,
            sales_order_id=data.sales_order_id,
            delivery_type=data.delivery_type,
            delivery_status=data.delivery_status,
            ship_to_party=data.ship_to_party,
            planned_delivery_date=data.planned_delivery_date,
            planned_gi_date=data.planned_gi_date,
            shipping_point=data.shipping_point,
        )
        db.add(db_delivery)
        for it in data.items:
            db_item = DeliveryItem(
                delivery_item_id=it.delivery_item_id,
                delivery_id=data.delivery_id,
                item_no=it.item_no,
                so_item_id=it.so_item_id,
                material_id=it.material_id,
                order_quantity=it.order_quantity or Decimal(0),
                delivery_quantity=it.delivery_quantity or Decimal(0),
                sales_unit=it.sales_unit,
                plant=it.plant,
                storage_location=it.storage_location,
                item_description=it.item_description,
                item_status="OPEN",
            )
            db.add(db_item)
        db.commit()
        return LogisticsService.get_delivery_detail(db, data.delivery_id)

    # --- Create Delivery from Sales Order ---
    @staticmethod
    def create_from_sales_order(db: Session, sales_order_id: str) -> dict:
        so = db.query(SalesOrder).options(joinedload(SalesOrder.items)).filter(SalesOrder.sales_order_id == sales_order_id).first()
        if not so:
            raise Exception("Sales order not found")

        existing = db.query(Delivery).filter(
            Delivery.sales_order_id == sales_order_id,
            Delivery.delivery_status != "CANCELLED",
        ).first()
        if existing:
            raise Exception(f"Delivery already exists for sales order {sales_order_id}: {existing.delivery_id}")

        timestamp = datetime.now().strftime('%y%m%d%H%M%S')
        delivery_id = f"DEL{timestamp}"

        db_delivery = Delivery(
            delivery_id=delivery_id,
            sales_order_id=sales_order_id,
            delivery_type="LF",
            delivery_status="OPEN",
            ship_to_party=so.ship_to_party or so.customer_id,
            planned_delivery_date=so.requested_delivery_date,
            planned_gi_date=so.requested_delivery_date,
            shipping_point=so.delivering_plant,
        )
        db.add(db_delivery)

        for so_item in so.items:
            order_quantity_value = so_item.order_quantity or Decimal(0)
            di_id = f"DI{delivery_id}{so_item.item_no:02d}"
            db_item = DeliveryItem(
                delivery_item_id=di_id,
                delivery_id=delivery_id,
                item_no=so_item.item_no,
                so_item_id=so_item.so_item_id,
                material_id=so_item.material_id,
                order_quantity=order_quantity_value,
                delivery_quantity=order_quantity_value,
                sales_unit=so_item.sales_unit,
                plant=so_item.plant,
                storage_location=so_item.storage_location,
                item_status="OPEN",
            )
            db.add(db_item)

        so.status = "IN_PROCESS"
        db.commit()
        return LogisticsService.get_delivery_detail(db, delivery_id)

    # ==================== BATCH PICKING ====================

    @staticmethod
    def start_picking(db: Session, delivery_id: str):
        db_delivery = LogisticsService._get_delivery_model(db, delivery_id)
        if not db_delivery:
            raise Exception("Delivery not found")
        if db_delivery.delivery_status not in ("OPEN",):
            raise Exception("Delivery must be OPEN to start picking")
        db_delivery.delivery_status = "PICKING"
        db_delivery.picking_date = datetime.now().date()
        db.commit()
        return LogisticsService.get_delivery_detail(db, delivery_id)

    @staticmethod
    def pick_batch(db: Session, delivery_id: str, items: Dict[str, Decimal],
                   storage_location: Optional[str] = None, picked_by: Optional[str] = None):
        """Record a picking batch. Can be called multiple times for batch picking."""
        db_delivery = LogisticsService._get_delivery_model(db, delivery_id)
        if not db_delivery:
            raise Exception("Delivery not found")
        if db_delivery.delivery_status != "PICKING":
            raise Exception("Delivery must be in PICKING status to record picks")

        timestamp = datetime.now().strftime('%y%m%d%H%M%S')

        # Find current max batch_no for this delivery
        max_batch = db.query(func.coalesce(func.max(PickRecord.batch_no), 0)).join(
            DeliveryItem, PickRecord.delivery_item_id == DeliveryItem.delivery_item_id
        ).filter(DeliveryItem.delivery_id == delivery_id).scalar()
        batch_no = int(max_batch or 0) + 1

        pick_idx = 0
        for db_item in db_delivery.items:
            di_id = db_item.delivery_item_id
            if di_id not in items:
                continue
            qty = Decimal(str(items[di_id]))
            remaining = (db_item.delivery_quantity or Decimal(0)) - (db_item.picked_quantity or Decimal(0))
            if qty > remaining:
                raise Exception(f"Item {db_item.item_no}: pick qty {qty} exceeds remaining {remaining}")
            if qty <= 0:
                continue

            pick_idx += 1
            pick_id = f"PK{timestamp}{pick_idx:02d}"
            pick_rec = PickRecord(
                pick_id=pick_id,
                delivery_item_id=di_id,
                batch_no=batch_no,
                pick_quantity=qty,
                storage_location=storage_location or db_item.storage_location,
                pick_date=datetime.now(),
                picked_by=picked_by or "SYSTEM",
            )
            db.add(pick_rec)

            # Accumulate picked quantity
            db_item.picked_quantity = (db_item.picked_quantity or Decimal(0)) + qty
            new_picked = db_item.picked_quantity
            if new_picked >= (db_item.delivery_quantity or Decimal(0)):
                db_item.item_status = "PICKED"
            elif new_picked > 0:
                db_item.item_status = "PARTIAL_PICKED"

        db.commit()
        return LogisticsService.get_delivery_detail(db, delivery_id)

    @staticmethod
    def confirm_picking(db: Session, delivery_id: str):
        """Confirm picking complete. Only allowed when ALL items are fully picked."""
        db_delivery = LogisticsService._get_delivery_model(db, delivery_id)
        if not db_delivery:
            raise Exception("Delivery not found")
        if db_delivery.delivery_status != "PICKING":
            raise Exception("Delivery must be in PICKING status to confirm")

        # Check all items are fully picked
        not_picked = []
        for item in db_delivery.items:
            picked = item.picked_quantity or Decimal(0)
            needed = item.delivery_quantity or Decimal(0)
            if picked < needed:
                not_picked.append(f"Item {item.item_no}: {picked}/{needed}")
        if not_picked:
            raise Exception("Cannot confirm: items not fully picked: " + "; ".join(not_picked))

        db_delivery.delivery_status = "SHIPPED"
        if not db_delivery.planned_gi_date:
            db_delivery.planned_gi_date = datetime.now().date()
        db.commit()
        return LogisticsService.get_delivery_detail(db, delivery_id)

    @staticmethod
    def ship_delivery(db: Session, delivery_id: str):
        db_delivery = LogisticsService._get_delivery_model(db, delivery_id)
        if not db_delivery:
            raise Exception("Delivery not found")
        if db_delivery.delivery_status != "SHIPPED":
            raise Exception("Delivery can only be put in transit after picking is confirmed")

        db_delivery.delivery_status = "IN_TRANSIT"
        if not db_delivery.carrier:
            db_delivery.carrier = "Internal Fleet"
        if not db_delivery.route:
            db_delivery.route = "Warehouse to Customer Site"
        if not db_delivery.tracking_no:
            db_delivery.tracking_no = f"TRK{datetime.now().strftime('%y%m%d%H%M%S')}"

        db.commit()
        return LogisticsService.get_delivery_detail(db, delivery_id)

    # ==================== BATCH PGI ====================

    @staticmethod
    def post_goods_issue(db: Session, delivery_id: str, partial_items: dict = None):
        """Post Goods Issue. Supports batch PGI - multiple GI batches per delivery."""
        db_delivery = LogisticsService._get_delivery_model(db, delivery_id)
        if not db_delivery:
            raise Exception("Delivery not found")
        if db_delivery.delivery_status == "PGI_DONE":
            raise Exception("Goods Issue already fully posted for this delivery")
        if db_delivery.delivery_status != "IN_TRANSIT":
            raise Exception("Goods Issue can only be posted after the delivery is in transit")

        incomplete_picks = []
        for item in db_delivery.items:
            picked_qty = item.picked_quantity or Decimal(0)
            needed_qty = item.delivery_quantity or Decimal(0)
            if picked_qty < needed_qty:
                incomplete_picks.append(f"Item {item.item_no}: picked {picked_qty}/{needed_qty}")
        if incomplete_picks:
            raise Exception("Cannot post Goods Issue: delivery is not fully picked. " + "; ".join(incomplete_picks))

        timestamp = datetime.now().strftime('%y%m%d%H%M%S')

        # Find current max batch_no across existing GI records for this delivery
        max_gi_batch = db.query(func.coalesce(func.max(GoodsIssue.batch_no), 0)).join(
            DeliveryItem, GoodsIssue.delivery_item_id == DeliveryItem.delivery_item_id
        ).filter(DeliveryItem.delivery_id == delivery_id).scalar()
        gi_batch_no = int(max_gi_batch or 0) + 1

        all_fully_issued = True
        gi_idx = 0
        for item in db_delivery.items:
            picked_qty = item.picked_quantity or Decimal(0)
            if picked_qty <= 0:
                continue

            # Calculate already issued quantity for this item
            already_issued = db.query(func.coalesce(func.sum(GoodsIssue.actual_quantity), 0)).filter(
                GoodsIssue.delivery_item_id == item.delivery_item_id
            ).scalar()
            already_issued = Decimal(str(already_issued or 0))

            remaining_to_issue = picked_qty - already_issued
            if remaining_to_issue <= 0:
                continue

            # Determine GI quantity: use partial input if provided, else issue all remaining
            gi_qty = remaining_to_issue
            if partial_items and item.delivery_item_id in partial_items:
                gi_qty = Decimal(str(partial_items[item.delivery_item_id]))
                if gi_qty > remaining_to_issue:
                    raise Exception(f"Item {item.item_no}: GI qty {gi_qty} exceeds unpicked {remaining_to_issue}")
                if gi_qty <= 0:
                    continue

            material = item.material
            if material and material.stock_quantity is not None:
                if material.stock_quantity < gi_qty:
                    raise Exception(f"Insufficient stock for material {item.material_id}")
                material.stock_quantity -= gi_qty

            gi_idx += 1
            gi_id = f"PGI{timestamp}{gi_idx:02d}"
            db_gi = GoodsIssue(
                goods_issue_id=gi_id,
                delivery_item_id=item.delivery_item_id,
                actual_quantity=gi_qty,
                posting_date=datetime.now().date(),
                warehouse=db_delivery.shipping_point,
                batch_no=gi_batch_no,
            )
            db.add(db_gi)

            # Update item status
            new_total_issued = already_issued + gi_qty
            if new_total_issued >= picked_qty:
                item.item_status = "COMPLETED"
            else:
                item.item_status = "PARTIAL_ISSUED"
                all_fully_issued = False

        fully_picked = all(
            (item.picked_quantity or Decimal(0)) >= (item.delivery_quantity or Decimal(0))
            for item in db_delivery.items
        )

        # Check if ALL items across ALL deliveries for this SO are fully issued
        if all_fully_issued and fully_picked:
            db_delivery.delivery_status = "PGI_DONE"
            db_delivery.actual_gi_date = datetime.now()

        if db_delivery.sales_order_id:
            db_so = db.query(SalesOrder).filter(SalesOrder.sales_order_id == db_delivery.sales_order_id).first()
            if db_so:
                so_items = db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == db_delivery.sales_order_id).all()
                so_fully_done = True
                for so_item in so_items:
                    total_issued = db.query(func.coalesce(func.sum(GoodsIssue.actual_quantity), 0)).join(
                        DeliveryItem, GoodsIssue.delivery_item_id == DeliveryItem.delivery_item_id
                    ).filter(DeliveryItem.so_item_id == so_item.so_item_id).scalar()
                    if Decimal(str(total_issued or 0)) < (so_item.order_quantity or Decimal(0)):
                        so_fully_done = False
                        break
                db_so.status = "IN_PROCESS" if not so_fully_done else "COMPLETED"

        db.commit()
        db.refresh(db_delivery)
        return LogisticsService.get_delivery_detail(db, delivery_id)

    # --- Pick Records ---
    @staticmethod
    def get_pick_records(db: Session, delivery_id: str) -> List[dict]:
        results = (
            db.query(PickRecord)
            .join(DeliveryItem, PickRecord.delivery_item_id == DeliveryItem.delivery_item_id)
            .join(Material, DeliveryItem.material_id == Material.material_id)
            .filter(DeliveryItem.delivery_id == delivery_id)
            .order_by(PickRecord.batch_no, PickRecord.pick_id)
            .all()
        )
        return [
            {
                "pick_id": pr.pick_id,
                "delivery_item_id": pr.delivery_item_id,
                "batch_no": pr.batch_no,
                "pick_quantity": float(pr.pick_quantity),
                "storage_location": pr.storage_location,
                "pick_date": pr.pick_date,
                "picked_by": pr.picked_by,
                "material_id": pr.delivery_item.material_id,
                "material_name": pr.delivery_item.material.material_name if pr.delivery_item.material else None,
            }
            for pr in results
        ]

    # --- Goods Issue Records ---
    @staticmethod
    def get_goods_issues(db: Session, delivery_id: str) -> List[dict]:
        results = (
            db.query(GoodsIssue)
            .join(DeliveryItem, GoodsIssue.delivery_item_id == DeliveryItem.delivery_item_id)
            .join(Material, DeliveryItem.material_id == Material.material_id)
            .join(Delivery, DeliveryItem.delivery_id == Delivery.delivery_id)
            .filter(Delivery.delivery_id == delivery_id)
            .order_by(GoodsIssue.batch_no)
            .all()
        )
        return [
            {
                "goods_issue_id": gi.goods_issue_id,
                "delivery_item_id": gi.delivery_item_id,
                "actual_quantity": gi.actual_quantity,
                "posting_date": gi.posting_date,
                "goods_issue_time": gi.goods_issue_time,
                "warehouse": gi.warehouse,
                "batch_no": gi.batch_no,
                "material_id": gi.delivery_item.material_id,
                "material_name": gi.delivery_item.material.material_name if gi.delivery_item.material else None,
            }
            for gi in results
        ]

    # --- SO Item Remaining Quantities ---
    @staticmethod
    def get_so_remaining_quantities(db: Session, sales_order_id: str):
        so_items = db.query(SalesOrderItem).filter(
            SalesOrderItem.sales_order_id == sales_order_id
        ).all()
        result = []
        for si in so_items:
            total_issued = db.query(func.coalesce(func.sum(GoodsIssue.actual_quantity), 0)).join(
                DeliveryItem, GoodsIssue.delivery_item_id == DeliveryItem.delivery_item_id
            ).filter(DeliveryItem.so_item_id == si.so_item_id).scalar()
            in_progress_delivered = db.query(func.coalesce(func.sum(DeliveryItem.delivery_quantity), 0)).join(
                Delivery, DeliveryItem.delivery_id == Delivery.delivery_id
            ).filter(
                DeliveryItem.so_item_id == si.so_item_id,
                Delivery.delivery_status.notin_(["PGI_DONE", "CANCELLED"])
            ).scalar()
            already_committed = Decimal(str(total_issued)) + (Decimal(str(in_progress_delivered)) or Decimal(0))
            remaining = (si.order_quantity or Decimal(0)) - already_committed
            material = db.query(Material).filter(Material.material_id == si.material_id).first()
            result.append({
                "so_item_id": si.so_item_id,
                "material_id": si.material_id,
                "material_name": material.material_name if material else None,
                "order_quantity": float(si.order_quantity or 0),
                "already_delivered": float(already_committed),
                "remaining_quantity": float(max(remaining, 0)),
                "sales_unit": si.sales_unit,
            })
        return result

logistics_service = LogisticsService()