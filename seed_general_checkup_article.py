"""
Seed the general health checkup article into the Health Digest.
"""
from datetime import datetime
import os
import re

from app import app, db
from models import Article, ArticleCategory, Specialty
from slugify import slugify


def format_inline(text):
    """Convert basic markdown inline styles to HTML."""
    if not text:
        return text
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def markdown_to_html(markdown_text):
    """Convert markdown to HTML."""
    lines = markdown_text.splitlines()
    html_parts = []
    paragraph_lines = []
    list_type = None

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            text = " ".join(paragraph_lines).strip()
            if text:
                html_parts.append(f"<p>{format_inline(text)}</p>")
            paragraph_lines = []

    def close_list():
        nonlocal list_type
        if list_type == "ul":
            html_parts.append("</ul>")
        elif list_type == "ol":
            html_parts.append("</ol>")
        list_type = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            close_list()
            html_parts.append(f"<h4>{format_inline(stripped[4:])}</h4>")
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            close_list()
            html_parts.append(f"<h3>{format_inline(stripped[3:])}</h3>")
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            close_list()
            html_parts.append(f"<h2>{format_inline(stripped[2:])}</h2>")
            continue

        ol_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if stripped.startswith("- "):
            if list_type != "ul":
                flush_paragraph()
                close_list()
                list_type = "ul"
                html_parts.append("<ul>")
            html_parts.append(f"<li>{format_inline(stripped[2:])}</li>")
            continue
        if ol_match:
            if list_type != "ol":
                flush_paragraph()
                close_list()
                list_type = "ol"
                html_parts.append("<ol>")
            html_parts.append(f"<li>{format_inline(ol_match.group(2))}</li>")
            continue

        if list_type:
            close_list()

        paragraph_lines.append(stripped)

    flush_paragraph()
    close_list()
    return "\n".join(html_parts)


def seed_general_checkup_article():
    with app.app_context():
        article_path = os.path.join(os.path.dirname(__file__), "article_general_checkup.md")
        if not os.path.exists(article_path):
            raise FileNotFoundError("article_general_checkup.md not found")

        with open(article_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        html_content = markdown_to_html(markdown_text)

        # Get or create General Health category
        category = ArticleCategory.query.filter_by(slug="general-health").first()
        if not category:
            category = ArticleCategory(
                name="General Health",
                slug="general-health",
                description="General health topics, checkups, and preventive care",
                icon="fa-heartbeat",
                display_order=10
            )
            db.session.add(category)
            db.session.flush()

        # Link to General Physician specialty
        specialty = Specialty.query.filter_by(name="General Physician").first()

        title = "When to See a Doctor in Nepal: A Guide to General Health Checkups"
        slug = slugify(title)

        summary = (
            "Don't wait until you're sick. Learn why annual health checkups matter, "
            "what tests you need at different ages, and how to find a trusted General Physician in Nepal."
        )

        meta_description = (
            "Guide to health checkups in Nepal: costs, what to expect, and how to find a verified General Physician near you."
        )

        meta_keywords = (
            "general physician Nepal, health checkup Kathmandu, annual checkup Nepal, "
            "doctor near me Nepal, full body checkup Nepal cost, health screening Kathmandu, "
            "MBBS doctor Nepal, best doctor Kathmandu"
        )

        existing = Article.query.filter_by(slug=slug).first()
        if existing:
            existing.title = title
            existing.category_id = category.id
            existing.summary = summary
            existing.content = html_content
            existing.meta_description = meta_description
            existing.meta_keywords = meta_keywords
            existing.related_specialty_id = specialty.id if specialty else None
            existing.is_published = True
            if not existing.published_at:
                existing.published_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
            print("Updated existing general checkup article.")
        else:
            article = Article(
                title=title,
                slug=slug,
                category_id=category.id,
                summary=summary,
                content=html_content,
                featured_image=None,
                author_name="RankSewa Team",
                meta_description=meta_description,
                meta_keywords=meta_keywords,
                related_specialty_id=specialty.id if specialty else None,
                is_published=True,
                is_featured=False,
                published_at=datetime.utcnow()
            )
            db.session.add(article)
            print("Created general checkup article.")

        db.session.commit()


if __name__ == "__main__":
    seed_general_checkup_article()
