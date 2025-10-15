from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import matplotlib.pyplot as plt
import sys
import seaborn as sns
import os
import shutil


def save_single_csv(df, output_path):
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    temp_dir = output_path + "_temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    df.coalesce(1).write.mode('overwrite').option('header', 'true').csv(temp_dir)
    
    csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
    if csv_files:
        csv_file = csv_files[0]
        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.move(os.path.join(temp_dir, csv_file), output_path)
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def perform_eda(df, data_name="dataset"):
    print("\n" + "="*80)
    print(f"EDA: {data_name}")
    print("="*80)
    
    print("\nSchema:")
    df.printSchema()

    print("\nRow Count:", df.count())
    print("Column Count:", len(df.columns))
    print("\nColumns:", df.columns)

    print("\nData Sample:")
    df.show(5)

    print("\nSummary Statistics:")
    df.describe().show()

    print("\nMissing Values Count:")
    missing_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns])
    missing_counts.show()

    print("\nDistinct Values Count:")
    distinct_counts = df.agg(*[countDistinct(c).alias(c) for c in df.columns])
    distinct_counts.show()

    numeric_cols = [f.name for f in df.schema.fields if isinstance(f.dataType, (IntegerType, DoubleType, FloatType, LongType))]
    if len(numeric_cols) > 1:
        pdf = df.select(numeric_cols).toPandas()
        corr = pdf.corr()
        plt.figure(figsize=(8,6))
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title(f'Correlation Matrix for {data_name}')
        plt.tight_layout()
        plt.savefig(f'output/eda_{data_name}_correlation.png')
        plt.close()
        print(f"\nCorrelation matrix saved to: output/eda_{data_name}_correlation.png")


def analyze_columns(customer_df, hotel_df):
    print("\n" + "="*80)
    print("Column Analysis")
    print("="*80)
    
    customer_cols = set(customer_df.columns)
    hotel_cols = set(hotel_df.columns)
    
    common_cols = customer_cols.intersection(hotel_cols)
    customer_only = customer_cols - hotel_cols - {'Booking_ID', 'arrival_date'}
    hotel_only = hotel_cols - customer_cols - {'booking_status', 'arrival_date_day_of_month'}
    
    print(f"\nCommon columns ({len(common_cols)}): {sorted(common_cols)}")
    print(f"Customer-only columns: {sorted(customer_only)}")
    print(f"Hotel-only columns: {sorted(hotel_only)}")
    print(f"\nCustomer records: {customer_df.count():,}")
    print(f"Hotel records: {hotel_df.count():,}")


def clean_customer_data(customer_df):
    print("\n" + "-"*80)
    print("Cleaning Customer Data")
    print("-"*80)
    
    customer_clean = customer_df \
        .withColumnRenamed('Booking_ID', 'booking_id') \
        .withColumnRenamed('arrival_date', 'arrival_date_day_of_month')
    
    customer_clean = customer_clean \
        .withColumn('hotel', lit('Unknown')) \
        .withColumn('country', lit('Unknown')) \
        .withColumn('email', lit('Unknown')) \
        .withColumn('arrival_date_week_number', lit(None).cast('integer'))
    
    print("Renamed columns and added missing fields")
    return customer_clean


def clean_hotel_data(hotel_df):
    print("\n" + "-"*80)
    print("Cleaning Hotel Data")
    print("-"*80)
    
    hotel_clean = hotel_df.withColumn(
        'booking_status',
        when(col('booking_status') == 0, 'Not_Canceled').otherwise('Canceled')
    )
    
    hotel_clean = hotel_clean.withColumn(
        'arrival_month',
        when(col('arrival_month') == 'January', 1)
        .when(col('arrival_month') == 'February', 2)
        .when(col('arrival_month') == 'March', 3)
        .when(col('arrival_month') == 'April', 4)
        .when(col('arrival_month') == 'May', 5)
        .when(col('arrival_month') == 'June', 6)
        .when(col('arrival_month') == 'July', 7)
        .when(col('arrival_month') == 'August', 8)
        .when(col('arrival_month') == 'September', 9)
        .when(col('arrival_month') == 'October', 10)
        .when(col('arrival_month') == 'November', 11)
        .when(col('arrival_month') == 'December', 12)
        .otherwise(0)
    )
    
    hotel_clean = hotel_clean.withColumn(
        'booking_id',
        concat(lit('HTL'), lpad(monotonically_increasing_id().cast('string'), 6, '0'))
    )
    
    # Reorder columns with booking_id first
    other_cols = [c for c in hotel_clean.columns if c != 'booking_id']
    hotel_clean = hotel_clean.select(['booking_id'] + other_cols)
    
    print("Standardized booking_status and arrival_month, generated booking IDs")
    return hotel_clean


