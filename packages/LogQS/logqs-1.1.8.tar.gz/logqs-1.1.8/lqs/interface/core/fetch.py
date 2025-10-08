from abc import abstractmethod
from typing import Optional, Union
from uuid import UUID

from lqs.interface.base.fetch import FetchInterface as BaseFetchInterface
import lqs.interface.core.models as models


class FetchInterface(BaseFetchInterface):
    @abstractmethod
    def _callback(self, **kwargs) -> models.CallbackDataResponse:
        pass

    def callback(self, callback_id: UUID):
        return self._callback(
            callback_id=callback_id,
        )

    @abstractmethod
    def _digestion(self, **kwargs) -> models.DigestionDataResponse:
        pass

    def digestion(self, digestion_id: UUID):
        """
        Fetches a digestion by ID.

        Args:
            digestion_id: The ID of the digestion to fetch.
        Returns:
            A data response for the digestion.
        """
        return self._digestion(
            digestion_id=digestion_id,
        )

    @abstractmethod
    def _digestion_part(self, **kwargs) -> models.DigestionPartDataResponse:
        pass

    def digestion_part(
        self, digestion_part_id: UUID, digestion_id: Optional[UUID] = None
    ):
        """
        Fetches a digestion part by ID.

        Args:
            digestion_part_id: The ID of the digestion part to fetch.
            digestion_id: The ID of the digestion to which the digestion part belongs.
        Returns:
            A data response for the digestion part.
        """
        return self._digestion_part(
            digestion_id=digestion_id,
            digestion_part_id=digestion_part_id,
        )

    @abstractmethod
    def _digestion_topic(self, **kwargs) -> models.DigestionTopicDataResponse:
        pass

    def digestion_topic(
        self, digestion_topic_id: UUID, digestion_id: Optional[UUID] = None
    ):
        """
        Fetches a digestion topic by ID.

        Args:
            digestion_topic_id: The ID of the digestion topic to fetch.
            digestion_id: The ID of the digestion to which the digestion topic belongs.
        Returns:
            A data response for the digestion topic.
        """
        return self._digestion_topic(
            digestion_id=digestion_id,
            digestion_topic_id=digestion_topic_id,
        )

    @abstractmethod
    def _group(self, **kwargs) -> models.GroupDataResponse:
        pass

    def group(self, group_id: UUID):
        """
        Fetches a group by ID.

        Args:
            group_id: The ID of the group to fetch.
        Returns:
            A data response for the group.
        """
        return self._group(
            group_id=group_id,
        )

    @abstractmethod
    def _hook(self, **kwargs) -> models.HookDataResponse:
        pass

    def hook(self, hook_id: UUID, workflow_id: Optional[UUID] = None):
        """
        Fetches a hook by ID.

        Args:
            hook_id: The ID of the hook to fetch.
            workflow_id: The ID of the workflow to which the hook belongs.
        Returns:
            A data response for the hook.
        """
        return self._hook(
            workflow_id=workflow_id,
            hook_id=hook_id,
        )

    @abstractmethod
    def _ingestion(self, **kwargs) -> models.IngestionDataResponse:
        pass

    def ingestion(self, ingestion_id: UUID):
        """
        Fetches an ingestion by ID.

        Args:
            ingestion_id: The ID of the ingestion to fetch.
        Returns:
            A data response for the ingestion.
        """
        return self._ingestion(
            ingestion_id=ingestion_id,
        )

    @abstractmethod
    def _ingestion_part(self, **kwargs) -> models.IngestionPartDataResponse:
        pass

    def ingestion_part(
        self, ingestion_part_id: UUID, ingestion_id: Optional[UUID] = None
    ):
        """
        Fetches an ingestion part by ID.

        Args:
            ingestion_part_id: The ID of the ingestion part to fetch.
            ingestion_id: The ID of the ingestion to which the ingestion part belongs.
        Returns:
            A data response for the ingestion part.
        """
        return self._ingestion_part(
            ingestion_id=ingestion_id,
            ingestion_part_id=ingestion_part_id,
        )

    @abstractmethod
    def _label(self, **kwargs) -> models.LabelDataResponse:
        pass

    def label(self, label_id: UUID):
        """
        Fetches a label by ID.

        Args:
            label_id: The ID of the label to fetch.
        Returns:
            A data response for the label.
        """
        return self._label(
            label_id=label_id,
        )

    @abstractmethod
    def _log(self, **kwargs) -> models.LogDataResponse:
        pass

    def log(self, log_id: UUID):
        """
        Fetches a log by ID.

        Args:
            log_id: The ID of the log to fetch.
        Returns:
            A data response for the log.
        """
        return self._log(
            log_id=log_id,
        )

    @abstractmethod
    def _log_object(self, **kwargs) -> Union[models.ObjectDataResponse, bytes]:
        pass

    def log_object(
        self,
        object_key: str,
        log_id: UUID,
        redirect: Optional[bool] = False,
        offset: Optional[int] = None,
        length: Optional[int] = None,
    ) -> Union[models.ObjectDataResponse, bytes]:
        """
        Fetches an object by key.

        Args:
            object_key: The key of the object to fetch.
            log_id: The ID of the log to which the object belongs.
            redirect: Whether to redirect to the object store or return the object directly. Defaults to False.
            offset: The offset from which to read the object.
            length: The length of the object to read.
        Returns:
            A data response for the object or the object itself as bytes if redirect is True.
        """
        return self._log_object(
            log_id=log_id,
            object_key=object_key,
            redirect=redirect,
            offset=offset,
            length=length,
        )

    @abstractmethod
    def _log_object_part(self, **kwargs) -> models.ObjectPartDataResponse:
        pass

    def log_object_part(self, object_key: str, part_number: int, log_id: UUID):
        """
        Fetches an object part by key and part number.

        Args:
            object_key: The key of the object to fetch.
            part_number: The part number of the object to fetch.
            log_id: The ID of the log to which the object belongs.
        Returns:
            A data response for the object part.
        """
        return self._log_object_part(
            object_key=object_key,
            part_number=part_number,
            log_id=log_id,
        )

    @abstractmethod
    def _object(self, **kwargs) -> Union[models.ObjectDataResponse, bytes]:
        pass

    def object(
        self,
        object_key: str,
        object_store_id: UUID,
        redirect: Optional[bool] = False,
        offset: Optional[int] = None,
        length: Optional[int] = None,
    ) -> Union[models.ObjectDataResponse, bytes]:
        """
        Fetches an object by key.

        Args:
            object_key: The key of the object to fetch.
            object_store_id: The ID of the object store to which the object belongs.
            redirect: Whether to redirect to the object store or return the object directly. Defaults to False.
            offset: The offset from which to read the object.
            length: The length of the object to read.
        Returns:
            A data response for the object or the object itself as bytes if redirect is True.
        """
        return self._object(
            object_store_id=object_store_id,
            object_key=object_key,
            redirect=redirect,
            offset=offset,
            length=length,
        )

    @abstractmethod
    def _object_part(self, **kwargs) -> models.ObjectPartDataResponse:
        pass

    def object_part(self, object_key: str, part_number: int, object_store_id: UUID):
        """
        Fetches an object part by key and part number.

        Args:
            object_key: The key of the object to fetch.
            part_number: The part number of the object to fetch.
            object_store_id: The ID of the object store to which the object belongs.
        Returns:
            A data response for the object part.
        """
        return self._object_part(
            object_key=object_key,
            part_number=part_number,
            object_store_id=object_store_id,
        )

    @abstractmethod
    def _object_store(self, **kwargs) -> models.ObjectStoreDataResponse:
        pass

    def object_store(self, object_store_id: UUID):
        """
        Fetches an object store by ID.

        Args:
            object_store_id: The ID of the object store to fetch.
        Returns:
            A data response for the object store.
        """
        return self._object_store(
            object_store_id=object_store_id,
        )

    @abstractmethod
    def _object_store_session_credentials(
        self, **kwargs
    ) -> models.ObjectStoreSessionCredentialsDataResponse:
        pass

    def object_store_session_credentials(self, object_store_id: UUID):
        """
        Fetches session credentials for an object store given its ID.

        Args:
            object_store_id: The ID of the object store to fetch.
        Returns:
            A data response for the object store session credentials.
        """
        return self._object_store_session_credentials(
            object_store_id=object_store_id,
        )

    @abstractmethod
    def _query(self, **kwargs) -> models.QueryDataResponse:
        pass

    def query(self, query_id: UUID, log_id: Optional[UUID] = None):
        """
        Fetches a query by ID.

        Args:
            query_id: The ID of the query to fetch.
            log_id: The ID of the log to which the query belongs.
        Returns:
            A data response for the query.
        """
        return self._query(
            log_id=log_id,
            query_id=query_id,
        )

    @abstractmethod
    def _record(self, **kwargs) -> models.RecordDataResponse:
        pass

    def record(
        self,
        timestamp: models.Int64,
        topic_id: UUID,
        include_auxiliary_data: bool = False,
        include_raw_data: bool = False,
        auxiliary_context: Optional[str] = None,
    ):
        """
        Fetches a record by timestamp and topic ID.

        Args:
            timestamp: The timestamp of the record to fetch.
            topic_id: The ID of the topic to which the record belongs.
            include_auxiliary_data: Whether to include auxiliary data in the record. Defaults to False.
            include_raw_data: Whether to include raw data in the record. Defaults to False.
            auxiliary_context: The context for the auxiliary data generation to include in the record. Defaults to None.
        Returns:
            A data response for the record.
        """
        return self._record(
            timestamp=timestamp,
            topic_id=topic_id,
            include_auxiliary_data=include_auxiliary_data,
            include_raw_data=include_raw_data,
            auxiliary_context=auxiliary_context,
        )

    @abstractmethod
    def _tag(self, **kwargs) -> models.TagDataResponse:
        pass

    def tag(self, tag_id: UUID, log_id: Optional[UUID] = None):
        """
        Fetches a tag by ID.

        Args:
            tag_id: The ID of the tag to fetch.
            log_id: The ID of the log to which the tag belongs.
        Returns:
            A data response for the tag.
        """
        return self._tag(
            log_id=log_id,
            tag_id=tag_id,
        )

    @abstractmethod
    def _topic(self, **kwargs) -> models.TopicDataResponse:
        pass

    def topic(self, topic_id: UUID):
        """
        Fetches a topic by ID.

        Args:
            topic_id: The ID of the topic to fetch.
        Returns:
            A data response for the topic.
        """
        return self._topic(
            topic_id=topic_id,
        )

    @abstractmethod
    def _workflow(self, **kwargs) -> models.WorkflowDataResponse:
        pass

    def workflow(self, workflow_id: UUID):
        """
        Fetches a workflow by ID.

        Args:
            workflow_id: The ID of the workflow to fetch.
        Returns:
            A data response for the workflow.
        """
        return self._workflow(
            workflow_id=workflow_id,
        )
