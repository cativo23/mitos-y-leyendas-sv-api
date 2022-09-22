from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.common.services import CRUDBaseService
from .country_service import country as country_service
from ..models import Character
from ..schemas import CharacterCreate, CharacterUpdate
from ...common.exceptions import ExistsException, NotFoundException, InactiveException


class CharacterService(CRUDBaseService[Character, CharacterCreate, CharacterUpdate]):

    def search(self, db: Session, *, term: str) -> Any:
        """
            Search characters by name.
        """
        return db.query(self.model).filter(self.model.name.ilike(f"%{term}%")).all()

    def create(self, db: Session, *, obj_in: CharacterCreate, image_path: str = None) -> Character:

        self.validate_country(db, obj_in.country_id)

        existing_character = self.get_by_name(db, name=obj_in.name)

        if existing_character:
            raise ExistsException(
                name=obj_in.name,
            )

        obj_in.image = image_path

        return super().create(db, obj_in=obj_in)

    def update(
            self, db: Session, *, db_obj: Character, obj_in: Union[CharacterUpdate, Dict[str, Any]]
    ) -> Character:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        print(update_data)

        self.validate_country(db, update_data.get('country_id'))

        existing_character = self.get_by_name(db, name=obj_in.name, exclude=db_obj.id)

        if existing_character:
            raise ExistsException(
                name=obj_in.name,
            )

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_by_name(self, db, name: str, exclude: int = None) -> Optional[Character]:
        """
         Get for a character by name.
         """
        if exclude:
            return db.query(self.model).filter(self.model.name == name).filter(self.model.id != exclude).first()

        return db.query(self.model).filter(self.model.name == name).first()

    @staticmethod
    def validate_country(db, country_id: int):
        country = country_service.validate_existence(db, item_id=country_id)

        if not country:
            raise NotFoundException(
                name="Country",
            )

        if not country.status:
            raise InactiveException(
                name="Country",
            )


character = CharacterService(Character)
