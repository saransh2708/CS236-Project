# Phase 1: Data Preparation & EDA in Spark  
**Course:** CS236 — Database Managenebt System  
**Authors:**  
- **Pankaj Sharma** (SID: XXXXXXXX)
- **Saransh Gupta** (SID: 862548920)  

---

## 0. Executive Summary
In this phase, we set up a local PySpark environment, used two CSV datasets (`customer-reservations.csv` and `hotel-booking.csv`), performed exploratory data analysis (EDA), and data preprocessing.  

---

## 1. Installation Process

### 1.1 Unpack the Project
```bash
unzip CS236-Project.zip
cd CS236-Project
```

### 1.2 Creating a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.4 Installing Java 11
```bash
brew install openjdk@11
export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home
export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
```

### 1.5 Running the Script
```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home \
&& export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH" \
&& spark-submit phase1-eda.py
```

## 2. Exploratory Data Analysis Process
This sections contains EDA process and findings that we performed on the datasets - `customer-reservations.csv` and `hotel-booking.csv`. Here we will answer What, Why and Insights we gained from the EDA steps that we performed.

---

### 2.1 Schema Inspection

#### Customer Reservations Schema

| Column Name | Data Type | Nullable |
|--------------|------------|-----------|
| Booking_ID | string | True |
| stays_in_weekend_nights | integer | True |
| stays_in_week_nights | integer | True |
| lead_time | integer | True |
| arrival_year | integer | True |
| arrival_month | integer | True |
| arrival_date | integer | True |
| market_segment_type | string | True |
| avg_price_per_room | double | True |
| booking_status | string | True |

---

#### Hotel Bookings Schema

| Column Name | Data Type | Nullable |
|--------------|------------|-----------|
| hotel | string | True |
| booking_status | integer | True |
| lead_time | integer | True |
| arrival_year | integer | True |
| arrival_month | string | True |
| arrival_date_week_number | integer | True |
| arrival_date_day_of_month | integer | True |
| stays_in_weekend_nights | integer | True |
| stays_in_week_nights | integer | True |
| market_segment_type | string | True |
| country | string | True |
| avg_price_per_room | double | True |
| email | string | True |


#### Why:
We did this step to confirm proper loading of datasets using PySpark and to get brief idea about the dataset like columns and its data types.

#### Insights:
- *Customer Reservations:* This Dataset contains columns of different data types. We have Numeric fields such as `lead_time`, `arrival_year`, and `avg_price_per_room`, and categorical fields like `market_segment_type` and `booking_status` were `StringType`.  
- *Hotel Bookings:* This Dataset contains columns of 2 data types. `arrival_month` was inferred as a `StringType` (e.g., "July", "September"), while other date components were integers.  

--- 

### 2.2 Size Inspection

#### Why:
We did to check the size of the database in order to fit within Spark in memory limits.

#### Insights:
- *Customer Reservations:* **36,275 rows × 10 columns** — each row represents one unique booking (`Booking_ID`).  
- *Hotel Bookings:* **78,703 rows × 13 columns** — includes additional contextual fields such as `hotel`, `country`, and `email`.  
- Both datasets are of moderate size and fit comfortably within Spark’s in-memory analysis limits.

### 2.3 Missing Values
#### Missing Values Count — Customer Reservations

| Column Name | Missing Values |
|--------------|----------------|
| Booking_ID | 0 |
| stays_in_weekend_nights | 0 |
| stays_in_week_nights | 0 |
| lead_time | 0 |
| arrival_year | 0 |
| arrival_month | 0 |
| arrival_date | 0 |
| market_segment_type | 0 |
| avg_price_per_room | 0 |
| booking_status | 0 |

---

#### Missing Values Count — Hotel Bookings

| Column Name | Missing Values |
|--------------|----------------|
| hotel | 0 |
| booking_status | 0 |
| lead_time | 0 |
| arrival_year | 0 |
| arrival_month | 0 |
| arrival_date_week_number | 0 |
| arrival_date_day_of_month | 0 |
| stays_in_weekend_nights | 0 |
| stays_in_week_nights | 0 |
| market_segment_type | 0 |
| country | 405 |
| avg_price_per_room | 0 |
| email | 0 |

