# Databricks notebook source
# MAGIC %pip install -e ..
# MAGIC %restart_python

# COMMAND ----------

from pathlib import Path
import sys
sys.path.append(str(Path.cwd().parent / 'src'))

# COMMAND ----------

from datetime import datetime

import pandas as pd
import yaml
from loguru import logger
from marvelous.logging import setup_logging
from marvelous.timer import Timer
from pyspark.sql import SparkSession

from configuration.config import ProjectConfig
from hotel_reservations.data_processor import DataProcessor

config = ProjectConfig.from_yaml(config_path="../hotelreservation_config.yml", env="dev")

setup_logging(log_file=f"logs/preprocess_hotelreservations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logger.info("Configuration loaded:")
logger.info(yaml.dump(config, default_flow_style=False))

# COMMAND ----------

# Load the house prices dataset
spark = SparkSession.builder.getOrCreate()

filepath = "../data/HotelReservations.csv"

# Load the data
df = pd.read_csv(filepath)


# COMMAND ----------

# Load the house prices dataset
with Timer() as preprocess_timer:
    # Initialize DataProcessor
    data_processor = DataProcessor(df, config, spark)

    # Preprocess the data
    data_processor.preprocess()

logger.info(f"Data preprocessing: {preprocess_timer}")

# COMMAND ----------

# Split the data
X_train, X_test = data_processor.split_data()
logger.info("Training set shape: %s", X_train.shape)
logger.info("Test set shape: %s", X_test.shape)

# COMMAND ----------

# Save to catalog
logger.info("Saving data to catalog")
data_processor.save_to_catalog(X_train, X_test)

# Enable change data feed (only once!)
logger.info("Enable change data feed")
data_processor.enable_change_data_feed()
