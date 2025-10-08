import io
import time
import datetime
from uuid import UUID
from typing import Iterator, Optional, Union, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor

import requests

from lqs.transcode import Transcode

if TYPE_CHECKING:
    from lqs.common.facade import CoreFacade
from lqs.interface.core.models import (
    Digestion,
    DigestionPart,
    DigestionPartIndexEntry,
    Record,
    ProcessState,
)


class DigestionUtils:
    def __init__(self, app: "CoreFacade"):
        self.app = app

    def digestion_part_index_entry_to_record(
        self,
        entry: tuple,
        log_id: Union[UUID, str] = "00000000-0000-0000-0000-000000000000",
        created_at: datetime.datetime = datetime.datetime.now(),
    ) -> Record:
        (
            topic_id,
            ingestion_id,
            source,
            data_offset,
            data_length,
            chunk_compression,
            chunk_offset,
            chunk_length,
            timestamp,
        ) = entry
        record = Record(
            log_id=log_id,
            topic_id=topic_id,
            timestamp=timestamp,
            ingestion_id=ingestion_id,
            data_offset=data_offset,
            data_length=data_length,
            chunk_compression=chunk_compression,
            chunk_offset=chunk_offset,
            chunk_length=chunk_length,
            source=source,
            error=None,
            query_data=None,
            auxiliary_data=None,
            raw_data=None,
            context=None,
            note=None,
            locked=False,
            locked_by=None,
            locked_at=None,
            lock_token=None,
            created_at=created_at,
            updated_at=None,
            deleted_at=None,
            created_by=None,
            updated_by=None,
            deleted_by=None,
        )
        return record

    def iter_digestion_part_records(
        self,
        digestion_part: Union[DigestionPart, UUID, str],
        digestion: Union[Digestion, UUID, str, None] = None,
        digestion_part_wait_duration: int = 60 * 30,
        stream_buffer_length: int = 1_000_000 * 32,
        raise_if_ready: bool = True,
        raise_if_queued: bool = False,
    ) -> Iterator[tuple[DigestionPartIndexEntry, bytes]]:
        if isinstance(digestion_part, DigestionPart):
            if digestion_part.index is None:
                # we have to fetch the digestion part to get the index
                digestion_part = self.app.fetch.digestion_part(
                    digestion_id="00000000-0000-0000-0000-000000000000",
                    digestion_part_id=digestion_part.id,
                ).data
        else:
            digestion_part = self.app.fetch.digestion_part(
                digestion_id="00000000-0000-0000-0000-000000000000",
                digestion_part_id=digestion_part,
            ).data

        if digestion is None:
            digestion = self.app.fetch.digestion(digestion_part.digestion_id).data
        else:
            if digestion.id != digestion_part.digestion_id:
                raise Exception(
                    f"Digestion ID {digestion_part.digestion_id} from digestion part does not match provided digestion ID {digestion.id}"
                )

        current_digestion_wait_time = time.time()
        while digestion_part.state != ProcessState.completed:
            if digestion_part.state == ProcessState.failed:
                raise Exception(
                    f"Digestion part {digestion_part.id} is in a failed state."
                )
            if digestion_part.state == ProcessState.queued:
                if raise_if_queued:
                    raise Exception(
                        f"Digestion part {digestion_part.id} is in a queued state."
                    )
            if digestion_part.state == ProcessState.ready:
                if raise_if_ready:
                    raise Exception(
                        f"Digestion part {digestion_part.id} is in a ready state."
                    )
            if time.time() - current_digestion_wait_time > digestion_part_wait_duration:
                raise Exception(
                    f"Digestion part {digestion_part.id} is not in completed state after waiting {digestion_part_wait_duration} seconds."
                )
            time.sleep(10)
            digestion_part = self.app.fetch.digestion_part(
                digestion_id=digestion.id, digestion_part_id=digestion_part.id
            ).data

        record_blob_key = (
            f"digestions/{digestion.id}/digestion_parts/{digestion_part.id}.bin"
        )
        record_blob_object = self.app.fetch.log_object(
            log_id=digestion.log_id,
            object_key=record_blob_key,
            redirect=False,
        ).data
        r = requests.get(record_blob_object.presigned_url, stream=True)
        r.raise_for_status()
        record_blob_data_stream = io.BufferedReader(r.raw, stream_buffer_length)
        for entry_tuple in digestion_part.index:
            (
                topic_id,
                ingestion_id,
                source,
                data_offset,
                data_length,
                chunk_compression,
                chunk_offset,
                chunk_length,
                timestamp,
            ) = entry_tuple
            record_length = data_length if chunk_length is None else chunk_length
            record_bytes = record_blob_data_stream.read(record_length)
            entry = DigestionPartIndexEntry(
                topic_id=topic_id,
                ingestion_id=ingestion_id,
                source=source,
                data_offset=data_offset,
                data_length=data_length,
                chunk_compression=chunk_compression,
                chunk_offset=chunk_offset,
                chunk_length=chunk_length,
                timestamp=timestamp,
            )
            yield entry, record_bytes

    def iter_digestion_records(
        self,
        digestion: Union[Digestion, UUID, str],
        digestion_part_wait_duration: int = 60 * 30,
        stream_buffer_length: int = 1_000_000 * 32,
        max_workers: Optional[int] = 10,
    ) -> Iterator[tuple[UUID, DigestionPartIndexEntry, bytes]]:
        """
        Iterate over records for a digestion.

        A digestion is a collection of digestion parts, which each contain an index of records. This method returns an iterator which yields a tuple with the following:

        - The digestion part ID.
        - The entry from the digestion part index.
        - The record bytes.

        This is useful for iterating over all records in a digestion, which can be more efficient than iterating over records through the API.
        The `max_workers` parameter determines the number of workers to use for fetching the record data in parallel. Set to `None` to use no threading.

        :param digestion: The digestion or digestion ID to use.
        :type digestion: Digestion | UUID | str
        :param digestion_part_wait_duration: The digestion part wait duration to use. Defaults to 60 * 30.
        :type digestion_part_wait_duration: int, optional
        :param stream_buffer_length: The stream buffer length to use. Defaults to 1_000_000 * 32.
        :type stream_buffer_length: int, optional
        :param max_workers: The maximum number of workers to use. Defaults to 10.
        :type max_workers: int, optional

        :yields: The digestion part ID, the entry, and the record bytes.
        """
        if isinstance(digestion, Digestion):
            digestion_id = digestion.id
        else:
            digestion_id = digestion
            digestion = self.app.fetch.digestion(digestion_id).data

        max_digestion_parts = (
            10_000  # TODO: configurable, raise error if too many parts
        )
        limit = 1000
        offset = 0
        digestion_parts_res = self.app.list.digestion_parts(
            digestion_id=digestion_id, limit=limit, offset=offset
        )
        digestion_parts = digestion_parts_res.data
        total_digestion_parts = digestion_parts_res.count
        if total_digestion_parts > max_digestion_parts:
            raise Exception(
                f"Too many digestion parts ({total_digestion_parts}) for extraction (must be less than {max_digestion_parts})"
            )

        while len(digestion_parts) < total_digestion_parts:
            offset += limit
            digestion_parts_res = self.app.list.digestion_parts(
                digestion_id=digestion_id, limit=limit, offset=offset
            )
            digestion_parts.extend(digestion_parts_res.data)
        digestion_parts_count = len(digestion_parts)
        if digestion_parts_count != total_digestion_parts:
            raise Exception(
                f"Expected {digestion_parts_count} digestion parts, but got {total_digestion_parts}"
            )

        if max_workers is None:
            for part_idx, digestion_part in enumerate(digestion_parts):
                self.app.logger.debug(
                    f"Processing digestion part {part_idx + 1} of {digestion_parts_count}"
                )
                for entry, record_bytes in self.iter_digestion_part_records(
                    digestion_part=digestion_part,
                    digestion=digestion,
                    digestion_part_wait_duration=digestion_part_wait_duration,
                    stream_buffer_length=stream_buffer_length,
                ):
                    yield digestion_part.id, entry, record_bytes
        else:

            def get_digestion_part_record_iter(digestion_part):
                items = []
                for entry, record_bytes in self.iter_digestion_part_records(
                    digestion_part=digestion_part,
                    digestion=digestion,
                    digestion_part_wait_duration=digestion_part_wait_duration,
                    stream_buffer_length=stream_buffer_length,
                ):
                    items.append((digestion_part.id, entry, record_bytes))
                return items

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for part_idx, digestion_part in enumerate(digestion_parts):
                    future = executor.submit(
                        get_digestion_part_record_iter, digestion_part
                    )
                    futures.append(future)
                for future_idx in range(len(futures)):
                    future = futures[future_idx]
                    for item in future.result():
                        yield item
                    futures[future_idx] = None

    def iter_digestion_data(
        self,
        digestion: Union[Digestion, UUID, str],
        deserialize_results: bool = False,
        transcoder: Optional[Transcode] = None,
        density_threshold: float = 0.9,
        max_contiguous_size: int = 100 * 1000 * 1000,
        max_contiguous_records: int = 1000,
        max_workers: Optional[int] = 2,
    ):
        if isinstance(digestion, Digestion):
            digestion_id = digestion.id
        else:
            digestion_id = digestion
            digestion = self.app.fetch.digestion(digestion_id).data

        log_id = digestion.log_id
        digestion_parts_res = self.app.list.digestion_parts(
            digestion_id=digestion_id, limit=1000
        )
        digestion_parts = digestion_parts_res.data
        digestion_parts_count = len(digestion_parts)
        if digestion_parts_count != digestion_parts_res.count:
            raise Exception(
                f"Expected {digestion_parts_count} digestion parts, but got {digestion_parts_res.count}"
            )

        def iter_digestion_records():
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = []
                for digestion_part in digestion_parts:
                    future = executor.submit(
                        self.app.fetch.digestion_part,
                        digestion_part_id=digestion_part.id,
                        digestion_id=digestion_id,
                    )
                    futures.append(future)
                for future in futures:
                    digestion_part = future.result().data
                    part_index = digestion_part.index
                    for entry in part_index:
                        record = self.digestion_part_index_entry_to_record(
                            entry=entry, log_id=log_id
                        )
                        yield record

        yield from self.iter_record_data(
            records=iter_digestion_records(),
            deserialize_results=deserialize_results,
            transcoder=transcoder,
            density_threshold=density_threshold,
            max_contiguous_size=max_contiguous_size,
            max_contiguous_records=max_contiguous_records,
            max_workers=max_workers,
        )
