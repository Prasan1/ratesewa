# RankSewa Product Roadmap

**Last Updated:** January 2, 2026
**Current Version:** 1.0 MVP

---

## Vision

Become Nepal's #1 platform for healthcare discovery, empowering patients to make informed decisions and helping doctors build their online reputation.

---

## Current Status (v1.0 - MVP Launched)

### ✅ Live Features
- Patient can search & discover doctors
- Patient can write reviews & earn rewards (gamification)
- Doctors can claim profiles
- All features FREE until April 25, 2026
- Health Digest (SEO content)
- OAuth login (Google)

### 📊 Success Metrics to Track
- Active users (weekly/monthly)
- Reviews written per week
- Doctor signups per week
- Health Digest traffic (organic vs social)
- Search-to-profile-view conversion rate

---

## Immediate Next Steps (Q1 2026 - Jan-Mar)

### Priority 1: Growth & Stability
- [ ] **Add Google Analytics** - Track user behavior
- [ ] **Add error monitoring** (Sentry or Rollbar)
- [ ] **Email notifications** when:
  - Doctor gets new review
  - User's review gets a response
  - User earns a new badge
- [ ] **Social sharing** - Improve share buttons on profiles
- [ ] **SEO improvements:**
  - Sitemap generation
  - Structured data (Schema.org) for doctors
  - Meta descriptions for all pages

### Priority 2: User Engagement
- [ ] **Helpful vote notifications** - Alert users when their review is marked helpful
- [ ] **Weekly/monthly leaderboards** - Create time-based competition
- [ ] **Review of the week** - Feature exceptional reviews
- [ ] **User profiles public** - Let users show off their badges
- [ ] **Referral system** - Users invite friends, earn bonus points

### Priority 3: Doctor Value-Add
- [ ] **Doctor dashboard improvements:**
  - Better analytics (demographics, traffic sources)
  - Review response templates
  - Export reviews as PDF
- [ ] **Verified patient badge** - Mark reviews from confirmed patients
- [ ] **Doctor comparison** - Let patients compare 2-3 doctors side-by-side

### Metrics Goal by End of Q1:
- 100+ active doctors
- 500+ reviews
- 1,000+ MAU (monthly active users)
- 10,000+ monthly organic visits

---

## Q2 2026 (Apr-Jun): Monetization & Growth

### Phase 1: Paid Tiers Go Live (April 26, 2026)
- [ ] **Implement Stripe payments**
- [ ] **Subscription management dashboard** for doctors
- [ ] **Grace period** (30 days) before downgrading
- [ ] **Email campaign** to notify doctors 30 days before pricing starts
- [ ] **Early adopter discount** - 20% off for first 100 paying doctors

### Phase 2: Advanced Features
- [ ] **Appointment booking integration:**
  - Simple calendar widget for doctors
  - Email/SMS confirmation to patients
  - Reminder system (1 day before)
- [ ] **Doctor working hours** - Show availability on profile
- [ ] **Insurance accepted** - Filter by insurance provider
- [ ] **Languages spoken** - Filter by doctor's languages

### Phase 3: Content Expansion
- [ ] **Allow top contributors to write articles** (gamification reward)
- [ ] **Video content** - Doctor Q&A videos
- [ ] **Health news** - Weekly roundup of Nepal health news
- [ ] **Patient stories** - Success stories from the community

### Metrics Goal by End of Q2:
- 200+ active doctors
- 50+ paying doctors (conversion rate target: 25%)
- 2,000+ MAU
- 25,000+ monthly organic visits
- Revenue: NPR 100,000+/month

---

## Q3-Q4 2026: Scale & New Features

### Clinic Manager Accounts (When Ready)
**Prerequisites:**
- ✅ 50+ active doctors achieved
- ✅ 3+ clinics expressing interest
- ✅ Proven payment flow working

**Implementation:**
- [ ] Re-enable clinic pricing tiers
- [ ] Clinic manager onboarding flow
- [ ] Multi-doctor management dashboard
- [ ] Bulk operations (edit multiple profiles)
- [ ] Clinic-level analytics

### Mobile App (When Ready)
**Prerequisites:**
- ✅ 5,000+ MAU
- ✅ Strong retention (30% return rate)
- ✅ Proven revenue model

**Features:**
- iOS & Android apps
- Push notifications (new review, response, badge)
- Offline mode for saved doctors
- Location-based recommendations
- Quick review submission

