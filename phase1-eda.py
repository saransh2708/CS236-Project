
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import matplotlib.pyplot as plt
import sys
import seaborn as sns

def perform_eda(df, data_name="dataset"):
    print("\nSchema:")
    df.printSchema()

    print("\nRow Count:")
    print(df.count())

    print("\nColumn Count:")
    print(len(df.columns))

    print("\nColumns:")
    print(df.columns)

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
        plt.savefig(f'eda_{data_name}_correlation.png')
        plt.close()

def main():
    # Create Spark session
    spark = SparkSession.builder \
        .appName("HotelBooking") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    # Load Data Sets
    customer_reservartions = spark.read.csv("data/customer-reservations.csv", header=True, inferSchema=True)
    hotel_bookings = spark.read.csv("data/hotel-booking.csv", header=True, inferSchema=True)

    if customer_reservartions is None or hotel_bookings is None:
        print("Datasets not loaded properly")   
        sys.exit(1)

    # EDA on customer_reservartions
    print("\nEDA on Customer Reservartions Data:")
    perform_eda(customer_reservartions, "customer_reservartions")

    # EDA on hotel_bookings
    print("\nEDA on Hotel Bookings Data:")
    perform_eda(hotel_bookings, "hotel_bookings")

    spark.stop()

if __name__ == "__main__":
    main()