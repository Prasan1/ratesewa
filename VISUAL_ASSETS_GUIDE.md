# RateSewa - Visual Assets Guide

## 🎨 Favicon & Logo

### Favicon Created! ✅

A Nepal-inspired favicon has been created with:
- **Temple/pagoda shape** - Represents Nepal's rich heritage
- **Medical cross** - Healthcare focus
- **Star** - Rating/quality theme
- **Nepal flag colors** - Red and blue gradient

**Location:** `static/favicon.svg`

**What it looks like:**
- Circular badge with red-blue gradient
- White temple/pagoda roof shape
- Red medical cross in center
- Gold star in corner

**Browser Support:**
- Modern browsers: SVG favicon
- Fallback: Will work even if .ico file missing

---

## 📸 Doctor Photos - Now Supported!

### ✅ What's New

Admins can now add doctor photos! Here's how it works:

### Adding Photos (Admin Panel)

1. **Go to Admin** → **Manage Doctors**
2. **Add/Edit a Doctor**
3. **Find "Photo URL" field**
4. **Upload photo to image hosting**, then paste URL

### How to Upload Photos

**Option 1: ImgBB (Recommended - Free & Easy)**
1. Go to: https://imgbb.com/
2. Click "Start uploading"
3. Select doctor's photo
4. Click "Upload"
5. Copy the "Direct link" URL
6. Paste into RateSewa Photo URL field

**Option 2: Imgur**
1. Go to: https://imgur.com/upload
2. Upload photo
3. Right-click image → "Copy image address"
4. Paste into RateSewa

**Option 3: Host on Your Server**
- Upload to `/static/doctors/` folder
- Use URL: `/static/doctors/doctor-name.jpg`
- Example: `/static/doctors/dr-rajendra-miya.jpg`

### Photo Requirements

**Recommended:**
- **Size:** 400x400 pixels minimum
- **Format:** JPG or PNG
- **File size:** Under 500KB
- **Style:** Professional headshot
- **Background:** Plain or clinical setting

**Will work:**
- Square or circular photos
- Color or black & white
- Various sizes (will be resized automatically)

### Default Placeholder

If no photo is uploaded:
- System shows a **default avatar**
- Uses https://picsum.photos (random but consistent per doctor)
- Different for each doctor (based on ID)
- Professional looking
- No "broken image" icons

### Technical Details

**Database Field:** `photo_url` (TEXT, nullable)

**Frontend Logic:**
```
If doctor has photo_url → Use it
Else → Use placeholder
If photo fails to load → Fallback to placeholder
```

**Where Photos Appear:**
- Doctor profile page (large, rounded)
- Homepage doctor cards (small, circular)
- Search results

---

## 🎨 Logo Design Recommendations

### Current Branding

**Name:** RateSewa
**Icon:** ⭐ Star (used in navbar)
**Colors:**
- Primary: `#2f6f6d` (Teal/green - medical/trust)
- Accent: `#DC143C` (Crimson red - Nepal flag)
- Secondary: `#003893` (Blue - Nepal flag)

### Logo Concept (For Future)

**Idea: Temple + Medical + Rating**

Elements to combine:
1. **Nepal Pagoda** outline (heritage)
2. **Medical symbol** (caduceus or plus)
3. **Star** for rating
4. **"RateSewa" text** in modern font

**Style:**
- Clean, modern
- Professional medical feel
- Nepali cultural touch
- Works in small sizes (favicon to billboard)

### DIY Logo Options

**Free Tools:**
1. **Canva** - https://canva.com
   - Templates for medical logos
   - Easy to use
   - Free tier available

2. **LogoMakr** - https://logomakr.com
   - Simple drag-and-drop
   - Medical & Nepal elements

3. **Hatchful by Shopify** - https://hatchful.shopify.com
   - AI-powered
   - Multiple variations
   - Free download

**Hire a Designer:**
- Fiverr: $5-$50
- 99designs: Competition style
- Local Nepali designers on Facebook

### Logo Specs Needed

**Sizes to create:**
- Square logo: 512x512px (for app icons)
- Wide logo: 1200x400px (for headers)
- Favicon: 32x32px (already created as SVG!)
- Social media: 1200x630px (for sharing)

