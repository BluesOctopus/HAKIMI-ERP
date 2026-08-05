from sqlalchemy.orm import Session
from app.models.material import Material, PricingCondition
from app.schemas.material import MaterialCreate, MaterialUpdate
from typing import List, Optional

class MaterialService:
    @staticmethod
    def get_materials(db: Session, skip: int = 0, limit: int = 100) -> List[Material]:
        return db.query(Material).offset(skip).limit(limit).all()

    @staticmethod
    def count_materials(db: Session) -> int:
        return db.query(Material).count()

    @staticmethod
    def get_material(db: Session, material_id: str) -> Optional[Material]:
        return db.query(Material).filter(Material.material_id == material_id).first()

    @staticmethod
    def create_material(db: Session, material_in: MaterialCreate) -> Material:
        db_material = Material(**material_in.model_dump())
        db.add(db_material)
        db.commit()
        db.refresh(db_material)
        return db_material

    @staticmethod
    def update_material(db: Session, material_id: str, material_in: MaterialUpdate) -> Optional[Material]:
        db_material = MaterialService.get_material(db, material_id)
        if not db_material:
            return None
        update_data = material_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_material, field, value)
        db.commit()
        db.refresh(db_material)
        return db_material

    @staticmethod
    def delete_material(db: Session, material_id: str) -> bool:
        db_material = MaterialService.get_material(db, material_id)
        if not db_material:
            return False
        # Materials are referenced by sales, delivery, invoice, and pricing rows.
        # Keep the row for historical documents and make it unavailable instead.
        db_material.status = "INACTIVE"
        db.commit()
        return True

    @staticmethod
    def get_pricing_conditions(db: Session, skip: int = 0, limit: int = 100,
                               condition_type: Optional[str] = None,
                               material_id: Optional[str] = None,
                               bp_id: Optional[str] = None) -> List[PricingCondition]:
        q = db.query(PricingCondition)
        if condition_type:
            q = q.filter(PricingCondition.condition_type == condition_type)
        if material_id:
            q = q.filter(PricingCondition.material_id == material_id)
        if bp_id:
            q = q.filter(PricingCondition.bp_id == bp_id)
        return q.offset(skip).limit(limit).all()

    @staticmethod
    def count_pricing_conditions(db: Session, condition_type: Optional[str] = None,
                                 material_id: Optional[str] = None,
                                 bp_id: Optional[str] = None) -> int:
        q = db.query(PricingCondition)
        if condition_type:
            q = q.filter(PricingCondition.condition_type == condition_type)
        if material_id:
            q = q.filter(PricingCondition.material_id == material_id)
        if bp_id:
            q = q.filter(PricingCondition.bp_id == bp_id)
        return q.count()

material_service = MaterialService()
