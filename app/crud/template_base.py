from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class TemplateCRUDBase:
    """
    A CRUD base class that uses raw, templatized SQL queries.

    This implementation is for comparison and benchmarking against the
    standard SQLAlchemy ORM approach.

    NOTE: This approach is generally NOT recommended as it bypasses
    many of the safety and convenience features of the ORM, such as
    model validation, relationship handling, and database portability.
    It can also be more prone to SQL injection if not handled carefully,
    although using bind parameters (like `:id`) still provides protection.
    """

    def __init__(self, table_name: str):
        """
        Initialize the CRUD object with the database table name.

        :param table_name: The name of the database table.
        """
        self.table_name = table_name

    def get(self, db: Session, id: Any) -> Optional[Dict]:
        """Fetch a single record by its ID."""
        query = text(f"SELECT * FROM {self.table_name} WHERE id = :id")
        result = db.execute(query, {"id": id}).fetchone()
        return dict(result._mapping) if result else None

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Dict]:
        """Fetch multiple records with pagination."""
        query = text(f"SELECT * FROM {self.table_name} ORDER BY id LIMIT :limit OFFSET :skip")
        result = db.execute(query, {"limit": limit, "skip": skip}).fetchall()
        return [dict(row._mapping) for row in result]

    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> Dict:
        """Create a new record."""
        columns = ", ".join(obj_in.keys())
        placeholders = ", ".join(f":{key}" for key in obj_in.keys())
        
        # For SQLite compatibility, use INSERT and then SELECT the created record
        insert_query = text(
            f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        )
        result = db.execute(insert_query, obj_in)
        db.commit()
        
        # Get the ID of the inserted record
        inserted_id = result.lastrowid
        
        # Fetch and return the created record
        return self.get(db, id=inserted_id)

    def update(self, db: Session, *, id: Any, obj_in: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing record by its ID."""
        if not obj_in:
            # If there's nothing to update, fetch and return the current state.
            return self.get(db, id=id)

        set_clause = ", ".join(f"{key} = :{key}" for key in obj_in.keys())
        params = obj_in.copy()
        params["id"] = id

        # For SQLite compatibility, use UPDATE and then SELECT the updated record
        update_query = text(
            f"UPDATE {self.table_name} SET {set_clause} WHERE id = :id"
        )
        result = db.execute(update_query, params)
        db.commit()
        
        # Check if any rows were affected
        if result.rowcount == 0:
            return None
            
        # Fetch and return the updated record
        return self.get(db, id=id)

    def remove(self, db: Session, *, id: Any) -> Optional[Dict]:
        """Delete a record by its ID."""
        # For SQLite compatibility, fetch the record before deletion
        record_to_delete = self.get(db, id=id)
        if not record_to_delete:
            return None
            
        delete_query = text(f"DELETE FROM {self.table_name} WHERE id = :id")
        result = db.execute(delete_query, {"id": id})
        db.commit()
        
        # Return the deleted record if deletion was successful
        return record_to_delete if result.rowcount > 0 else None
