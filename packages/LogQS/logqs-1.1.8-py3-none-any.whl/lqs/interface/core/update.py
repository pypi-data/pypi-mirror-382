from abc import abstractmethod
from typing import Optional
from uuid import UUID

from lqs.interface.base.update import UpdateInterface as BaseUpdateInterface
import lqs.interface.core.models as models


class UpdateInterface(BaseUpdateInterface):
    @abstractmethod
    def _callback(self, **kwargs) -> models.CallbackDataResponse:
        pass

    def callback(
        self,
        callback_id: UUID,
        data: models.CallbackUpdateRequest,
    ):
        """
        Update a callback.

        Args:
            callback_id: The id of the callback to update.
            data: The data to update the callback with.
        Returns:
            A data response containing the updated callback.
        """
        return self._callback(
            callback_id=callback_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _digestion(self, **kwargs) -> models.DigestionDataResponse:
        pass

    def digestion(
        self,
        digestion_id: UUID,
        data: models.DigestionUpdateRequest,
        lock_token: Optional[str] = None,
    ):
        """
        Update a digestion.

        Args:
            digestion_id: The id of the digestion to update.
            data: The data to update the digestion with.
            lock_token: TODO: update this description
        Returns:
            A data response containing the updated digestion.
        """
        return self._digestion(
            digestion_id=digestion_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _digestion_part(self, **kwargs) -> models.DigestionPartDataResponse:
        pass

    def digestion_part(
        self,
        digestion_part_id: UUID,
        data: models.DigestionPartUpdateRequest,
        digestion_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Update a digestion part.

        Args:
            digestion_part_id: The id of the digestion part to update.
            data: The data to update the digestion part with.
            digestion_id (optional): The id of the digestion to which the digestion part belongs.
        Returns:
            A data response containing the updated digestion part.
        """
        return self._digestion_part(
            digestion_id=digestion_id,
            digestion_part_id=digestion_part_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _digestion_topic(self, **kwargs) -> models.DigestionTopicDataResponse:
        pass

    def digestion_topic(
        self,
        digestion_topic_id: UUID,
        data: models.DigestionTopicUpdateRequest,
        digestion_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Update a digestion topic.

        Args:
            digestion_topic_id: The id of the digestion topic to update.
            data: The data to update the digestion topic with.
            digestion_id (optional): The id of the digestion to which the digestion topic belongs.
        Returns:
            A data response containing the updated digestion topic.
        """
        return self._digestion_topic(
            digestion_id=digestion_id,
            digestion_topic_id=digestion_topic_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _group(self, **kwargs) -> models.GroupDataResponse:
        pass

    def group(
        self,
        group_id: UUID,
        data: models.GroupUpdateRequest,
        lock_token: Optional[str] = None,
    ):
        """
        Update a group.

        Args:
            group_id: The id of the group to update.
            data: The data to update the group with.
        Returns:
            A data response containing the updated group.
        """
        return self._group(
            group_id=group_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _hook(self, **kwargs) -> models.HookDataResponse:
        pass

    def hook(
        self,
        hook_id: UUID,
        data: models.HookUpdateRequest,
        workflow_id: Optional[UUID] = None,
    ):
        """
        Update a hook.

        Args:
            hook_id: The id of the hook to update.
            data: The data to update the hook with.
            workflow_id (optional): The id of the workflow to which the hook belongs.
        Returns:
            A data response containing the updated hook.
        """
        return self._hook(
            workflow_id=workflow_id,
            hook_id=hook_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _ingestion(self, **kwargs) -> models.IngestionDataResponse:
        pass

    def ingestion(
        self,
        ingestion_id: UUID,
        data: models.IngestionUpdateRequest,
        lock_token: Optional[str] = None,
    ):
        """
        Update an ingestion.

        Args:
            ingestion_id: The id of the ingestion to update.
            data: The data to update the ingestion with.
        Returns:
            A data response containing the updated ingestion.
        """
        return self._ingestion(
            ingestion_id=ingestion_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _ingestion_part(self, **kwargs) -> models.IngestionPartDataResponse:
        pass

    def ingestion_part(
        self,
        ingestion_part_id: UUID,
        data: models.IngestionPartUpdateRequest,
        ingestion_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Update an ingestion part.

        Args:
            ingestion_part_id: The id of the ingestion part to update.
            data: The data to update the ingestion part with.
            ingestion_id (optional): The id of the ingestion to which the ingestion part belongs.
        Returns:
            A data response containing the updated ingestion part.
        """
        return self._ingestion_part(
            ingestion_id=ingestion_id,
            ingestion_part_id=ingestion_part_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _label(self, **kwargs) -> models.LabelDataResponse:
        pass

    def label(self, label_id: UUID, data: models.LabelUpdateRequest):
        """
        Update a label.

        Args:
            label_id: The id of the label to update.
            data: The data to update the label with.
        Returns:
            A data response containing the updated label.
        """
        return self._label(
            label_id=label_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _log(self, **kwargs) -> models.LogDataResponse:
        pass

    def log(
        self,
        log_id: UUID,
        data: models.LogUpdateRequest,
        lock_token: Optional[str] = None,
    ):
        """
        Update a log.

        Args:
            log_id: The id of the log to update.
            data: The data to update the log with.
        Returns:
            A data response containing the updated log.
        """
        return self._log(
            log_id=log_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _log_object(self, **kwargs) -> models.ObjectDataResponse:
        pass

    def log_object(
        self,
        log_id: UUID,
        object_key: str,
        data: models.ObjectUpdateRequest,
        lock_token: Optional[str] = None,
    ):
        """
        Update a log object.

        Args:
            log_id: The id of the log to which the object belongs.
            object_key: The key of the object to update.
            data: The data to update the object with.
        Returns:
            A data response containing the updated object.
        """
        return self._log_object(
            log_id=log_id,
            object_key=object_key,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _object(self, **kwargs) -> models.ObjectDataResponse:
        pass

    def object(
        self, object_store_id: UUID, object_key: str, data: models.ObjectUpdateRequest
    ):
        """
        Update an object.

        Args:
            object_store_id: The id of the object store to which the object belongs.
            object_key: The key of the object to update.
            data: The data to update the object with.
        Returns:
            A data response containing the updated object.
        """
        return self._object(
            object_store_id=object_store_id,
            object_key=object_key,
            data=self._process_data(data),
        )

    @abstractmethod
    def _object_store(self, **kwargs) -> models.ObjectStoreDataResponse:
        pass

    def object_store(
        self, object_store_id: UUID, data: models.ObjectStoreUpdateRequest
    ):
        """
        Update an object store.

        Args:
            object_store_id: The id of the object store to update.
            data: The data to update the object store with.
        Returns:
            A data response containing the updated object store.
        """
        return self._object_store(
            object_store_id=object_store_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _query(self, **kwargs) -> models.QueryDataResponse:
        pass

    def query(
        self,
        query_id: UUID,
        data: models.QueryUpdateRequest,
        log_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Update a query.

        Args:
            query_id: The id of the query to update.
            data: The data to update the query with.
            log_id (optional): The id of the log to which the query belongs.
        Returns:
            A data response containing the updated query.
        """
        return self._query(
            log_id=log_id,
            query_id=query_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _record(self, **kwargs) -> models.RecordDataResponse:
        pass

    def record(
        self,
        timestamp: models.Int64,
        topic_id: UUID,
        data: models.RecordUpdateRequest,
        lock_token: Optional[str] = None,
    ):
        """
        Update a record.

        Args:
            timestamp: The timestamp of the record to update.
            topic_id: The id of the topic to which the record belongs.
            data: The data to update the record with.
        Returns:
            A data response containing the updated record.
        """
        return self._record(
            timestamp=timestamp,
            topic_id=topic_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _tag(self, **kwargs) -> models.TagDataResponse:
        pass

    def tag(
        self,
        tag_id: UUID,
        data: models.TagUpdateRequest,
        log_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Update a tag.

        Args:
            tag_id: The id of the tag to update.
            data: The data to update the tag with.
            log_id (optional): The id of the log to which the tag belongs.
        Returns:
            A data response containing the updated tag.
        """
        return self._tag(
            log_id=log_id,
            tag_id=tag_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _topic(self, **kwargs) -> models.TopicDataResponse:
        pass

    def topic(
        self,
        topic_id: UUID,
        data: models.TopicUpdateRequest,
        lock_token: Optional[str] = None,
    ):
        """
        Update a topic.

        Args:
            topic_id: The id of the topic to update.
            data: The data to update the topic with.
        Returns:
            A data response containing the updated topic.
        """
        return self._topic(
            topic_id=topic_id,
            data=self._process_data(data),
            lock_token=lock_token,
        )

    @abstractmethod
    def _workflow(self, **kwargs) -> models.WorkflowDataResponse:
        pass

    def workflow(self, workflow_id: UUID, data: models.WorkflowUpdateRequest):
        """
        Update a workflow.

        Args:
            workflow_id: The id of the workflow to update.
            data: The data to update the workflow with.
        Returns:
            A data response containing the updated workflow.
        """
        return self._workflow(
            workflow_id=workflow_id,
            data=self._process_data(data),
        )
