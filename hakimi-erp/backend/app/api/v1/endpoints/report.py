from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.report_service import report_service
from app.schemas.base import ResponseModel
from typing import Optional

router = APIRouter()

@router.get("/sales-performance", response_model=ResponseModel)
def sales_performance(days: int = 30, db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_sales_performance(db, days))

@router.get("/financial-summary", response_model=ResponseModel)
def financial_summary(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_financial_summary(db))

@router.get("/financial-detail", response_model=ResponseModel)
def financial_detail(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_financial_detail(db))

@router.get("/delivery-stats", response_model=ResponseModel)
def delivery_stats(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_delivery_stats(db))

@router.get("/customer-analysis", response_model=ResponseModel)
def customer_analysis(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_customer_analysis(db))

@router.get("/inventory-turnover", response_model=ResponseModel)
def inventory_turnover(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_inventory_turnover(db))

@router.get("/pricing-conditions", response_model=ResponseModel)
def pricing_conditions_report(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_pricing_conditions_report(db))

@router.get("/tax-compliance", response_model=ResponseModel)
def tax_compliance(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_tax_compliance_report(db))

@router.get("/quotation-conversion", response_model=ResponseModel)
def quotation_conversion(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_quotation_conversion_report(db))

@router.get("/dashboard-summary", response_model=ResponseModel)
def dashboard_summary(db: Session = Depends(get_db)):
    return ResponseModel(data=report_service.get_dashboard_summary(db))

