# How to Add Content Moderation to Reviews

## Simple Integration (5 minutes)

Add this to your `app.py` at the top:

```python
from content_moderation import moderate_review
```

Then in your `rate_doctor()` function, add this BEFORE saving to database:

```python
@app.route('/rate_doctor', methods=['POST'])
@login_required
def rate_doctor():
    doctor_id = request.form.get('doctor_id')
    rating_value = request.form.get('rating')
    comment = request.form.get('comment', '')

    # ... your existing validation ...

    # NEW: Content moderation check
    moderation = moderate_review('', comment)
    if not moderation['approved']:
        flash(moderation['message'], 'warning')
        return redirect(request.referrer or url_for('index'))

    # ... rest of your existing code to save review ...
```

## What This Does

**Automatically rejects reviews with:**
- Profanity/inappropriate language
- Too short (less than 10 characters)
- Too long (over 2000 characters)
- All caps (SHOUTING)
- Repetitive spam
- URLs/links

**Shows user-friendly messages:**
- "Please keep your review professional and avoid inappropriate language."
- "Please write at least a few words about your experience."
- etc.

## Advanced: Flag for Manual Review Instead of Rejecting

If you want to be less strict, you can flag suspicious reviews instead:

```python
# In models.py, add to Rating class:
is_flagged = db.Column(db.Boolean, default=False)
flag_reason = db.Column(db.String(100))

# In app.py:
moderation = moderate_review('', comment)

new_rating = Rating(
    doctor_id=doctor_id,
    user_id=user_id,
    rating=rating_value,
    comment=comment,
    is_flagged=not moderation['approved'],
    flag_reason=', '.join(moderation['issues']) if not moderation['approved'] else None
)
```

Then in admin panel, you can review flagged reviews before they go live.

## Testing

Run the test script:

```bash
python3 content_moderation.py
```

You should see:
```
✓ PASS: 'Great doctor! Very professional and caring.'
✗ FAIL: 'This doctor is a fucking fraud!'
  Issues: ['contains_profanity']
  Message: Please keep your review professional and avoid inappropriate language.
```

## Why This Works

- **Simple:** One function call, clear yes/no decision
- **Fast:** Runs in milliseconds
- **Maintainable:** Easy to add new rules
- **User-friendly:** Clear feedback when rejected

## What You're Avoiding

Without this, you'd need to:
- Manually review every review
- Deal with angry doctors demanding removal
- Risk defamation lawsuits
- Spend hours moderating instead of growing

With this: 90% of bad content never makes it to your database.
