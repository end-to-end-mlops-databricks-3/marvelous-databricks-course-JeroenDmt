# Databricks notebook source
# MAGIC %pip install -e ..
# MAGIC %restart_python

# COMMAND ----------

from pathlib import Path
import sys
sys.path.append(str(Path.cwd().parent / 'src'))

# COMMAND ----------

import mlflow
from pyspark.sql import SparkSession

from configuration.config import ProjectConfig, Tags
from house_price.models.basic_model import BasicModel

from dotenv import load_dotenv
from marvelous.common import is_databricks

# COMMAND ----------

# If you have DEFAULT profile and are logged in with DEFAULT profile,
# skip these lines

# if not is_databricks():
#     load_dotenv()
#     profile = os.environ["PROFILE"]
#     mlflow.set_tracking_uri(f"databricks://{profile}")
#     mlflow.set_registry_uri(f"databricks-uc://{profile}")


config = ProjectConfig.from_yaml(config_path="../houseprice_config.yml", env="dev")
spark = SparkSession.builder.getOrCreate()
tags = Tags(**{"git_sha": "abcd12345", "branch": "week2", "job_run_id": "your_job_run_id"})

# COMMAND ----------

4# Initialize model with the config path
basic_model = BasicModel(config=config, tags=tags, spark=spark)

# COMMAND ----------

basic_model.load_data()
basic_model.prepare_features()

# COMMAND ----------

# Train + log the model (runs everything including MLflow logging)
basic_model.train()
basic_model.log_model()

# COMMAND ----------

run_id = mlflow.search_runs(
    experiment_names=["/Shared/house-prices-basic"], filter_string="tags.branch='week2'"
).run_id[0]

model = mlflow.sklearn.load_model(f"runs:/{run_id}/lightgbm-pipeline-model")

# COMMAND ----------

# Retrieve dataset for the current run
basic_model.retrieve_current_run_dataset()

# COMMAND ----------

# Retrieve metadata for the current run
basic_model.retrieve_current_run_metadata()

# COMMAND ----------

# Register model
basic_model.register_model()

# COMMAND ----------

# Predict on the test set

test_set = spark.table(f"{config.catalog_name}.{config.schema_name}.house_test_set").limit(10)

X_test = test_set.drop(config.target).toPandas()

predictions_df = basic_model.load_latest_model_and_predict(X_test)

# COMMAND ----------
