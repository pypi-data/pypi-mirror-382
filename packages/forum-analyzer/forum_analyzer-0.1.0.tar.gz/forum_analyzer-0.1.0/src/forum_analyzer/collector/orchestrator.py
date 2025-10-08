"""
Data collection orchestrator for Discourse Forum.

This module ties together the API client, database models, and
checkpoint manager to orchestrate the collection of forum data with
proper error handling, progress reporting, and checkpoint support for
resumable operations.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

from .api_client import ForumAPIClient
from .models import Base, Category, Topic, User, Post
from .checkpoint_manager import CheckpointManager
from ..config.settings import Settings, get_settings

logger = logging.getLogger(__name__)
console = Console()


class CollectionOrchestrator:
    """Orchestrates the collection of forum data with checkpoint support."""

    def __init__(
        self,
        api_client: ForumAPIClient,
        db_session: Session,
        checkpoint_mgr: CheckpointManager,
        settings: Settings,
    ):
        """
        Initialize the orchestrator.

        Args:
            api_client: Configured ForumAPIClient instance
            db_session: SQLAlchemy database session
            checkpoint_mgr: CheckpointManager instance
            settings: Application settings
        """
        self.api_client = api_client
        self.db_session = db_session
        self.checkpoint_mgr = checkpoint_mgr
        self.settings = settings
        self.stats = {
            "topics_processed": 0,
            "posts_collected": 0,
            "users_added": 0,
            "topics_updated": 0,
            "posts_added": 0,
        }

    async def collect_category(
        self,
        category_id: int,
        full_fetch: bool = True,
        page_limit: Optional[int] = None,
    ) -> Dict[str, int]:
        """
        Collect all topics and posts from a category.

        Args:
            category_id: Category ID (e.g., 18)
            full_fetch: If True, fetch all pages; if False, incremental update
            page_limit: Optional limit on number of pages to collect
                (for testing)

        Returns:
            Dictionary with collection statistics

        Raises:
            Exception: For fatal errors after saving checkpoint
        """
        logger.info(
            f"Starting {'full' if full_fetch else 'incremental'} collection "
            f"for category ID: {category_id}"
        )

        try:
            # Fetch category metadata first
            category_metadata = await self.api_client.fetch_category_metadata(
                category_id
            )
            await self._store_category(category_metadata)

            if full_fetch:
                await self._full_collection(category_id, page_limit)
            else:
                await self._incremental_update(category_id)

            # Mark checkpoint as completed
            self.checkpoint_mgr.clear_checkpoint(
                category_id=category_id,
                checkpoint_type="category_page",
            )

            logger.info(f"Collection completed for category ID: {category_id}")
            self._log_statistics()

            return self.stats

        except Exception as e:
            logger.error(f"Fatal error during collection: {e}", exc_info=True)
            # Save checkpoint with error status
            self.checkpoint_mgr.save_checkpoint(
                category_id=category_id,
                checkpoint_type="category_page",
                status="error",
                error_message=str(e),
            )
            raise

    async def _full_collection(
        self, category_id: int, page_limit: Optional[int] = None
    ) -> None:
        """
        Perform full collection of all topics in a category.

        Args:
            category_id: Category ID
            page_limit: Optional limit on number of pages to collect
        """
        # Load checkpoint if resuming
        checkpoint = self.checkpoint_mgr.get_checkpoint(
            category_id=category_id,
            checkpoint_type="category_page",
        )

        current_page = checkpoint.last_page if checkpoint else 0
        processed_count = checkpoint.total_processed if checkpoint else 0

        logger.info(
            f"Resuming from page {current_page}, "
            f"{processed_count} topics already processed"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            # Create progress tasks
            page_task = progress.add_task(
                "[cyan]Fetching pages...", total=None
            )
            topic_task = progress.add_task(
                "[green]Processing topics...", total=processed_count
            )

            page = current_page
            has_more = True
            topics_since_checkpoint = 0

            while has_more:
                try:
                    # Fetch category page
                    progress.update(
                        page_task, description=f"[cyan]Fetching page {page}..."
                    )

                    category_data = await self.api_client.fetch_category_page(
                        category_id, page=page
                    )

                    if not category_data:
                        logger.warning(f"No data returned for page {page}")
                        break

                    topic_list = category_data.get("topic_list", {})
                    topics = topic_list.get("topics", [])

                    if not topics:
                        logger.info(f"No more topics found at page {page}")
                        break

                    # Update progress total
                    progress.update(
                        topic_task, total=progress.tasks[1].total + len(topics)
                    )

                    # Process each topic
                    for topic_summary in topics:
                        topic_id = topic_summary.get("id")
                        if not topic_id:
                            continue

                        try:
                            await self._collect_topic(topic_id, category_id)
                            processed_count += 1
                            topics_since_checkpoint += 1
                            self.stats["topics_processed"] += 1
                            progress.update(topic_task, advance=1)

                            # Save checkpoint every 10 topics
                            if topics_since_checkpoint >= 10:
                                self.checkpoint_mgr.save_checkpoint(
                                    category_id=category_id,
                                    checkpoint_type="category_page",
                                    last_page=page,
                                    total_processed=processed_count,
                                    status="in_progress",
                                )
                                topics_since_checkpoint = 0

                        except Exception as e:
                            logger.error(
                                f"Error processing topic {topic_id}: {e}",
                                exc_info=True,
                            )
                            # Continue with next topic

                    # Save checkpoint after each page
                    self.checkpoint_mgr.save_checkpoint(
                        category_id=category_id,
                        checkpoint_type="category_page",
                        last_page=page,
                        total_processed=processed_count,
                        status="in_progress",
                    )
                    topics_since_checkpoint = 0

                    # Check if page limit reached
                    if page_limit and page + 1 >= page_limit:
                        logger.info(
                            "page_limit_reached",
                            page=page + 1,
                            limit=page_limit,
                        )
                        break

                    # Check if there are more pages
                    has_more = topic_list.get("more_topics_url") is not None
                    page += 1

                except Exception as e:
                    logger.error(
                        f"Error fetching page {page}: {e}", exc_info=True
                    )
                    # Save checkpoint and stop
                    self.checkpoint_mgr.save_checkpoint(
                        category_id=category_id,
                        checkpoint_type="category_page",
                        last_page=page,
                        total_processed=processed_count,
                        status="error",
                        error_message=str(e),
                    )
                    break

    async def _incremental_update(self, category_id: int) -> None:
        """
        Update existing data with new posts/topics since last run.

        Args:
            category_id: Category ID
        """
        logger.info(f"Starting incremental update for category {category_id}")

        # Fetch first page to get recent topics
        category_data = await self.api_client.fetch_category_page(
            category_id, page=0
        )

        if not category_data:
            logger.warning("No data returned for incremental update")
            return

        topics = category_data.get("topic_list", {}).get("topics", [])

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[green]Checking for updates...", total=len(topics)
            )

            for topic_summary in topics:
                topic_id = topic_summary.get("id")
                if not topic_id:
                    continue

                # Check if topic exists and has new activity
                existing_topic = self.db_session.get(Topic, topic_id)

                api_last_posted = topic_summary.get("last_posted_at")
                if api_last_posted:
                    api_last_posted_dt = datetime.fromisoformat(
                        api_last_posted.replace("Z", "+00:00")
                    )

                    if existing_topic and existing_topic.last_posted_at:
                        # Only fetch if there's new activity
                        # Ensure timezone-aware comparison
                        db_last_posted = existing_topic.last_posted_at
                        if db_last_posted.tzinfo is None:
                            db_last_posted = db_last_posted.replace(
                                tzinfo=timezone.utc
                            )

                        if api_last_posted_dt <= db_last_posted:
                            progress.update(task, advance=1)
                            continue

                try:
                    # Fetch topic with new/updated posts
                    await self._collect_topic(topic_id, category_id)

                    if existing_topic:
                        self.stats["topics_updated"] += 1
                    else:
                        self.stats["topics_processed"] += 1

                    progress.update(task, advance=1)

                except Exception as e:
                    logger.error(
                        f"Error updating topic {topic_id}: {e}", exc_info=True
                    )
                    progress.update(task, advance=1)

    async def _collect_topic(self, topic_id: int, category_id: int) -> None:
        """
        Fetch and store a single topic with all posts.

        Args:
            topic_id: Topic ID to fetch
            category_id: Category ID this topic belongs to
        """
        logger.debug(f"Collecting topic {topic_id}")

        try:
            # Fetch full topic details
            topic_data = await self.api_client.fetch_topic(topic_id)

            if not topic_data:
                logger.warning(f"No data returned for topic {topic_id}")
                return

            # Extract posts and users
            post_stream = topic_data.get("post_stream", {})
            posts_data = post_stream.get("posts", [])

            # Store users from posts
            await self._store_users(posts_data)

            # Store or update topic
            await self._store_topic(topic_data, category_id)

            # Store posts
            await self._store_posts(posts_data, topic_id)

            # Commit transaction
            self.db_session.commit()

        except SQLAlchemyError as e:
            logger.error(
                f"Database error for topic {topic_id}: {e}", exc_info=True
            )
            self.db_session.rollback()
            raise

        except Exception as e:
            logger.error(
                f"Error collecting topic {topic_id}: {e}", exc_info=True
            )
            self.db_session.rollback()
            raise

    async def _store_category(self, category_metadata: Dict[str, Any]) -> None:
        """
        Store or update category in database.

        Args:
            category_metadata: Category metadata from API
        """
        try:
            category_id = category_metadata.get("id")
            category = self.db_session.get(Category, category_id)

            if not category:
                category = Category(
                    id=category_id,
                    name=category_metadata.get("name", ""),
                    slug=category_metadata.get("slug", ""),
                    description=category_metadata.get("description", ""),
                    topic_count=category_metadata.get("topic_count", 0),
                    post_count=category_metadata.get("post_count", 0),
                    last_scraped_at=datetime.utcnow(),
                )
                self.db_session.add(category)
                logger.debug(f"Added category: {category.name}")
            else:
                # Update category stats
                category.topic_count = category_metadata.get(
                    "topic_count", category.topic_count
                )
                category.post_count = category_metadata.get(
                    "post_count", category.post_count
                )
                category.last_scraped_at = datetime.utcnow()
                logger.debug(f"Updated category: {category.name}")

            self.db_session.commit()

        except SQLAlchemyError as e:
            logger.error(f"Error storing category: {e}", exc_info=True)
            self.db_session.rollback()
            raise

    async def _store_users(self, posts_data: List[Dict[str, Any]]) -> None:
        """
        Store or update users from posts.

        Args:
            posts_data: List of post data dictionaries
        """
        for post_data in posts_data:
            username = post_data.get("username")
            if not username:
                continue

            try:
                user = self.db_session.get(User, username)

                post_created = post_data.get("created_at")
                if post_created:
                    post_created_dt = datetime.fromisoformat(
                        post_created.replace("Z", "+00:00")
                    )
                else:
                    post_created_dt = None

                if not user:
                    user = User(
                        username=username,
                        post_count=1,
                        first_seen=post_created_dt,
                        last_seen=post_created_dt,
                    )
                    self.db_session.add(user)
                    self.stats["users_added"] += 1
                    logger.debug(f"Added user: {username}")
                else:
                    # Update user stats
                    user.post_count += 1
                    if post_created_dt:
                        # Ensure timezone-aware comparison
                        first_seen = user.first_seen
                        last_seen = user.last_seen

                        # Make database datetime timezone-aware if needed
                        if first_seen and first_seen.tzinfo is None:
                            first_seen = first_seen.replace(
                                tzinfo=timezone.utc
                            )
                        if last_seen and last_seen.tzinfo is None:
                            last_seen = last_seen.replace(tzinfo=timezone.utc)

                        if not first_seen or post_created_dt < first_seen:
                            user.first_seen = post_created_dt
                        if not last_seen or post_created_dt > last_seen:
                            user.last_seen = post_created_dt

            except SQLAlchemyError as e:
                logger.error(
                    f"Error storing user {username}: {e}", exc_info=True
                )
                # Continue with other users

    async def _store_topic(
        self, topic_data: Dict[str, Any], category_id: int
    ) -> None:
        """
        Store or update topic in database.

        Args:
            topic_data: Full topic data from API
            category_id: Category ID
        """
        topic_id = topic_data.get("id")
        if not topic_id:
            return

        try:
            topic = self.db_session.get(Topic, topic_id)

            # Parse timestamps
            created_at = topic_data.get("created_at")
            if created_at:
                created_at = datetime.fromisoformat(
                    created_at.replace("Z", "+00:00")
                )

            last_posted_at = topic_data.get("last_posted_at")
            if last_posted_at:
                last_posted_at = datetime.fromisoformat(
                    last_posted_at.replace("Z", "+00:00")
                )

            if not topic:
                topic = Topic(
                    id=topic_id,
                    category_id=category_id,
                    title=topic_data.get("title", ""),
                    slug=topic_data.get("slug", ""),
                    created_at=created_at,
                    last_posted_at=last_posted_at,
                    reply_count=topic_data.get("reply_count", 0),
                    view_count=topic_data.get("views", 0),
                    like_count=topic_data.get("like_count", 0),
                    word_count=topic_data.get("word_count", 0),
                    accepted_answer=topic_data.get(
                        "has_accepted_answer", False
                    ),
                    closed=topic_data.get("closed", False),
                    archived=topic_data.get("archived", False),
                    pinned=topic_data.get("pinned", False),
                    visible=topic_data.get("visible", True),
                    scraped_at=datetime.utcnow(),
                )
                self.db_session.add(topic)
                logger.debug(f"Added topic: {topic.title}")
            else:
                # Update topic with latest data
                topic.title = topic_data.get("title", topic.title)
                topic.last_posted_at = last_posted_at or topic.last_posted_at
                topic.reply_count = topic_data.get(
                    "reply_count", topic.reply_count
                )
                topic.view_count = topic_data.get("views", topic.view_count)
                topic.like_count = topic_data.get(
                    "like_count", topic.like_count
                )
                topic.word_count = topic_data.get(
                    "word_count", topic.word_count
                )
                topic.accepted_answer = topic_data.get(
                    "has_accepted_answer", topic.accepted_answer
                )
                topic.closed = topic_data.get("closed", topic.closed)
                topic.archived = topic_data.get("archived", topic.archived)
                topic.pinned = topic_data.get("pinned", topic.pinned)
                topic.visible = topic_data.get("visible", topic.visible)
                topic.scraped_at = datetime.utcnow()
                logger.debug(f"Updated topic: {topic.title}")

        except SQLAlchemyError as e:
            logger.error(f"Error storing topic {topic_id}: {e}", exc_info=True)
            raise

    async def _store_posts(
        self, posts_data: List[Dict[str, Any]], topic_id: int
    ) -> None:
        """
        Store posts in database (skip duplicates).

        Args:
            posts_data: List of post data dictionaries
            topic_id: Topic ID these posts belong to
        """
        for post_data in posts_data:
            post_id = post_data.get("id")
            if not post_id:
                continue

            # Check if post already exists
            existing_post = self.db_session.get(Post, post_id)
            if existing_post:
                continue

            try:
                # Parse timestamps
                created_at = post_data.get("created_at")
                if created_at:
                    created_at = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )

                updated_at = post_data.get("updated_at")
                if updated_at:
                    updated_at = datetime.fromisoformat(
                        updated_at.replace("Z", "+00:00")
                    )

                post = Post(
                    id=post_id,
                    topic_id=topic_id,
                    post_number=post_data.get("post_number", 0),
                    username=post_data.get("username", ""),
                    created_at=created_at,
                    updated_at=updated_at,
                    reply_count=post_data.get("reply_count", 0),
                    quote_count=post_data.get("quote_count", 0),
                    incoming_link_count=post_data.get(
                        "incoming_link_count", 0
                    ),
                    reads=post_data.get("reads", 0),
                    readers_count=post_data.get("readers_count", 0),
                    score=post_data.get("score", 0.0),
                    like_count=post_data.get("like_count", 0),
                    cooked=post_data.get("cooked", ""),
                    raw=post_data.get("raw", ""),
                    is_accepted_answer=post_data.get("accepted_answer", False),
                    scraped_at=datetime.utcnow(),
                )
                self.db_session.add(post)
                self.stats["posts_collected"] += 1
                self.stats["posts_added"] += 1
                logger.debug(f"Added post {post_id} to topic {topic_id}")

            except SQLAlchemyError as e:
                logger.error(
                    f"Error storing post {post_id}: {e}", exc_info=True
                )
                # Continue with other posts

    def _log_statistics(self) -> None:
        """Log collection statistics."""
        console.print("\n[bold green]Collection Statistics:[/bold green]")
        console.print(f"  Topics processed: {self.stats['topics_processed']}")
        console.print(f"  Topics updated: {self.stats['topics_updated']}")
        console.print(f"  Posts collected: {self.stats['posts_collected']}")
        console.print(f"  Posts added: {self.stats['posts_added']}")
        console.print(f"  Users added: {self.stats['users_added']}")


async def collect_category(
    category_id: int,
    full_fetch: bool = True,
    settings: Optional[Settings] = None,
    page_limit: Optional[int] = None,
) -> Dict[str, int]:
    """
    Collect all topics and posts from a category.

    This is a convenience function that sets up all required components
    and orchestrates the collection.

    Args:
        category_id: Category ID (e.g., 18)
        full_fetch: If True, fetch all pages; if False, incremental update
        settings: Optional Settings instance (will load from config if not
            provided)
        page_limit: Optional limit on number of pages to collect (for testing)

    Returns:
        Dictionary with collection statistics
    """
    if settings is None:
        settings = get_settings()

    # Create database engine and session
    engine = create_engine(settings.database.url, echo=settings.database.echo)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()

    # Initialize checkpoint manager
    checkpoint_dir = Path(settings.scraping.checkpoint_dir)
    checkpoint_mgr = CheckpointManager(
        session=db_session,
        checkpoint_dir=checkpoint_dir,
    )

    # Initialize API client
    async with ForumAPIClient(
        base_url=settings.api.base_url,
        category_path=settings.api.category_path,
        rate_limit=settings.api.rate_limit,
        timeout=settings.api.timeout,
        max_retries=settings.api.max_retries,
    ) as api_client:
        # Create orchestrator
        orchestrator = CollectionOrchestrator(
            api_client=api_client,
            db_session=db_session,
            checkpoint_mgr=checkpoint_mgr,
            settings=settings,
        )

        try:
            stats = await orchestrator.collect_category(
                category_id=category_id,
                full_fetch=full_fetch,
                page_limit=page_limit,
            )
            return stats
        finally:
            db_session.close()


async def incremental_update(
    category_id: int,
    settings: Optional[Settings] = None,
) -> Dict[str, int]:
    """
    Update existing data with new posts/topics since last run.

    Uses last_posted_at timestamps to detect changes.

    Args:
        category_id: Category ID (e.g., 18)
        settings: Optional Settings instance (will load from config if not
            provided)

    Returns:
        Dictionary with collection statistics
    """
    return await collect_category(
        category_id=category_id,
        full_fetch=False,
        settings=settings,
    )
