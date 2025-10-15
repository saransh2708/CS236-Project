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
   - Customer Reservations missing: hotel, country, email, arrival_date_week_number
   - Hotel Bookings missing: booking_id

## Cleaning Decisions

### Customer Reservations Dataset
- Renamed `Booking_ID` to `booking_id` for consistency
- Renamed `arrival_date` to `arrival_date_day_of_month`
- Added missing columns with default values:
  - hotel = 'Unknown'
  - country = 'Unknown'
  - email = 'Unknown'
  - arrival_date_week_number = 0

### Hotel Bookings Dataset
- Converted booking_status from 0/1 to 'Not_Canceled'/'Canceled' to match customer format
- Converted arrival_month from text (January, February...) to numeric (1, 2, ..., 12)
- Generated booking_id with format HTL000001, HTL000002, etc.

### Final Merged Dataset
- Converted booking_status to boolean field `is_canceled` (True/False)
- Added `data_source` column to track which system each record came from
- Both datasets aligned to 15 common columns before merging

## Merge Approach

Used UNION operation (vertical concatenation) rather than JOIN because:
- Datasets come from independent systems
- No natural join key between them
- Goal is to combine all records, not match them
- Preserves all records from both sources

## Final Schema

Merged dataset has 15 columns:
- booking_id
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
- data_source

## Notes

- Used 'Unknown' instead of NULL for missing data to be explicit about what's missing
- Boolean is_canceled field is database-ready and more intuitive than text status
- data_source field allows filtering and analysis by original system