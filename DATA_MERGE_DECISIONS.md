# Data Merge Decisions

## Dataset Overview

We merged two hotel booking datasets:
- Customer reservations: 36,275 records from customer booking system
- Hotel bookings: 78,705 records from hotel management system
- Total merged: 114,980 records

## Key Challenges

1. **Different column names for same data**
   - `Booking_ID` (customer) vs no ID field (hotel)
   - `arrival_date` (customer) vs `arrival_date_day_of_month` (hotel)

2. **Different data formats**
   - booking_status: text in Customer Reservations, 0/1 in Hotel Bookings
   - arrival_month: numeric in Customer Reservations, text names in Hotel Bookings

3. **Missing columns**
   - Customer Reservations missing: hotel, country, email, arrival_date_week_number (added as NULL)
   - Hotel Bookings missing: booking_id (generated with offset to prevent ID collision)

## Cleaning Decisions

### Customer Reservations Dataset
- Renamed `Booking_ID` to `booking_id` for consistency
- Renamed `arrival_date` to `arrival_date_day_of_month`
- Added missing columns with NULL values:
  - hotel = NULL
  - country = NULL
  - email = NULL
  - arrival_date_week_number = NULL
- Removed duplicate rows

### Hotel Bookings Dataset
- Converted booking_status from 0/1 to 'Not_Canceled'/'Canceled' to match customer reservations dataset format
- Converted arrival_month from text (January, February...) to numeric (1, 2, ..., 12)
- Generated booking_id with format INN50000, INN50001, etc. (offset to avoid collision with customer IDs)
- Removed duplicate rows

### Final Merged Dataset
- Converted booking_status to boolean field `is_canceled` (True/False)
- Renamed booking_id to `id` for simplicity
- Both datasets aligned to 14 common columns before merging

## Merge Approach

Used UNION operation (vertical concatenation) rather than JOIN because:
- Datasets come from independent systems
- No natural join key between them
- Goal is to combine all records, not match them
- Preserves all records from both sources

After union, removed duplicate rows based on business fields (excluding booking_id) to ensure data quality. Deduplication uses: hotel, lead_time, arrival dates, stay nights, market segment, country, price, and email.

## Final Schema

Merged dataset has 14 columns:
- id
- hotel
- is_canceled (boolean)
- lead_time
- arrival_year
- arrival_month
- arrival_date_week_number
- arrival_date_day_of_month
- stays_in_weekend_nights
- stays_in_week_nights
- market_segment_type
- country
- avg_price_per_room
- email

## Notes

- Missing data represented as NULL (blank in CSV) for proper database handling
- Boolean is_canceled field is database-ready and more intuitive than text status
- booking_id renamed to id for simplicity
- Hotel booking IDs start at INN50000 to avoid collision with customer IDs (INN00001-INN36275)