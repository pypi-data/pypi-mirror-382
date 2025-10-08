"""LLM-based analysis of forum topics using Claude API."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from ..collector.models import LLMAnalysis, Post, ProblemTheme, Topic
from ..config.settings import Settings

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Analyzes forum topics using Claude API to identify problems."""

    def __init__(self, settings: Settings):
        """Initialize the analyzer.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.client = Anthropic(api_key=settings.llm_analysis.api_key)

        # Create database session using database URL
        engine = create_engine(settings.database.url)

        # Auto-migrate schema if needed
        from ..collector.models import migrate_schema

        migrate_schema(engine)

        self.SessionLocal = sessionmaker(bind=engine)

    def analyze_topic(
        self, topic_id: int, force: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single topic.

        Args:
            topic_id: Topic ID to analyze
            force: Re-analyze even if already analyzed

        Returns:
            Analysis results or None if skipped
        """
        with self.SessionLocal() as session:
            # Check if already analyzed
            if not force:
                existing = session.execute(
                    select(LLMAnalysis).where(LLMAnalysis.topic_id == topic_id)
                ).scalar_one_or_none()
                if existing:
                    logger.info(f"Topic {topic_id} already analyzed, skipping")
                    return None

            # Get topic with posts
            topic = session.execute(
                select(Topic).where(Topic.id == topic_id)
            ).scalar_one_or_none()

            if not topic:
                logger.error(f"Topic {topic_id} not found")
                return None

            posts = (
                session.execute(
                    select(Post)
                    .where(Post.topic_id == topic_id)
                    .order_by(Post.post_number)
                )
                .scalars()
                .all()
            )

            # Get dynamic categories
            categories = self._get_categories(session)

            # Prepare context
            logger.info(f"Analyzing topic ID: {topic.id} - '{topic.title}'")
            context = self._prepare_topic_context(topic, posts)

            # Call Claude API with dynamic categories
            analysis = self._call_claude_api(context, categories)

            if analysis:
                # Store results
                self._store_analysis(session, topic_id, analysis)
                return analysis

            return None

    def analyze_batch(
        self,
        limit: Optional[int] = None,
        force: bool = False,
        progress: Optional["Progress"] = None,
    ) -> Dict[str, Any]:
        """Analyze multiple topics in batch.

        Args:
            limit: Maximum number of topics to analyze
            force: Re-analyze already analyzed topics
            progress: Rich progress bar object

        Returns:
            Summary of analysis results
        """
        with self.SessionLocal() as session:
            # Get topics to analyze
            query = select(Topic)

            if not force:
                # Only unanalyzed topics
                subquery = select(LLMAnalysis).where(
                    LLMAnalysis.topic_id == Topic.id
                )
                query = query.where(~subquery.exists())

            if limit:
                query = query.limit(limit)

            topics = session.execute(query).scalars().all()

            logger.info(f"Analyzing {len(topics)} topics")

            results = {
                "total": len(topics),
                "analyzed": 0,
                "skipped": 0,
                "errors": 0,
                "categories": {},
                "severities": {},
            }

            if progress:
                task = progress.add_task(
                    "[cyan]Analyzing...", total=len(topics)
                )

            for topic in topics:
                if progress:
                    progress.update(
                        task, description=f"Analyzing topic {topic.id}"
                    )
                try:
                    analysis = self.analyze_topic(topic.id, force=force)
                    if analysis:
                        results["analyzed"] += 1

                        # Track categories and severities
                        category = analysis.get("category", "unknown")
                        severity = analysis.get("severity", "unknown")

                        results["categories"][category] = (
                            results["categories"].get(category, 0) + 1
                        )
                        results["severities"][severity] = (
                            results["severities"].get(severity, 0) + 1
                        )
                    else:
                        results["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error analyzing topic {topic.id}: {e}")
                    results["errors"] += 1
                if progress:
                    progress.update(task, advance=1)

            return results

    def _get_categories(self, session) -> Optional[List[str]]:
        """Get categories from existing themes or return None.

        Returns:
            List of theme names if themes exist, None otherwise
            to allow free-form categorization
        """
        themes = session.execute(select(ProblemTheme)).scalars().all()

        if themes:
            # Use discovered theme names as categories
            return [theme.theme_name for theme in themes]
        else:
            # No themes yet - let Claude determine categories freely
            return None

    def identify_themes(
        self, min_topics: int = 3, context_limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Identify common problem themes from collected topics.

        Args:
            min_topics: Minimum number of topics to form a theme
            context_limit: Maximum number of topics to include in context

        Returns:
            List of identified themes
        """
        with self.SessionLocal() as session:
            # Get all topics with their posts
            topics = (
                session.execute(select(Topic).where(Topic.reply_count >= 0))
                .scalars()
                .all()
            )

            if not topics:
                logger.warning("No topics found")
                return []

            logger.info(f"Found {len(topics)} topics for theme identification")

            # Prepare context for theme identification
            limit = (
                context_limit
                if context_limit is not None
                else self.settings.llm_analysis.theme_context_limit
            )
            context = self._prepare_theme_context(topics, session, limit)

            logger.debug(f"Context length: {len(context)} characters")
            if len(context) < 50:
                logger.warning(f"Context is very short: {context}")
                return []

            # Call Claude API
            themes = self._identify_themes_via_api(context, min_topics)

            if themes:
                # Store themes
                for theme in themes:
                    self._store_theme(session, theme)

            return themes

    def ask_question(
        self, question: str, context_limit: Optional[int] = None
    ) -> str:
        """Ask a question about the forum data.

        Args:
            question: Question to ask
            context_limit: Maximum number of topics in context

        Returns:
            Answer from Claude
        """
        limit = context_limit or self.settings.llm_analysis.ask.context_limit

        with self.SessionLocal() as session:
            # Get recent analyzed topics for context
            analyses = session.execute(
                select(LLMAnalysis, Topic)
                .join(Topic, LLMAnalysis.topic_id == Topic.id)
                .order_by(LLMAnalysis.analyzed_at.desc())
                .limit(limit)
            ).all()

            if not analyses:
                return (
                    "No analyzed topics found. " "Please run analysis first."
                )

            # Prepare context
            context = self._prepare_ask_context(analyses, question)

            # Call Claude API
            answer = self._answer_question_via_api(context)

            return answer

    def _prepare_topic_context(self, topic: Topic, posts: List[Post]) -> str:
        """Prepare context for topic analysis, truncating if necessary."""
        header = f"""Topic: {topic.title}
Created: {topic.created_at}
Posts: {topic.reply_count}
Views: {topic.view_count}
Likes: {topic.like_count}

"""

        full_content = ""
        for post in posts:
            full_content += f"\n--- Post {post.post_number} "
            full_content += f"by {post.username} ---\n"
            content = (
                post.raw if post.raw and post.raw.strip() else post.cooked
            )
            full_content += f"{content}\n"

        max_len = self.settings.llm_analysis.context_char_limit
        if len(header) + len(full_content) <= max_len:
            return header + full_content

        # If too long, apply smart truncation
        if len(posts) > 6:
            first_posts = posts[:3]
            last_posts = posts[-3:]

            truncated_content = ""
            for post in first_posts:
                truncated_content += f"\n--- Post {post.post_number} "
                truncated_content += f"by {post.username} ---\n"
                content = (
                    post.raw if post.raw and post.raw.strip() else post.cooked
                )
                truncated_content += f"{content}\n"

            truncated_content += (
                "\n[... middle of conversation truncated ...]\n"
            )

            for post in last_posts:
                truncated_content += f"\n--- Post {post.post_number} "
                truncated_content += f"by {post.username} ---\n"
                content = (
                    post.raw if post.raw and post.raw.strip() else post.cooked
                )
                truncated_content += f"{content}\n"

            final_context = header + truncated_content
            # Final check to ensure even the truncated version fits
            return final_context[:max_len]

        # Fallback for topics with <= 6 posts but still too long
        return (header + full_content)[:max_len]

    def _call_claude_api(
        self, context: str, categories: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Call Claude API for topic analysis."""
        # Prepare category instruction based on available categories
        if categories:
            category_list = ", ".join(categories)
            category_instruction = f"2. category: One of [{category_list}]"
        else:
            category_instruction = (
                "2. category: An appropriate category that describes "
                "the type of problem or discussion"
            )

        system_prompt = f"""You are analyzing developer forum \
posts to identify problems that need solving.

Analyze the topic and provide:
1. core_problem: Clear, concise problem description (1-2 sentences)
{category_instruction}
3. severity: One of [critical, high, medium, low]
4. key_terms: Array of important technical terms (3-7 terms)
5. root_cause: Brief analysis of what's causing the problem

Return ONLY valid JSON matching this schema:
{{
  "core_problem": "string",
  "category": "string",
  "severity": "string",
  "key_terms": ["string"],
  "root_cause": "string"
}}"""

        try:
            logger.debug(
                "Calling Claude API with model: "
                f"{self.settings.llm_analysis.model}"
            )

            message = self.client.messages.create(
                model=self.settings.llm_analysis.model,
                max_tokens=self.settings.llm_analysis.max_tokens,
                temperature=self.settings.llm_analysis.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": context}],
            )

            logger.debug(f"Message object type: {type(message)}")
            logger.debug(f"Message content: {message.content}")

            # Parse response - handle both list and direct text access
            if (
                hasattr(message.content, "__iter__")
                and len(message.content) > 0
            ):
                response_text = message.content[0].text
            else:
                logger.error(
                    f"Unexpected message.content structure: {message.content}"
                )
                return None

            logger.debug(f"Response text length: {len(response_text)}")
            logger.debug(f"Response text preview: {response_text[:200]}")

            # Try to parse JSON, handle potential issues
            if not response_text or response_text.strip() == "":
                logger.error("Empty response from Claude API")
                return None

            # Strip markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove closing ```
            response_text = response_text.strip()

            logger.debug(f"Cleaned response: {response_text[:200]}")

            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError as je:
                logger.error(
                    f"Failed to parse JSON response: {response_text[:500]}"
                )
                logger.error(f"JSON error: {je}")
                return None

            return analysis

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            logger.exception(e)  # This will log the full stack trace
            return None

    def _store_analysis(
        self, session: Session, topic_id: int, analysis: Dict[str, Any]
    ) -> None:
        """Store analysis results in database."""
        # Note: "category" field stores the CLASSIFICATION (problem type),
        # not the Discourse forum category. See glossary for terminology.
        llm_analysis = LLMAnalysis(
            topic_id=topic_id,
            core_problem=analysis.get("core_problem"),
            category=analysis.get("category"),  # Classification
            severity=analysis.get("severity"),
            key_terms=json.dumps(analysis.get("key_terms", [])),
            root_cause=analysis.get("root_cause"),
            model_version=self.settings.llm_analysis.model,
            analyzed_at=datetime.utcnow(),
        )

        session.merge(llm_analysis)
        session.commit()

        logger.info(f"Stored analysis for topic {topic_id}")

    def _prepare_theme_context(
        self, topics: List[Topic], session, limit: int
    ) -> str:
        """Prepare context for theme identification from raw topics."""
        context = "Forum Topics:\n\n"

        for topic in topics[:limit]:
            # Get first post for content
            first_post = session.execute(
                select(Post)
                .where(Post.topic_id == topic.id)
                .order_by(Post.post_number)
                .limit(1)
            ).scalar_one_or_none()

            post_content = ""
            if first_post:
                # Truncate long content
                content = first_post.raw or first_post.cooked or ""
                post_content = (
                    content[:300] + "..." if len(content) > 300 else content
                )

            context += f"""Topic ID: {topic.id}
Title: {topic.title}
Views: {topic.view_count or 0}
Posts: {topic.reply_count or 0}
Content: {post_content}

"""

        return context

    def _identify_themes_via_api(
        self, context: str, min_topics: int
    ) -> List[Dict[str, Any]]:
        """Identify themes using Claude API."""
        system_prompt = f"""You are identifying common problem themes \
across developer forum topics.

Analyze the topics and identify recurring themes that appear in at \
least {min_topics} topics.

For each theme, provide:
1. theme_name: Short descriptive name (3-5 words)
2. description: Clear description of the theme
3. affected_topic_ids: Array of topic IDs with this theme
4. severity_distribution: Counts by severity level

Return ONLY valid JSON array:
[
  {{
    "theme_name": "string",
    "description": "string",
    "affected_topic_ids": [int],
    "severity_distribution": {{"critical": int, "high": int, \
"medium": int, "low": int}}
  }}
]"""

        try:
            logger.info(
                f"Calling Claude API for theme identification "
                f"(model: {self.settings.llm_analysis.model})"
            )

            message = self.client.messages.create(
                model=self.settings.llm_analysis.model,
                max_tokens=self.settings.llm_analysis.max_tokens,
                temperature=self.settings.llm_analysis.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": context}],
            )

            logger.info("Received response from Claude API")

            # Parse response
            response_text = message.content[0].text

            # Log raw response for debugging
            logger.debug(f"Raw API response: {response_text[:500]}")

            # Extract JSON from response
            # Handle case where response has explanatory text before JSON
            json_start = response_text.find("[")
            json_end = response_text.rfind("]")

            if json_start == -1 or json_end == -1:
                logger.error("No JSON array found in response")
                logger.error(f"Response: {response_text[:1000]}")
                return []

            # Extract just the JSON array
            response_text = response_text[json_start : json_end + 1]

            # Check if response is empty
            if not response_text:
                logger.error("Empty response from Claude API")
                return []

            # Log cleaned response for debugging
            logger.debug(f"Cleaned response: {response_text[:500]}")

            themes = json.loads(response_text)

            return themes

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response text: {response_text[:1000]}")
            return []
        except Exception as e:
            logger.error(f"Error identifying themes: {e}")
            logger.error(
                (
                    "Response text: "
                    f"{response_text[:1000] if 'response_text' in locals() else 'N/A'}"
                )
            )
            return []

    def _store_theme(self, session: Session, theme: Dict[str, Any]) -> None:
        """Store theme in database."""
        problem_theme = ProblemTheme(
            theme_name=theme.get("theme_name"),
            description=theme.get("description"),
            affected_topic_ids=json.dumps(theme.get("affected_topic_ids", [])),
            severity_distribution=json.dumps(
                theme.get("severity_distribution", {})
            ),
            topic_count=len(theme.get("affected_topic_ids", [])),
            analyzed_at=datetime.utcnow(),
        )

        session.add(problem_theme)
        session.commit()

        logger.info(f"Stored theme: {theme.get('theme_name')}")

    def _prepare_ask_context(
        self, analyses: List[tuple], question: str
    ) -> str:
        """Prepare context for question answering."""
        context = f"Question: {question}\n\nForum Data Context:\n\n"

        for analysis, topic in analyses:
            context += f"""Topic: {topic.title}
Problem: {analysis.core_problem}
Category: {analysis.category}
Severity: {analysis.severity}
Root Cause: {analysis.root_cause}

"""

        return context

    def _answer_question_via_api(self, context: str) -> str:
        """Answer question using Claude API."""
        system_prompt = """You are a helpful assistant analyzing \
developer forum data.

Answer the user's question based on the analyzed forum topics \
provided.
Be specific, cite relevant topics when appropriate, and provide \
actionable insights.
If you don't have enough information to answer, say so clearly."""

        try:
            message = self.client.messages.create(
                model=self.settings.llm_analysis.model,
                max_tokens=self.settings.llm_analysis.max_tokens,
                temperature=self.settings.llm_analysis.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": context}],
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"Error: {str(e)}"
