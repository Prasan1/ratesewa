"""
Sitemap generator for RankSewa
Helps Google discover and index all doctor profiles and articles
"""

from flask import make_response, url_for
from datetime import datetime


def generate_sitemap(app, db):
    """Generate XML sitemap for Google Search Console"""
    from models import Doctor, Article, City, Specialty

    with app.app_context():
        pages = []

        # Homepage (highest priority)
        pages.append({
            'loc': url_for('index', _external=True),
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '1.0'
        })

        # Main pages
        main_routes = [
            ('health_digest', 'weekly', '0.8'),
            ('doctors', 'daily', '0.9'),
            ('pricing', 'monthly', '0.7'),
        ]

        for route, freq, priority in main_routes:
            try:
                pages.append({
                    'loc': url_for(route, _external=True),
                    'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
                    'changefreq': freq,
                    'priority': priority
                })
            except:
                pass  # Skip if route doesn't exist

        # All active doctor profiles
        doctors = Doctor.query.filter_by(is_active=True).all()
        for doctor in doctors:
            pages.append({
                'loc': url_for('doctor_profile', slug=doctor.slug, _external=True),
                'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.9' if doctor.is_verified else '0.7'  # Verified doctors = higher priority
            })

        # All published articles
        articles = Article.query.filter_by(is_published=True).all()
        for article in articles:
            lastmod = article.updated_at if article.updated_at else article.created_at
            pages.append({
                'loc': url_for('article_detail', slug=article.slug, _external=True),
                'lastmod': lastmod.strftime('%Y-%m-%d') if lastmod else datetime.utcnow().strftime('%Y-%m-%d'),
                'changefreq': 'monthly',
                'priority': '0.6'
            })

        # Build XML
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

        for page in pages:
            sitemap_xml += '  <url>\n'
            sitemap_xml += f'    <loc>{page["loc"]}</loc>\n'
            sitemap_xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
            sitemap_xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
            sitemap_xml += f'    <priority>{page["priority"]}</priority>\n'
            sitemap_xml += '  </url>\n'

        sitemap_xml += '</urlset>'

        return sitemap_xml
