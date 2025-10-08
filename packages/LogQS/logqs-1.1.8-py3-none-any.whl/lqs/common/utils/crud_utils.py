from typing import List, Optional, Callable, Any, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from lqs.common.facade import CoreFacade
from lqs.common.exceptions import ConflictException, NotFoundException


class CRUDUtils:
    def __init__(self, app: "CoreFacade"):
        self.app = app

    def fetch_by_name_or_create(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        list_params: dict = {},
        create_if_missing: bool = True,
        create_params: dict = {},
        create_func: Optional[Callable] = None,
        list_func: Optional[Callable] = None,
        fetch_func: Optional[Callable] = None,
    ) -> Any:
        """
        Fetch or create a resource by name.

        This function fetches a resource by id if provided, or by name if provided,
        or creates the resource if it doesn't exist and ``create_if_missing`` is True.

        If no resource id or name is provided, the function returns None.

        :param resource_type: The type of the resource.
        :type resource_type: str
        :param resource_id: The id of the resource. Defaults to None.
        :type resource_id: str, optional
        :param resource_name: The name of the resource. Defaults to None.
        :type resource_name: str, optional
        :param list_params: Additional parameters to use when listing the resource. Defaults to ``{}``.
        :type list_params: dict, optional
        :param create_if_missing: Whether to create the resource if it doesn't exist. Defaults to True.
        :type create_if_missing: bool, optional
        :param create_params: Additional parameters to use when creating the resource. Defaults to ``{}``.
        :type create_params: dict, optional
        :param create_func: The function to use when creating the resource. Defaults to None.
        :type create_func: Callable, optional
        :param list_func: The function to use when listing the resource. Defaults to None.
        :type list_func: Callable, optional
        :param fetch_func: The function to use when fetching the resource. Defaults to None.
        :type fetch_func: Callable, optional

        :raises NotFoundException: If no resource is found and ``create_if_missing`` is False.

        :returns: The fetched or created resource, or None if no resource is found or created.
        :rtype: Any
        """
        resource = None
        if resource_id is None and resource_name is not None:
            # if no resource id is provided, we try to find the resource by name
            resources = list_func(name=resource_name, **list_params).data
            if len(resources) == 0:
                # we didn't find the resource by name
                if create_if_missing:
                    # if we're allowed to create the resource, we create it using the provided parameters
                    try:
                        resource = create_func(name=resource_name, **create_params).data
                    except ConflictException:
                        # resource with the name may have been created while we were trying to create the resource
                        resources = list_func(name=resource_name, **list_params).data
                        if len(resources) == 0:
                            raise NotFoundException(
                                f"No {resource_type} found with name {resource_name}"
                            )
                        resource = resources[0]
                else:
                    raise NotFoundException(
                        f"No {resource_type} found with name {resource_name}"
                    )
            else:
                # we use the found resource
                resource = resources[0]
        elif resource_id is not None and resource_name is None:
            # if no resource name is provided, we try to find the resource by id
            resource = fetch_func(resource_id).data

        return resource

    def list_all(
        self,
        list_method,
        limit=100,
        start_offset=0,
        max_workers=10,
        **kwargs,
    ) -> List[Any]:
        """
        List all resources.

        This function lists all resources using the provided list method.

        :param list_method: The method to use to list the resources.
        :type list_method: Callable
        :param limit: The maximum number of resources to list at a time. Defaults to 100.
        :type limit: int, optional
        :param start_offset: The offset to start listing resources from. Defaults to 0.
        :type start_offset: int, optional
        :param max_workers: The maximum number of workers to use when listing resources. Defaults to 10.
        :type max_workers: int, optional
        :param kwargs: Additional parameters to pass to the list method.
        :type kwargs: dict

        :returns: The list of resources.
        :rtype: List[Any]
        """

        current_offset = start_offset

        kwargs["limit"] = limit
        kwargs["offset"] = current_offset
        resources = []
        res = list_method(**kwargs)
        resources += res.data
        total_count = res.count
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            while current_offset + limit < total_count:
                current_offset += limit
                kwargs["offset"] = current_offset
                future = executor.submit(list_method, **kwargs)
                futures.append(future)

            for future in futures:
                res = future.result()
                resources += res.data
        return resources

    def fetch_all(
        self,
        list_method,
        fetch_function,
        limit=100,
        start_offset=0,
        max_workers=10,
        **kwargs,
    ) -> List[Any]:
        """
        Fetch all resources.

        This function first lists all resources using the provided list method, then fetches each resource.
        This is useful for process part resources, which do not return the full resource when listed.

        :param list_method: The method to use to list the resources.
        :type list_method: Callable
        :param fetch_function: The function to use to fetch the resources given an instance of the resource.
        :type fetch_function: Callable
        :param limit: The maximum number of resources to list at a time. Defaults to 100.
        :type limit: int, optional
        :param start_offset: The offset to start listing resources from. Defaults to 0.
        :type start_offset: int, optional
        :param max_workers: The maximum number of workers to use when listing resources. Defaults to 10.
        :type max_workers: int, optional
        :param kwargs: Additional parameters to pass to the list method.
        :type kwargs: dict

        :returns: The list of resources.
        :rtype: List[Any]
        """
        shallow_resources = self.list_all(
            list_method=list_method,
            limit=limit,
            start_offset=start_offset,
            max_workers=max_workers,
            **kwargs,
        )
        resources = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for resource in shallow_resources:
                future = executor.submit(fetch_function, resource)
                futures.append(future)

            for future in futures:
                resources.append(future.result())
        return resources
