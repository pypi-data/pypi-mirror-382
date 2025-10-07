from pyspark.sql import SparkSession

class SparkClient:

    """
    A client allowing the SDK to use a Spark Session to execute Spark SQL commands, like creating tables and views.
    """

    def __init__(self, spark_session: SparkSession):

        """
        Initialize the SparkClient

        Parameters:
        spark_session (SparkSession): Your Spark session (e.g., of the notebook you are using)
        """

        print("Initializing Spark Session")
        self.spark_session = spark_session

    def __run_sql(self, sql_text):
        self.spark_session.sql(sql_text)

    def __get_sql(self, sql_text):
        return self.spark_session.sql(sql_text)

    def __get_df(self, data, schema=None):
        return self.spark_session.createDataFrame(data, schema)