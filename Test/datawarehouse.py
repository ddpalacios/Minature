from datetime import date, date
from delta.tables import DeltaTable
import datetime
from pyspark.sql.functions import regexp_replace


class DataWarehouse:
    def __init__(self):
        self.account_name = "impactanalyticsdatalake"
        self.current_batch = None

    def __get_latest_date(self, input_path):
        dates = []

        year_folders = mssparkutils.fs.ls(input_path)

        if len(year_folders) == 0:
            return
        for year in year_folders:
            month_folders = mssparkutils.fs.ls(year.path)
            for month in month_folders:
                day_folders = mssparkutils.fs.ls(month.path)
                for day in day_folders:
                    folder_date_str = '/'.join(day.path.split('/')[-3:])
                    folder_date = datetime.datetime.strptime(folder_date_str, '%Y/%m/%d')
                    dates.append(folder_date)

        # Find the most recent date
        most_recent_date = max(dates)
        # Get the most recent folder
        most_recent_folder = most_recent_date.strftime('%Y/%m/%d')

        batch_data_directory = "{}/{}".format(input_path, most_recent_folder)
        current_batch = mssparkutils.fs.ls(batch_data_directory)
        return current_batch

    def get_current_batch(self, data_stage, department, datasource):
        # Construct the input path based on the container, account_name, department, and datasource
        container = f"impact-analytics-{data_stage}-data-lake"
        input_path = f'abfs://{container}@{self.account_name}.dfs.core.windows.net/{department}/{datasource}'
        latest_batch_folder = self.__get_latest_date(input_path)
        self.current_batch = latest_batch_folder
        return latest_batch_folder

    def get_dataframe(self, file_path):
        return spark.read.load(file_path)

    def create_temporary_views_from_current_batch(self):
        if self.current_batch is None:
            return
        for file_name in self.current_batch:
            file_path = file_name.path
            file_name = file_name.name
            dataframe = self.get_dataframe(file_path)
            for df_col in dataframe.columns:
                if '$' in df_col:
                    old_col_name = df_col
                    new_col_name = df_col.replace('$', '_')
                    dataframe = dataframe.withColumnRenamed(old_col_name, new_col_name)

            substring = file_name[file_name.rfind("_") + 1:file_name.rfind(".parquet")]
            file_name = file_name.replace("_" + substring, "")
            file_name = file_name.replace(".parquet", "")
            file_name = file_name.replace("$", "_")
            dataframe.createOrReplaceTempView(file_name)

    def is_path_empty(self, path):
        files_list = mssparkutils.fs.ls(path)
        return len(files_list) == 0

    def write_to_container(self, data_stage, department, datasource, dataframe, merge_key_column=None):
        if data_stage.lower() == "bronze":
            return

        container = f"impact-analytics-{data_stage}-data-lake"
        container_path = f'abfs://{container}@{self.account_name}.dfs.core.windows.net/{department}/{datasource}'
        dataframe = dataframe.withColumn("Customer", regexp_replace("Customer", "\\.+$", ""))

        if self.is_path_empty(container_path):
            # If the silver container is empty, write the transformed data as a new Delta table
            dataframe.write.partitionBy("batch_year", "batch_month", "batch_day", "Customer").format("delta").mode(
                "overwrite").save(container_path)

        else:
            # If the silver container has data, perform a merge operation
            stage_data = DeltaTable.forPath(spark, container_path)
            merge_condition = f"old_data.{merge_key_column} = new_data.{merge_key_column}"

            # Merge the transformed data with the existing silver data
            stage_data.alias("old_data") \
                .merge(dataframe.alias("new_data"), merge_condition) \
                .whenNotMatchedInsertAll() \
                .execute()

            # Optimize the table by compacting small files and updating the statistics
            spark.sql(f"OPTIMIZE delta.`{container_path}` ZORDER BY (batch_date, Customer)")





