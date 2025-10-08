"""
Pruning Config Business Logic Service.
Handles all prune configuration-related business operations independent of HTTP concerns.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Union, cast
from sqlalchemy.orm import Session

from borgitory.models.database import PruneConfig, Repository
from borgitory.models.schemas import PruneConfigCreate, PruneConfigUpdate
from borgitory.constants.retention import RetentionFieldHandler, RetentionConfigProtocol

logger = logging.getLogger(__name__)


@dataclass
class PruneConfigOperationResult:
    """Result of a prune configuration operation (create, update, enable, disable)."""

    success: bool
    config: Optional[PruneConfig] = None
    error_message: Optional[str] = None

    @property
    def is_error(self) -> bool:
        """Check if the operation resulted in an error."""
        return not self.success or self.error_message is not None

    def raise_if_error(self) -> None:
        """Raise an exception if the operation failed."""
        if self.is_error:
            raise ValueError(self.error_message or "Prune config operation failed")


@dataclass
class PruneConfigDeleteResult:
    """Result of prune configuration deletion operations."""

    success: bool
    config_name: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def is_error(self) -> bool:
        """Check if the deletion resulted in an error."""
        return not self.success or self.error_message is not None


class PruneService:
    """Service for prune configuration business logic operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_prune_configs(self, skip: int = 0, limit: int = 100) -> List[PruneConfig]:
        """Get all prune configurations with pagination."""
        return self.db.query(PruneConfig).offset(skip).limit(limit).all()

    def get_prune_config_by_id(self, config_id: int) -> Optional[PruneConfig]:
        """Get a prune configuration by ID."""
        config = self.db.query(PruneConfig).filter(PruneConfig.id == config_id).first()
        if not config:
            raise Exception(f"Prune configuration with id {config_id} not found")
        return config

    def create_prune_config(
        self, prune_config: PruneConfigCreate
    ) -> PruneConfigOperationResult:
        """
        Create a new prune configuration.

        Returns:
            tuple: (success, config_or_none, error_message_or_none)
        """
        try:
            existing = (
                self.db.query(PruneConfig)
                .filter(PruneConfig.name == prune_config.name)
                .first()
            )
            if existing:
                return PruneConfigOperationResult(
                    success=False,
                    error_message="A prune policy with this name already exists",
                )

            db_config = PruneConfig()
            db_config.name = prune_config.name
            db_config.strategy = prune_config.strategy
            db_config.keep_within_days = prune_config.keep_within_days
            RetentionFieldHandler.copy_fields(
                cast(RetentionConfigProtocol, prune_config),
                cast(RetentionConfigProtocol, db_config),
            )
            db_config.show_list = prune_config.show_list
            db_config.show_stats = prune_config.show_stats
            db_config.save_space = prune_config.save_space
            db_config.enabled = True

            self.db.add(db_config)
            self.db.commit()
            self.db.refresh(db_config)

            return PruneConfigOperationResult(success=True, config=db_config)

        except Exception as e:
            self.db.rollback()
            return PruneConfigOperationResult(
                success=False,
                error_message=f"Failed to create prune configuration: {str(e)}",
            )

    def update_prune_config(
        self, config_id: int, prune_config_update: PruneConfigUpdate
    ) -> PruneConfigOperationResult:
        """
        Update an existing prune configuration.

        Returns:
            tuple: (success, config_or_none, error_message_or_none)
        """
        try:
            config = (
                self.db.query(PruneConfig).filter(PruneConfig.id == config_id).first()
            )
            if not config:
                return PruneConfigOperationResult(
                    success=False, error_message="Prune configuration not found"
                )

            update_dict = prune_config_update.model_dump(exclude_unset=True)
            if "name" in update_dict and update_dict["name"] != config.name:
                existing = (
                    self.db.query(PruneConfig)
                    .filter(
                        PruneConfig.name == update_dict["name"],
                        PruneConfig.id != config_id,
                    )
                    .first()
                )
                if existing:
                    return PruneConfigOperationResult(
                        success=False,
                        error_message="A prune policy with this name already exists",
                    )

            for field, value in update_dict.items():
                if hasattr(config, field):
                    setattr(config, field, value)

            self.db.commit()
            self.db.refresh(config)

            return PruneConfigOperationResult(success=True, config=config)

        except Exception as e:
            self.db.rollback()
            return PruneConfigOperationResult(
                success=False,
                error_message=f"Failed to update prune configuration: {str(e)}",
            )

    def enable_prune_config(self, prune_config_id: int) -> PruneConfigOperationResult:
        """
        Enable a prune configuration.

        Returns:
            tuple: (success, config_or_none, error_message_or_none)
        """
        try:
            config = (
                self.db.query(PruneConfig)
                .filter(PruneConfig.id == prune_config_id)
                .first()
            )
            if not config:
                return PruneConfigOperationResult(
                    success=False, error_message="Prune configuration not found"
                )

            config.enabled = True
            self.db.commit()
            self.db.refresh(config)

            return PruneConfigOperationResult(success=True, config=config)

        except Exception as e:
            self.db.rollback()
            return PruneConfigOperationResult(
                success=False,
                error_message=f"Failed to enable prune configuration: {str(e)}",
            )

    def disable_prune_config(self, prune_config_id: int) -> PruneConfigOperationResult:
        """
        Disable a prune configuration.

        Returns:
            tuple: (success, config_or_none, error_message_or_none)
        """
        try:
            config = (
                self.db.query(PruneConfig)
                .filter(PruneConfig.id == prune_config_id)
                .first()
            )
            if not config:
                return PruneConfigOperationResult(
                    success=False, error_message="Prune configuration not found"
                )

            config.enabled = False
            self.db.commit()
            self.db.refresh(config)

            return PruneConfigOperationResult(success=True, config=config)

        except Exception as e:
            self.db.rollback()
            return PruneConfigOperationResult(
                success=False,
                error_message=f"Failed to disable prune configuration: {str(e)}",
            )

    def delete_prune_config(self, prune_config_id: int) -> PruneConfigDeleteResult:
        """
        Delete a prune configuration.

        Returns:
            tuple: (success, config_name_or_none, error_message_or_none)
        """
        try:
            config = (
                self.db.query(PruneConfig)
                .filter(PruneConfig.id == prune_config_id)
                .first()
            )
            if not config:
                return PruneConfigDeleteResult(
                    success=False, error_message="Prune configuration not found"
                )

            config_name = config.name
            self.db.delete(config)
            self.db.commit()

            return PruneConfigDeleteResult(success=True, config_name=config_name)

        except Exception as e:
            self.db.rollback()
            return PruneConfigDeleteResult(
                success=False,
                error_message=f"Failed to delete prune configuration: {str(e)}",
            )

    def get_configs_with_descriptions(
        self,
    ) -> List[Dict[str, Union[str, int, bool, None]]]:
        """
        Get all prune configurations with computed description fields.

        Returns:
            List of dictionaries with config data and computed fields
        """
        try:
            prune_configs_raw = self.get_prune_configs()

            processed_configs = []
            for config in prune_configs_raw:
                if config.strategy == "simple":
                    description = f"Keep archives within {config.keep_within_days} days"
                else:
                    description = RetentionFieldHandler.build_description(config)

                processed_config = config.__dict__.copy()
                processed_config["description"] = description
                processed_configs.append(processed_config)

            return processed_configs

        except Exception as e:
            logger.error(f"Error getting configs with descriptions: {str(e)}")
            return []

    def get_form_data(self) -> Dict[str, List[Repository]]:
        """Get data needed for prune form."""
        try:
            repositories = self.db.query(Repository).all()

            return {
                "repositories": repositories,
            }
        except Exception as e:
            logger.error(f"Error getting form data: {str(e)}")
            return {
                "repositories": [],
            }
