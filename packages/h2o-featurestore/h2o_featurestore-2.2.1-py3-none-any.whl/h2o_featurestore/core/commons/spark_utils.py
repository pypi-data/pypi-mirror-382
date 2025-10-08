class SparkUtils:
    @staticmethod
    def configure_user_spark(spark):
        spark.conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
        spark.conf.set("fs.wasbs.impl.disable.cache", "true")
        spark.conf.set("fs.gs.impl.disable.cache", "true")
        spark.conf.set("fs.wasb.impl.disable.cache", "true")
        spark.conf.set("fs.abfss.impl.disable.cache", "true")
        spark.conf.set("fs.abfs.impl.disable.cache", "true")
        spark.conf.set("fs.s3a.impl.disable.cache", "true")
        spark.conf.set("fs.s3n.impl.disable.cache", "true")
        spark.conf.set("fs.s3.impl.disable.cache", "true")
        spark.conf.set("spark.sql.parquet.datetimeRebaseModeInWrite", "CORRECTED")
        spark.conf.set("spark.sql.parquet.datetimeRebaseModeInRead", "CORRECTED")
        spark.conf.set("spark.sql.parquet.int96RebaseModeInRead", "CORRECTED")
        spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")
        spark.sparkContext._jsc.hadoopConfiguration().set(
            "mapreduce.fileoutputcommitter.cleanup-failures.ignored", "true"
        )
        spark.sparkContext._jsc.hadoopConfiguration().set("mapreduce.fileoutputcommitter.cleanup.skipped", "true")
        spark.sparkContext._jsc.hadoopConfiguration().set("mapreduce.fileoutputcommitter.algorithm.version", "2")