#### Why:
We did this step to find incomplete fields to decide whether to remove them or to fill in mean value.

#### Insights:
- *Customer Reservations:* **0 missing values** across all the columns.  
- *Hotel Bookings:* Only the `country` column contained **405 missing values** all other columns were complete.  
- Overall both the dataset were almost complete with only Hotel Booking having very less percentage of missing values.

---

### 2.4 Distinct Values Inspection

#### Distinct Values Count — Customer Reservations

| Column Name | Distinct Count |
|--------------|----------------|
| Booking_ID | 36,275 |
| stays_in_weekend_nights | 8 |
| stays_in_week_nights | 18 |
| lead_time | 352 |
| arrival_year | 2 |
| arrival_month | 12 |
| arrival_date | 31 |
| market_segment_type | 5 |
| avg_price_per_room | 3,930 |
| booking_status | 2 |

---

#### Distinct Values Count — Hotel Bookings

| Column Name | Distinct Count |
|--------------|----------------|
| hotel | 2 |
| booking_status | 2 |
| lead_time | 439 |
| arrival_year | 2 |
| arrival_month | 12 |
| arrival_date_week_number | 53 |
| arrival_date_day_of_month | 31 |
| stays_in_weekend_nights | 17 |
| stays_in_week_nights | 32 |
| market_segment_type | 8 |
| country | 159 |
| avg_price_per_room | 6,985 |
| email | 77,144 

#### Why:
This is essential EDA process which results in determining primary keys, redundancy and also helps in process of prediction.

#### Insights:
- *Customer Reservations:*  
  - `Booking_ID` had **36,275 unique values**, which means every row can be uniquely identified from the `Booking_ID` hence it can be used as a primary.  
  - `market_segment_type` had **5 categories** and can be used to draw significant inference from the data.  
  - `booking_status` had **2 values** — *Canceled* and *Not_Canceled*.  
  - No duplicate rows found.  
- *Hotel Bookings:*  
  - `hotel` had 2 values (*City Hotel*, *Resort Hotel*).  
  - `market_segment_type` had 8 categories.  
  - `country` had 159 unique codes.  
  - `email` had 77,144 unique entries, nearly matching total rows, implying one booking per customer.  

---

### 2.5 Correlation Inspection

#### Correlation map - Customer Reservations
![Correlation for Customer Reservation](./output/eda_customer_reservartions_correlation.png)

#### Correlation map - Hotel Bookings
![Correlation for Customer Reservation](./output/eda_hotel_bookings_correlation.png)

#### Why: 
This steps helps us in finding strong and weak relationships between continuous variables.
 
#### Insights:
- **Customer Reservations**
  - `stays_in_week_nights` and `stays_in_weekend_nights` show a **moderate positive correlation (0.18)** which seems reasonable as customers might extend their stays for the weekend if booked initially for the week days.
  - `lead_time` has **very weak or no correlation** with `avg_price_per_room` (≈ -0.06). This insight was kind of surprising as booking earlier had little or no effect in average room price.
  - Other relationships are near zero, confirming that most numeric fields (dates, lead time, price) are largely independent.

- **Hotel Bookings**
  - `stays_in_week_nights` and `stays_in_weekend_nights` have a **strong positive correlation (~0.50)** with same reasoning as above.
  - `lead_time` and `booking_status` are **positively correlated (~0.33)** which means bookings made far in advance are slightly more likely to be canceled.  
  - `lead_time` and `avg_price_per_room` show a **weak negative correlation (-0.10)** — earlier bookings tend to be marginally cheaper.
  - Other variables show near-zero correlations, suggesting minimal temporal dependencies.

---

### Summary

Both the datasets are well structured and mostly clean. With EDA steps performed, we were able to find some useful insights from the datasets. These findings are useful in next steps of the data pre processing. 