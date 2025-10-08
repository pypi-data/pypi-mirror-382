"""Forum analysis and reporting module."""

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from sqlalchemy import create_engine, select, func, and_, or_, desc
from sqlalchemy.orm import Session

from forum_analyzer.collector.models import Topic, Post, User, Category


# Common stop words to filter out from keyword analysis
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "will",
    "with",
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
    "can",
    "do",
    "does",
    "this",
    "these",
    "those",
    "my",
    "your",
    "i",
    "you",
    "we",
    "they",
    "not",
    "but",
    "or",
    "if",
    "any",
    "all",
    "get",
    "using",
    "use",
    "need",
    "have",
}


# Category keywords for problem classification
CATEGORY_KEYWORDS = {
    "webhook_delivery": [
        "webhook",
        "delivery",
        "receive",
        "trigger",
        "not getting",
        "not receiving",
        "not working",
        "stopped",
        "missing",
    ],
    "authentication": [
        "auth",
        "token",
        "api key",
        "credentials",
        "permission",
        "access",
        "unauthorized",
        "forbidden",
        "401",
        "403",
    ],
    "payload_data": [
        "payload",
        "data",
        "json",
        "field",
        "missing",
        "format",
        "parse",
        "schema",
        "structure",
        "body",
    ],
    "timeout_performance": [
        "timeout",
        "delay",
        "slow",
        "performance",
        "latency",
        "response time",
        "hanging",
        "stuck",
    ],
    "configuration": [
        "setup",
        "config",
        "install",
        "configure",
        "settings",
        "initialization",
        "environment",
    ],
    "error_codes": [
        "error",
        "500",
        "404",
        "502",
        "503",
        "failed",
        "failure",
        "exception",
        "crash",
    ],
}


