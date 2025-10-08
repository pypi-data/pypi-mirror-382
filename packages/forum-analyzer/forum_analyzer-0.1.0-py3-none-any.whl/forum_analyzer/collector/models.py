"""SQLAlchemy ORM models for the forum database."""

import logging
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    inspect,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Session

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Category(Base):
    """Category model."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    description = Column(Text)
    topic_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    last_scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topics = relationship(
        "Topic", back_populates="category", cascade="all, delete-orphan"
    )
    checkpoints = relationship(
        "Checkpoint", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', " f"slug='{self.slug}')>"


class Topic(Base):
    """Topic model."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    created_at = Column(DateTime)
    last_posted_at = Column(DateTime)
    reply_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    accepted_answer = Column(Boolean, default=False)
    closed = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    pinned = Column(Boolean, default=False)
    visible = Column(Boolean, default=True)
    scraped_at = Column(DateTime)

    # Relationships
    category = relationship("Category", back_populates="topics")
    posts = relationship("Post", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<Topic(id={self.id}, title='{self.title[:50]}...', "
            f"category_id={self.category_id})>"
        )


class Post(Base):
    """Post model."""

    __tablename__ = "posts"
    __table_args__ = (
        UniqueConstraint("topic_id", "post_number", name="uix_topic_post_number"),
    )

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    post_number = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    reply_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    incoming_link_count = Column(Integer, default=0)
    reads = Column(Integer, default=0)
    readers_count = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    like_count = Column(Integer, default=0)
    cooked = Column(Text)  # HTML version
    raw = Column(Text)  # Markdown version
    is_accepted_answer = Column(Boolean, default=False)
    scraped_at = Column(DateTime)

    # Relationships
    topic = relationship("Topic", back_populates="posts")

    def __repr__(self) -> str:
        return (
            f"<Post(id={self.id}, topic_id={self.topic_id}, "
            f"post_number={self.post_number}, username='{self.username}')>"
        )


class Checkpoint(Base):
    """Checkpoint model for resumable scraping."""

    __tablename__ = "checkpoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    checkpoint_type = Column(String, nullable=False)
    last_page = Column(Integer)
    last_topic_id = Column(Integer)
    total_processed = Column(Integer, default=0)
    status = Column(
        String, default="in_progress"
    )  # 'in_progress', 'completed', 'error'
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="checkpoints")

    def __repr__(self) -> str:
        return (
            f"<Checkpoint(id={self.id}, category_id={self.category_id}, "
            f"type='{self.checkpoint_type}', status='{self.status}')>"
        )


class User(Base):
    """User model (derived from posts)."""

    __tablename__ = "users"

    username = Column(String, primary_key=True)
    post_count = Column(Integer, default=0)
    topic_count = Column(Integer, default=0)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', " f"post_count={self.post_count})>"


class LLMAnalysis(Base):
    """LLM analysis results for topics."""

    __tablename__ = "llm_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, unique=True)
    core_problem = Column(Text)
    # NOTE: Stores CLASSIFICATION (problem type), not forum category
    category = Column(String(100))
    severity = Column(String(50))
    key_terms = Column(Text)  # JSON
    root_cause = Column(Text)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50))

    # Relationship
    topic = relationship("Topic", backref="llm_analysis")

    def __repr__(self) -> str:
        return (
            f"<LLMAnalysis(id={self.id}, topic_id={self.topic_id}, "
            f"category={self.category})>"
        )


class ProblemTheme(Base):
    """Aggregated problem themes across topics."""

    __tablename__ = "problem_themes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    theme_name = Column(String(200), nullable=False)
    description = Column(Text)
    affected_topic_ids = Column(Text)  # JSON
    severity_distribution = Column(Text)  # JSON
    topic_count = Column(Integer, default=0)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<ProblemTheme(id={self.id}, theme_name={self.theme_name}, "
            f"topic_count={self.topic_count})>"
        )


def migrate_schema(engine):
    """Ensure all tables exist, creating new ones if needed.

    This function performs automatic schema migration by checking which tables
    exist and creating any missing ones. It's safe to call multiple times as
    SQLAlchemy's create_all() is idempotent and only creates missing tables.

    Args:
        engine: SQLAlchemy engine instance
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Tables we expect to exist
    expected_tables = {
        "categories",
        "topics",
        "posts",
        "users",
        "checkpoints",
        "llm_analysis",
        "problem_themes",
    }

    missing_tables = expected_tables - set(existing_tables)

    if missing_tables:
        logger.info(f"Creating missing tables: {missing_tables}")
        Base.metadata.create_all(engine)
        logger.info("Schema migration complete")
    else:
        logger.debug("All tables exist, no migration needed")


def create_database(database_url: str) -> None:
    """Create all database tables.

    Args:
        database_url: SQLAlchemy database URL
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)


def get_session(database_url: str) -> Session:
    """Get a database session.

    Args:
        database_url: SQLAlchemy database URL

    Returns:
        SQLAlchemy Session instance
    """
    engine = create_engine(database_url)
    return Session(engine)
