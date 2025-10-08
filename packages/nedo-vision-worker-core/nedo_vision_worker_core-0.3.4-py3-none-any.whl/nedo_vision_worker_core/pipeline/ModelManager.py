import logging
from typing import Dict, Optional, Set

from ..repositories.AIModelRepository import AIModelRepository
from ..detection.BaseDetector import BaseDetector
from ..detection.YOLODetector import YOLODetector
from ..detection.RFDETRDetector import RFDETRDetector
from ..models.ai_model import AIModelEntity


class ModelManager:
    """Manages loading and caching of AI models to avoid redundant loads."""

    def __init__(self):
        self._detector_cache: Dict[str, BaseDetector] = {}
        self._model_repo = AIModelRepository()
        logging.info("🤖 ModelManager initialized.")

    def get_detector(self, model_id: str) -> Optional[BaseDetector]:
        """
        Retrieves a detector by its model ID.

        This method implements a lazy-loading and cache-validation strategy:
        1. It fetches the latest model metadata from the database.
        2. If a detector is already cached, it validates its metadata against the DB version.
        3. If the cached version is stale (e.g., version or classes changed), it's evicted.
        4. If no detector is cached or the cache was stale, it loads the detector on-demand.
        """
        if not model_id:
            return None

        # 1. Fetch the current model state from the database
        db_model: AIModelEntity = self._model_repo.get_model(model_id)
        if not db_model:
            # If the model doesn't exist in DB, ensure it's not in cache either
            if model_id in self._detector_cache:
                logging.info(f"🧹 Removing detector for deleted model {model_id} from cache.")
                del self._detector_cache[model_id]
            return None

        # 2. Check if a detector is cached
        if model_id in self._detector_cache:
            cached_detector = self._detector_cache[model_id]
            
            # 3. Check if the cached version is stale
            if self._has_metadata_changed(cached_detector.metadata, db_model):
                logging.info(f"Reloading detector for model {model_id} due to metadata changes.")
                del self._detector_cache[model_id]
                # Fall through to load the new version
            else:
                # Cache is fresh, return it
                logging.debug(f"🧠 Detector for model {model_id} found in cache and is fresh.")
                return cached_detector

        # 4. If not cached or was stale, load it now
        return self._load_and_cache_detector(model_id, db_model)

    def _load_and_cache_detector(self, model_id: str, db_model: AIModelEntity) -> Optional[BaseDetector]:
        """Creates a detector from a DB model entity and caches it."""
        logging.info(f"🔄 Loading model {model_id} (version: {db_model.version}) from database to create detector...")

        # Check model readiness before attempting to load
        if not db_model.is_ready_for_use():
            if db_model.is_downloading():
                logging.warning(f"⏳ Model {model_id} is still downloading. Skipping detector load.")
            elif db_model.has_download_failed():
                logging.error(f"❌ Model {model_id} download failed: {db_model.download_error}")
            else:
                logging.warning(f"⚠️ Model {model_id} is not ready for use (status: {db_model.download_status})")
            return None

        detector_type = db_model.type.lower()
        detector: Optional[BaseDetector] = None
        try:
            if detector_type == "yolo":
                detector = YOLODetector(db_model)
            elif detector_type == "rf_detr":
                detector = RFDETRDetector(db_model)
            else:
                raise ValueError(f"Unsupported model type: {detector_type}")

            if detector and detector.model is not None:
                self._detector_cache[model_id] = detector
                logging.info(f"✅ Detector for model {model_id} loaded and cached successfully.")
                return detector
            else:
                logging.error(f"❌ Failed to load detector for model: {db_model.name}")
                return None

        except Exception as e:
            logging.error(f"❌ Error creating detector for model {db_model.name}: {e}")
            return None

    def _has_metadata_changed(self, cached_model: AIModelEntity, db_model: AIModelEntity) -> bool:
        """Check if critical model metadata has changed."""
        if cached_model.version != db_model.version:
            logging.info(
                f"🔄 Model {db_model.id} version changed "
                f"({cached_model.version} -> {db_model.version})."
            )
            return True

        # Compare classes
        cached_classes = set(cached_model.get_classes() or [])
        db_classes = set(db_model.get_classes() or [])
        if cached_classes != db_classes:
            logging.info(f"🔄 Model {db_model.id} classes changed.")
            return True
        
        # Compare PPE class groups
        cached_ppe_groups = cached_model.get_ppe_class_groups() or {}
        db_ppe_groups = db_model.get_ppe_class_groups() or {}
        if cached_ppe_groups != db_ppe_groups:
            logging.info(f"🔄 Model {db_model.id} PPE groups changed.")
            return True
        
        # Compare main class
        if cached_model.get_main_class() != db_model.get_main_class():
            logging.info(f"🔄 Model {db_model.id} main class changed.")
            return True
        
        return False

    def sync_cache(self, active_model_ids: Set[str]):
        """
        Removes detectors from the cache if their corresponding models are no longer in the database
        or are not being used by any active pipeline.
        """
        cached_ids = set(self._detector_cache.keys())
        stale_ids = cached_ids - active_model_ids
        
        for model_id in stale_ids:
            del self._detector_cache[model_id]
            logging.info(f"🧹 Removed unused detector for model {model_id} from cache.")

    def clear_cache(self):
        """Clears the detector cache."""
        logging.info("🧹 Clearing all detectors from cache.")
        self._detector_cache.clear()