class ForumAnalyzer:
    """Analyze forum data and generate insights."""

    def __init__(self, db_path: str):
        """Initialize the analyzer.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")

    def get_most_discussed_topics(self, limit: int = 20) -> List[Dict]:
        """Get topics with most replies/views.

        Args:
            limit: Maximum number of topics to return.

        Returns:
            List of topic dictionaries with title, reply_count, views, url.
        """
        with Session(self.engine) as session:
            topics = session.scalars(
                select(Topic)
                .filter(Topic.visible.is_(True))
                .order_by(desc(Topic.reply_count), desc(Topic.view_count))
                .limit(limit)
            ).all()

            return [
                {
                    "id": topic.id,
                    "title": topic.title,
                    "reply_count": topic.reply_count,
                    "views": topic.view_count,
                    "likes": topic.like_count,
                    "created_at": topic.created_at,
                    "accepted_answer": topic.accepted_answer,
                }
                for topic in topics
            ]

    def get_frequent_keywords_from_titles(
        self, limit: int = 30
    ) -> List[Tuple[str, int]]:
        """Extract and count keywords from topic titles.

        Filters out common words and focuses on technical terms.

        Args:
            limit: Maximum number of keywords to return.

        Returns:
            List of (keyword, count) tuples sorted by frequency.
        """
        with Session(self.engine) as session:
            topics = session.scalars(
                select(Topic).filter(Topic.visible.is_(True))
            ).all()

            # Extract words from all titles
            word_counter = Counter()
            for topic in topics:
                # Convert to lowercase and split
                words = re.findall(r"\b[a-z]{3,}\b", topic.title.lower())

                # Filter out stop words and count
                for word in words:
                    if word not in STOP_WORDS:
                        word_counter[word] += 1

            return word_counter.most_common(limit)

    def get_topics_by_activity_trend(self) -> Dict:
        """Group topics by time period and identify trends.

        Returns:
            Dictionary with time period statistics.
        """
        with Session(self.engine) as session:
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)

            # Last week
            last_week = (
                session.scalar(
                    select(func.count())
                    .select_from(Topic)
                    .filter(
                        and_(
                            Topic.created_at >= week_ago,
                            Topic.visible.is_(True),
                        )
                    )
                )
                or 0
            )

            # Last month
            last_month = (
                session.scalar(
                    select(func.count())
                    .select_from(Topic)
                    .filter(
                        and_(
                            Topic.created_at >= month_ago,
                            Topic.created_at < week_ago,
                            Topic.visible.is_(True),
                        )
                    )
                )
                or 0
            )

            # All time
            all_time = (
                session.scalar(
                    select(func.count())
                    .select_from(Topic)
                    .filter(Topic.visible.is_(True))
                )
                or 0
            )

            # Recent active topics (based on last_posted_at)
            recent_active = session.scalars(
                select(Topic)
                .filter(
                    and_(
                        Topic.last_posted_at >= week_ago,
                        Topic.visible.is_(True),
                    )
                )
                .order_by(desc(Topic.last_posted_at))
                .limit(10)
            ).all()

            return {
                "last_week": last_week,
                "last_month": last_month,
                "older": all_time - last_week - last_month,
                "total": all_time,
                "recent_active": [
                    {
                        "id": topic.id,
                        "title": topic.title,
                        "last_posted_at": topic.last_posted_at,
                        "reply_count": topic.reply_count,
                    }
                    for topic in recent_active
                ],
            }

    def get_unanswered_topics(self, threshold: int = 2) -> List[Dict]:
        """Get topics with few replies (potential unresolved issues).

        Args:
            threshold: Maximum reply count to consider as unanswered.

        Returns:
            List of topic dictionaries.
        """
        with Session(self.engine) as session:
            topics = session.scalars(
                select(Topic)
                .filter(
                    and_(
                        Topic.reply_count <= threshold,
                        Topic.accepted_answer.is_(False),
                        Topic.visible.is_(True),
                    )
                )
                .order_by(desc(Topic.view_count))
                .limit(50)
            ).all()

            return [
                {
                    "id": topic.id,
                    "title": topic.title,
                    "reply_count": topic.reply_count,
                    "views": topic.view_count,
                    "created_at": topic.created_at,
                }
                for topic in topics
            ]

    def get_high_engagement_topics(self, min_likes: int = 5) -> List[Dict]:
        """Get topics with high like counts (community-validated issues).

        Args:
            min_likes: Minimum like count threshold.

        Returns:
            List of topic dictionaries.
        """
        with Session(self.engine) as session:
            topics = session.scalars(
                select(Topic)
                .filter(
                    and_(
                        Topic.like_count >= min_likes, Topic.visible.is_(True)
                    )
                )
                .order_by(desc(Topic.like_count))
                .limit(30)
            ).all()

            return [
                {
                    "id": topic.id,
                    "title": topic.title,
                    "reply_count": topic.reply_count,
                    "views": topic.view_count,
                    "likes": topic.like_count,
                    "created_at": topic.created_at,
                    "accepted_answer": topic.accepted_answer,
                }
                for topic in topics
            ]

    def search_topics_by_keyword(self, keyword: str) -> List[Dict]:
        """Find topics containing specific keyword in title or first post.

        Args:
            keyword: Search keyword (case-insensitive).

        Returns:
            List of matching topic dictionaries.
        """
        with Session(self.engine) as session:
            # Search in titles
            pattern = f"%{keyword.lower()}%"
            topics = session.scalars(
                select(Topic)
                .filter(
                    and_(
                        func.lower(Topic.title).like(pattern),
                        Topic.visible.is_(True),
                    )
                )
                .order_by(desc(Topic.reply_count))
                .limit(50)
            ).all()

            return [
                {
                    "id": topic.id,
                    "title": topic.title,
                    "reply_count": topic.reply_count,
                    "views": topic.view_count,
                    "likes": topic.like_count,
                    "created_at": topic.created_at,
                    "accepted_answer": topic.accepted_answer,
                }
                for topic in topics
            ]

    def detect_common_error_patterns(self) -> Dict[str, List[Dict]]:
        """Search for common error patterns in titles.

        Returns:
            Dictionary mapping pattern names to matching topics.
        """
        patterns = {
            "webhook_failed": [
                "webhook%failed",
                "webhook%not%working",
                "webhook%stopped",
            ],
            "webhook_delivery": [
                "%not%receiving",
                "%delivery%issue",
                "%missing%webhook",
            ],
            "authentication": [
                "auth%",
                "%token%",
                "%unauthorized%",
                "%403%",
                "%401%",
            ],
            "timeout": ["timeout%", "%delay%", "%slow%", "%hanging%"],
            "payload_issues": [
                "payload%",
                "%json%",
                "%data%missing%",
                "%parse%",
            ],
            "configuration": ["%setup%", "%config%", "%install%"],
            "api_errors": ["%500%", "%502%", "%503%", "%404%", "%error%"],
        }

        results = {}

        with Session(self.engine) as session:
            for pattern_name, pattern_variants in patterns.items():
                # Combine all variants with OR
                conditions = [
                    func.lower(Topic.title).like(variant)
                    for variant in pattern_variants
                ]

                topics = session.scalars(
                    select(Topic)
                    .filter(and_(or_(*conditions), Topic.visible.is_(True)))
                    .order_by(desc(Topic.reply_count))
                    .limit(20)
                ).all()

                if topics:
                    results[pattern_name] = [
                        {
                            "id": topic.id,
                            "title": topic.title,
                            "reply_count": topic.reply_count,
                            "views": topic.view_count,
                            "created_at": topic.created_at,
                        }
                        for topic in topics
                    ]

        return results

    def get_problem_category_distribution(self) -> Dict[str, int]:
        """Categorize topics by problem type based on keywords.

        Returns:
            Dictionary mapping category names to topic counts.
        """
        distribution = defaultdict(int)

        with Session(self.engine) as session:
            topics = session.scalars(
                select(Topic).filter(Topic.visible.is_(True))
            ).all()

            for topic in topics:
                title_lower = topic.title.lower()
                categorized = False

                # Check each category
                for category_name, keywords in CATEGORY_KEYWORDS.items():
                    if any(keyword in title_lower for keyword in keywords):
                        distribution[category_name] += 1
                        categorized = True
                        break  # Assign to first matching category

                if not categorized:
                    distribution["general_questions"] += 1

        return dict(distribution)

    def get_database_stats(self) -> Dict:
        """Get overall database statistics.

        Returns:
            Dictionary with counts of categories, topics, posts, users.
        """
        with Session(self.engine) as session:
            return {
                "categories": session.scalar(
                    select(func.count()).select_from(Category)
                )
                or 0,
                "topics": session.scalar(
                    select(func.count()).select_from(Topic)
                )
                or 0,
                "posts": session.scalar(select(func.count()).select_from(Post))
                or 0,
                "users": session.scalar(select(func.count()).select_from(User))
                or 0,
            }

    def generate_summary_report(self) -> str:
        """Generate a comprehensive text report.

        Returns:
            Formatted text report with all analysis results.
        """
        # Gather all data
        stats = self.get_database_stats()
        top_topics = self.get_most_discussed_topics(20)
        keywords = self.get_frequent_keywords_from_titles(30)
        trends = self.get_topics_by_activity_trend()
        unanswered = self.get_unanswered_topics(2)
        high_engagement = self.get_high_engagement_topics(5)
        error_patterns = self.detect_common_error_patterns()
        categories = self.get_problem_category_distribution()

        # Build report
        lines = [
            "# Forum Analysis Report",
            "",
            (
                f"Generated: "
                f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            ),
            "",
            "## Summary Statistics",
            "",
            f"- **Total Categories**: {stats['categories']}",
            f"- **Total Topics**: {stats['topics']}",
            f"- **Total Posts**: {stats['posts']}",
            f"- **Total Users**: {stats['users']}",
            "",
            "## Activity Trends",
            "",
            f"- **Last Week**: {trends['last_week']} new topics",
            f"- **Last Month**: {trends['last_month']} new topics",
            f"- **Older**: {trends['older']} topics",
            "",
            "### Recently Active Topics",
            "",
        ]

        for topic in trends["recent_active"][:5]:
            last_posted = (
                topic["last_posted_at"].strftime("%Y-%m-%d")
                if topic["last_posted_at"]
                else "N/A"
            )
            lines.append(
                f"- **{topic['title']}** ({topic['reply_count']} replies, "
                f"last active: {last_posted})"
            )

        lines.extend(
            [
                "",
                "## Most Discussed Topics",
                "",
            ]
        )

        for i, topic in enumerate(top_topics[:15], 1):
            solved = "✓" if topic["accepted_answer"] else ""
            lines.append(
                f"{i}. **{topic['title']}** {solved}  \n"
                f"   {topic['reply_count']} replies, {topic['views']} views, "
                f"{topic['likes']} likes"
            )

        lines.extend(
            [
                "",
                "## Common Keywords",
                "",
            ]
        )

        # Group keywords by frequency ranges
        for keyword, count in keywords[:20]:
            lines.append(f"- **{keyword}**: {count} occurrences")

        lines.extend(
            [
                "",
                "## Problem Categories",
                "",
            ]
        )

        total_categorized = sum(categories.values())
        for category, count in sorted(
            categories.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (
                (count / total_categorized * 100)
                if total_categorized > 0
                else 0
            )
            category_name = category.replace("_", " ").title()
            lines.append(
                f"- **{category_name}**: {count} topics ({percentage:.1f}%)"
            )

        lines.extend(
            [
                "",
                "## Common Error Patterns",
                "",
            ]
        )

        for pattern_name, topics in sorted(
            error_patterns.items(), key=lambda x: len(x[1]), reverse=True
        ):
            if topics:
                pattern_title = pattern_name.replace("_", " ").title()
                lines.append(f"### {pattern_title} ({len(topics)} topics)")
                lines.append("")
                for topic in topics[:5]:
                    lines.append(
                        f"- {topic['title']} ({topic['reply_count']} replies)"
                    )
                lines.append("")

        lines.extend(
            [
                "## Potentially Unanswered Questions",
                "",
                (
                    f"*Topics with ≤2 replies and no accepted answer "
                    f"({len(unanswered)} found)*"
                ),
                "",
            ]
        )

        for topic in unanswered[:10]:
            created = (
                topic["created_at"].strftime("%Y-%m-%d")
                if topic["created_at"]
                else "N/A"
            )
            lines.append(
                f"- **{topic['title']}**  \n"
                f"  {topic['reply_count']} replies, {topic['views']} views, "
                f"created: {created}"
            )

        lines.extend(
            [
                "",
                "## High Engagement Topics",
                "",
                f"*Topics with ≥5 likes ({len(high_engagement)} found)*",
                "",
            ]
        )

        for topic in high_engagement[:10]:
            solved = "✓" if topic["accepted_answer"] else ""
            lines.append(
                f"- **{topic['title']}** {solved}  \n"
                f"  {topic['likes']} likes, {topic['reply_count']} replies, "
                f"{topic['views']} views"
            )

        return "\n".join(lines)

    def export_report_to_markdown(self, output_path: str) -> None:
        """Save report as markdown file.

        Args:
            output_path: Path where the markdown file will be saved.
        """
        report = self.generate_summary_report()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding="utf-8")
