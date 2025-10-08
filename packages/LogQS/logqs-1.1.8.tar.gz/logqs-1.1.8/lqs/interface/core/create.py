from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from lqs.interface.base.create import CreateInterface as BaseCreateInterface
import lqs.interface.core.models as models
from lqs.interface.core.models import ProcessState


class CreateInterface(BaseCreateInterface):
    @abstractmethod
    def _callback(self, **kwargs) -> models.CallbackDataResponse:
        pass

    def callback(
        self,
        name: str,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        managed: Optional[bool] = False,
        default: Optional[bool] = False,
        disabled: Optional[bool] = False,
        uri: Optional[str] = None,
        secret: Optional[str] = None,
        parameter_schema: Optional[dict] = None,
    ):
        return self._callback(
            name=name,
            note=note,
            context=context,
            managed=managed,
            default=default,
            disabled=disabled,
            uri=uri,
            secret=secret,
            parameter_schema=parameter_schema,
        )

    def _callback_by_model(
        self,
        data: models.CallbackCreateRequest,
    ):
        return self.callback(**data.model_dump())

    @abstractmethod
    def _digestion(self, **kwargs) -> models.DigestionDataResponse:
        pass

    def digestion(
        self,
        log_id: UUID,
        name: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        workflow_id: Optional[UUID] = None,
        workflow_context: Optional[dict] = None,
        state: ProcessState = ProcessState.ready,
        lock_token: Optional[str] = None,
    ):
        """
        Create a digestion.

        :param log_id: The ID of the log to which the digestion should be added.
        :type log_id: str
        :param name: The name of the digestion. Defaults to None.
        :type name: str, optional
        :param context: The context to use for the digestion. Defaults to None.
        :type context: dict, optional
        :param note: A note about the digestion. Defaults to None.
        :type note: str, optional
        :param locked: Whether the digestion is locked. Defaults to False.
        :type locked: bool, optional
        :param workflow_id: The ID of the workflow to use for the digestion. Defaults to None.
        :type workflow_id: str, optional
        :param workflow_context: The context to use for the workflow. Defaults to None.
        :type workflow_context: dict, optional
        :param state: The state of the digestion. Defaults to ProcessState.ready.
        :type state: ProcessState, optional
        :returns: A data response with the created digestion.
        :rtype: DigestionDataResponse
        """

        return self._digestion(
            log_id=log_id,
            name=name,
            note=note,
            context=context,
            locked=locked,
            workflow_id=workflow_id,
            workflow_context=workflow_context,
            state=state,
            lock_token=lock_token,
        )

    def _digestion_by_model(
        self,
        data: models.DigestionCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.digestion(**data.model_dump(), lock_token=lock_token)

    @abstractmethod
    def _digestion_part(self, **kwargs) -> models.DigestionPartDataResponse:
        pass

    def digestion_part(
        self,
        digestion_id: UUID,
        sequence: int,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        workflow_id: Optional[UUID] = None,
        workflow_context: Optional[dict] = None,
        state: ProcessState = ProcessState.ready,
        index: Optional[List[models.DigestionPartIndex]] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Create a digestion part.

        :param digestion_id: The ID of the digestion to which the digestion part should be added.
        :type digestion_id: str
        :param sequence: The sequence of the digestion part.
        :type sequence: int
        :param locked: Whether the digestion part is locked. Defaults to False.
        :type locked: bool, optional
        :param workflow_id: The ID of the workflow to use for the digestion part. Defaults to None.
        :type workflow_id: str, optional
        :param workflow_context: The context to use for the workflow. Defaults to None.
        :type workflow_context: dict, optional
        :param state: The state of the digestion part. Defaults to ProcessState.ready.
        :type state: ProcessState, optional
        :param index: The index of the digestion part. Defaults to None.
        :type index: int, optional
        :returns: A data response with the created digestion part.
        :rtype: DigestionPartDataResponse
        """
        return self._digestion_part(
            digestion_id=digestion_id,
            sequence=sequence,
            context=context,
            locked=locked,
            workflow_id=workflow_id,
            workflow_context=workflow_context,
            state=state,
            index=index,
            lock_token=lock_token,
        )

    def _digestion_part_by_model(
        self,
        data: models.DigestionPartCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.digestion_part(**data.model_dump(), lock_token=lock_token)

    def _digestion_part_for_digestion_by_model(
        self,
        digestion_id: UUID,
        data: models.DigestionPartForDigestionCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.digestion_part(
            digestion_id=digestion_id, **data.model_dump(), lock_token=lock_token
        )

    @abstractmethod
    def _digestion_topic(self, **kwargs) -> models.DigestionTopicDataResponse:
        pass

    def digestion_topic(
        self,
        digestion_id: UUID,
        topic_id: UUID,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        frequency: Optional[float] = None,
        query_data_filter: Optional[dict] = None,
        context_filter: Optional[dict] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Create a digestion topic.

        :param digestion_id: The ID of the digestion to which the digestion topic should be added.
        :type digestion_id: str
        :param topic_id: The ID of the topic to be digested.
        :type topic_id: str
        :param start_time: The start time of the digestion topic. Defaults to None.
        :type start_time: int, optional
        :param end_time: The end time of the digestion topic. Defaults to None.
        :type end_time: int, optional
        :param frequency: The frequency of the digestion topic. Defaults to None.
        :type frequency: float, optional
        :param query_data_filter: The data filter of the digestion topic. Defaults to None.
        :type query_data_filter: dict, optional
        :param context_filter: The context filter of the digestion topic. Defaults to None.
        :type context_filter: dict, optional
        :returns: A data response with the created digestion topic.
        :rtype: DigestionTopicDataResponse
        """
        return self._digestion_topic(
            digestion_id=digestion_id,
            topic_id=topic_id,
            start_time=start_time,
            end_time=end_time,
            frequency=frequency,
            query_data_filter=query_data_filter,
            context_filter=context_filter,
            lock_token=lock_token,
        )

    def _digestion_topic_by_model(
        self,
        data: models.DigestionTopicCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.digestion_topic(**data.model_dump(), lock_token=lock_token)

    def _digestion_topic_for_digestion_by_model(
        self,
        digestion_id: UUID,
        data: models.DigestionTopicForDigestionCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.digestion_topic(
            digestion_id=digestion_id, **data.model_dump(), lock_token=lock_token
        )

    @abstractmethod
    def _group(self, **kwargs) -> models.GroupDataResponse:
        pass

    def group(
        self,
        name: str,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        default_workflow_id: Optional[UUID] = None,
    ):
        """
        Create a group.

        :param name: The name of the group.
        :type name: str
        :param note: A note about the group. Defaults to None.
        :type note: str, optional
        :param context: The context to use for the group. Defaults to None.
        :type context: dict, optional
        :param locked: Whether the group is locked. Defaults to False.
        :type locked: bool, optional
        :param default_workflow_id: The ID of the default workflow for the group. Defaults to None.
        :type default_workflow_id: str, optional
        :returns: A data response with the created group.
        :rtype: GroupDataResponse
        """
        return self._group(
            name=name,
            note=note,
            context=context,
            locked=locked,
            default_workflow_id=default_workflow_id,
        )

    def _group_by_model(self, data: models.GroupCreateRequest):
        return self.group(**data.model_dump())

    @abstractmethod
    def _hook(self, **kwargs) -> models.HookDataResponse:
        pass

    def hook(
        self,
        workflow_id: UUID,
        trigger_process: str,
        trigger_state: str,
        name: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        managed: Optional[bool] = False,
        disabled: Optional[bool] = False,
        uri: Optional[str] = None,
        secret: Optional[str] = None,
    ):
        """
        Create a hook.

        :param workflow_id: The ID of the workflow to which the hook should be added.
        :type workflow_id: str
        :param trigger_process: The process to trigger.
        :type trigger_process: str
        :param trigger_state: The state to trigger.
        :type trigger_state: str
        :param name: The name of the hook. Defaults to None.
        :type name: str, optional
        :param note: A note about the hook. Defaults to None.
        :type note: str, optional
        :param context: The context to use for the hook. Defaults to None.
        :type context: dict, optional
        :param managed: Whether the hook is managed. Defaults to False.
        :type managed: bool, optional
        :param disabled: Whether the hook is disabled. Defaults to False.
        :type disabled: bool, optional
        :param uri: The URI of the hook. Defaults to None.
        :type uri: str, optional
        :param secret: The secret of the hook. Defaults to None.
        :type secret: str, optional
        :returns: A data response with the created hook.
        :rtype: HookDataResponse
        """
        return self._hook(
            workflow_id=workflow_id,
            trigger_process=trigger_process,
            trigger_state=trigger_state,
            name=name,
            note=note,
            context=context,
            managed=managed,
            disabled=disabled,
            uri=uri,
            secret=secret,
        )

    def _hook_by_model(self, data: models.HookCreateRequest):
        return self.hook(**data.model_dump())

    def _hook_for_workflow_by_model(
        self, workflow_id: UUID, data: models.HookForWorkflowCreateRequest
    ):
        return self.hook(workflow_id=workflow_id, **data.model_dump())

    @abstractmethod
    def _ingestion(self, **kwargs) -> models.IngestionDataResponse:
        pass

    def ingestion(
        self,
        log_id: UUID,
        name: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        object_store_id: Optional[UUID] = None,
        object_key: Optional[str] = None,
        locked: Optional[bool] = False,
        workflow_id: Optional[UUID] = None,
        workflow_context: Optional[dict] = None,
        state: ProcessState = ProcessState.ready,
        lock_token: Optional[str] = None,
    ):
        """
        Create an ingestion.

        :param log_id: The ID of the log to which the ingestion should be added.
        :type log_id: str
        :param name: The name of the ingestion. Defaults to None.
        :type name: str, optional
        :param note: A note about the ingestion. Defaults to None.
        :type note: str, optional
        :param context: The context to use for the ingestion. Defaults to None.
        :type context: dict, optional
        :param object_store_id: The ID of the object store to use for the ingestion. Defaults to None.
        :type object_store_id: str, optional
        :param object_key: The key of the object to use for the ingestion. Defaults to None.
        :type object_key: str, optional
        :param locked: Whether the ingestion is locked. Defaults to False.
        :type locked: bool, optional
        :param workflow_id: The ID of the workflow to use for the ingestion. Defaults to None.
        :type workflow_id: str, optional
        :param workflow_context: The context to use for the workflow. Defaults to None.
        :type workflow_context: dict, optional
        :param state: The state of the ingestion. Defaults to ProcessState.ready.
        :type state: ProcessState, optional
        :returns: A data response with the created ingestion.
        :rtype: IngestionDataResponse
        """
        return self._ingestion(
            log_id=log_id,
            name=name,
            note=note,
            context=context,
            object_store_id=object_store_id,
            object_key=object_key,
            locked=locked,
            workflow_id=workflow_id,
            workflow_context=workflow_context,
            state=state,
            lock_token=lock_token,
        )

    def _ingestion_by_model(
        self,
        data: models.IngestionCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.ingestion(**data.model_dump(), lock_token=lock_token)

    @abstractmethod
    def _ingestion_part(self, **kwargs) -> models.IngestionPartDataResponse:
        pass

    def ingestion_part(
        self,
        ingestion_id: UUID,
        sequence: int,
        source: Optional[str] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        workflow_id: Optional[UUID] = None,
        workflow_context: Optional[dict] = None,
        state: ProcessState = ProcessState.ready,
        index: Optional[List[models.IngestionPartIndex]] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Create an ingestion part.

        :param ingestion_id: The ID of the ingestion to which the ingestion part should be added.
        :type ingestion_id: str
        :param sequence: The sequence of the ingestion part.
        :type sequence: int
        :param source: The source of the ingestion part. Defaults to None.
        :type source: str, optional
        :param locked: Whether the ingestion part is locked. Defaults to False.
        :type locked: bool, optional
        :param workflow_id: The ID of the workflow to use for the ingestion part. Defaults to None.
        :type workflow_id: str, optional
        :param workflow_context: The context to use for the workflow. Defaults to None.
        :type workflow_context: dict, optional
        :param state: The state of the ingestion part. Defaults to ProcessState.queued.
        :type state: ProcessState, optional
        :param index: The index of the ingestion part. Defaults to None.
        :type index: int, optional
        :returns: A data response with the created ingestion part.
        :rtype: IngestionPartDataResponse
        """
        return self._ingestion_part(
            ingestion_id=ingestion_id,
            sequence=sequence,
            source=source,
            context=context,
            locked=locked,
            workflow_id=workflow_id,
            workflow_context=workflow_context,
            state=state,
            index=index,
            lock_token=lock_token,
        )

    def _ingestion_part_by_model(
        self,
        data: models.IngestionPartCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.ingestion_part(**data.model_dump(), lock_token=lock_token)

    def _ingestion_part_for_ingestion_by_model(
        self,
        ingestion_id: UUID,
        data: models.IngestionPartForIngestionCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.ingestion_part(
            ingestion_id=ingestion_id, **data.model_dump(), lock_token=lock_token
        )

    @abstractmethod
    def _label(self, **kwargs) -> models.LabelDataResponse:
        pass

    def label(
        self, value: str, note: Optional[str] = None, category: Optional[str] = None
    ):
        """
        Create a label.

        :param value: The value of the label.
        :type value: str
        :param note: A note about the label. Defaults to None.
        :type note: str, optional
        :returns: A data response with the created label.
        :rtype: LabelDataResponse
        """
        return self._label(
            value=value,
            note=note,
            category=category,
        )

    def _label_by_model(self, data: models.LabelCreateRequest):
        return self.label(**data.model_dump())

    @abstractmethod
    def _log(self, **kwargs) -> models.LogDataResponse:
        pass

    def log(
        self,
        group_id: UUID,
        name: str,
        note: Optional[str] = None,
        base_timestamp: Optional[int] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        default_workflow_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Create a log.

        :param group_id: The ID of the group to which the log should be added.
        :type group_id: str
        :param name: The name of the log.
        :type name: str
        :param note: A note about the log. Defaults to None.
        :type note: str, optional
        :param base_timestamp: The base timestamp of the log. Defaults to None.
        :type base_timestamp: int, optional
        :param context: The context to use for the log. Defaults to None.
        :type context: dict, optional
        :param locked: Whether the log is locked. Defaults to False.
        :type locked: bool, optional
        :param default_workflow_id: The ID of the default workflow for the log. Defaults to None.
        :type default_workflow_id: str, optional
        :returns: A data response with the created log.
        :rtype: LogDataResponse
        """
        return self._log(
            group_id=group_id,
            name=name,
            note=note,
            base_timestamp=base_timestamp,
            context=context,
            locked=locked,
            default_workflow_id=default_workflow_id,
            lock_token=lock_token,
        )

    def _log_by_model(
        self,
        data: models.LogCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.log(**data.model_dump(), lock_token=lock_token)

    @abstractmethod
    def _log_object(self, **kwargs) -> models.ObjectDataResponse:
        pass

    def log_object(
        self,
        key: str,
        log_id: UUID,
        content_type: Optional[str] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Create a log object.

        :param key: The key of the log object.
        :type key: str
        :param log_id: The ID of the log to which the log object should be added.
        :type log_id: str
        :param content_type: The content type of the log object. Defaults to None.
        :type content_type: str, optional
        :returns: A data response with the created log object.
        :rtype: LogObjectDataResponse
        """
        return self._log_object(
            key=key,
            log_id=log_id,
            content_type=content_type,
            lock_token=lock_token,
        )

    def _log_object_by_model(
        self,
        log_id: UUID,
        data: models.ObjectCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.log_object(
            log_id=log_id, **data.model_dump(), lock_token=lock_token
        )

    @abstractmethod
    def _log_object_part(self, **kwargs) -> models.ObjectPartDataResponse:
        pass

    def log_object_part(
        self,
        object_key: str,
        size: int,
        log_id: UUID,
        part_number: Optional[int] = None,
    ):
        """
        Create a log object part.

        :param object_key: The key of the log object to which the log object part should be added.
        :type object_key: str
        :param size: The size of the log object part.
        :type size: int
        :param log_id: The ID of the log to which the log object part should be added.
        :type log_id: str
        :param part_number: The part number of the log object part. Defaults to None.
        :type part_number: int, optional
        :returns: A data response with the created log object part.
        :rtype: LogObjectPartDataResponse
        """
        return self._log_object_part(
            object_key=object_key,
            log_id=log_id,
            part_number=part_number,
            size=size,
        )

    def _log_object_part_by_model(
        self, object_key: str, log_id: UUID, data: models.ObjectPartCreateRequest
    ):
        return self.log_object_part(
            object_key=object_key, log_id=log_id, **data.model_dump()
        )

    @abstractmethod
    def _object(self, **kwargs) -> models.ObjectDataResponse:
        pass

    def object(
        self,
        key: str,
        object_store_id: UUID,
        content_type: Optional[str] = None,
    ):
        """
        Create an object.

        :param key: The key of the object.
        :type key: str
        :param object_store_id: The ID of the object store to which the object should be added.
        :type object_store_id: str
        :param content_type: The content type of the object. Defaults to None.
        :type content_type: str, optional
        :returns: A data response with the created object.
        :rtype: ObjectDataResponse
        """
        return self._object(
            key=key,
            object_store_id=object_store_id,
            content_type=content_type,
        )

    def _object_by_model(self, object_store_id: UUID, data: models.ObjectCreateRequest):
        return self.object(object_store_id=object_store_id, **data.model_dump())

    @abstractmethod
    def _object_part(self, **kwargs) -> models.ObjectPartDataResponse:
        pass

    def object_part(
        self,
        object_key: str,
        size: int,
        object_store_id: UUID,
        part_number: Optional[int] = None,
    ):
        """
        Create an object part.

        :param object_key: The key of the object to which the object part should be added.
        :type object_key: str
        :param size: The size of the object part.
        :type size: int
        :param object_store_id: The ID of the object store to which the object part should be added.
        :type object_store_id: str
        :param part_number: The part number of the object part. Defaults to None.
        :type part_number: int, optional
        :returns: A data response with the created object part.
        :rtype: ObjectPartDataResponse
        """
        return self._object_part(
            object_key=object_key,
            object_store_id=object_store_id,
            part_number=part_number,
            size=size,
        )

    def _object_part_by_model(
        self,
        object_key: str,
        object_store_id: UUID,
        data: models.ObjectPartCreateRequest,
    ):
        return self.object_part(
            object_key=object_key, object_store_id=object_store_id, **data.model_dump()
        )

    @abstractmethod
    def _object_store(self, **kwargs) -> models.ObjectStoreDataResponse:
        pass

    def object_store(
        self,
        name: str,
        bucket_name: str,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        disabled: Optional[bool] = False,
        default: Optional[bool] = False,
        read_only: Optional[bool] = False,
        managed: Optional[bool] = False,
        key_prefix: Optional[str] = None,
    ):
        """
        Create an object store.

        :param name: The name of the object store. Must be unique within the DataStore.
        :type name: str
        :param bucket_name: The name of the bucket.
        :type bucket_name: str
        :param access_key_id: The access key ID of the object store. Defaults to None.
        :type access_key_id: str, optional
        :param secret_access_key: The secret access key of the object store. Defaults to None.
        :type secret_access_key: str, optional
        :param region_name: The region name of the object store. Defaults to None.
        :type region_name: str, optional
        :param endpoint_url: The endpoint URL of the object store. Defaults to None.
        :type endpoint_url: str, optional
        :param note: A note about the object store. Defaults to None.
        :type note: str, optional
        :param context: The context to use for the object store. Defaults to None.
        :type context: dict, optional
        :param disabled: Whether the object store is disabled. Defaults to False.
        :type disabled: bool, optional
        :returns: A data response with the created object store.
        :rtype: ObjectStoreDataResponse
        """
        return self._object_store(
            name=name,
            bucket_name=bucket_name,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
            note=note,
            context=context,
            disabled=disabled,
            default=default,
            read_only=read_only,
            managed=managed,
            key_prefix=key_prefix,
        )

    def _object_store_by_model(self, data: models.ObjectStoreCreateRequest):
        return self.object_store(**data.model_dump())

    @abstractmethod
    def _query(self, **kwargs) -> models.QueryDataResponse:
        pass

    def query(
        self,
        log_id: UUID,
        name: Optional[str] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        statement: Optional[str] = None,
        parameters: Optional[dict] = None,
    ):
        """
        Create a query.

        :param log_id: The ID of the log to which the query should be added.
        :type log_id: str
        :param name: The name of the query. Defaults to None.
        :type name: str, optional
        :param note: A note about the query. Defaults to None.
        :type note: str, optional
        :param context: The context to use for the query. Defaults to None.
        :type context: dict, optional
        :param statement: The statement of the query. Defaults to None.
        :type statement: str, optional
        :param parameters: The parameters of the query. Defaults to None.
        :type parameters: dict, optional
        :returns: A data response with the created query.
        :rtype: QueryDataResponse
        """
        return self._query(
            log_id=log_id,
            name=name,
            note=note,
            context=context,
            statement=statement,
            parameters=parameters,
        )

    def _query_by_model(self, data: models.QueryCreateRequest):
        return self.query(**data.model_dump())

    def _query_for_log_by_model(
        self, log_id: UUID, data: models.QueryForLogCreateRequest
    ):
        return self.query(log_id=log_id, **data.model_dump())

    @abstractmethod
    def _record(self, **kwargs) -> models.RecordDataResponse:
        pass

    def record(
        self,
        timestamp: int,
        topic_id: UUID,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        locked: Optional[bool] = False,
        query_data: Optional[dict] = None,
        auxiliary_data: Optional[dict] = None,
        data_offset: Optional[int] = None,
        data_length: Optional[int] = None,
        chunk_compression: Optional[str] = None,
        chunk_offset: Optional[int] = None,
        chunk_length: Optional[int] = None,
        source: Optional[str] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Create a record.

        :param timestamp: The timestamp of the record.
        :type timestamp: int
        :param topic_id: The ID of the topic to which the record should be added.
        :type topic_id: str
        :param note: A note about the record. Defaults to None.
        :type note: str, optional
        :param context: The context to use for the record. Defaults to None.
        :type context: dict, optional
        :param locked: Whether the record is locked. Defaults to False.
        :type locked: bool, optional
        :param query_data: A JSON representation of the record's message data which is queryable. Defaults to None.
        :type query_data: dict, optional
        :param auxiliary_data: A JSON representation of the record's message data which is not queryable. Defaults to None.
        :type auxiliary_data: dict, optional
        :param data_offset: The data offset of the record. Defaults to None.
        :type data_offset: int, optional
        :param data_length: The data length of the record. Defaults to None.
        :type data_length: int, optional
        :param chunk_compression: The chunk compression of the record. Defaults to None.
        :type chunk_compression: str, optional
        :param chunk_offset: The chunk offset of the record. Defaults to None.
        :type chunk_offset: int, optional
        :param chunk_length: The chunk length of the record. Defaults to None.
        :type chunk_length: int, optional
        :param source: The source of the record. Defaults to None.
        :type source: str, optional
        :returns: A data response with the created record.
        :rtype: RecordDataResponse
        """
        return self._record(
            timestamp=timestamp,
            topic_id=topic_id,
            note=note,
            context=context,
            locked=locked,
            query_data=query_data,
            auxiliary_data=auxiliary_data,
            data_offset=data_offset,
            data_length=data_length,
            chunk_compression=chunk_compression,
            chunk_offset=chunk_offset,
            chunk_length=chunk_length,
            source=source,
            lock_token=lock_token,
        )

    def _record_by_model(
        self,
        topic_id: UUID,
        data: models.RecordCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.record(
            topic_id=topic_id, **data.model_dump(), lock_token=lock_token
        )

    @abstractmethod
    def _tag(self, **kwargs) -> models.TagDataResponse:
        pass

    def tag(
        self,
        label_id: UUID,
        log_id: UUID,
        topic_id: Optional[UUID] = None,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Create a tag.

        :param label_id: The ID of the label to which the tag should be added.
        :type label_id: str
        :param log_id: The ID of the log to which the tag should be added.
        :type log_id: str
        :param topic_id: The ID of the topic to which the tag should be added. Defaults to None.
        :type topic_id: str, optional
        :param note: A note about the tag. Defaults to None.
        :type note: str, optional
        :param context: The context to use for the tag. Defaults to None.
        :type context: dict, optional
        :param start_time: The start time of the tag. Defaults to None.
        :type start_time: int, optional
        :param end_time: The end time of the tag. Defaults to None.
        :type end_time: int, optional
        :returns: A data response with the created tag.
        :rtype: TagDataResponse
        """
        return self._tag(
            label_id=label_id,
            log_id=log_id,
            topic_id=topic_id,
            note=note,
            context=context,
            start_time=start_time,
            end_time=end_time,
            lock_token=lock_token,
        )

    def _tag_by_model(
        self,
        data: models.TagCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.tag(**data.model_dump(), lock_token=lock_token)

    def _tag_for_log_by_model(
        self,
        log_id: UUID,
        data: models.TagForLogCreateRequest,
        lock_token: Optional[str] = None,
    ):
        return self.tag(log_id=log_id, **data.model_dump(), lock_token=lock_token)

    @abstractmethod
    def _topic(self, **kwargs) -> models.TopicDataResponse:
        pass

    def topic(
        self,
        log_id: UUID,
        name: str,
        note: Optional[str] = None,
        base_timestamp: Optional[int] = None,
        context: Optional[dict] = None,
        associated_topic_id: Optional[UUID] = None,
        locked: Optional[bool] = False,
        strict: Optional[bool] = False,
        type_name: Optional[str] = None,
        type_encoding: Optional[str] = None,
        type_data: Optional[str] = None,
        type_schema: Optional[dict] = None,
        lock_token: Optional[str] = None,
    ):
        """
        Create a topic.

        :param log_id: The ID of the log to which the topic should be added.
        :type log_id: str
        :param name: The name of the topic.
        :type name: str
        :param note: A note about the topic. Defaults to None.
        :type note: str, optional
        :param base_timestamp: The base timestamp of the topic. Defaults to None.
        :type base_timestamp: int, optional
        :param context: The context to use for the topic. Defaults to None.
        :type context: dict, optional
        :param associated_topic_id: The ID of the associated topic. Defaults to None.
        :type associated_topic_id: str, optional
        :param locked: Whether the topic is locked. Defaults to False.
        :type locked: bool, optional
        :param strict: Whether the topic is strict. Defaults to False.
        :type strict: bool, optional
        :param type_name: The type name of the topic. Defaults to None.
        :type type_name: str, optional
        :param type_encoding: The type encoding of the topic. Defaults to None.
        :type type_encoding: str, optional
        :param type_data: The type data of the topic. Defaults to None.
        :type type_data: str, optional
        :param type_schema: The type schema of the topic. Defaults to None.
        :type type_schema: str, optional
        :returns: A data response with the created topic.
        :rtype: TopicDataResponse
        """
        return self._topic(
            log_id=log_id,
            name=name,
            note=note,
            base_timestamp=base_timestamp,
            context=context,
            associated_topic_id=associated_topic_id,
            locked=locked,
            strict=strict,
            type_name=type_name,
            type_encoding=type_encoding,
            type_data=type_data,
            type_schema=type_schema,
            lock_token=lock_token,
        )

    def _topic_by_model(
        self, data: models.TopicCreateRequest, lock_token: Optional[str] = None
    ):
        return self.topic(**data.model_dump(), lock_token=lock_token)

    @abstractmethod
    def _workflow(self, **kwargs) -> models.WorkflowDataResponse:
        pass

    def workflow(
        self,
        name: str,
        process_type: models.ProcessType = models.ProcessType.digestion,
        note: Optional[str] = None,
        context: Optional[dict] = None,
        default: Optional[bool] = False,
        disabled: Optional[bool] = False,
        managed: Optional[bool] = False,
        context_schema: Optional[dict] = None,
    ):
        """
        Create a workflow.

        :param name: The name of the workflow.
        :type name: str
        :param note: A note about the workflow. Defaults to None.
        :type note: str, optional
        :param context: The context to use for the workflow. Defaults to None.
        :type context: dict, optional
        :param default: Whether the workflow is default. Defaults to False.
        :type default: bool, optional
        :param disabled: Whether the workflow is disabled. Defaults to False.
        :type disabled: bool, optional
        :param managed: Whether the workflow is managed. Defaults to False.
        :type managed: bool, optional
        :param context_schema: The context schema of the workflow. Defaults to None.
        :type context_schema: dict, optional
        :returns: A data response with the created workflow.
        :rtype: WorkflowDataResponse
        """
        return self._workflow(
            name=name,
            process_type=process_type,
            note=note,
            context=context,
            default=default,
            disabled=disabled,
            managed=managed,
            context_schema=context_schema,
        )

    def _workflow_by_model(self, data: models.WorkflowCreateRequest):
        return self.workflow(**data.model_dump())
