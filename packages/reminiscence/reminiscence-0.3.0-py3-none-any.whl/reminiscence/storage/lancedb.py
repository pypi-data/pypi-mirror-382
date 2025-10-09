"""LanceDB storage backend - Safe multi-format serialization with nested structure support."""

import json
import hashlib
import base64
import time
from typing import List, Dict, Any, Tuple
import lancedb
import pyarrow as pa

try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

from .base import StorageBackend
from ..types import CacheEntry
from ..utils.logging import get_logger
from ..utils.fingerprint import create_fingerprint

logger = get_logger(__name__)


class LanceDBBackend(StorageBackend):
    """LanceDB implementation with safe multi-format serialization (Singleton per db_uri)."""

    _instances: Dict[str, "LanceDBBackend"] = {}
    _lock = None

    def __new__(cls, config, embedding_dim: int, metrics=None):
        """Create or return existing instance for the same db_uri."""
        db_uri = config.db_uri

        if db_uri not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[db_uri] = instance
            logger.debug("storage_backend_created", db_uri=db_uri)
        else:
            logger.debug("storage_backend_reused", db_uri=db_uri)

        return cls._instances[db_uri]

    def __init__(self, config, embedding_dim: int, metrics=None):
        """Initialize LanceDB backend (only runs once per db_uri)."""
        if self._initialized:
            return

        self.config = config
        self.embedding_dim = embedding_dim
        self.metrics = metrics
        self.db = lancedb.connect(config.db_uri)
        self.schema = self._create_schema()
        self.table = self._init_table()
        self._index_created = False
        self._initialized = True

        logger.info(
            "storage_backend_initialized",
            db_uri=config.db_uri,
            table=config.table_name,
            embedding_dim=embedding_dim,
        )

    def _create_schema(self) -> pa.Schema:
        """Create PyArrow schema with fixed-size embedding for vector search."""
        return pa.schema(
            [
                pa.field("id", pa.string()),
                pa.field("query_text", pa.string()),
                pa.field("context", pa.string()),
                pa.field("context_hash", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), self.embedding_dim)),
                pa.field("result", pa.string()),
                pa.field("result_type", pa.string()),
                pa.field("timestamp", pa.float64()),
                pa.field("metadata", pa.string()),
            ]
        )

    def _init_table(self):
        """Initialize or open LanceDB table."""
        try:
            table = self.db.open_table(self.config.table_name)
            logger.debug("table_opened", name=self.config.table_name)
            return table
        except Exception:
            table = self.db.create_table(
                self.config.table_name, schema=self.schema, mode="overwrite"
            )
            logger.debug("table_created", name=self.config.table_name)
            return table

    @classmethod
    def _clear_instances(cls):
        """Clear all singleton instances (for testing only)."""
        cls._instances.clear()

    def _is_special_type(self, value: Any) -> bool:
        """Check if value is a DataFrame, array, or other special type."""
        if hasattr(value, "to_dict") and hasattr(value, "columns"):
            return True
        if hasattr(value, "to_arrow"):
            return True
        if hasattr(value, "__class__") and value.__class__.__name__ == "Table":
            return True
        if hasattr(value, "dtype") and hasattr(value, "shape"):
            return True
        return False

    def _serialize_nested_dict(self, result: dict) -> Tuple[str, str]:
        """Serialize dict that may contain DataFrames/arrays."""
        serialized_dict = {}
        special_types = {}

        for key, value in result.items():
            if self._is_special_type(value):
                serialized_value, value_type = self._serialize_result(value)
                serialized_dict[key] = f"__special__{key}"
                special_types[key] = {"data": serialized_value, "type": value_type}
            elif isinstance(value, (dict, list, tuple)):
                nested_serialized, nested_type = self._serialize_result(value)
                if nested_type.startswith("nested_"):
                    serialized_dict[key] = f"__special__{key}"
                    special_types[key] = {
                        "data": nested_serialized,
                        "type": nested_type,
                    }
                else:
                    serialized_dict[key] = value
            else:
                serialized_dict[key] = value

        final_data = {"base": serialized_dict, "special": special_types}

        if HAS_ORJSON:
            return orjson.dumps(final_data).decode("utf-8"), "nested_dict"
        else:
            return json.dumps(final_data), "nested_dict"

    def _serialize_nested_list(self, result: list) -> Tuple[str, str]:
        """Serialize list that may contain DataFrames/arrays."""
        serialized_list = []
        special_types = {}

        for idx, value in enumerate(result):
            if self._is_special_type(value):
                serialized_value, value_type = self._serialize_result(value)
                serialized_list.append(f"__special__{idx}")
                special_types[str(idx)] = {"data": serialized_value, "type": value_type}
            elif isinstance(value, (dict, list, tuple)):
                nested_serialized, nested_type = self._serialize_result(value)
                if nested_type.startswith("nested_"):
                    serialized_list.append(f"__special__{idx}")
                    special_types[str(idx)] = {
                        "data": nested_serialized,
                        "type": nested_type,
                    }
                else:
                    serialized_list.append(value)
            else:
                serialized_list.append(value)

        final_data = {"base": serialized_list, "special": special_types}

        if HAS_ORJSON:
            return orjson.dumps(final_data).decode("utf-8"), "nested_list"
        else:
            return json.dumps(final_data), "nested_list"

    def _serialize_result(self, result: Any) -> Tuple[str, str]:
        """Serialize result with optimal format selection."""
        if isinstance(result, dict):
            return self._serialize_nested_dict(result)

        if isinstance(result, (list, tuple)):
            return self._serialize_nested_list(result)

        if hasattr(result, "__class__") and result.__class__.__name__ == "Table":
            try:
                sink = pa.BufferOutputStream()
                with pa.ipc.new_stream(sink, result.schema) as writer:
                    writer.write_table(result)
                buffer = sink.getvalue()
                return (
                    base64.b64encode(buffer.to_pybytes()).decode("utf-8"),
                    "arrow_ipc",
                )
            except Exception as e:
                logger.warning("arrow_serialization_failed", error=str(e))

        if hasattr(result, "to_dict") and hasattr(result, "columns"):
            try:
                arrow_table = pa.Table.from_pandas(result)
                sink = pa.BufferOutputStream()
                with pa.ipc.new_stream(sink, arrow_table.schema) as writer:
                    writer.write_table(arrow_table)
                buffer = sink.getvalue()
                return (
                    base64.b64encode(buffer.to_pybytes()).decode("utf-8"),
                    "pandas_arrow",
                )
            except Exception as e:
                logger.warning("pandas_serialization_failed", error=str(e))

        if hasattr(result, "to_arrow"):
            try:
                arrow_table = result.to_arrow()
                sink = pa.BufferOutputStream()
                with pa.ipc.new_stream(sink, arrow_table.schema) as writer:
                    writer.write_table(arrow_table)
                buffer = sink.getvalue()
                return (
                    base64.b64encode(buffer.to_pybytes()).decode("utf-8"),
                    "polars_arrow",
                )
            except Exception as e:
                logger.warning("polars_serialization_failed", error=str(e))

        if hasattr(result, "dtype") and hasattr(result, "shape"):
            try:
                import numpy as np

                if isinstance(result, np.ndarray):
                    arrow_array = pa.array(result.flatten())
                    arrow_table = pa.Table.from_arrays([arrow_array], names=["values"])
                    sink = pa.BufferOutputStream()
                    with pa.ipc.new_stream(sink, arrow_table.schema) as writer:
                        writer.write_table(arrow_table)
                    buffer = sink.getvalue()

                    metadata = {"shape": list(result.shape), "dtype": str(result.dtype)}
                    encoded = base64.b64encode(buffer.to_pybytes()).decode("utf-8")
                    final_data = {"data": encoded, "metadata": metadata}

                    if HAS_ORJSON:
                        return orjson.dumps(final_data).decode("utf-8"), "numpy_arrow"
                    else:
                        return json.dumps(final_data), "numpy_arrow"
            except Exception as e:
                logger.warning("numpy_serialization_failed", error=str(e))

        try:
            if HAS_ORJSON:
                serialized = orjson.dumps(result).decode("utf-8")
                return serialized, "orjson"
            else:
                return json.dumps(result), "json"
        except (TypeError, ValueError) as e:
            logger.error(
                "json_serialization_failed", error=str(e), type=type(result).__name__
            )
            raise TypeError(
                f"Type {type(result).__name__} is not serializable. "
                f"Supported types: dict, list, str, int, float, bool, None, "
                f"pandas.DataFrame, polars.DataFrame, pyarrow.Table, numpy.ndarray"
            )

    def _deserialize_nested_dict(self, data: str) -> dict:
        """Deserialize nested dict with special types."""
        if HAS_ORJSON:
            parsed = orjson.loads(data.encode("utf-8"))
        else:
            parsed = json.loads(data)

        base_dict = parsed["base"]
        special_types = parsed["special"]

        result = {}
        for key, value in base_dict.items():
            if isinstance(value, str) and value.startswith("__special__"):
                special_key = value.replace("__special__", "")
                special_data = special_types[special_key]["data"]
                special_type = special_types[special_key]["type"]
                result[key] = self._deserialize_result(special_data, special_type)
            else:
                result[key] = value

        return result

    def _deserialize_nested_list(self, data: str) -> list:
        """Deserialize nested list with special types."""
        if HAS_ORJSON:
            parsed = orjson.loads(data.encode("utf-8"))
        else:
            parsed = json.loads(data)

        base_list = parsed["base"]
        special_types = parsed["special"]

        result = []
        for idx, value in enumerate(base_list):
            if isinstance(value, str) and value.startswith("__special__"):
                special_key = str(idx)
                special_data = special_types[special_key]["data"]
                special_type = special_types[special_key]["type"]
                result.append(self._deserialize_result(special_data, special_type))
            else:
                result.append(value)

        return result

    def _deserialize_numpy(self, data: str) -> Any:
        """Deserialize numpy array."""
        import numpy as np

        if HAS_ORJSON:
            parsed = orjson.loads(data.encode("utf-8"))
        else:
            parsed = json.loads(data)

        encoded_data = parsed["data"]
        metadata = parsed["metadata"]

        buffer = base64.b64decode(encoded_data.encode("utf-8"))
        reader = pa.ipc.open_stream(buffer)
        arrow_table = reader.read_all()

        flat_array = arrow_table["values"].to_numpy()

        shape = tuple(metadata["shape"])
        dtype = np.dtype(metadata["dtype"])

        return flat_array.reshape(shape).astype(dtype)

    def _deserialize_result(self, data: str, result_type: str) -> Any:
        """Deserialize result from string based on type indicator."""
        if result_type == "nested_dict":
            return self._deserialize_nested_dict(data)

        if result_type == "nested_list":
            return self._deserialize_nested_list(data)

        if result_type == "numpy_arrow":
            return self._deserialize_numpy(data)

        if result_type == "arrow_ipc":
            buffer = base64.b64decode(data.encode("utf-8"))
            reader = pa.ipc.open_stream(buffer)
            return reader.read_all()

        elif result_type == "pandas_arrow":
            buffer = base64.b64decode(data.encode("utf-8"))
            reader = pa.ipc.open_stream(buffer)
            arrow_table = reader.read_all()
            return arrow_table.to_pandas()

        elif result_type == "polars_arrow":
            buffer = base64.b64decode(data.encode("utf-8"))
            reader = pa.ipc.open_stream(buffer)
            arrow_table = reader.read_all()
            try:
                import polars as pl

                return pl.from_arrow(arrow_table)
            except ImportError:
                logger.warning("polars_not_available", returning="arrow_table")
                return arrow_table

        elif result_type == "orjson":
            if HAS_ORJSON:
                return orjson.loads(data.encode("utf-8"))
            else:
                return json.loads(data)

        elif result_type == "json":
            return json.loads(data)

        elif result_type == "repr":
            obj = json.loads(data)
            return obj.get("__repr__")

        else:
            logger.error("unknown_result_type", type=result_type)
            return None

    def count(self) -> int:
        """Get number of entries."""
        return self.table.count_rows()

    def add(self, entries: List[CacheEntry]):
        """Add cache entries with context hash for fast lookup."""
        start = time.perf_counter()

        data = []
        for entry in entries:
            try:
                context_json = json.dumps(entry.context, sort_keys=True)
                context_hash = create_fingerprint(entry.context)
                serialized_result, result_type = self._serialize_result(entry.result)

                data.append(
                    {
                        "id": self._generate_id(entry),
                        "query_text": entry.query_text,
                        "context": context_json,
                        "context_hash": context_hash,
                        "embedding": entry.embedding,
                        "result": serialized_result,
                        "result_type": result_type,
                        "timestamp": entry.timestamp,
                        "metadata": json.dumps(entry.metadata)
                        if entry.metadata
                        else "{}",
                    }
                )
            except TypeError as e:
                logger.error(
                    "entry_skipped_unserializable", error=str(e), query=entry.query_text
                )

                if self.metrics:
                    if not hasattr(self.metrics, "storage_add_errors"):
                        self.metrics.storage_add_errors = 0
                    self.metrics.storage_add_errors += 1

                continue
            except Exception as e:
                logger.error(
                    "serialization_failed", error=str(e), entry_query=entry.query_text
                )

                if self.metrics:
                    if not hasattr(self.metrics, "storage_add_errors"):
                        self.metrics.storage_add_errors = 0
                    self.metrics.storage_add_errors += 1

                continue

        if data:
            try:
                self.table.add(data)

                elapsed_ms = (time.perf_counter() - start) * 1000

                if self.metrics:
                    if not hasattr(self.metrics, "storage_adds"):
                        self.metrics.storage_adds = 0
                    self.metrics.storage_adds += len(data)

                    if not hasattr(self.metrics, "storage_add_latencies_ms"):
                        self.metrics.storage_add_latencies_ms = []
                    self.metrics.storage_add_latencies_ms.append(elapsed_ms)

                    if len(self.metrics.storage_add_latencies_ms) > 1000:
                        self.metrics.storage_add_latencies_ms = (
                            self.metrics.storage_add_latencies_ms[-1000:]
                        )

                logger.debug(
                    "storage_add",
                    entries_count=len(data),
                    latency_ms=round(elapsed_ms, 2),
                )

            except Exception as e:
                logger.error("storage_add_failed", error=str(e))

                if self.metrics:
                    if not hasattr(self.metrics, "storage_add_errors"):
                        self.metrics.storage_add_errors = 0
                    self.metrics.storage_add_errors += 1

                raise

    def search(
        self,
        embedding: List[float],
        context: Dict[str, Any],
        limit: int = 50,
        similarity_threshold: float = 0.85,
    ) -> List[CacheEntry]:
        """Hybrid search: hash-based context filter + semantic similarity."""
        start = time.perf_counter()

        context_hash = (
            create_fingerprint(context) if context else create_fingerprint({})
        )

        where_clause = f"context_hash = '{context_hash}'"

        query = self.table.search(embedding).metric("cosine").limit(limit)
        query = query.where(where_clause)

        try:
            results = query.to_arrow()

            elapsed_ms = (time.perf_counter() - start) * 1000

            if self.metrics:
                if not hasattr(self.metrics, "storage_searches"):
                    self.metrics.storage_searches = 0
                self.metrics.storage_searches += 1

                if not hasattr(self.metrics, "storage_search_latencies_ms"):
                    self.metrics.storage_search_latencies_ms = []
                self.metrics.storage_search_latencies_ms.append(elapsed_ms)

                if len(self.metrics.storage_search_latencies_ms) > 1000:
                    self.metrics.storage_search_latencies_ms = (
                        self.metrics.storage_search_latencies_ms[-1000:]
                    )

            logger.debug(
                "storage_search",
                results_count=len(results),
                latency_ms=round(elapsed_ms, 2),
            )

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "search_failed",
                error=str(e),
                latency_ms=round(elapsed_ms, 2),
                exc_info=True,
            )

            if self.metrics:
                if not hasattr(self.metrics, "storage_search_errors"):
                    self.metrics.storage_search_errors = 0
                self.metrics.storage_search_errors += 1

            return []

        entries = []
        for i in range(len(results)):
            try:
                distance = results["_distance"][i].as_py()
                similarity = 1.0 - distance

                if similarity < similarity_threshold:
                    continue

                context_dict = json.loads(results["context"][i].as_py())
                result_data = results["result"][i].as_py()
                result_type = results["result_type"][i].as_py()
                result_obj = self._deserialize_result(result_data, result_type)

                metadata_str = results["metadata"][i].as_py()
                metadata_obj = (
                    json.loads(metadata_str)
                    if metadata_str and metadata_str != "{}"
                    else None
                )

                entry = CacheEntry(
                    query_text=results["query_text"][i].as_py(),
                    context=context_dict,
                    embedding=list(results["embedding"][i]),
                    result=result_obj,
                    timestamp=results["timestamp"][i].as_py(),
                    similarity=similarity,
                    metadata=metadata_obj,
                )
                entries.append(entry)

            except Exception as e:
                logger.error("deserialization_failed", index=i, error=str(e))
                continue

        entries.sort(key=lambda x: x.similarity or 0, reverse=True)

        return entries

    def to_arrow(self):
        """Convert to Arrow table."""
        return self.table.to_arrow()

    def delete_by_filter(self, filter_expr: str):
        """Delete entries matching filter."""
        if self.config.db_uri == "memory://":
            raise NotImplementedError("Use delete_by_condition for memory://")
        else:
            self.table.delete(filter_expr)
            try:
                self.table.compact_files()
            except AttributeError:
                pass

    def delete_by_condition(self, condition_func):
        """Delete by custom condition (for memory mode)."""
        if self.config.db_uri == "memory://":
            arrow_table = self.to_arrow()
            mask = condition_func(arrow_table)
            filtered = arrow_table.filter(mask)

            self.table = self.db.create_table(
                self.config.table_name,
                data=filtered if len(filtered) > 0 else None,
                schema=self.schema if len(filtered) == 0 else None,
                mode="overwrite",
            )
        else:
            raise NotImplementedError("Use delete_by_filter for persistent storage")

    def clear(self):
        """Clear all entries from cache."""
        self.table = self.db.create_table(
            self.config.table_name,
            schema=self.schema,
            mode="overwrite",
        )
        self._index_created = False

    def has_index(self) -> bool:
        """Check if index exists."""
        return self._index_created

    def create_index(self, num_partitions: int, num_sub_vectors: int):
        """Create IVF-PQ index for vector search."""
        logger.info(
            "creating_index",
            partitions=num_partitions,
            sub_vectors=num_sub_vectors,
            entries=self.count(),
        )

        self.table.create_index(
            num_partitions=num_partitions,
            num_sub_vectors=num_sub_vectors,
        )
        self._index_created = True
        logger.info("index_created")

    def maybe_auto_create_index(self, threshold: int, num_partitions: int):
        """Create index if threshold reached."""
        if self._index_created:
            return

        count = self.count()
        if count >= threshold:
            logger.info("auto_creating_index", count=count, threshold=threshold)
            num_sub_vectors = max(1, self.embedding_dim // 4)
            self.create_index(num_partitions, num_sub_vectors)

    def get_storage_stats(self) -> dict:
        """Get storage-specific statistics."""
        if not self.metrics:
            return {}

        search_latencies = getattr(self.metrics, "storage_search_latencies_ms", [])
        add_latencies = getattr(self.metrics, "storage_add_latencies_ms", [])

        avg_search = (
            sum(search_latencies) / len(search_latencies) if search_latencies else 0
        )
        avg_add = sum(add_latencies) / len(add_latencies) if add_latencies else 0

        return {
            "total_entries": self.count(),
            "total_searches": getattr(self.metrics, "storage_searches", 0),
            "total_adds": getattr(self.metrics, "storage_adds", 0),
            "avg_search_latency_ms": round(avg_search, 2),
            "avg_add_latency_ms": round(avg_add, 2),
            "search_errors": getattr(self.metrics, "storage_search_errors", 0),
            "add_errors": getattr(self.metrics, "storage_add_errors", 0),
            "index_created": self._index_created,
        }

    def _generate_id(self, entry: CacheEntry) -> str:
        """Generate unique ID for entry using full SHA256 hash."""
        data = f"{entry.query_text}:{json.dumps(entry.context, sort_keys=True)}:{entry.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
