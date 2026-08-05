from sqlalchemy.orm import Session
from app.models.customer import BusinessPartner
from app.schemas.customer import BusinessPartnerCreate, BusinessPartnerUpdate
from typing import List, Optional

class CustomerService:
    @staticmethod
    def get_partners(db: Session, skip: int = 0, limit: int = 100) -> List[BusinessPartner]:
        return db.query(BusinessPartner).offset(skip).limit(limit).all()

    @staticmethod
    def count_partners(db: Session) -> int:
        return db.query(BusinessPartner).count()

    @staticmethod
    def get_partner(db: Session, bp_id: str) -> Optional[BusinessPartner]:
        return db.query(BusinessPartner).filter(BusinessPartner.bp_id == bp_id).first()

    @staticmethod
    def create_partner(db: Session, partner_in: BusinessPartnerCreate) -> BusinessPartner:
        db_partner = BusinessPartner(**partner_in.model_dump())
        db.add(db_partner)
        db.commit()
        db.refresh(db_partner)
        return db_partner

    @staticmethod
    def update_partner(db: Session, bp_id: str, partner_in: BusinessPartnerUpdate) -> Optional[BusinessPartner]:
        db_partner = CustomerService.get_partner(db, bp_id)
        if not db_partner:
            return None
        
        update_data = partner_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_partner, field, value)
        
        db.commit()
        db.refresh(db_partner)
        return db_partner

    @staticmethod
    def delete_partner(db: Session, bp_id: str) -> bool:
        db_partner = CustomerService.get_partner(db, bp_id)
        if not db_partner:
            return False

        # Business partners are referenced by sales, finance, and contact rows.
        # Marking the record inactive preserves those historical references.
        db_partner.status = "INACTIVE"
        if not db_partner.block_reason:
            db_partner.block_reason = "Soft deleted"
        db.commit()
        return True

customer_service = CustomerService()
