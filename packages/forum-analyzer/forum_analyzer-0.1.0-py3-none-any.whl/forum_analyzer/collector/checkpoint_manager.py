"""Checkpoint manager for resumable scraping."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from .models import Checkpoint

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manage scraping checkpoints for resumability."""

    def __init__(
        self,
        session: Session,
        checkpoint_dir: Optional[Path] = None,
    ):
        """Initialize checkpoint manager.

        Args:
            session: Database session
            checkpoint_dir: Directory for checkpoint files (optional)
        """
        self.session = session
        self.checkpoint_dir = checkpoint_dir
        if checkpoint_dir:
            checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        category_id: int,
        checkpoint_type: str,
        last_page: Optional[int] = None,
        last_topic_id: Optional[int] = None,
        total_processed: int = 0,
        status: str = "in_progress",
        error_message: Optional[str] = None,
    ) -> Checkpoint:
        """Save a checkpoint to the database.

        Args:
            category_id: Category ID
            checkpoint_type: Type ('category_page' or 'topic')
            last_page: Last processed page number
            last_topic_id: Last processed topic ID
            total_processed: Total items processed
            status: Checkpoint status
            error_message: Error message if any

        Returns:
            Created or updated checkpoint
        """
        # Find existing checkpoint
        checkpoint = (
            self.session.query(Checkpoint)
            .filter_by(
                category_id=category_id,
                checkpoint_type=checkpoint_type,
            )
            .order_by(Checkpoint.id.desc())
            .first()
        )

        if checkpoint and checkpoint.status == "in_progress":
            # Update existing checkpoint
            checkpoint.last_page = last_page
            checkpoint.last_topic_id = last_topic_id
            checkpoint.total_processed = total_processed
            checkpoint.status = status
            checkpoint.error_message = error_message
            checkpoint.updated_at = datetime.utcnow()
        else:
            # Create new checkpoint
            checkpoint = Checkpoint(
                category_id=category_id,
                checkpoint_type=checkpoint_type,
                last_page=last_page,
                last_topic_id=last_topic_id,
                total_processed=total_processed,
                status=status,
                error_message=error_message,
            )
            self.session.add(checkpoint)

        self.session.commit()
        logger.info(
            f"Saved checkpoint: category={category_id}, "
            f"type={checkpoint_type}, status={status}"
        )

        # Save to file if directory is set
        if self.checkpoint_dir:
            self._save_to_file(checkpoint)

        return checkpoint

    def get_checkpoint(
        self,
        category_id: int,
        checkpoint_type: str,
    ) -> Optional[Checkpoint]:
        """Get the latest checkpoint for a category.

        Args:
            category_id: Category ID
            checkpoint_type: Checkpoint type

        Returns:
            Latest checkpoint or None
        """
        checkpoint = (
            self.session.query(Checkpoint)
            .filter_by(
                category_id=category_id,
                checkpoint_type=checkpoint_type,
                status="in_progress",
            )
            .order_by(Checkpoint.id.desc())
            .first()
        )

        return checkpoint

    def clear_checkpoint(
        self,
        category_id: int,
        checkpoint_type: str,
    ) -> None:
        """Clear checkpoint by marking as completed.

        Args:
            category_id: Category ID
            checkpoint_type: Checkpoint type
        """
        checkpoint = self.get_checkpoint(category_id, checkpoint_type)
        if checkpoint:
            checkpoint.status = "completed"
            checkpoint.updated_at = datetime.utcnow()
            self.session.commit()
            logger.info(
                f"Cleared checkpoint: category={category_id}, "
                f"type={checkpoint_type}"
            )

    def _save_to_file(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to JSON file.

        Args:
            checkpoint: Checkpoint to save
        """
        if not self.checkpoint_dir:
            return

        filename = (
            f"checkpoint_{checkpoint.category_id}_" f"{checkpoint.checkpoint_type}.json"
        )
        filepath = self.checkpoint_dir / filename

        data = {
            "id": checkpoint.id,
            "category_id": checkpoint.category_id,
            "checkpoint_type": checkpoint.checkpoint_type,
            "last_page": checkpoint.last_page,
            "last_topic_id": checkpoint.last_topic_id,
            "total_processed": checkpoint.total_processed,
            "status": checkpoint.status,
            "error_message": checkpoint.error_message,
            "created_at": (
                checkpoint.created_at.isoformat() if checkpoint.created_at else None
            ),
            "updated_at": (
                checkpoint.updated_at.isoformat() if checkpoint.updated_at else None
            ),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Saved checkpoint to file: {filepath}")

    def load_from_file(
        self,
        category_id: int,
        checkpoint_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Load checkpoint from JSON file.

        Args:
            category_id: Category ID
            checkpoint_type: Checkpoint type

        Returns:
            Checkpoint data or None
        """
        if not self.checkpoint_dir:
            return None

        filename = f"checkpoint_{category_id}_{checkpoint_type}.json"
        filepath = self.checkpoint_dir / filename

        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            data = json.load(f)

        logger.debug(f"Loaded checkpoint from file: {filepath}")
        return data
