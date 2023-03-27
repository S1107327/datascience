from pyspark.context import SparkContext
from pyspark.sql.functions import *
from pyspark.sql.session import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import *
import pandas

sc = SparkContext.getOrCreate()
spark = SparkSession(sc)
sqlContext = SQLContext(sc)

path_kaggle = "/media/lorenzo/Partizione Dati/Downloads Linux/dataset_aereoporti.csv"
path = "/media/lorenzo/Partizione Dati/Downloads Linux/Airline_Delay_Cause.csv"
path_clean = "/home/lorenzo/Desktop"

dataset_kaggle = spark.read.format("csv").option("header", "true").load(path_kaggle)
dataset_not_clean = spark.read.format("csv").option("header", "true").load(path)
airports = spark.read.format("csv").option("header", "true").load("/media/lorenzo/Partizione Dati/Downloads Linux/us-airports.csv")
# CONVERSIONE DEL TIPO DELLE COLONNE YEAR, MONTH, ARR_FLIGHTS,ARR_DEL15, ARR_DIVERTED, ARR_CANCELLED IN INTERO
dataset_not_clean = dataset_not_clean.withColumn("year", col("year").cast(IntegerType()))
dataset_not_clean = dataset_not_clean.withColumn("month", col("month").cast(IntegerType()))
dataset_not_clean = dataset_not_clean.withColumn("arr_flights", col("arr_flights").cast(IntegerType()))\
    .withColumn("arr_del15", col("arr_del15").cast(IntegerType()))\
    .withColumn("arr_diverted", col("arr_diverted").cast(IntegerType()))\
    .withColumn("arr_cancelled", col("arr_cancelled").cast(IntegerType()))
# STESSO LAVORO FATTO PER IL DATASET DI KAGGLE
dataset_kaggle = dataset_kaggle.withColumn("year", col("year").cast(IntegerType()))
dataset_kaggle = dataset_kaggle.withColumn("month", col("month").cast(IntegerType()))
dataset_kaggle = dataset_kaggle.withColumn("arr_ontime", col("arr_ontime").cast(IntegerType()))\
    .withColumn("arr_flights", col("arr_flights").cast(IntegerType())).withColumn("arr_del15", col("arr_del15").cast(IntegerType()))\
    .withColumn("arr_diverted", col("arr_diverted").cast(IntegerType())).withColumn("arr_cancelled", col("arr_cancelled").cast(IntegerType()))
# RINOMINATA COLONNA ARR_DELAY IN MIN_DELAY
dataset_not_clean = dataset_not_clean.withColumnRenamed("arr_delay", "min_delay")
#dataset_not_clean = dataset_not_clean.withColumn("carrier", when(col('carrier') == 'XE', 'EV').otherwise(col("carrier")))
# ELIMINAZIONE DAL DATASET DI RIGHE CON ARR_FLIGHTS NULL
dataset_not_clean = dataset_not_clean.filter(col("arr_flights").isNotNull())
# ADEGUAMENTO NOME DI UNA COMPAGNIA CHE HA SEMPLICEMENTE CAMBIATO ESTENSIONE SOCIETARIA
dataset_not_clean = dataset_not_clean.withColumn("carrier_name", when(col('carrier_name') == 'ExpressJet Airlines LLC',
                                                                      'ExpressJet Airlines Inc.').otherwise(col("carrier_name")))
# RICAVATA COLONNA PER GLI AEREI IN ORARIO COME DIFFERENZA E CONVERSIONE AD INTERO DELLA STESSA
dataset_not_clean = dataset_not_clean.withColumn("arr_ontime",
                                                 col("arr_flights")-col("arr_del15")-col("arr_diverted")-col("arr_cancelled"))
dataset_not_clean = dataset_not_clean.withColumn("arr_ontime", col("arr_ontime").cast(IntegerType()))
# CREAZIONE DELLA COLONNA CITY CON CORREZIONI PUNTUALI LEGATE AD ALCUNE CITTÀ
dataset_not_clean = dataset_not_clean.withColumn("city", trim(split(split("airport_name", '[:]')[0], '[,]')[0]))
dataset_not_clean = dataset_not_clean.withColumn("city", when(col("city") == "Adak Island", "Adak").otherwise(col("city")))
dataset_not_clean = dataset_not_clean.withColumn("city", when(col("city").contains("/"), split("city", "[/]")[0])
                                                 .otherwise(col("city")))
# CREAZIONE DELLA COLONNA STATE CON CORREZIONE UTILIZZANDO I CODICI ISO PER RICONOSCERE I PAESI
dataset_not_clean = dataset_not_clean.withColumn("state", trim(split(split("airport_name", '[,]')[1], '[:]')[0]))
dataset_not_clean = dataset_not_clean.withColumn("state", when(col("city") == "Guam", "GU")
                                                 .when(col("city") == "Pago Pago", "AS")
                                                 .when(col("city") == "Saipan", "MP").otherwise(col("state")))
# CREAZIONE DELLA COLONNA COUNTRY PER OTTENERE LA SUDDIVISIONE IN PIÙ LIVELLI
dataset_not_clean = dataset_not_clean.withColumn("country", when(col("state") == "PR", "PR")
                                                 .when(col("state") == "VI", "VI")
                                                 .when(col("state") == "GU", "GU")
                                                 .when(col("state") == "AS", "AS")
                                                 .when(col("state") == "MP", "MP")
                                                 .otherwise("US"))
# CREAZIONE DELLA COLONNA AIRPORT NAME CON SOLO NOME DELL'AEROPORTO
dataset_not_clean = dataset_not_clean.withColumn("airport_name", trim(split("airport_name", '[:]')[1]))
# CREAZIONE DELLA COLONNA TRIMESTRE O QUARTER IN INGLESE NEI FORMATI ACCETATTI DA QLIK E TABLEAU
dataset_not_clean = dataset_not_clean.withColumn("quarter", concat(lit("Q"), ceil(col("month")/3)))
# JOIN DATASET UFFICIALE CON QUELLO DI KAGGLE PER OTTENERE LATITUDINE E LONGITUDINE
joined_dataset = dataset_not_clean.join(airports, dataset_not_clean["airport"] == airports["iata_code"], "left").select(dataset_not_clean.schema.names+["latitude_deg", "longitude_deg"])
to_select = joined_dataset.schema.names
lat_lon_add = dataset_kaggle.select(col("state").alias("k_state"),col("airport").alias("k_airport"), "latitude", "longitude").filter("state == ' TT'").distinct()
joined_dataset = joined_dataset.join(lat_lon_add, joined_dataset["airport"] == lat_lon_add["k_airport"], "left").select(to_select+["latitude", "longitude"])
joined_dataset = joined_dataset.withColumn("latitude_deg", when(col("latitude_deg").isNull(), col("latitude")).otherwise(col("latitude_deg")))
joined_dataset = joined_dataset.withColumn("longitude_deg", when(col("longitude_deg").isNull(), col("longitude")).otherwise(col("longitude_deg")))
# MANTENIMENTO SOLO DELLE COLONNE DI INTERESSE
joined_dataset = joined_dataset.select(to_select)
# ELIMINAZIONE DELLE RIGHE CHE CONTENGONO NULL IN ARR_FLIGHTS
# SCRITTURA DEL DATAFRAME SU PANDAS
joined_dataset.toPandas().to_csv(f"{path_clean}/dataset_aeroporti_clean.csv", index=False)

