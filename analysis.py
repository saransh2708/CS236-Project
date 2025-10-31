# Load output/merged_hotel_data.csv for analysis using PySpark

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, sum,
    when, round as _round, desc
)
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

def load_and_analyze_data(file_path="output/merged_hotel_data.csv"):
    """
    Load the merged hotel data CSV file and perform initial analysis.
    
    Args:
        file_path (str): Path to the merged hotel data CSV file
    
    Returns:
        DataFrame: The loaded Spark DataFrame
    """
    # Initialize Spark session
    spark = SparkSession.builder.appName("HotelDataAnalysis").getOrCreate()
    
    # Load the CSV file
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    
    # Display the first few rows of the DataFrame
    print("=== First 5 rows ===")
    df.show(5)
    
    # Cancellation Rates
    cancellation_rates_df = cancellation_rate(df)
    averages_df = averages(df)
    monthly_bookings_df = monthly_bookings(df)
    seasonality_df = seasonality(df)

    print("\n=== Cancellation Rates ===")
    cancellation_rates_df.show()
    print("\n=== Averages ===")
    averages_df.show()
    print("\n=== Monthly Bookings ===")
    monthly_bookings_df.show()
    print("\n=== Seasonality ===")
    seasonality_df.show()
    
    return df

def cancellation_rate(df):
    """
    Calculate cancellation rates for each month
    """
    # Convert is_canceled to numeric (1 for true, 0 for false)
    cancellation_df = df.groupBy("arrival_month").agg(
        sum(when(col("is_canceled") == "true", 1).otherwise(0)).alias("canceled_count"),
        count("*").alias("total_bookings")
    )
    
    # Calculate cancellation rate as percentage
    cancellation_df = cancellation_df.withColumn(
        "cancellation_rate_percent",
        _round((col("canceled_count") / col("total_bookings")) * 100, 2)
    ).orderBy("arrival_month")
    
    return cancellation_df

def averages(df):
    """
    Compute average price and average number of nights for each month
    """
    # Calculate total nights stayed
    df_with_nights = df.withColumn(
        "total_nights",
        col("stays_in_weekend_nights") + col("stays_in_week_nights")
    )
    
    # Group by month and calculate averages
    averages_df = df_with_nights.groupBy("arrival_month").agg(
        _round(avg("avg_price_per_room"), 2).alias("avg_price_per_room"),
        _round(avg("total_nights"), 2).alias("avg_nights_stayed")
    ).orderBy("arrival_month")
    
    return averages_df

def monthly_bookings(df):
    """
    Count monthly bookings by market segment. In categories, the
    term TA means Travel Agents and TO mean Tour Operators.
    """
    # Group by arrival_month and market_segment_type
    bookings_df = df.groupBy("arrival_month", "market_segment_type").agg(
        count("*").alias("booking_count")
    ).orderBy("arrival_month", "market_segment_type")
    
    return bookings_df

def seasonality(df):
    """
    Identify the most popular month of the year for bookings based on revenue
    """
    # Calculate revenue for each booking
    df_with_revenue = df.withColumn(
        "total_nights",
        col("stays_in_weekend_nights") + col("stays_in_week_nights")
    ).withColumn(
        "revenue",
        col("avg_price_per_room") * col("total_nights")
    )
    
    # Group by month and sum revenue
    seasonality_df = df_with_revenue.groupBy("arrival_month").agg(
        sum("revenue").alias("total_revenue"),
        count("*").alias("total_bookings")
    ).withColumn(
        "total_revenue",
        _round(col("total_revenue"), 2)
    ).orderBy(desc("total_revenue"))
    
    return seasonality_df

if __name__ == "__main__":
    # Load and analyze the data
    dataframe = load_and_analyze_data()