from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.api.v1.endpoints import auth, customer, material, sales, logistics, finance, report, assistant

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

protected_router = APIRouter(dependencies=[Depends(get_current_user)])
protected_router.include_router(customer.router, prefix="/master/partners", tags=["Customer Master"])
protected_router.include_router(material.router, prefix="/master/materials", tags=["Material Master"])
protected_router.include_router(sales.router, prefix="/sales", tags=["Sales Management"])
protected_router.include_router(logistics.router, prefix="/logistics", tags=["Logistics"])
protected_router.include_router(finance.router, prefix="/finance", tags=["Finance"])
protected_router.include_router(report.router, prefix="/reports", tags=["Reports"])
protected_router.include_router(assistant.router, prefix="/assistant", tags=["Assistant"])
api_router.include_router(protected_router)