### Advanced Search & Discovery
- [ ] **AI-powered recommendations** - Suggest doctors based on symptoms
- [ ] **Filter by:**
  - Hospital affiliations
  - Insurance accepted
  - Telemedicine availability
  - Gender preference
  - Languages spoken
- [ ] **Map view** - See nearby doctors on a map
- [ ] **Virtual consultations** - Book video calls with doctors

### Community Features
- [ ] **Q&A Forum** - Ask health questions, doctors answer
- [ ] **Doctor AMA (Ask Me Anything)** - Live sessions
- [ ] **Patient support groups** - Connect patients with similar conditions
- [ ] **Health challenges** - Gamified wellness programs

### Metrics Goal by End of 2026:
- 500+ active doctors
- 150+ paying doctors
- 10,000+ MAU
- 100,000+ monthly visits
- Revenue: NPR 500,000+/month

---

## Long-Term Vision (2027+)

### Product Expansion
- [ ] **Telemedicine platform** - Built-in video consultation
- [ ] **Prescription management** - Digital prescriptions
- [ ] **Health records** - Personal health record storage
- [ ] **Pharmacy integration** - Order medicines from reviewed pharmacies
- [ ] **Lab test booking** - Schedule lab tests online
- [ ] **Hospital reviews** - Expand beyond individual doctors

### Geographic Expansion
- [ ] Cover all major cities in Nepal (currently: Kathmandu, Pokhara, etc.)
- [ ] Include hospitals and clinics outside major cities
- [ ] Regional language support (Nepali, Newari, etc.)

### Advanced Analytics & AI
- [ ] **Sentiment analysis** on reviews
- [ ] **Predictive analytics** for doctor demand
- [ ] **Chatbot** for health guidance
- [ ] **Symptom checker** - AI-powered triage

### B2B Offerings
- [ ] **Hospital dashboard** - Manage multiple doctors
- [ ] **Corporate wellness** - Company health programs
- [ ] **Insurance partnerships** - Direct billing
- [ ] **White-label solution** - Sell platform to hospitals

---

## Feature Backlog (Ideas for Future)

### Patient Experience
- Edit/delete own reviews (within 24 hours)
- Compare doctors side-by-side
- Save favorite doctors
- Share doctor profiles
- Request appointment via WhatsApp
- Doctor wait time estimates
- Real patient photos (with consent)

### Doctor Tools
- Automated appointment reminders
- Patient feedback surveys
- Marketing analytics dashboard
- Competitor analysis
- SEO tips for profile optimization
- Export patient insights
- Integration with practice management software

### Content & SEO
- Health calculator tools (BMI, pregnancy due date, etc.)
- Disease-specific landing pages
- Doctor interviews and spotlights
- Patient success stories
- Health tips newsletter
- Seasonal health campaigns

### Technical Improvements
- [ ] **Performance:** Redis caching, CDN for all assets
- [ ] **Search:** Elasticsearch for better search
- [ ] **API:** Public API for third-party integrations
- [ ] **PWA:** Progressive Web App for offline capability
- [ ] **A/B Testing:** Test features before full rollout

---

## Risks & Mitigation

### Risk 1: Doctors don't pay after April 25
**Mitigation:**
- Early communication (30 days notice)
- Show clear value (analytics, review responses)
- Offer discounts for annual payment
- Free tier always available (basic listing)

### Risk 2: Low user engagement / Not enough reviews
**Mitigation:**
- Gamification keeps users coming back
- Email campaigns to inactive users
- Contests and challenges
- Reward top reviewers with special badges

### Risk 3: Fake reviews / Spam
**Mitigation:**
- Verified patient badges (coming soon)
- Flag/report system (already built)
- Admin review queue
- Rate limiting on review submission (TODO)
- CAPTCHA (TODO)

### Risk 4: Competition from larger platforms
**Mitigation:**
- Focus on Nepal market (local advantage)
- Build community, not just directory
- Gamification creates stickiness
- Health Digest for SEO moat
- Respond faster to user feedback

### Risk 5: Technical infrastructure can't scale
**Mitigation:**
- DigitalOcean auto-scales
- Add caching before bottlenecks
- Monitor performance metrics
- Database optimization
- CDN for static assets

---

## Decision Log

### Major Decisions Made

