from azure.storage.blob.aio import BlobServiceClient
from Osdental.Storage import IStorageService
from Osdental.Shared.Logger import logger
from Osdental.Shared.Enums.Message import Message

class AzureBlobStorage(IStorageService):

    def __init__(self, connection_string: str, container_name: str):
        self.connection_string = connection_string
        self.container_name = container_name
        self.client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.client.get_container_client(self.container_name)

    async def upload(self, blob_name: str, data: bytes | str) -> str:
        """
        Uploads a blob. Returns the blob URL.
        """
        try:
            async with self.container_client:
                blob_client = self.container_client.get_blob_client(blob_name)
                if isinstance(data, str):
                    data = data.encode("utf-8")
                await blob_client.upload_blob(data, overwrite=True)
                return blob_client.url
        except Exception as e:
            logger.error(f'Azure Blob upload error: {str(e)}')
            raise ValueError(f'{Message.UNEXPECTED_ERROR_MSG}: {str(e)}')

    async def download(self, blob_name: str) -> bytes:
        """
        Download a blob.
        """
        try:
            async with self.container_client:
                blob_client = self.container_client.get_blob_client(blob_name)
                stream = await blob_client.download_blob()
                return await stream.readall()
        except Exception as e:
            logger.error(f'Azure Blob download error: {str(e)}')
            raise ValueError(f'{Message.UNEXPECTED_ERROR_MSG}: {str(e)}')

    async def delete(self, blob_name: str) -> None:
        """
        Deletes a blob.
        """
        try:
            async with self.container_client:
                blob_client = self.container_client.get_blob_client(blob_name)
                await blob_client.delete_blob()
        except Exception as e:
            logger.error(f'Azure Blob delete error: {str(e)}')
            raise ValueError(f'{Message.UNEXPECTED_ERROR_MSG}: {str(e)}')
