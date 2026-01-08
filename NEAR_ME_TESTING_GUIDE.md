# "Near Me" Feature - Local Testing Guide

## Overview
The "near me" feature allows users to find doctors sorted by distance from their current location.

## Setup Instructions

### 1. Run Database Migration

```bash
cd /home/ppaudyal/Documents/drprofile/doctor_directory
python3 add_doctor_coordinates.py
```

This will add `latitude` and `longitude` columns to the doctors table.

### 2. Start Flask Application

```bash
export FLASK_APP=app.py
export SECRET_KEY=test-secret-key
python3 app.py
```

The app should start on `http://localhost:5000`

## Testing Steps

### Step 1: Add Coordinates to Test Doctors

1. Go to: `http://localhost:5000/admin/doctors`
2. Login as admin
3. Edit a doctor profile
4. Scroll to the "Geolocation" section
5. Add coordinates:
   - **For Kathmandu doctors**:
     - Latitude: `27.7172`
     - Longitude: `85.3240`
   - **For Lalitpur doctors**:
     - Latitude: `27.6667`
     - Longitude: `85.3333`
   - **For Pokhara doctors**:
     - Latitude: `28.2096`
     - Longitude: `83.9856`

6. Save the doctor profile

**Tip:** Find exact coordinates on Google Maps:
- Open Google Maps
- Right-click on the clinic location
- Click "What's here?"
- Copy the coordinates shown

### Step 2: Test the API Directly

#### Test 1: Get doctors without location (regular search)

```bash
curl "http://localhost:5000/doctors"
```

**Expected:** Returns JSON with all doctors, no `distance_km` field

#### Test 2: Get doctors sorted by distance from Kathmandu center

```bash
curl "http://localhost:5000/doctors?lat=27.7172&lng=85.3240&sort=distance"
```

**Expected:**
- Returns JSON with doctors
- Doctors near Kathmandu show `distance_km` field
- Sorted by closest first

#### Test 3: Get doctors sorted by distance from Pokhara

```bash
curl "http://localhost:5000/doctors?lat=28.2096&lng=83.9856&sort=distance"
```

**Expected:**
- Pokhara doctors appear first (smaller distance_km)
- Kathmandu doctors appear later (200+ km away)

### Step 3: Test in Browser (Optional UI)

Create a simple test page to try the geolocation API:

```html
<!-- Save as test_nearme.html in templates/ folder -->
<!DOCTYPE html>
<html>
<head>
    <title>Near Me Test</title>
</head>
<body>
    <h1>Test "Near Me" Feature</h1>
    <button id="nearMeBtn">Find Doctors Near Me</button>
    <div id="results"></div>

    <script>
    document.getElementById('nearMeBtn').addEventListener('click', function() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                fetch(`/doctors?lat=${lat}&lng=${lng}&sort=distance`)
                    .then(res => res.json())
                    .then(data => {
                        const results = document.getElementById('results');
                        results.innerHTML = '<h2>Nearby Doctors:</h2>';

                        data.doctors.forEach(doc => {
                            const distanceText = doc.distance_km
                                ? `${doc.distance_km} km away`
                                : 'Distance unknown';

                            results.innerHTML += `
                                <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
                                    <h3>${doc.name}</h3>
                                    <p>${doc.specialty_name} - ${doc.city_name}</p>
                                    <p><strong>${distanceText}</strong></p>
                                </div>
                            `;
                        });
                    });
            });
        }
    });
    </script>
</body>
</html>
```

## Expected Behavior

### When User Has Coordinates
- Doctors with lat/lng show actual distances (e.g., "2.5 km away")
- Sorted closest to farthest
- Doctors without coordinates appear at the end

### When User Doesn't Provide Location
- Standard search (sorted by rating/relevance)
- No distance information shown

## Sample Test Data

Add these coordinates to some doctors for testing:

| Location | Doctor | Latitude | Longitude |
|----------|--------|----------|-----------|
| Kathmandu (Bansbari - NMC area) | Dr. Test 1 | 27.7325 | 85.3240 |
| Lalitpur (Patan Dhoka) | Dr. Test 2 | 27.6667 | 85.3200 |
| Bhaktapur (Durbar Square) | Dr. Test 3 | 27.6710 | 85.4298 |
| Pokhara (Lakeside) | Dr. Test 4 | 28.2096 | 83.9856 |
| Biratnagar (Center) | Dr. Test 5 | 26.4525 | 87.2718 |

## Troubleshooting

### Issue: "latitude/longitude column doesn't exist"
**Solution:** Run the migration script first: `python3 add_doctor_coordinates.py`

### Issue: Geolocation permission denied
**Solution:**
- Check browser console for errors
- Make sure you're accessing via HTTPS (or localhost)
- Click "Allow" when browser asks for location permission

### Issue: All distances show as 9999 km
**Solution:** Check that doctors have latitude/longitude values set in admin panel

### Issue: Distances seem wrong
**Solution:**
- Verify coordinates are in decimal degrees format (not DMS)
- Check coordinates are for Nepal (lat: 26-30, lng: 80-88)
- Make sure latitude/longitude aren't swapped

## What to Check

✅ Database has latitude/longitude columns
✅ Admin form shows coordinate input fields
✅ Coordinates save correctly when editing doctor
✅ API returns distance_km when lat/lng/sort provided
✅ Doctors sorted by distance (closest first)
✅ Doctors without coordinates appear at end
✅ Distance calculation seems accurate (use Google Maps to verify)

## Next Steps After Testing

Once local testing is successful:

1. Test with real doctor addresses
2. Add UI components to frontend (homepage, search results)
3. Deploy to production
4. Monitor for any issues

## Useful Resources

- **Google Maps Coordinate Finder**: https://www.google.com/maps
- **Distance Calculator**: https://www.distance.to/
- **Haversine Formula**: https://en.wikipedia.org/wiki/Haversine_formula

## Questions?

If you encounter issues:
1. Check browser console for errors
2. Check Flask server logs
3. Verify database has been migrated
4. Test API endpoint directly with curl first