**Jan 2, 2026 - Hide Clinic Manager Features for MVP**
- **Decision:** Remove clinic pricing from public view
- **Reason:** Too complex for MVP, need market validation first
- **Reversible:** Yes, code intact, see CLINIC_FEATURE_GUIDE.md
- **Next Review:** When we hit 50+ active doctors

**Dec 2025 - Add Gamification**
- **Decision:** Implement points, badges, leaderboard
- **Reason:** Solve "no immediate value for users" problem
- **Result:** TBD (just launched)

**Dec 2025 - Add Health Digest**
- **Decision:** Create SEO-driven health content
- **Reason:** Attract organic traffic, position as health resource
- **Result:** TBD (just launched)

**Dec 2025 - Free Until April 25**
- **Decision:** All features free during launch period
- **Reason:** Remove friction, build user base first
- **Tradeoff:** Delayed revenue, but better long-term

---

## Experiment Ideas (To Test)

### Growth Experiments
- [ ] Referral rewards (both parties get points)
- [ ] Doctor leaderboard (most reviewed, highest rated)
- [ ] Limited-time badges (review 3 doctors this month)
- [ ] Social proof on homepage (X reviews written today)
- [ ] Exit intent popup (don't leave without reviewing)

### Monetization Experiments
- [ ] Annual subscription discount (2 months free)
- [ ] Freemium features (basic analytics free, advanced paid)
- [ ] Sponsored placements (different from featured)
- [ ] Premium badges (featured + promoted)

### Engagement Experiments
- [ ] Email digests (top doctors in your area this week)
- [ ] Push notifications for new doctors in favorite specialty
- [ ] Streak rewards (review daily for a week)
- [ ] Challenges (review 3 specialties, unlock badge)

---

## Success Criteria for Each Phase

### MVP Success (by Mar 2026):
- ✅ 100+ doctors claimed profiles
- ✅ 500+ reviews written
- ✅ 1,000+ registered users
- ✅ 10% user retention (return in 30 days)

### Growth Success (by Jun 2026):
- ✅ 25% free-to-paid conversion on April 26
- ✅ 50+ active paying doctors
- ✅ 20% MoM growth in new users
- ✅ NPR 100K+ MRR

### Scale Success (by Dec 2026):
- ✅ 500+ total doctors
- ✅ 150+ paying doctors
- ✅ 10,000+ MAU
- ✅ NPR 500K+ MRR
- ✅ Break-even or profitable

---

## Resources Needed

### Immediate (Q1 2026)
- **Time:** 10-15 hrs/week for maintenance & growth features
- **Money:**
  - Hosting: $25/month (DigitalOcean)
  - Domain: $15/year
  - Email service: $15/month (SendGrid)
  - Error monitoring: $26/month (Sentry)
  - **Total:** ~$70/month

### Growth Phase (Q2-Q4 2026)
- **Time:** 20-30 hrs/week (consider part-time help)
- **Money:**
  - Increased hosting: $50-100/month
  - Marketing: $200-500/month (Google Ads, Facebook)
  - Design help: $500-1000 one-time
  - **Total:** ~$300-700/month

### Scale Phase (2027+)
- **Time:** Full-time or hire team
- **Money:**
  - Hosting: $200+/month
  - Marketing: $2,000+/month
  - Team: Salaries for developer, designer, marketer
  - **Total:** Depends on funding/revenue

---

## When to Pivot / Shut Down

### Red Flags to Watch
- ⚠️ After 6 months, still <50 active doctors
- ⚠️ After April 26, <10% conversion to paid
- ⚠️ User retention <5% (nobody comes back)
- ⚠️ Revenue consistently <operating costs
- ⚠️ Better funded competitor dominates market

### Pivot Options
- **Pivot 1:** Focus only on clinics (B2B model)
- **Pivot 2:** Sell to hospitals (white-label)
- **Pivot 3:** Become content site (Health Digest focus)
- **Pivot 4:** Telemedicine platform (not directory)

---

## How to Use This Roadmap

1. **Review quarterly** - Update based on actual progress
2. **Prioritize ruthlessly** - Don't try to build everything
3. **Validate assumptions** - Test before big builds
4. **Celebrate milestones** - Acknowledge progress
5. **Stay flexible** - Adjust based on user feedback

**Remember:** This is a living document. Reality > Plan.

---

**Next Review Date:** April 1, 2026 (post-launch review)
