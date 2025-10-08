from abc import abstractmethod
from typing import Optional
from uuid import UUID

from lqs.interface.base.delete import DeleteInterface as BaseDeleteInterface
import lqs.interface.core.models as models


class DeleteInterface(BaseDeleteInterface):
    @abstractmethod
    def _callback(self, **kwargs):
        pass

    def callback(self, callback_id: UUID):
        return self._callback(
            callback_id=callback_id,
        )

    @abstractmethod
    def _digestion(self, **kwargs):
        pass

    def digestion(self, digestion_id: UUID, lock_token: Optional[str] = None):
        """
        Delete a digestion.

        Args:
            digestion_id (UUID): ID of the digestion to delete.
        Returns:
            None
        """
        return self._digestion(
            digestion_id=digestion_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _digestion_part(self, **kwargs):
        pass

    def digestion_part(
        self,
        digestion_part_id: UUID,
        digestion_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Delete a digestion part.

        Args:
            digestion_part_id (UUID): ID of the digestion part to delete.
            digestion_id (UUID, optional): ID of the digestion to which the digestion part belongs.
        Returns:
            None
        """
        return self._digestion_part(
            digestion_part_id=digestion_part_id,
            digestion_id=digestion_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _digestion_topic(self, **kwargs):
        pass

    def digestion_topic(
        self,
        digestion_topic_id: UUID,
        digestion_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Delete a digestion topic.

        Args:
            digestion_topic_id (UUID): ID of the digestion topic to delete.
            digestion_id (UUID, optional): ID of the digestion to which the digestion topic belongs.
        Returns:
            None
        """
        return self._digestion_topic(
            digestion_topic_id=digestion_topic_id,
            digestion_id=digestion_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _group(self, **kwargs):
        pass

    def group(self, group_id: UUID, lock_token: Optional[str] = None):
        """
        Delete a group.

        Args:
            group_id (UUID): ID of the group to delete.
        Returns:
            None
        """
        return self._group(
            group_id=group_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _hook(self, **kwargs):
        pass

    def hook(self, hook_id: UUID, workflow_id: Optional[UUID] = None):
        """
        Delete a hook.

        Args:
            hook_id (UUID): ID of the hook to delete.
            workflow_id (UUID, optional): ID of the workflow to which the hook belongs.
        Returns:
            None
        """
        return self._hook(
            hook_id=hook_id,
            workflow_id=workflow_id,
        )

    @abstractmethod
    def _ingestion(self, **kwargs):
        pass

    def ingestion(self, ingestion_id: UUID, lock_token: Optional[str] = None):
        """
        Delete an ingestion.

        Args:
            ingestion_id (UUID): ID of the ingestion to delete.
        Returns:
            None
        """
        return self._ingestion(
            ingestion_id=ingestion_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _ingestion_part(self, **kwargs):
        pass

    def ingestion_part(
        self,
        ingestion_part_id: UUID,
        ingestion_id: Optional[UUID],
        lock_token: Optional[str] = None,
    ):
        """
        Delete an ingestion part.

        Args:
            ingestion_part_id (UUID): ID of the ingestion part to delete.
            ingestion_id (UUID, optional): ID of the ingestion to which the ingestion part belongs.
        Returns:
            None
        """
        return self._ingestion_part(
            ingestion_part_id=ingestion_part_id,
            ingestion_id=ingestion_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _label(self, **kwargs):
        pass

    def label(self, label_id: UUID):
        """
        Delete a label.

        Args:
            label_id (UUID): ID of the label to delete.
        Returns:
            None
        """
        return self._label(
            label_id=label_id,
        )

    @abstractmethod
    def _log(self, **kwargs):
        pass

    def log(self, log_id: UUID, lock_token: Optional[str] = None):
        """
        Delete a log.

        Args:
            log_id (UUID): ID of the log to delete.
        Returns:
            None
        """
        return self._log(log_id=log_id, lock_token=lock_token)

    @abstractmethod
    def _log_object(self, **kwargs):
        pass

    def log_object(
        self, log_id: UUID, object_key: str, lock_token: Optional[str] = None
    ):
        """
        Delete a log object.

        Args:
            log_id (UUID): ID of the log to which the log object belongs.
            object_key (str): Key of the log object to delete.
        Returns:
            None
        """
        return self._log_object(
            log_id=log_id,
            object_key=object_key,
            lock_token=lock_token,
        )

    @abstractmethod
    def _object(self, **kwargs):
        pass

    def object(self, object_store_id: UUID, object_key: str):
        """
        Delete an object.

        Args:
            object_store_id (UUID): ID of the object store to which the object belongs.
            object_key (str): Key of the object to delete.
        Returns:
            None
        """
        return self._object(
            object_store_id=object_store_id,
            object_key=object_key,
        )

    @abstractmethod
    def _object_store(self, **kwargs):
        pass

    def object_store(self, object_store_id: UUID):
        """
        Delete an object store.

        Args:
            object_store_id (UUID): ID of the object store to delete.
        Returns:
            None
        """
        return self._object_store(
            object_store_id=object_store_id,
        )

    @abstractmethod
    def _query(self, **kwargs):
        pass

    def query(
        self,
        query_id: UUID,
        log_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Delete a query.

        Args:
            query_id (UUID): ID of the query to delete.
            log_id (UUID, optional): ID of the log to which the query belongs.
        Returns:
            None
        """
        return self._query(
            query_id=query_id,
            log_id=log_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _record(self, **kwargs):
        pass

    def record(
        self,
        timestamp: models.Int64,
        topic_id: UUID,
        lock_token: Optional[str] = None,
    ):
        """
        Delete a record.

        Args:
            timestamp (int): Timestamp of the record to delete.
            topic_id (UUID): ID of the topic to which the record belongs.
        Returns:
            None
        """
        return self._record(
            timestamp=timestamp, topic_id=topic_id, lock_token=lock_token
        )

    @abstractmethod
    def _tag(self, **kwargs):
        pass

    def tag(
        self,
        tag_id: UUID,
        log_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Delete a tag.

        Args:
            tag_id (UUID): ID of the tag to delete.
            log_id (UUID, optional): ID of the log to which the tag belongs.
        Returns:
            None
        """
        return self._tag(
            tag_id=tag_id,
            log_id=log_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _topic(self, **kwargs):
        pass

    def topic(self, topic_id: UUID, lock_token: Optional[str] = None):
        """
        Delete a topic.

        Args:
            topic_id (UUID): ID of the topic to delete.
        Returns:
            None
        """
        return self._topic(
            topic_id=topic_id,
            lock_token=lock_token,
        )

    @abstractmethod
    def _workflow(self, **kwargs):
        pass

    def workflow(self, workflow_id: UUID):
        """
        Delete a workflow.

        Args:
            workflow_id (UUID): ID of the workflow to delete.
        Returns:
            None
        """
        return self._workflow(
            workflow_id=workflow_id,
        )