def merge_datasets(customer_df, hotel_df):
    print("\n" + "="*80)
    print("Data Merge Process")
    print("="*80)
    
    analyze_columns(customer_df, hotel_df)
    
    customer_clean = clean_customer_data(customer_df)
    hotel_clean = clean_hotel_data(hotel_df)
    
    print("\n" + "-"*80)
    print("Saving cleaned datasets")
    print("-"*80)
    save_single_csv(customer_clean, 'output/customer_reservations_cleaned.csv')
    print("Saved: output/customer_reservations_cleaned.csv")
    save_single_csv(hotel_clean, 'output/hotel_bookings_cleaned.csv')
    print("Saved: output/hotel_bookings_cleaned.csv")
    
    print("\n" + "-"*80)
    print("Aligning schemas")
    print("-"*80)
    
    customer_for_merge = customer_clean.withColumn('data_source', lit('customer_reservations'))
    hotel_for_merge = hotel_clean.withColumn('data_source', lit('hotel_bookings'))

    # Added manually after inspecting common columns and EDA results
    unified_columns = [
        'booking_id', 'hotel', 'booking_status', 'lead_time', 
        'arrival_year', 'arrival_month', 'arrival_date_week_number',
        'arrival_date_day_of_month', 'stays_in_weekend_nights', 
        'stays_in_week_nights', 'market_segment_type', 
        'country', 'avg_price_per_room', 'email', 'data_source'
    ]
    
    customer_aligned = customer_for_merge.select(*unified_columns)
    hotel_aligned = hotel_for_merge.select(*unified_columns)
    print(f"Aligned to {len(unified_columns)} common columns")
    
    print("\n" + "-"*80)
    print("Merging datasets")
    print("-"*80)
    merged_df = customer_aligned.union(hotel_aligned)
    print(f"Customer records: {customer_aligned.count():,}")
    print(f"Hotel records: {hotel_aligned.count():,}")
    print(f"Total merged: {merged_df.count():,}")
    
    print("\n" + "-"*80)
    print("Converting booking status to boolean")
    print("-"*80)
    merged_df = merged_df \
        .withColumn('is_canceled', when(col('booking_status') == 'Canceled', True).otherwise(False)) \
        .drop('booking_status')
    
    print("Converted booking_status to is_canceled (boolean)")
    
    print("\n" + "-"*80)
    print("Merged Data Summary")
    print("-"*80)
    print("\nSchema:")
    merged_df.printSchema()
    print("\nSample:")
    merged_df.show(5, truncate=False)
    print("\nRecords by source:")
    merged_df.groupBy('data_source').count().show()
    print("\nCancellation distribution:")
    merged_df.groupBy('is_canceled').count().show()
    
    print("\n" + "-"*80)
    print("Saving merged dataset")
    print("-"*80)
    save_single_csv(merged_df, 'output/merged_hotel_data.csv')
    print("Saved: output/merged_hotel_data.csv")
    
    return merged_df

def main():
    spark = SparkSession.builder \
        .appName("HotelBookingAnalysis") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    print("\n" + "="*80)
    print("Hotel Booking Data Analysis")
    print("="*80)

    customer_df = spark.read.csv("data/customer-reservations.csv", header=True, inferSchema=True)
    hotel_df = spark.read.csv("data/hotel-booking.csv", header=True, inferSchema=True)

    if customer_df is None or hotel_df is None:
        print("Error: Datasets not loaded")   
        sys.exit(1)

    perform_eda(customer_df, "customer_reservations")
    perform_eda(hotel_df, "hotel_bookings")

    merged_data = merge_datasets(customer_df, hotel_df)
    
    print("\n" + "="*80)
    print(f"Complete. Total records: {merged_data.count():,}")
    print("="*80)

    spark.stop()

if __name__ == "__main__":
    main()