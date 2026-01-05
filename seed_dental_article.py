"""
Seed the dental care article into the Health Digest.
Reads article_dental_care.md and inserts/updates the article in the database.
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
    # Bold first to avoid clashing with italics.
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def markdown_to_html(markdown_text):
    """Convert a limited subset of markdown to HTML for this article."""
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


def seed_dental_article():
    with app.app_context():
        article_path = os.path.join(os.path.dirname(__file__), "article_dental_care.md")
        if not os.path.exists(article_path):
            raise FileNotFoundError("article_dental_care.md not found")

        with open(article_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        html_content = markdown_to_html(markdown_text)

        category = ArticleCategory.query.filter_by(slug="oral-health").first()
        if not category:
            category = ArticleCategory(
                name="Oral Health",
                slug="oral-health",
                description="Dental care, oral hygiene, and prevention tips",
                icon="fa-tooth",
                display_order=9
            )
            db.session.add(category)
            db.session.flush()

        specialty = Specialty.query.filter_by(name="Dentist").first()

        title = "Why Dental Care Matters: A Guide for Nepal"
        slug = slugify(title)

        summary = (
            "Dental care is often ignored in Nepal until pain starts. "
            "This guide explains why regular checkups matter, common issues, "
            "and practical steps to protect your oral health."
        )

        existing = Article.query.filter_by(slug=slug).first()
        if existing:
            existing.title = title
            existing.category_id = category.id
            existing.summary = summary
            existing.content = html_content
            existing.meta_description = "Why dental care matters in Nepal: prevention tips, warning signs, and practical habits for long-term oral health."
            existing.meta_keywords = "dental care Nepal, oral health, dentist Nepal, gum disease, cavities, oral cancer"
            existing.related_specialty_id = specialty.id if specialty else None
            existing.is_published = True
            if not existing.published_at:
                existing.published_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
            print("Updated existing dental care article.")
        else:
            article = Article(
                title=title,
                slug=slug,
                category_id=category.id,
                summary=summary,
                content=html_content,
                featured_image=None,
                author_name="RankSewa Team",
                meta_description="Why dental care matters in Nepal: prevention tips, warning signs, and practical habits for long-term oral health.",
                meta_keywords="dental care Nepal, oral health, dentist Nepal, gum disease, cavities, oral cancer",
                related_specialty_id=specialty.id if specialty else None,
                is_published=True,
                is_featured=False,
                published_at=datetime.utcnow()
            )
            db.session.add(article)
            print("Created dental care article.")

        db.session.commit()


if __name__ == "__main__":
    seed_dental_article()
