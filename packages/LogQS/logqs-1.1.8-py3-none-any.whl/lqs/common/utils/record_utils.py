import io
import os
import base64
import time
from uuid import UUID
from typing import Iterator, Iterable, List, Optional, Union, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event

import requests
from PIL import Image as ImagePIL

if TYPE_CHECKING:
    from lqs.common.facade import CoreFacade
from .utils import (
    get_relative_object_path,
    decompress_chunk_bytes,
    get_record_image,
)
from lqs.transcode import Transcode
from lqs.interface.core.models import (
    Ingestion,
    Object,
    Record,
    Topic,
)


class RecordUtils:
    def __init__(self, app: "CoreFacade"):
        self.app = app

    def get_record_image(
        self,
        record_data: dict | bytes,
        max_size: Optional[int] = None,
        format: str = "WEBP",
        format_params: dict = {},
        renormalize: bool = True,
        reset_position: bool = True,
        return_bytes: bool = False,
        **kwargs,
    ) -> Union[ImagePIL.Image, io.BytesIO, None]:
        """
        A convenience method which takes deserialized record data from a standard image topic and returns the image as a PIL Image or BytesIO object.

        :param record_data: The record data.
        :type record_data: dict | bytes
        :param max_size: The maximum width or height to downscale to. Defaults to None, which means no downscaling.
        :type max_size: int, optional
        :param format: The output format to use. Defaults to "WEBP".
        :type format: str, optional
        :param format_params: The format parameters to use. Defaults to {}.
        :type format_params: dict, optional
        :param renormalize: Whether to renormalize the image, which is necessary for visualization in some cases. Defaults to True.
        :type renormalize: bool, optional
        :param reset_position: Whether to reset the position offset position of the BytesIO object. Defaults to True.
        :type reset_position: bool, optional
        :param return_bytes: Whether to return the image as a BytesIO object. Defaults to False.
        :type return_bytes: bool, optional
        :returns: The image, either as a PIL Image or BytesIO object, or None if the record data does not contain an image.
        :rtype: Union[ImagePIL.Image, io.BytesIO, None]
        """
        return get_record_image(
            record_data=record_data,
            max_size=max_size,
            format=format,
            format_params=format_params,
            renormalize=renormalize,
            reset_position=reset_position,
            return_bytes=return_bytes,
            **kwargs,
        )

    def iter_topic_records(
        self,
        topic: Union[Topic, UUID, str],
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        per_request_limit: int = 1000,
        frequency: Optional[float] = None,
        include_auxiliary_data: bool = False,
    ):
        """
        Iterate over records for a topic.

        :param topic: The topic to use.
        :type topic: Topic | UUID | str
        :param start_time: The start time to use. Defaults to None.
        :type start_time: int, optional
        :param end_time: The end time to use. Defaults to None.
        :type end_time: int, optional
        :param per_request_limit: The limit to use for each request. Defaults to 1000.
        :type per_request_limit: int, optional
        :param frequency: The frequency to use for each request. Defaults to None.
        :type frequency: float, optional
        :param include_auxiliary_data: Whether to include auxiliary data. Defaults to False.
        :type include_auxiliary_data: bool, optional
        :yields: The record.
        :rtype: Record
        """
        if isinstance(topic, Topic):
            topic_id = topic.id
        else:
            topic_id = topic
        with ThreadPoolExecutor() as executor:
            records = self.app.list.record(
                topic_id=topic_id,
                timestamp_gte=start_time,
                timestamp_lte=end_time,
                limit=per_request_limit,
                frequency=frequency,
                include_auxiliary_data=include_auxiliary_data,
            ).data
            if len(records) == 0:
                return
            last_record = records[-1]
            last_record_timestamp = last_record.timestamp
            records_future = executor.submit(
                self.app.list.record,
                topic_id=topic_id,
                timestamp_gt=last_record_timestamp,
                timestamp_lte=end_time,
                limit=per_request_limit,
                frequency=frequency,
                include_auxiliary_data=include_auxiliary_data,
            )
            while len(records) > 0:
                yield from records
                records_res = records_future.result()
                records = records_res.data
                if len(records) == 0:
                    break
                last_record = records[-1]
                last_record_timestamp = last_record.timestamp
                records_future = executor.submit(
                    self.app.list.record,
                    topic_id=topic_id,
                    timestamp_gt=last_record_timestamp,
                    timestamp_lte=end_time,
                    limit=per_request_limit,
                    frequency=frequency,
                    include_auxiliary_data=include_auxiliary_data,
                )

    def iter_topics_records(
        self,
        topics: List[Union[Topic, UUID, str]],
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        per_request_limit: int = 1000,
        frequency: Optional[float] = None,
        include_auxiliary_data: bool = False,
    ):
        """
        Iterate over records for multiple topics.

        :param topics: The topics to use.
        :type topics: List[Topic | UUID | str]
        :param start_time: The start time to use. Defaults to None.
        :type start_time: int, optional
        :param end_time: The end time to use. Defaults to None.
        :type end_time: int, optional
        :param per_request_limit: The limit to use for each request. Defaults to 1000.
        :type per_request_limit: int, optional
        :param frequency: The frequency to use for each request. Defaults to None.
        :type frequency: float, optional
        :param include_auxiliary_data: Whether to include auxiliary data. Defaults to False.
        :type include_auxiliary_data: bool, optional
        :yields: The record.
        :rtype: Record
        """
        topic_ids = []
        for topic in topics:
            if isinstance(topic, Topic):
                topic_ids.append(topic.id)
            else:
                topic_ids.append(topic)
        record_iters = {
            topic_id: self.iter_topic_records(
                topic=topic_id,
                start_time=start_time,
                end_time=end_time,
                per_request_limit=per_request_limit,
                frequency=frequency,
                include_auxiliary_data=include_auxiliary_data,
            )
            for topic_id in topic_ids
        }
        next_records = {topic_id: None for topic_id in topic_ids}
        while True:
            for topic_id, record_iter in record_iters.items():
                if next_records[topic_id] is None:
                    next_records[topic_id] = next(record_iter, None)
            next_topic_id = None
            next_record = None
            for topic_id, record in next_records.items():
                if record is not None:
                    if next_record is None or record.timestamp < next_record.timestamp:
                        next_topic_id = topic_id
                        next_record = record
            if next_record is None:
                break
            yield next_record
            next_records[next_topic_id] = next(record_iters[next_topic_id], None)

    def load_auxiliary_data_image(self, source: Union[Record, dict]):
        if isinstance(source, Record):
            auxiliary_data = source.get_auxiliary_data()
        else:
            auxiliary_data = source

        if auxiliary_data is None:
            return None
        if "image" not in auxiliary_data:
            return None
        encoded_webp_data = auxiliary_data["image"]
        decoded_webp_data = base64.b64decode(encoded_webp_data)
        image = ImagePIL.open(io.BytesIO(decoded_webp_data))
        return image

    def get_deserialized_record_data(
        self,
        record: Record,
        topic: Optional[Topic] = None,
        ingestion: Optional[Ingestion] = None,
        transcoder: Optional[Transcode] = None,
    ) -> dict:
        if transcoder is None:
            transcoder = Transcode()

        if topic is None:
            topic = self.app.fetch.topic(record.topic_id).data

        message_bytes = self.fetch_record_bytes(record=record, ingestion=ingestion)

        return transcoder.deserialize(
            type_encoding=topic.type_encoding,
            type_name=topic.type_name,
            type_data=topic.type_data,
            message_bytes=message_bytes,
        )

    def fetch_record_bytes(
        self,
        record: Record,
        ingestion: Optional[Ingestion] = None,
        decompress_chunk: bool = True,
        return_full_chunk: bool = False,
    ) -> bytes:

        if ingestion is None:
            ingestion = self.app.fetch.ingestion(record.ingestion_id).data

        object_store_id = (
            str(ingestion.object_store_id)
            if ingestion.object_store_id is not None
            else None
        )
        object_key = str(ingestion.object_key)

        if record.source is not None:
            # if the record has a source, we need to get the relative path from the object_key
            object_key = get_relative_object_path(
                object_key=object_key, source=record.source
            )

        if object_store_id is None:
            # the data is coming from a log object
            message_bytes: bytes = self.app.fetch.log_object(
                object_key=object_key,
                log_id=record.log_id,
                redirect=True,
                offset=record.data_offset,
                length=record.data_length,
            )
        else:
            # the data is coming from an object store
            message_bytes: bytes = self.app.fetch.object(
                object_key=object_key,
                object_store_id=object_store_id,
                redirect=True,
                offset=record.data_offset,
                length=record.data_length,
            )

        if record.chunk_compression is not None and record.chunk_compression not in [
            "",
            "none",
        ]:
            if decompress_chunk:
                # if the record is compressed, we need to decompress it
                message_bytes = decompress_chunk_bytes(
                    chunk_bytes=message_bytes,
                    chunk_compression=record.chunk_compression,
                    chunk_length=record.chunk_length,
                )
                if not return_full_chunk:
                    # we only return the relevant part of the chunk
                    message_bytes = message_bytes[
                        record.chunk_offset : record.chunk_offset + record.chunk_length
                    ]
            else:
                if not return_full_chunk:
                    raise Exception(
                        "Cannot return partial chunk without decompressing it."
                    )

        return message_bytes

    def get_record_set(
        self,
        records: Iterable[Record],
        carryover_record: Optional[Record] = None,
        density_threshold: float = 0.9,
        max_contiguous_size: int = 100 * 1000 * 1000,  # 100 MB
        max_contiguous_records: int = 1000,
    ) -> tuple[list[list[Record]], Optional[Record]]:
        record_set: list[Record] = []
        relevant_length = 0
        full_length = 0
        start_offset = None
        last_ingestion_id = None
        last_source = None
        last_offset = None

        if carryover_record is not None:
            record_set.append(carryover_record)
            start_offset = carryover_record.data_offset
            last_ingestion_id = carryover_record.ingestion_id
            last_source = carryover_record.source
            last_offset = carryover_record.data_offset + carryover_record.data_length
            carryover_record = None
        leftover_record: Optional[Record] = None

        for record in records:
            if start_offset is None:
                start_offset = record.data_offset
            if last_ingestion_id is None:
                last_ingestion_id = record.ingestion_id
            if last_source is None:
                last_source = record.source
            if last_offset is None:
                last_offset = record.data_offset + record.data_length

            if (record.data_offset + record.data_length) < last_offset:
                # ensure records are ordered properly by offset
                leftover_record = record
                break

            relevant_length += record.data_length
            full_length = record.data_offset + record.data_length - start_offset
            if (
                relevant_length / full_length > density_threshold
                and last_ingestion_id == record.ingestion_id
                and last_source == record.source
                and len(record_set) < max_contiguous_records
                and full_length < max_contiguous_size
                and record.data_offset + record.data_length >= last_offset
            ):
                record_set.append(record)
                last_offset = record.data_offset + record.data_length
            else:
                if len(record_set) == 0:
                    raise Exception("Record set cannot be empty.")
                leftover_record = record
                break
        return record_set, leftover_record

    def get_presigned_url(
        self,
        object_key: str,
        object_store_id: Union[UUID, str, None] = None,
        log_id: Union[UUID, str, None] = None,
        start_offset: Optional[int] = None,
        end_offset: Optional[int] = None,
    ) -> str:
        params = dict(object_key=object_key, redirect=False)
        if object_store_id is None:
            # the data is coming from a log object
            params["log_id"] = log_id
            if start_offset is not None:
                params["offset"] = start_offset
                if end_offset is not None:
                    params["length"] = end_offset - start_offset
            object_meta: Object = self.app.fetch.log_object(**params).data
        else:
            # the data is coming from an object store
            params["object_store_id"] = object_store_id
            if start_offset is not None:
                params["offset"] = start_offset
                if end_offset is not None:
                    params["length"] = end_offset - start_offset
            object_meta: Object = self.app.fetch.object(**params).data
        presigned_url = object_meta.presigned_url
        return presigned_url

    def iter_dense_record_data(
        self,
        records: Iterable[Record],
        deserialize_results: bool = True,
        transcoder: Optional[Transcode] = None,
        stream_data: bool = True,
        ingestions: dict[str, Ingestion] = {},
        topics: dict[str, Topic] = {},
        presigned_urls: dict[str, str] = {},
        use_cache: bool = False,
        cache_dir: str = "/tmp/lqs",
        read_from_cache: bool = True,
        write_to_cache: bool = True,
    ) -> Iterator[tuple[Record, Union[bytes, dict]]]:
        if transcoder is None:
            transcoder = Transcode()

        object_key: Optional[str] = None
        source: Optional[str] = None

        start_offset = None
        end_offset = None
        datastore_id = self.app.get_datastore_id()
        for record in records:
            if use_cache and read_from_cache:
                # we check if the record data is in the cache and, if so, skip it here
                record_data_path = f"{cache_dir}/datastores/{datastore_id}/logs/{record.log_id}/topics/{record.topic_id}/records/{record.timestamp:09}.bin"
                if os.path.exists(record_data_path):
                    continue
            ingestion_id = str(record.ingestion_id)
            if ingestion_id not in ingestions:
                ingestions[ingestion_id] = self.app.fetch.ingestion(ingestion_id).data
            ingestion = ingestions[ingestion_id]

            if object_key is None:
                object_key = str(ingestion.object_key)
                if record.source is not None:
                    source = record.source
                    object_key = get_relative_object_path(
                        object_key=object_key, source=record.source
                    )

            if record.ingestion_id != ingestion.id:
                raise Exception(
                    f"All records must have the same ingestion. Found {record.ingestion_id} and {ingestion.id}."
                )

            if record.source != source:
                raise Exception(
                    f"All records must have the same source. Found {record.source} and {source}."
                )

            if start_offset is None:
                start_offset = record.data_offset

            if end_offset is None:
                end_offset = record.data_offset + record.data_length

            current_end_offset = record.data_offset + record.data_length
            if current_end_offset < end_offset:
                raise Exception(
                    f"Records must be ordered by data offset. Found current end offset {current_end_offset} less than last end offset {end_offset}."
                )
            else:
                end_offset = current_end_offset

        presigned_url = presigned_urls.get(object_key, None)
        if presigned_url is None and object_key is not None:
            # TODO: we assume object_key is unique, but it may exist across object stores
            presigned_url = self.get_presigned_url(
                object_key=object_key,
                object_store_id=ingestion.object_store_id,
                log_id=ingestion.log_id,
                # TODO: we can't request the presigned URL with a range, so we need to fetch the whole object
                # we should update this to fetch specific ranges and request new presigned URLs as needed
                # start_offset=start_offset,
                # end_offset=end_offset,
            )
            presigned_urls[object_key] = presigned_url

        def get_data_stream(presigned_url):
            headers = {
                "Range": f"bytes={start_offset}-{end_offset - 1}",
            }
            if stream_data:
                buffer_length = 1_000_000 * 32  # 32 MB
                r = requests.get(presigned_url, headers=headers, stream=True)
                r.raise_for_status()
                data_stream = io.BufferedReader(r.raw, buffer_length)
            else:
                r = requests.get(presigned_url, headers=headers, stream=False)
                r.raise_for_status()
                data_stream = io.BytesIO(r.content)
            return data_stream

        data_stream: Optional[Union[io.BufferedReader, io.BytesIO]] = None
        if presigned_url is not None:
            try:
                data_stream = get_data_stream(presigned_url)
            except Exception as e:
                self.app.logger.debug(f"Error getting data stream: {e}")
                self.app.logger.debug("Generating new presigned URL and trying again.")
                presigned_url = self.get_presigned_url(
                    object_key=object_key,
                    object_store_id=ingestion.object_store_id,
                    log_id=ingestion.log_id,
                    # TODO: we can't request the presigned URL with a range, so we need to fetch the whole object
                    # we should update this to fetch specific ranges and request new presigned URLs as needed
                    # start_offset=start_offset,
                    # end_offset=end_offset,
                )
                presigned_urls[object_key] = presigned_url
                data_stream = get_data_stream(presigned_url)

        # Now we can iterate over the records and read the data from the stream
        decompressed_bytes: Optional[bytes] = None
        compressed_chunk_offset: Optional[int] = None
        current_offset = start_offset
        for record in records:
            if use_cache and read_from_cache:
                # we check if the record data is in the cache and, if so, load it here
                record_data_path = f"{cache_dir}/datastores/{datastore_id}/logs/{record.log_id}/topics/{record.topic_id}/records/{record.timestamp:09}.bin"
                if os.path.exists(record_data_path):
                    with open(record_data_path, "rb") as f:
                        record_data = f.read()
                    if deserialize_results:
                        # if we want to deserialize the results, we need the topic
                        topic_id = str(record.topic_id)
                        if topic_id not in topics:
                            # if we haven't seen this record's topic yet, we fetch it here
                            topics[topic_id] = self.app.fetch.topic(
                                record.topic_id
                            ).data
                        topic = topics[topic_id]
                        record_data = transcoder.deserialize(
                            type_encoding=topic.type_encoding,
                            type_name=topic.type_name,
                            type_data=topic.type_data,
                            message_bytes=record_data,
                        )
                    yield (record, record_data)
                    continue

            data_offset = record.data_offset
            data_length = record.data_length

            if (
                compressed_chunk_offset is not None
                and record.chunk_compression is not None
                and record.data_offset == compressed_chunk_offset
            ):
                message_bytes = decompressed_bytes[
                    record.chunk_offset : record.chunk_offset + record.chunk_length
                ]
            else:
                data_stream.read(data_offset - current_offset)
                message_bytes = data_stream.read(data_length)
                current_offset = data_offset + data_length

                if (
                    record.chunk_compression is not None
                    and record.chunk_compression not in ["", "none"]
                ):
                    decompressed_bytes = decompress_chunk_bytes(
                        chunk_bytes=message_bytes,
                        chunk_compression=record.chunk_compression,
                        chunk_length=record.chunk_length,
                    )
                    message_bytes = decompressed_bytes[
                        record.chunk_offset : record.chunk_offset + record.chunk_length
                    ]
                    compressed_chunk_offset = record.data_offset

            if use_cache and write_to_cache:
                # we write the record data to the cache
                record_data_path = f"{cache_dir}/datastores/{datastore_id}/logs/{record.log_id}/topics/{record.topic_id}/records/{record.timestamp:09}.bin"
                os.makedirs(os.path.dirname(record_data_path), exist_ok=True)
                with open(record_data_path, "wb") as f:
                    f.write(message_bytes)

            if deserialize_results:
                # if we want to deserialize the results, we need the topic
                topic_id = str(record.topic_id)
                if topic_id not in topics:
                    # if we haven't seen this record's topic yet, we fetch it here
                    topics[topic_id] = self.app.fetch.topic(record.topic_id).data
                topic = topics[topic_id]
                record_data = transcoder.deserialize(
                    type_encoding=topic.type_encoding,
                    type_name=topic.type_name,
                    type_data=topic.type_data,
                    message_bytes=message_bytes,
                )
                yield (record, record_data)
            else:
                yield (record, message_bytes)

    def iter_record_data(
        self,
        records: Iterable[Record],
        deserialize_results: bool = False,
        transcoder: Optional[Transcode] = None,
        density_threshold: float = 0.9,
        max_contiguous_size: int = 100 * 1000 * 1000,
        max_contiguous_records: int = 1000,
        max_workers: Optional[int] = 2,
        order_by_timestamp: bool = True,
        stop_event: Optional[Event] = None,
        use_cache: bool = False,
        cache_dir: str = "/tmp/lqs",
        read_from_cache: bool = True,
        write_to_cache: bool = True,
    ) -> Iterator[tuple[Record, Union[bytes, dict]]]:
        """
        Given a set of records, yield the record and its data.

        :param records: The records to use.
        :type records: Iterable[Record]
        :param deserialize_results: Whether to deserialize the results. Defaults to False.
        :type deserialize_results: bool, optional
        :param transcoder: The transcoder to use. Defaults to None.
        :type transcoder: Transcode, optional
        :param density_threshold: The density threshold to use. Defaults to 0.9.
        :type density_threshold: float, optional
        :param max_contiguous_size: The maximum contiguous size to use. Defaults to 100 * 1000 * 1000.
        :type max_contiguous_size: int, optional
        :param max_contiguous_records: The maximum contiguous records to use. Defaults to 1000.
        :type max_contiguous_records: int, optional
        :param max_workers: The maximum number of workers to use. Defaults to 2.
        :type max_workers: int | None, optional
        :param order_by_timestamp: Whether to order the records by timestamp. Defaults to True.
        :type order_by_timestamp: bool, optional
        :param stop_event: An event to signal stopping the iteration. Defaults to None.
        :type stop_event: Event, optional
        :yields: The record and the record data.
        :rtype: tuple[Record, dict | bytes]
        :param use_cache: Whether to use caching for record data. Defaults to False.
        :type use_cache: bool, optional
        :param cache_dir: The directory to use for caching. Defaults to "/tmp/lqs".
        :type cache_dir: str, optional
        :param read_from_cache: Whether to read from cache if available. Defaults to True.
        :type read_from_cache: bool, optional
        :param write_to_cache: Whether to write to cache after fetching. Defaults to True.
        :type write_to_cache: bool, optional
        """
        if stop_event is None:
            stop_event = Event()

        generating_record_sets = True
        kill_threads = False
        record_sets: list[list[Record]] = []

        accumulated_records = {}
        original_record_ordering = []

        if transcoder is None:
            transcoder = Transcode()
        ingestions: dict[str, Ingestion] = {}
        topics: dict[str, Topic] = {}
        presigned_urls: dict[str, str] = {}

        if isinstance(records, list):
            records = iter(records)

        # We generate record sets in a thread so that we can start processing records as soon as possible.
        # A record set is a set of records which conform to our density requirements and can be processed together.
        # i.e., they're batches of records that should be fetched from object storage in one chunk.
        def generate_record_sets():
            nonlocal generating_record_sets
            nonlocal kill_threads
            try:
                record_set_count = 0
                record_set_sizes = {}
                leftover_record = None
                self.app.logger.debug("Generating record sets...")
                while not stop_event.is_set():
                    if kill_threads:
                        break
                    record_set, leftover_record = self.get_record_set(
                        records=records,
                        carryover_record=leftover_record,
                        density_threshold=density_threshold,
                        max_contiguous_size=max_contiguous_size,
                        max_contiguous_records=max_contiguous_records,
                    )
                    for record in record_set:
                        if record.timestamp not in accumulated_records:
                            accumulated_records[record.timestamp] = {}
                        accumulated_records[record.timestamp][record.topic_id] = None
                        original_record_ordering.append(record)
                    record_sets.append(record_set)
                    record_set_count += 1
                    record_set_sizes[record_set_count] = len(record_set)
                    if leftover_record is None:
                        break
                generating_record_sets = False
                self.app.logger.debug(
                    f"Done generating {record_set_count} record sets."
                )
            except Exception as e:
                self.app.logger.error(
                    {
                        "log_type": "generate_record_sets_error",
                        "exception": str(e),
                    }
                )
                kill_threads = True
                raise e

            # the following is for debugging only
            try:
                _record_set_sizes = list(record_set_sizes.values())
                record_set_sizes_1 = len(
                    [size for size in _record_set_sizes if size == 1]
                )
                record_set_sizes_lt_10 = len(
                    [size for size in _record_set_sizes if size < 10 and size > 1]
                )
                record_set_sizes_gt_10 = len(
                    [size for size in _record_set_sizes if size > 10]
                )
                self.app.logger.debug(
                    f"Record set sizes: 1={record_set_sizes_1}, >1,<10={record_set_sizes_lt_10}, >10={record_set_sizes_gt_10}"
                )
            except Exception as e:
                self.app.logger.debug(f"Error calculating record set sizes: {e}")

        # We process record sets in a thread so that we can parallelize the fetching of record data.
        def process_record_set(record_set):
            nonlocal kill_threads
            if kill_threads or stop_event.is_set():
                return
            max_attempts = 3
            for attempt_idx in range(1, max_attempts + 1):
                try:
                    record_data_iter = self.iter_dense_record_data(
                        records=record_set,
                        deserialize_results=deserialize_results,
                        transcoder=transcoder,
                        ingestions=ingestions,
                        topics=topics,
                        presigned_urls=presigned_urls,
                        use_cache=use_cache,
                        cache_dir=cache_dir,
                        read_from_cache=read_from_cache,
                        write_to_cache=write_to_cache,
                    )
                    for record, record_data in record_data_iter:
                        if stop_event.is_set():
                            return
                        try:
                            accumulated_records[record.timestamp][record.topic_id] = (
                                record,
                                record_data,
                            )
                        except KeyError:
                            pass
                    break
                except Exception as e:
                    self.app.logger.debug(
                        f"Error on attempt {attempt_idx} in process_record_set: {e}"
                    )
                    if attempt_idx == max_attempts:
                        self.app.logger.error(
                            {
                                "log_type": "process_record_set_error",
                                "exception": str(e),
                            }
                        )
                        kill_threads = True
                        raise e

        # We process accumulated records in a thread so that we can yield record data as it becomes available.
        # This function just runs process_record_set as record sets become available (i.e., nested threads).
        def process_accumulated_records():
            nonlocal kill_threads
            try:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = []
                    while generating_record_sets or len(record_sets):
                        if kill_threads or stop_event.is_set():
                            break
                        if len(record_sets) == 0:
                            time.sleep(0.1)
                            continue
                        record_set = record_sets.pop(0)
                        if len(record_set):
                            future = executor.submit(process_record_set, record_set)
                            futures.append(future)
                    for future in as_completed(futures):
                        if stop_event.is_set():
                            break
                        future.result()
            except Exception as e:
                self.app.logger.error(
                    {
                        "log_type": "process_accumulated_records_error",
                        "exception": str(e),
                    }
                )
                kill_threads = True
                raise e

        # This is the main runner which starts the two main threads and yields record data as it becomes available.
        with ThreadPoolExecutor() as executor:
            generate_record_sets_future = executor.submit(generate_record_sets)
            process_accumulated_records_future = executor.submit(
                process_accumulated_records
            )
            current_record = None
            printed = False
            while generating_record_sets or len(accumulated_records) > 0:
                try:
                    if kill_threads or stop_event.is_set():
                        break
                    if len(accumulated_records) == 0:
                        time.sleep(0.1)
                        continue

                    if order_by_timestamp:
                        timestamp = min(accumulated_records)
                        while len(accumulated_records[timestamp]) > 0:
                            if kill_threads or stop_event.is_set():
                                break
                            topic_id = min(accumulated_records[timestamp])
                            result = accumulated_records[timestamp][topic_id]
                            if result is None:
                                time.sleep(0.1)
                                continue
                            del accumulated_records[timestamp][topic_id]
                            record, record_data = result
                            yield record, record_data
                        del accumulated_records[timestamp]
                    else:
                        if current_record is None:
                            if len(original_record_ordering) == 0:
                                if generating_record_sets:
                                    time.sleep(0.1)
                                    continue
                                else:
                                    break
                            current_record = original_record_ordering.pop(0)
                        timestamp = current_record.timestamp
                        topic_id = current_record.topic_id
                        if timestamp not in accumulated_records:
                            time.sleep(0.1)
                            continue
                        if topic_id not in accumulated_records[timestamp]:
                            time.sleep(0.1)
                            if not printed:
                                print(f"Waiting for {topic_id} at {timestamp}")
                                print(
                                    f"Topic IDs: {list(accumulated_records[timestamp].keys())}"
                                )
                                printed = True
                            continue
                        result = accumulated_records[timestamp][topic_id]
                        if result is None:
                            time.sleep(0.1)
                            continue
                        del accumulated_records[timestamp][topic_id]
                        record, record_data = result
                        current_record = None
                        printed = False
                        yield record, record_data
                except KeyboardInterrupt as e:
                    kill_threads = True
                    raise e
            generate_record_sets_future.result()
            process_accumulated_records_future.result()
