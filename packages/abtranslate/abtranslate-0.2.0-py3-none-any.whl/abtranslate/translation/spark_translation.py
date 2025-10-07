import os
import shutil
from pathlib import Path
import logging

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import pandas_udf
from pyspark import SparkFiles
from pyspark.sql.types import StringType
from pyspark.sql import functions as F

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.DEBUG)

PACKAGES_PATH = "/tmp/abtranslate/packages/"
MODELS_PATH = "/tmp/abtranslate/model/"

def translate_column(translator_config=None, 
                     translation_config=None, 
                     optimized_config=True):
    
    package_dir = Path(f"/tmp/abtranslate/packages")
    
    # Ensure package directory exists
    package_dir.mkdir(parents=True, exist_ok=True)

    @pandas_udf(StringType())
    def translate_udf(column):
        import ctranslate2
        import numpy
        import pandas
        from abtranslate.translator.package import load_argostranslate_model
        logger.info("Data received on UDF, length, ", len(column))

        package_path = SparkFiles.get("model.zip")
        logger.info("Model found at :", package_path)

        if not os.path.exists(package_path):
            raise FileNotFoundError(f"Model path {package_path} doesn't exist")

        # Update the global PACKAGE_DIR constant BEFORE loading the package
        import abtranslate.config.constants
        abtranslate.config.constants.PACKAGE_DIR = package_dir
        
        # Load package ONCE outside UDF
        package = load_argostranslate_model(package_path)

        # Build translator once
        if translator_config:
            translator = package.load_translator(translator_config, optimized_config=optimized_config, lazy_load=False)
        else:
            translator = package.load_translator(optimized_config=optimized_config, lazy_load=False)

        sample_input = [ '发动机左侧在飞行前检查中发现有轻微的机油渗漏。', 
                            '技术人员确认渗漏区域位于涡轮壳体附近，并进行了初步清洁。', 
                            '随后安排进一步的检查以确定是否需要更换密封件。', ]
        
        
        task_id = os.getenv('SPARK_TASK_ATTEMPT_ID', str(os.getpid()))
        sample_results = translator.translate_batch(sample_input)
        logger.info(f"Translator initialized on task id {task_id}")
        logger.info(f"Taranslation result of sample text: ", sample_results)

        try:
            if translation_config:
                results = translator.translate_batch(column, translation_config)
            else:
                results = translator.translate_batch(column)
            return results
            
        except Exception as e:
            import pandas as pd 
            logger.error(f"Translation failed: {e}")
            return pd.Series([f"TRANSLATION_ERROR :{e}"] * len(column))

    return translate_udf

def translate_with_udf(
    model_path: str,
    spark_df: DataFrame,
    input_column_name: str,
    output_column_name: str,
    translator_config=None,
    translation_config=None,
    optimized_config=True,
) -> DataFrame:
    
    spark = SparkSession.builder.getOrCreate()
    # task_id = os.getenv('SPARK_TASK_ATTEMPT_ID', str(os.getpid()))
    
    # Create task-specific package directory
    package_dir = Path(f"/tmp/abtranslate/packages")
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy model to a standardized name in the package directory
    dst_model_path = package_dir / "model.zip"
    
    # Copy to executor-local dir if not already there
    if not dst_model_path.exists():
        shutil.copy(model_path, dst_model_path)
        logger.info(f"Copied model from {model_path} to {dst_model_path}")

    # Add to Spark distributed files
    spark.sparkContext.addFile(str(dst_model_path))
    logger.info(f"Added {dst_model_path} to Spark distributed files")

    # Apply the translation UDF
    translate_udf = translate_column(
        translator_config=translator_config,
        translation_config=translation_config,
        optimized_config=optimized_config
    )

    logger.info(f"Proceed translation of column {input_column_name} as {output_column_name}")
    df_translated = spark_df.withColumn(
        output_column_name,
        translate_udf(F.col(input_column_name))
    )

    logger.info("Dataframe translated with UDF finished, result:", df_translated.head())

    return df_translated