from sqlalchemy.orm import Session
from app.models.sales import Inquiry, InquiryItem, Quotation, QuotationItem, SalesOrder, SalesOrderItem
from app.schemas.sales import (
    InquiryCreate, QuotationCreate, SalesOrderCreate,
    InquiryItemCreate, QuotationItemCreate, SalesOrderItemCreate
)
from typing import List, Optional
from datetime import datetime

class SalesService:
    # --- Inquiry ---
    @staticmethod
    def get_inquiries(db: Session, skip: int = 0, limit: int = 100, 
                      inquiry_id: Optional[str] = None, 
                      customer_name: Optional[str] = None,
                      status: Optional[str] = None) -> List[Inquiry]:
        from app.models.customer import BusinessPartner
        query = db.query(Inquiry)
        if inquiry_id:
            query = query.filter(Inquiry.inquiry_id.ilike(f"%{inquiry_id}%"))
        if customer_name:
            query = query.join(BusinessPartner, Inquiry.customer_id == BusinessPartner.bp_id).filter(BusinessPartner.bp_name.ilike(f"%{customer_name}%"))
        if status:
            query = query.filter(Inquiry.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_inquiry(db: Session, inquiry_id: str) -> Optional[Inquiry]:
        return db.query(Inquiry).filter(Inquiry.inquiry_id == inquiry_id).first()

    @staticmethod
    def create_inquiry(db: Session, inquiry_in: InquiryCreate) -> Inquiry:
        data = inquiry_in.model_dump()
        items_data = data.pop("items")
        db_inquiry = Inquiry(**data)
        db.add(db_inquiry)
        
        for item in items_data:
            db_item = InquiryItem(**item, inquiry_id=db_inquiry.inquiry_id)
            db.add(db_item)
            
        db.commit()
        db.refresh(db_inquiry)
        return db_inquiry

    @staticmethod
    def update_inquiry(db: Session, inquiry_id: str, inquiry_in: dict) -> Inquiry:
        db_inquiry = SalesService.get_inquiry(db, inquiry_id)
        if not db_inquiry:
            raise Exception("Inquiry not found")
        
        items_data = inquiry_in.pop("items", [])
        for key, value in inquiry_in.items():
            if hasattr(db_inquiry, key):
                setattr(db_inquiry, key, value)
        
        # Simple implementation: delete and recreate items
        db.query(InquiryItem).filter(InquiryItem.inquiry_id == inquiry_id).delete()
        for item in items_data:
            db_item = InquiryItem(**item, inquiry_id=inquiry_id)
            db.add(db_item)
            
        db.commit()
        db.refresh(db_inquiry)
        return db_inquiry

    # --- Quotation ---
    @staticmethod
    def get_quotations(db: Session, skip: int = 0, limit: int = 100,
                       quotation_id: Optional[str] = None,
                       customer_name: Optional[str] = None,
                       status: Optional[str] = None) -> List[Quotation]:
        from app.models.customer import BusinessPartner
        query = db.query(Quotation)
        if quotation_id:
            query = query.filter(Quotation.quotation_id.ilike(f"%{quotation_id}%"))
        if customer_name:
            query = query.join(BusinessPartner, Quotation.customer_id == BusinessPartner.bp_id).filter(BusinessPartner.bp_name.ilike(f"%{customer_name}%"))
        if status:
            query = query.filter(Quotation.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_quotation(db: Session, quotation_id: str) -> Optional[Quotation]:
        return db.query(Quotation).filter(Quotation.quotation_id == quotation_id).first()

    @staticmethod
    def create_quotation(db: Session, quotation_in: QuotationCreate) -> Quotation:
        data = quotation_in.model_dump()
        items_data = data.pop("items")
        db_quotation = Quotation(**data)
        db.add(db_quotation)
        
        for item in items_data:
            db_item = QuotationItem(**item, quotation_id=db_quotation.quotation_id)
            db.add(db_item)
        
        # If created from inquiry, close the inquiry
        if db_quotation.inquiry_id:
            db_inquiry = SalesService.get_inquiry(db, db_quotation.inquiry_id)
            if db_inquiry:
                db_inquiry.status = "COMPLETED"
            
        db.commit()
        db.refresh(db_quotation)
        return db_quotation

    @staticmethod
    def update_quotation(db: Session, quotation_id: str, quotation_in: dict) -> Quotation:
        db_quotation = SalesService.get_quotation(db, quotation_id)
        if not db_quotation:
            raise Exception("Quotation not found")
        
        items_data = quotation_in.pop("items", [])
        for key, value in quotation_in.items():
            if hasattr(db_quotation, key):
                setattr(db_quotation, key, value)
        
        db.query(QuotationItem).filter(QuotationItem.quotation_id == quotation_id).delete()
        for item in items_data:
            db_item = QuotationItem(**item, quotation_id=quotation_id)
            db.add(db_item)
            
        db.commit()
        db.refresh(db_quotation)
        return db_quotation

    # --- Sales Order ---
    @staticmethod
    def get_orders(db: Session, skip: int = 0, limit: int = 100,
                   sales_order_id: Optional[str] = None,
                   customer_name: Optional[str] = None,
                   status: Optional[str] = None) -> List[SalesOrder]:
        from app.models.customer import BusinessPartner
        query = db.query(SalesOrder)
        if sales_order_id:
            query = query.filter(SalesOrder.sales_order_id.ilike(f"%{sales_order_id}%"))
        if customer_name:
            query = query.join(BusinessPartner, SalesOrder.customer_id == BusinessPartner.bp_id).filter(BusinessPartner.bp_name.ilike(f"%{customer_name}%"))
        if status:
            query = query.filter(SalesOrder.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_order(db: Session, sales_order_id: str) -> Optional[SalesOrder]:
        return db.query(SalesOrder).filter(SalesOrder.sales_order_id == sales_order_id).first()

    @staticmethod
    def create_order(db: Session, order_in: SalesOrderCreate) -> SalesOrder:
        data = order_in.model_dump()
        items_data = data.pop("items")

        requested_id = (data.get("sales_order_id") or "").strip()
        if not requested_id:
            raise Exception("Sales order ID is required")
        if SalesService.get_order(db, requested_id):
            raise Exception(f"Sales order ID already exists: {requested_id}")
        data["sales_order_id"] = requested_id

        db_order = SalesOrder(**data)
        db.add(db_order)
        
        for item in items_data:
            db_item = SalesOrderItem(**item, sales_order_id=db_order.sales_order_id)
            # Simulate ATP: confirm quantity
            db_item.confirmed_quantity = db_item.order_quantity
            db_item.availability_status = "CONFIRMED"
            db.add(db_item)
            
        # If created from quotation, close the quotation
        if db_order.quotation_id:
            db_quotation = SalesService.get_quotation(db, db_order.quotation_id)
            if db_quotation:
                db_quotation.status = "COMPLETED"
                
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def update_order(db: Session, sales_order_id: str, order_in: dict) -> SalesOrder:
        db_order = SalesService.get_order(db, sales_order_id)
        if not db_order:
            raise Exception("Order not found")
        
        items_data = order_in.pop("items", [])
        new_id = str(order_in.get("sales_order_id") or "").strip()
        if new_id and new_id != sales_order_id:
            existing = db.query(SalesOrder).filter(SalesOrder.sales_order_id == new_id).first()
            if existing:
                raise Exception(f"Sales order ID already exists: {new_id}")
        for key, value in order_in.items():
            if hasattr(db_order, key):
                setattr(db_order, key, value)
        
        db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == sales_order_id).delete()
        for item in items_data:
            db_item = SalesOrderItem(**item, sales_order_id=sales_order_id)
            db.add(db_item)
            
        db.commit()
        db.refresh(db_order)
        return db_order

sales_service = SalesService()
