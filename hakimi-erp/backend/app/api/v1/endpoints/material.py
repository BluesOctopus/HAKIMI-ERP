from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.material import Material, MaterialCreate, MaterialUpdate, PricingCondition
from app.schemas.base import ResponseModel, PaginatedData, Pagination
from app.services.material_service import material_service

router = APIRouter()


# ---- Pricing Conditions (MUST be before /{material_id}) ----
@router.get("/pricing-conditions", response_model=ResponseModel[PaginatedData[PricingCondition]])
def read_pricing_conditions(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    condition_type: str = Query(None),
    material_id: str = Query(None),
    bp_id: str = Query(None),
):
    skip = (page - 1) * page_size
    items = material_service.get_pricing_conditions(
        db, skip=skip, limit=page_size,
        condition_type=condition_type, material_id=material_id, bp_id=bp_id
    )
    total = material_service.count_pricing_conditions(
        db, condition_type=condition_type, material_id=material_id, bp_id=bp_id
    )
    return ResponseModel(data=PaginatedData(
        items=items,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size if total else 0,
        )
    ))


# ---- Sales Organizations (MUST be before /{material_id}) ----
@router.get("/sales-organizations")
def read_sales_organizations(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    from app.models.material import SalesOrganization
    skip = (page - 1) * page_size
    items = db.query(SalesOrganization).offset(skip).limit(page_size).all()
    total = db.query(SalesOrganization).count()
    result = []
    for item in items:
        result.append({
            "sales_org_id": item.sales_org_id,
            "description": item.description,
            "distribution_channel": item.distribution_channel,
            "division": item.division,
            "currency": item.currency or "CNY",
            "country": item.country or "CN",
            "status": item.status or "ACTIVE",
        })
    return ResponseModel(data=PaginatedData(
        items=result,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size if total else 0,
        )
    ))


# ---- Materials CRUD ----
@router.get("/", response_model=ResponseModel[PaginatedData[Material]])
def read_materials(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    skip = (page - 1) * page_size
    materials = material_service.get_materials(db, skip=skip, limit=page_size)
    total = material_service.count_materials(db)
    return ResponseModel(
        data=PaginatedData(
            items=materials,
            pagination=Pagination(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=(total + page_size - 1) // page_size if total else 0,
            )
        )
    )

@router.post("/", response_model=ResponseModel[Material], status_code=status.HTTP_201_CREATED)
def create_material(
    *,
    db: Session = Depends(get_db),
    material_in: MaterialCreate
):
    db_material = material_service.get_material(db, material_id=material_in.material_id)
    if db_material:
        raise HTTPException(status_code=400, detail="Material with this ID already exists.")
    material = material_service.create_material(db, material_in=material_in)
    return ResponseModel(data=material)

@router.get("/{material_id}", response_model=ResponseModel[Material])
def read_material(material_id: str, db: Session = Depends(get_db)):
    material = material_service.get_material(db, material_id=material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return ResponseModel(data=material)

@router.patch("/{material_id}", response_model=ResponseModel[Material])
def update_material(material_id: str, material_in: MaterialUpdate, db: Session = Depends(get_db)):
    material = material_service.update_material(db, material_id=material_id, material_in=material_in)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return ResponseModel(data=material)

@router.delete("/{material_id}", response_model=ResponseModel[bool])
def delete_material(material_id: str, db: Session = Depends(get_db)):
    success = material_service.delete_material(db, material_id=material_id)
    if not success:
        raise HTTPException(status_code=404, detail="Material not found")
    return ResponseModel(data=True)
