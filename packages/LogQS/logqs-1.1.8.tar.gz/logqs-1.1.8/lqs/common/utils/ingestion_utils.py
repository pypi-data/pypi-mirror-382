import datetime
from uuid import UUID
from typing import Optional, Union, TYPE_CHECKING

from lqs.transcode import Transcode

if TYPE_CHECKING:
    from lqs.common.facade import CoreFacade
from lqs.interface.core.models import (
    Ingestion,
    IngestionPart,
    Record,
)


class IngestionUtils:
    def __init__(self, app: "CoreFacade"):
        self.app = app

    def ingestion_part_index_entry_to_record(
        self,
        entry: tuple,
        ingestion_id: Union[UUID, str],
        source: Optional[str] = None,
        log_id: Union[UUID, str] = "00000000-0000-0000-0000-000000000000",
        created_at: datetime.datetime = datetime.datetime.now(),
    ) -> Record:
        context = None
        if len(entry) == 7:
            (
                topic_id,
                data_offset,
                data_length,
                chunk_compression,
                chunk_offset,
                chunk_length,
                timestamp,
            ) = entry
        elif len(entry) == 8:
            (
                topic_id,
                data_offset,
                data_length,
                chunk_compression,
                chunk_offset,
                chunk_length,
                timestamp,
                context,
            ) = entry
        else:
            raise ValueError(f"Invalid index entry length: {len(entry)}")
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
            context=context,
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

    def iter_ingestion_part_data(
        self,
        ingestion_part: Union[IngestionPart, UUID, str],
        ingestion: Optional[Ingestion] = None,
        deserialize_results: bool = False,
        transcoder: Optional[Transcode] = None,
        density_threshold: float = 0.9,
        max_contiguous_size: int = 100 * 1000 * 1000,
        max_contiguous_records: int = 1000,
        max_workers: Optional[int] = 2,
    ):
        if isinstance(ingestion_part, IngestionPart):
            ingestion_part_id = ingestion_part.id
            if ingestion_part.index is None:
                ingestion_part = self.app.fetch.ingestion_part(
                    ingestion_part_id=ingestion_part_id,
                    ingestion_id="00000000-0000-0000-0000-000000000000",
                ).data
        else:
            ingestion_part_id = ingestion_part
            ingestion_part = self.app.fetch.ingestion_part(
                ingestion_part_id=ingestion_part_id,
                ingestion_id="00000000-0000-0000-0000-000000000000",
            ).data

        if ingestion is None:
            ingestion = self.app.fetch.ingestion(ingestion_part.ingestion_id).data

        def iter_ingestion_part_records():
            part_index = ingestion_part.index
            for entry in part_index:
                record = self.ingestion_part_index_entry_to_record(
                    entry=entry,
                    ingestion_id=ingestion_part.ingestion_id,
                    source=ingestion_part.source,
                    log_id=ingestion.log_id,
                )
                yield record

        yield from self.iter_record_data(
            records=iter_ingestion_part_records(),
            deserialize_results=deserialize_results,
            transcoder=transcoder,
            density_threshold=density_threshold,
            max_contiguous_size=max_contiguous_size,
            max_contiguous_records=max_contiguous_records,
            max_workers=max_workers,
        )
