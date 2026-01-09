#!/usr/bin/env python3
"""
Simple content moderation for reviews
English-only profanity detection and quality checks
"""

from better_profanity import profanity

# Initialize profanity filter
profanity.load_censor_words()

def check_review_content(text):
    """
    Check review content for profanity and quality issues

    Returns:
        dict: {
            'is_clean': bool,
            'issues': list of issues found,
            'censored_text': text with profanity censored (for logging)
        }
    """
    issues = []

    # Check for profanity
    if profanity.contains_profanity(text):
        issues.append('contains_profanity')

    # Check minimum length (prevent spam)
    words = [w for w in text.strip().split() if w]
    if len(words) < 2:
        issues.append('too_short')

    # Check maximum length (prevent spam)
    if len(text) > 2000:
        issues.append('too_long')

    # Check for all caps (usually spam/rant)
    if text.isupper() and len(text) > 20:
        issues.append('all_caps')

    # Check for excessive repetition (spam detection)
    words = text.split()
    if len(words) > 5 and len(set(words)) / len(words) < 0.3:
        issues.append('repetitive')

    # Check for URL spam
    if 'http://' in text.lower() or 'https://' in text.lower() or 'www.' in text.lower():
        issues.append('contains_url')

    return {
        'is_clean': len(issues) == 0,
        'issues': issues,
        'censored_text': profanity.censor(text)
    }


def moderate_review(rating_text, comment_text=''):
    """
    Moderate a review before saving to database

    Returns:
        dict: {
            'approved': bool,
            'issues': list,
            'message': str (user-friendly message if rejected)
        }
    """
    # Check rating text (doctor name, etc) - only if provided
    if rating_text and rating_text.strip():
        rating_check = check_review_content(rating_text)
    else:
        rating_check = {'is_clean': True, 'issues': []}

    # Check comment if provided
    if comment_text and comment_text.strip():
        comment_check = check_review_content(comment_text)
    else:
        comment_check = {'is_clean': True, 'issues': []}

    # Combine issues
    all_issues = rating_check['issues'] + comment_check['issues']

    # Determine if approved
    approved = len(all_issues) == 0

    # Generate user-friendly message
    message = ''
    if not approved:
        if 'contains_profanity' in all_issues:
            message = 'Please keep your review professional and avoid inappropriate language.'
        elif 'too_short' in all_issues:
            message = 'Please write at least a few words about your experience.'
        elif 'too_long' in all_issues:
            message = 'Your review is too long. Please keep it under 2000 characters.'
        elif 'all_caps' in all_issues:
            message = 'Please don\'t write in all capital letters.'
        elif 'repetitive' in all_issues:
            message = 'Your review appears repetitive. Please write a genuine experience.'
        elif 'contains_url' in all_issues:
            message = 'Please don\'t include links in your review.'
        else:
            message = 'Your review doesn\'t meet our community guidelines.'

    return {
        'approved': approved,
        'issues': all_issues,
        'message': message
    }


# Example usage
if __name__ == '__main__':
    # Test cases
    test_reviews = [
        ("Great doctor! Very professional and caring.", True),
        ("This doctor is a fucking fraud!", False),
        ("Good", False),  # Too short
        ("TERRIBLE TERRIBLE TERRIBLE DOCTOR!!!", False),  # All caps + repetitive
        ("Check out my website www.spam.com", False),  # URL
    ]

    print("Testing content moderation:\n")
    for text, should_pass in test_reviews:
        result = moderate_review('', text)
        status = "✓ PASS" if result['approved'] == should_pass else "✗ FAIL"
        print(f"{status}: '{text[:50]}'")
        if not result['approved']:
            print(f"  Issues: {result['issues']}")
            print(f"  Message: {result['message']}")
        print()
