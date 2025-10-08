from abc import ABC, abstractmethod

class IStorageService(ABC): 

    @abstractmethod
    async def upload(self, blob_name: str, data: bytes | str) -> str:
        """ Download a file from blob storage """
        pass


    @abstractmethod
    async def download(self, blob_name: str) -> bytes:
        """ Upload a file to blob storage """
        pass


    @abstractmethod
    async def delete(self, blob_name: str) -> None:
        """ Delete a file from blob storage """
        pass