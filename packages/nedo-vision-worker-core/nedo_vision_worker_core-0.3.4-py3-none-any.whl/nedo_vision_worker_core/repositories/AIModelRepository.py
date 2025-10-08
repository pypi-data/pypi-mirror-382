import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..database.DatabaseManager import DatabaseManager
from ..models.ai_model import AIModelEntity

class AIModelRepository:
    """Handles storage of AI Models into SQLite using SQLAlchemy."""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("default")

    def get_models(self) -> list:
        """
        Retrieves all AI models from the database.

        Returns:
            list: A list of AIModelEntity objects.
        """
        try:
            self.session.expire_all()
            models = self.session.query(AIModelEntity).all()
            
            for model in models:
                self.session.expunge(model)

            return models
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving models: {e}")
            return []

    def get_model(self, model_id: str) -> AIModelEntity | None:
        """
        Retrieves a single AI model by its ID.

        Args:
            model_id: The ID of the model to retrieve.

        Returns:
            An AIModelEntity object or None if not found.
        """
        try:
            self.session.expire_all()
            model = self.session.query(AIModelEntity).filter_by(id=model_id).first()
            if model:
                self.session.expunge(model)
            return model
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving model {model_id}: {e}")
            return None