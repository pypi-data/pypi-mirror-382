from azure.storage.blob import BlobServiceClient, BlobPrefix
from azure.core.exceptions import ResourceExistsError
from datetime import datetime

from gfa_ml.data_model.storage import AzureBlobConfig, BlobItemList
import pandas as pd
from io import StringIO, BytesIO
import logging

azure_logger = logging.getLogger("azure")
azure_logger.setLevel(logging.WARNING)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class AzureBlobStorageClient:
    def __init__(self, config: AzureBlobConfig):
        self.config = config
        self.blob_service_client = BlobServiceClient.from_connection_string(
            config.connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            config.container_name
        )

    def upload_blob(self, blob_name: str, data):
        self.container_client.upload_blob(name=blob_name, data=data)

    def download_blob(self, blob_name: str):
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.download_blob().readall()

    def list_items(self, prefix: str = None):
        folders = []
        files = []
        blobs = self.container_client.walk_blobs(
            name_starts_with=prefix or "", delimiter="/"
        )
        for item in blobs:
            if isinstance(item, BlobPrefix):  # this is a "folder"
                folders.append(item.name)
            else:  # this is a file/blob
                files.append(item.name)

        return BlobItemList(folders=folders, files=files)

    def load_csv(self, blob_name: str, **kwargs) -> pd.DataFrame:
        """Load a CSV blob into a Pandas DataFrame."""
        blob_client = self.container_client.get_blob_client(blob_name)
        data = blob_client.download_blob().readall()
        return pd.read_csv(StringIO(data.decode("utf-8")), **kwargs)

    def load_parquet(self, blob_name: str, **kwargs) -> pd.DataFrame:
        """Load a Parquet blob into a Pandas DataFrame."""
        blob_client = self.container_client.get_blob_client(blob_name)
        data = blob_client.download_blob().readall()
        return pd.read_parquet(BytesIO(data), **kwargs)

    def mkdir_if_not_exist(self, folder_name: str):
        """
        Create a 'directory' (virtual folder) if it doesn't exist.
        In Azure Blob, folders are simulated by blobs ending with '/'.
        """
        if not folder_name.endswith("/"):
            folder_name += "/"

        blob_client = self.container_client.get_blob_client(folder_name)

        try:
            # Upload a zero-byte placeholder blob for the folder
            blob_client.upload_blob(b"", overwrite=False)
            logging.info(f"Created folder '{folder_name}'")
        except ResourceExistsError:
            logging.info(f"Folder '{folder_name}' already exists")

    def concat_csvs_in_range(
        self, prefix: str, start_date: str, end_date: str, **kwargs
    ) -> pd.DataFrame:
        """
        Concatenate CSV blobs whose filenames fall within the date range.
        Dates are strings in 'YYYYMMDD' format.
        """
        start_dt = datetime.strptime(start_date, "%Y%m%d")
        end_dt = datetime.strptime(end_date, "%Y%m%d")

        # List blobs with prefix
        blob_items = self.list_items(prefix)
        blobs = blob_items.files

        dataframes = []
        for blob in blobs:
            fname = blob.split("/")[-1]  # just the file name
            parts = fname.split(".")
            if len(parts) < 4:
                continue

            try:
                file_start = datetime.strptime(parts[2][:8], "%Y%m%d")
            except ValueError:
                continue

            if start_dt <= file_start <= end_dt:
                logging.debug(f"Loading {fname}...")
                df = self.load_csv(blob, **kwargs)
                dataframes.append(df)

        if not dataframes:
            logging.info("No files found in the given date range.")
            return pd.DataFrame()

        return pd.concat(dataframes, ignore_index=True)

    def upload_dataframe(
        self, df: pd.DataFrame, blob_name: str, file_type: str = "csv", **kwargs
    ):
        """
        Upload a Pandas DataFrame to Azure Blob Storage.

        Parameters:
        - df: the Pandas DataFrame to upload
        - blob_name: path in the container, e.g., "data/myfile.csv"
        - file_type: "csv" or "parquet"
        - kwargs: additional arguments passed to pd.to_csv or pd.to_parquet
        """
        blob_client = self.container_client.get_blob_client(blob_name)

        if file_type.lower() == "csv":
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False, **kwargs)
            blob_client.upload_blob(csv_buffer.getvalue(), overwrite=True)

        elif file_type.lower() == "parquet":
            parquet_buffer = BytesIO()
            df.to_parquet(parquet_buffer, index=False, **kwargs)
            blob_client.upload_blob(parquet_buffer.getvalue(), overwrite=True)

        else:
            raise ValueError("file_type must be 'csv' or 'parquet'")

        logging.info(f"Uploaded DataFrame to {blob_name} ({file_type.upper()})")
