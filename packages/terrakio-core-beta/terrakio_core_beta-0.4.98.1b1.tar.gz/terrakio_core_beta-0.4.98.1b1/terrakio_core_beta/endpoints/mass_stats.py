import os
import time
import typer
from typing import Dict, Any, Optional, List
from dateutil import parser

from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

from ..exceptions import (
    CreateCollectionError,
    GetCollectionError,
    ListCollectionsError,
    CollectionNotFoundError,
    CollectionAlreadyExistsError,
    InvalidCollectionTypeError,
    DeleteCollectionError,
    ListTasksError,
    UploadRequestsError,
    UploadArtifactsError,
    GetTaskError,
    TaskNotFoundError,
    DownloadFilesError,
    CancelTaskError,
    CancelCollectionTasksError,
    CancelAllTasksError,
)
from ..helper.decorators import require_api_key

import aiohttp  # Make sure this is imported at the top


class MassStats:
    def __init__(self, client):
        self._client = client
        self.console = Console()

    async def track_progress(self, task_id):
        task_info = await self.get_task(task_id=task_id)
        number_of_jobs = task_info["task"]["total"]
        start_time = parser.parse(task_info["task"]["createdAt"])
        
        self.console.print(f"[bold cyan]Tracking task: {task_id}[/bold cyan]")
        
        completed_jobs_info = []
        
        def get_job_description(job_info, include_status=False):
            if not job_info:
                return "No job info"
            
            service = job_info.get("service", "Unknown service")
            desc = service
            
            if include_status:
                status = job_info.get("status", "unknown")
                desc += f" - {status}"
            
            return desc
        
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        )
        
        with progress:
            last_completed_count = 0
            current_job_task = None
            current_job_description = None
            
            while len(completed_jobs_info) < number_of_jobs:
                task_info = await self.get_task(task_id=task_id)
                completed_number = task_info["task"]["completed"]
                current_job_info = task_info["currentJob"]
                
                if completed_number > last_completed_count:
                    if current_job_task is not None:
                        completed_description = current_job_description.replace(" - pending", "").replace(" - running", "").replace(" - waiting", "")
                        completed_description += " - completed"
                        
                        progress.update(
                            current_job_task,
                            description=f"[{last_completed_count + 1}/{number_of_jobs}] {completed_description}",
                            completed=100
                        )
                        completed_jobs_info.append({
                            "task": current_job_task,
                            "description": completed_description,
                            "job_number": last_completed_count + 1
                        })
                        current_job_task = None
                        current_job_description = None
                    
                    last_completed_count = completed_number
                
                if current_job_info:
                    status = current_job_info["status"]
                    current_job_description = get_job_description(current_job_info, include_status=True)
                    
                    total_value = current_job_info.get("total", 0)
                    completed_value = current_job_info.get("completed", 0)
                    
                    if total_value == -9999:
                        percent = 0
                    elif total_value > 0:
                        percent = int(completed_value / total_value * 100)
                    else:
                        percent = 0
                    
                    if current_job_task is None:
                        current_job_task = progress.add_task(
                            f"[{completed_number + 1}/{number_of_jobs}] {current_job_description}",
                            total=100,
                            start_time=start_time
                        )
                    else:
                        progress.update(
                            current_job_task,
                            description=f"[{completed_number + 1}/{number_of_jobs}] {current_job_description}",
                            completed=percent
                        )
                    
                    if status == "Error":
                        self.console.print("[bold red]Error![/bold red]")
                        raise typer.Exit(code=1)
                    if status == "Cancelled":
                        self.console.print("[bold orange]Cancelled![/bold orange]")
                        raise typer.Exit(code=1)
                    elif status == "Completed":
                        completed_description = current_job_description.replace(" - pending", "").replace(" - running", "").replace(" - waiting", "")
                        completed_description += " - completed"
                        progress.update(
                            current_job_task, 
                            description=f"[{completed_number + 1}/{number_of_jobs}] {completed_description}",
                            completed=100
                        )
                
                if completed_number == number_of_jobs and current_job_info is None:
                    if current_job_task is not None:
                        completed_description = current_job_description.replace(" - pending", "").replace(" - running", "").replace(" - waiting", "")
                        completed_description += " - completed"
                        progress.update(
                            current_job_task,
                            description=f"[{number_of_jobs}/{number_of_jobs}] {completed_description}",
                            completed=100
                        )
                        completed_jobs_info.append({
                            "task": current_job_task,
                            "description": completed_description,
                            "job_number": number_of_jobs
                        })
                    break
                
                time.sleep(10)
        
        self.console.print(f"[bold green]All {number_of_jobs} jobs finished![/bold green]")

    @require_api_key
    async def create_collection(
        self, 
        collection: str, 
        bucket: Optional[str] = None, 
        location: Optional[str] = None, 
        collection_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Create a collection for the current user.

        Args:
            collection: The name of the collection (required)
            bucket: The bucket to use (optional, admin only)
            location: The location to use (optional, admin only)
            collection_type: The type of collection to create (optional, defaults to "basic")
            
        Returns:
            API response as a dictionary containing the collection id
            
        Raises:
            CollectionAlreadyExistsError: If the collection already exists
            InvalidCollectionTypeError: If the collection type is invalid
            CreateCollectionError: If the API request fails due to unknown reasons
        """
        payload = {
            "collection_type": collection_type
        }
        
        if bucket is not None:
            payload["bucket"] = bucket
        
        if location is not None:
            payload["location"] = location
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}", json=payload)

        if status != 200:
            if status == 400:
                raise CollectionAlreadyExistsError(f"Collection {collection} already exists", status_code=status)
            if status == 422:
                raise InvalidCollectionTypeError(f"Invalid collection type: {collection_type}", status_code=status)
            raise CreateCollectionError(f"Create collection failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def delete_collection(
        self, 
        collection: str, 
        full: Optional[bool] = False, 
        outputs: Optional[list] = [], 
        data: Optional[bool] = False
    ) -> Dict[str, Any]:
        """
        Delete a collection by name.

        Args:
            collection: The name of the collection to delete (required)
            full: Delete the full collection (optional, defaults to False)
            outputs: Specific output folders to delete (optional, defaults to empty list)
            data: Whether to delete raw data (xdata folder) (optional, defaults to False)
            
        Returns:
            API response as a dictionary confirming deletion
            
        Raises:
            CollectionNotFoundError: If the collection is not found
            DeleteCollectionError: If the API request fails due to unknown reasons
        """
        payload = {
            "full": full,
            "outputs": outputs,
            "data": data
        }
        
        response, status = await self._client._terrakio_request("DELETE", f"collections/{collection}", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise DeleteCollectionError(f"Delete collection failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def get_collection(self, collection: str) -> Dict[str, Any]:
        """
        Get a collection by name.

        Args:
            collection: The name of the collection to retrieve(required)
            
        Returns:
            API response as a dictionary containing collection information
            
        Raises:
            CollectionNotFoundError: If the collection is not found
            GetCollectionError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("GET", f"collections/{collection}")

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetCollectionError(f"Get collection failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def list_collections(
        self,
        collection_type: Optional[str] = None,
        limit: Optional[int] = 10,
        page: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """
        List collections for the current user.

        Args:
            collection_type: Filter by collection type (optional)
            limit: Number of collections to return (optional, defaults to 10)
            page: Page number (optional, defaults to 0)
            
        Returns:
            API response as a list of dictionaries containing collection information
            
        Raises:
            ListCollectionsError: If the API request fails due to unknown reasons
        """
        params = {}
        
        if collection_type is not None:
            params["collection_type"] = collection_type
        
        if limit is not None:
            params["limit"] = limit
            
        if page is not None:
            params["page"] = page
        
        response, status = await self._client._terrakio_request("GET", "collections", params=params)
        if status != 200:
            raise ListCollectionsError(f"List collections failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def list_tasks(
        self,
        limit: Optional[int] = 10,
        page: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """
        List tasks for the current user.

        Args:
            limit: Number of tasks to return (optional, defaults to 10)
            page: Page number (optional, defaults to 0)
        
        Returns:
            API response as a list of dictionaries containing task information
            
        Raises:
            ListTasksError: If the API request fails due to unknown reasons
        """
        params = {
            "limit": limit,
            "page": page
        }
        response, status = await self._client._terrakio_request("GET", "tasks", params=params)

        if status != 200:
            raise ListTasksError(f"List tasks failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def upload_requests(
        self,
        collection: str
    ) -> Dict[str, Any]:
        """
        Retrieve signed url to upload requests for a collection.

        Args:
            collection: Name of collection
        
        Returns:
            API response as a dictionary containing the upload URL

        Raises:
            CollectionNotFoundError: If the collection is not found
            UploadRequestsError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("GET", f"collections/{collection}/upload/requests")

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise UploadRequestsError(f"Upload requests failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def upload_artifacts(
        self,
        collection: str,
        file_type: str,
        compressed: Optional[bool] = True
    ) -> Dict[str, Any]:
        """
        Retrieve signed url to upload artifact file to a collection.

        Args:
            collection: Name of collection
            file_type: The extension of the file
            compressed: Whether to compress the file using gzip or not (defaults to True)
        
        Returns:
            API response as a dictionary containing the upload URL

        Raises:
            CollectionNotFoundError: If the collection is not found
            UploadArtifactsError: If the API request fails due to unknown reasons
        """
        params = {
            "file_type": file_type,
            "compressed": str(compressed).lower(),
        }

        response, status = await self._client._terrakio_request("GET", f"collections/{collection}/upload", params=params)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise UploadArtifactsError(f"Upload artifacts failed with status {status}", status_code=status)

        return response
        
    @require_api_key
    async def get_task(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Get task information by task ID.

        Args:
            task_id: ID of task to track
        
        Returns:
            API response as a dictionary containing task information

        Raises:
            TaskNotFoundError: If the task is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("GET", f"tasks/info/{task_id}")

        if status != 200:
            if status == 404:
                raise TaskNotFoundError(f"Task {task_id} not found", status_code=status)
            raise GetTaskError(f"Get task failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def generate_data(
        self,
        collection: str,
        output: str,
        skip_existing: Optional[bool] = True,
        force_loc: Optional[bool] = None,
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate data for a collection.

        Args:
            collection: Name of collection
            output: Output type (str)
            force_loc: Write data directly to the cloud under this folder
            skip_existing: Skip existing data
            server: Server to use
        
        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        payload = {"output": output, "skip_existing": skip_existing}
        
        if force_loc is not None:
            payload["force_loc"] = force_loc
        if server is not None:
            payload["server"] = server
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/generate_data", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Generate data failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def training_samples(
        self,
        collection: str,
        expressions: list[str],
        filters: list[str],
        aoi: dict,
        samples: int,
        crs: str,
        tile_size: int,
        res: float,
        output: str,
        year_range: Optional[list[int]] = None,
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate training samples for a collection.

        Args:
            collection: Name of collection
            expressions: List of expressions for each sample
            filters: Expressions to filter sample areas
            aoi: AOI to sample from (geojson dict)
            samples: Number of samples to generate
            crs: CRS of AOI
            tile_size: Pixel width and height of samples
            res: Resolution of samples
            output: Sample output type
            year_range: Optional year range filter
            server: Server to use

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        payload = {
            "expressions": expressions,
            "filters": filters,
            "aoi": aoi,
            "samples": samples,
            "crs": crs,
            "tile_size": tile_size,
            "res": res,
            "output": output
        }
        
        if year_range is not None:
            payload["year_range"] = year_range
        if server is not None:
            payload["server"] = server
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/training_samples", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Training sample failed with status {status}", status_code=status)
        
        return response

    # @require_api_key
    # async def post_processing(
    #     self,
    #     collection: str,
    #     folder: str,
    #     consumer: str
    # ) -> Dict[str, Any]:
    #     """
    #     Run post processing for a collection.

    #     Args:
    #         collection: Name of collection
    #         folder: Folder to store output
    #         consumer: Post processing script

    #     Returns:
    #         API response as a dictionary containing task information

    #     Raises:
    #         CollectionNotFoundError: If the collection is not found
    #         GetTaskError: If the API request fails due to unknown reasons
    #     """
    #     # payload = {
    #     #     "folder": folder,
    #     #     "consumer": consumer
    #     # }
    #     # we have the consumer as a string, we need to read in the file and then pass in the content
    #     with open(consumer, 'rb') as f:
    #         files = {
    #             'consumer': ('consumer.py', f.read(), 'text/plain')
    #         }
    #         data = {
    #             'folder': folder
    #         }
        
    #     # response, status = await self._client._terrakio_request("POST", f"collections/{collection}/post_process", json=payload)
    #     response, status = await self._client._terrakio_request(
    #         "POST",
    #         f"collections/{collection}/post_process",
    #         files=files,
    #         data=data
    #     )
    #     if status != 200:
    #         if status == 404:
    #             raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
    #         raise GetTaskError(f"Post processing failed with status {status}", status_code=status)
        
    #     return response


    @require_api_key
    async def post_processing(
        self,
        collection: str,
        folder: str,
        consumer: str
    ) -> Dict[str, Any]:
        """
        Run post processing for a collection.

        Args:
            collection: Name of collection
            folder: Folder to store output
            consumer: Path to post processing script

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        # Read file and build multipart form data
        with open(consumer, 'rb') as f:
            form = aiohttp.FormData()
            form.add_field('folder', folder)  # Add text field
            form.add_field(
                'consumer',  # Field name
                f.read(),  # File content
                filename='consumer.py',  # Filename
                content_type='text/x-python'  # MIME type
            )
        
        # Send using data= with FormData object (NOT files=)
        response, status = await self._client._terrakio_request(
            "POST",
            f"collections/{collection}/post_process",
            data=form  # ✅ Pass FormData as data
        )
        
        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Post processing failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def zonal_stats(
        self,
        collection: str,
        id_property: str,
        column_name: str,
        expr: str,
        resolution: Optional[int] = 1,
        in_crs: Optional[str] = "epsg:4326",
        out_crs: Optional[str] = "epsg:4326"
    ) -> Dict[str, Any]:
        """
        Run zonal stats over uploaded geojson collection.

        Args:
            collection: Name of collection
            id_property: Property key in geojson to use as id
            column_name: Name of new column to add
            expr: Terrak.io expression to evaluate
            resolution: Resolution of request (optional, defaults to 1)
            in_crs: CRS of geojson (optional, defaults to "epsg:4326")
            out_crs: Desired output CRS (optional, defaults to "epsg:4326")

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        payload = {
            "id_property": id_property,
            "column_name": column_name,
            "expr": expr,
            "resolution": resolution,
            "in_crs": in_crs,
            "out_crs": out_crs
        }
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/zonal_stats", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Zonal stats failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def zonal_stats_transform(
        self,
        collection: str,
        consumer: str
    ) -> Dict[str, Any]:
        """
        Transform raw data in collection. Creates a new collection.

        Args:
            collection: Name of collection
            consumer: Post processing script (file path or script content)

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        if os.path.isfile(consumer):
            with open(consumer, 'r') as f:
                script_content = f.read()
        else:
            script_content = consumer

        files = {
            'consumer': ('script.py', script_content, 'text/plain')
        }
        
        response, status = await self._client._terrakio_request(
            "POST", 
            f"collections/{collection}/transform", 
            files=files
        )

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Transform failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def download_files(
        self,
        collection: str,
        file_type: str,
        page: Optional[int] = 0,
        page_size: Optional[int] = 100,
        folder: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get list of signed urls to download files in collection.

        Args:
            collection: Name of collection
            file_type: Whether to return raw or processed (after post processing) files
            page: Page number (optional, defaults to 0)
            page_size: Number of files to return per page (optional, defaults to 100)
            folder: If processed file type, which folder to download files from (optional)

        Returns:
            API response as a dictionary containing list of download URLs

        Raises:
            CollectionNotFoundError: If the collection is not found
            DownloadFilesError: If the API request fails due to unknown reasons
        """
        params = {"file_type": file_type}
        
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if folder is not None:
            params["folder"] = folder

        response, status = await self._client._terrakio_request("GET", f"collections/{collection}/download", params=params)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise DownloadFilesError(f"Download files failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def cancel_task(
        self,
        task_id: str
    ):
        """
        Cancel a task by task ID.

        Args:
            task_id: ID of task to cancel

        Returns:
            API response as a dictionary containing task information

        Raises:
            TaskNotFoundError: If the task is not found
            CancelTaskError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("POST", f"tasks/cancel/{task_id}")
        if status != 200:
            if status == 404:
                raise TaskNotFoundError(f"Task {task_id} not found", status_code=status)
            raise CancelTaskError(f"Cancel task failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def cancel_collection_tasks(
        self,
        collection: str
    ):
        """
        Cancel all tasks for a collection.

        Args:
            collection: Name of collection

        Returns:
            API response as a dictionary containing task information for the collection

        Raises:
            CollectionNotFoundError: If the collection is not found
            CancelCollectionTasksError: If the API request fails due to unknown reasons
        """

        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/cancel")
        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise CancelCollectionTasksError(f"Cancel collection tasks failed with status {status}", status_code=status)
    
        return response

    @require_api_key
    async def cancel_all_tasks(
        self
    ):
        """
        Cancel all tasks for the current user.

        Returns:
            API response as a dictionary containing task information for all tasks

        Raises:
            CancelAllTasksError: If the API request fails due to unknown reasons
        """

        response, status = await self._client._terrakio_request("POST", "tasks/cancel")

        if status != 200:
            raise CancelAllTasksError(f"Cancel all tasks failed with status {status}", status_code=status)

        return response