**File formats:**
- PNG with transparent background
- SVG (vector, scales perfectly)
- JPG (for backgrounds)

---

## 🖼️ Future Visual Assets

### When You Have Time

**1. Doctor Placeholder Avatar**
- Create generic doctor silhouette
- Professional looking
- Better than random photos
- File: `static/img/default-doctor.png`

**2. Homepage Hero Image**
- Nepal medical scene
- Doctors or hospitals
- Happy patients
- Size: 1920x600px

**3. Social Media Graphics**
- Facebook cover: 820x312px
- Twitter header: 1500x500px
- Instagram posts: 1080x1080px

**4. Email Templates**
- Welcome email banner
- Notification email graphics
- Newsletter header

---

## 📁 Folder Structure (Recommended)

```
static/
├── favicon.svg              ← Favicon (✅ created)
├── favicon.ico              ← Fallback (optional)
├── img/
│   ├── logo.svg             ← Main logo
│   ├── logo-white.svg       ← White version for dark backgrounds
│   ├── default-doctor.png   ← Default doctor avatar
│   └── hero.jpg             ← Homepage hero image
├── doctors/                 ← Doctor photos (if self-hosted)
│   ├── dr-rajendra-miya.jpg
│   ├── dr-shila-rana.jpg
│   └── ...
└── social/                  ← Social media graphics
    ├── facebook-cover.jpg
    ├── twitter-header.jpg
    └── og-image.jpg         ← For link previews
```

---

## ✅ Quick Checklist

- [x] Favicon created (SVG with Nepal theme)
- [x] Favicon added to base template
- [x] Doctor photo field added to database
- [x] Photo URL field in admin form
- [x] Photos display on profile pages
- [x] Photos display in search results
- [x] Fallback to placeholder if missing
- [x] Error handling if photo fails to load
- [ ] Create custom logo (optional)
- [ ] Upload doctor photos (as you add them)
- [ ] Create social media graphics (optional)

---

## 🎯 For Launch Tomorrow

**Minimum (Already Done):**
- ✅ Favicon works
- ✅ Doctor photos supported
- ✅ Default placeholders look professional

**Nice to Have (Can Do Later):**
- Custom logo design
- Upload actual doctor photos
- Social media graphics

---

## 📖 How-To Examples

### Example 1: Add Photo for Dr. Rajendra Prasad Miya

1. Get doctor's professional photo
2. Upload to ImgBB.com
3. Copy direct link: `https://i.ibb.co/xyz123/doctor.jpg`
4. Login to RateSewa admin
5. Go to Manage Doctors
6. Click Edit on Dr. Rajendra Prasad Miya
7. Paste URL in "Photo URL" field
8. Click Save
9. ✅ Photo now shows on profile!

### Example 2: Self-Host Doctor Photo

1. Save photo as `dr-rajendra-miya.jpg`
2. Upload to `static/doctors/` folder
3. In admin panel, enter: `/static/doctors/dr-rajendra-miya.jpg`
4. Save
5. ✅ Photo loads from your server!

---

## 🛠️ Troubleshooting

**Photo doesn't show:**
- Check URL is publicly accessible
- Verify URL starts with `http://` or `https://`
- Try opening URL in new browser tab
- Check image file isn't too large (keep under 2MB)

**Photo looks distorted:**
- Use square photos (same width & height)
- Recommended: 400x400px or larger
- Photos are automatically cropped to circles

**Default placeholder shows instead:**
- This is normal if no photo_url is set
- Add photo URL in admin panel to override

---

## 💡 Pro Tips

1. **Compress photos** before uploading
   - Use TinyPNG.com
   - Reduces file size by 70%
   - Faster page loads

2. **Consistent style** for all doctor photos
   - Same background color
   - Similar lighting
   - Same framing (headshot)
   - Professional attire

3. **Name files clearly**
   - `dr-firstname-lastname.jpg`
   - Easy to manage
   - SEO-friendly

4. **Backup photos**
   - Keep originals in safe place
   - If using external hosting, download copies

---

**Status:** Visual assets system is ready! Favicon live, doctor photos supported.

**Last Updated:** 2025-12-31
