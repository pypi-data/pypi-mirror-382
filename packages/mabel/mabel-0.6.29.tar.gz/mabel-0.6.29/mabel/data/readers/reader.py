import datetime
from typing import Dict
from typing import Optional
from typing import Union

from orso.logging import get_logger

from mabel.data.internals.dictset import STORAGE_CLASS
from mabel.data.internals.dictset import DictSet
from mabel.data.internals.dnf_filters import DnfFilters
from mabel.data.internals.expression import Expression
from mabel.data.readers.internals.cursor import Cursor
from mabel.data.readers.internals.inline_evaluator import Evaluator
from mabel.data.readers.internals.multiprocess_wrapper import processed_reader
from mabel.data.readers.internals.parallel_reader import EXTENSION_TYPE
from mabel.data.readers.internals.parallel_reader import KNOWN_EXTENSIONS
from mabel.data.readers.internals.parallel_reader import ParallelReader
from mabel.data.readers.internals.parallel_reader import pass_thru
from mabel.errors import DataNotFoundError
from mabel.errors import InvalidCombinationError
from mabel.utils.dates import parse_delta
from mabel.utils.parameter_validator import validate

# fmt:off
RULES = [
    {"name": "cursor", "required": False, "warning": None, "incompatible_with": []},
    {"name": "dataset", "required": True, "warning": None, "incompatible_with": []},
    {"name": "end_date", "required": False, "warning": None, "incompatible_with": []},
    {"name": "freshness_limit", "required": False, "warning": None, "incompatible_with": []},
    {"name": "inner_reader", "required": False, "warning": None, "incompatible_with": []},
    {"name": "raw_path", "required": False, "warning": "raw_path will be deprecated, use `partitions` with an empty list", "incompatible_with": ["freshness_limit"]},
    {"name": "select", "required": False, "warning": None, "incompatible_with": []},
    {"name": "start_date", "required": False, "warning": None, "incompatible_with": []},
    {"name": "filters", "required": False, "warning": "", "incompatible_with": []},
    {"name": "persistence", "required": False, "warning": "", "incompatible_with": []},
    {"name": "override_format", "required": False, "warning": "", "incompatible_with": []},
    {"name": "multiprocess", "required": False, "warning": "", "incompatible_with": ["cursor"]},
    {"name": "valid_dataset_prefixes", "required": False},
    {"name": "partitions", "required": False, "warning": None, "incompatible_with": ["raw_path"]},
    {"name": "partition_filter", "required":False, "warning":"`partition_filter` is not expected to be a permanent addition to the API", "incompatible_with": ["freshness_limit"] },
    {"name": "project", "required":False, "warning":"`project` is no longer required for most Readers", "incompatible_with": []}
]
# fmt:on


class AccessDenied(Exception):
    pass


@validate(RULES)
def Reader(
    *,  # force all paramters to be keyworded
    select: str = "*",
    dataset: str = "",
    filters: Optional[str] = None,
    inner_reader=None,  # type:ignore
    raw_path: bool = None,
    persistence: STORAGE_CLASS = STORAGE_CLASS.NO_PERSISTANCE,
    override_format: Optional[str] = None,
    multiprocess: bool = False,
    cursor: Optional[Union[str, Dict]] = None,
    valid_dataset_prefixes: Optional[list] = None,
    partitions=["year_{yyyy}/month_{mm}/day_{dd}"],
    partition_filter=None,
    **kwargs,
) -> DictSet:
    """
    Reads records from a data store, opinionated toward Google Cloud Storage but a
    filesystem reader is available to assist with local development.

    The Reader will iterate over a set of files and return them to the caller as a
    single stream of records. The files can be read from a single folder or can be
    matched over a set of date/time formatted folder names. This is useful to read
    over a set of logs. The date range is provided as part of the call; this is
    essentially a way to partition the data by date/time.

    The reader can filter records to return a subset, for JSON formatted data the
    records can be converted to dictionaries before filtering. JSON data can also
    be used to select columns, so not all read data is returned.

    The reader does not support aggregations, calculations or grouping of data, it
    is a log reader and returns log entries. The reader can convert a set into
    _Pandas_ dataframe, or the _dictset_ helper library can perform some activities
    on the set in a more memory efficient manner.

    Note:
        Different _inner_readers_ may take or require additional parameters. This
        class has a decorator which helps to ensure it is called correctly.

    Parameters:
        select: string (optional):
            A select expression, this is usually a comma separated list of field names
            although can include predefined functions. Default is "*" which presents
            all of the fields in the dataset.
        dataset: string:
            The path to the data source (exact syntax differs per inner_reader)
        filters: string or list/tuple (optional):
            STRING:
            An expression which when evaluated for each row, if False the row will
            be removed from the resulant data set, like the WHERE clause of of a SQL
            statement.
            LIST/TUPLE:
            Filter expressed as DNF.
        inner_reader: BaseReader (optional):
            The reader class to perform the data access Operators, the default is
            GoogleCloudStorageReader
        start_date: datetime (optional):
            The starting date of the range to read over, default is today
        end_date: datetime (optional):
            The end date of the range to read over, default is today
        freshness_limit: string (optional):
            a time delta string (e.g. 6h30m = 6hours and 30 minutes) which
            incidates the maximum age of a dataset before it is no longer
            considered fresh. Where the 'time' of a dataset cannot be
            determined, it will be treated as midnight (00:00) for the date.
        persistence: STORAGE_CLASS (optional)
            How to cache the results, the default is NO_PERSISTANCE which will almost
            always return a generator. MEMORY should only be used where the dataset
            isn't huge and DISK is many times slower than MEMORY. COMPRESSED_MEMORY
            fits in between, usually faster than DISK but slower than MEMORY.
        cursor: dictionary (or string)
            Resume read from a given point (assumes other parameters are the same).
            If a JSON string is provided, it will converted to a dictionary.
        override_format: string (optional)
            Override the format detection - sometimes users know better.
        multiprocess: boolean (optional)
            Split the task over multiple CPUs to improve throughput. Note that there
            are conditions that must be met for the multiprocessor to be safe which
            may mean even though this is set, data is accessed serially.
        valid_dataset_prefixes: list (optional)
            Raises an error if the start of the dataset isn't on the list. The
            intended use is for situations where an external agent can initiate
            the request (such as the Query application). This allows a whitelist
            of allowable resources to be defined.
        partitions: list (optional)
            List of folder names, with datetime placeholders, to use to build a path
            to the data files.
        partition_filter: tuple (optional)
            Provide a hint on how to filter the partitions, as a single tuple in DNF
            notiation, this may be ignored.

    Returns:
        DictSet

    """
    # We can provide an optional whitelist of prefixes that we allow access to
    # - this doesn't replace a proper ACL and permissions model, but can provide
    # some control if other options are limited or unavailable.
    if valid_dataset_prefixes:
        if not any(
            [
                True
                for prefix in valid_dataset_prefixes
                if str(dataset).startswith(prefix)
            ]
        ):
            raise AccessDenied("Access has been denied to this Dataset (prefix).")

    # lazy loading of dependency - in this case the Google GCS Reader
    # eager loading will cause failures when we try to load the google-cloud
    # libraries and they aren't installed.
    if inner_reader is None:
        from ...adapters.google import GoogleCloudStorageReader

        inner_reader = GoogleCloudStorageReader

    # handle transitional states - use the new features to override the legacy features
    if str(raw_path).upper() == "TRUE":
        partitions = None

    # instantiate the injected reader class
    reader_class = inner_reader(
        dataset=dataset,
        partitions=partitions,
        partition_filter=partition_filter,
        **kwargs,
    )  # type:ignore

    arg_dict = kwargs.copy()
    arg_dict["select"] = f"{select}"
    arg_dict["dataset"] = f"{dataset}"
    arg_dict["inner_reader"] = f"{inner_reader.__name__}"  # type:ignore
    arg_dict["filters"] = filters
    get_logger().debug(arg_dict)

    # number of days to walk backwards to find records
    freshness_limit = parse_delta(kwargs.get("freshness_limit", ""))

    if (
        freshness_limit and reader_class.start_date != reader_class.end_date
    ):  # pragma: no cover
        raise InvalidCombinationError(
            "freshness_limit can only be used when the start and end dates are the same"
        )

    return DictSet(
        _LowLevelReader(
            reader_class=reader_class,
            freshness_limit=freshness_limit,
            select=select,
            filters=filters,
            override_format=override_format,
            cursor=cursor,
            multiprocess=multiprocess,
        ),
        storage_class=persistence,
    )


class _LowLevelReader(object):
    def __init__(
        self,
        reader_class,
        freshness_limit,
        select,
        filters,
        override_format,
        cursor,
        multiprocess,
    ):
        self.reader_class = reader_class
        self.freshness_limit = freshness_limit
        self.select = select
        self.override_format = override_format
        self.cursor = cursor
        self._inner_line_reader = None
        self.multiprocess = multiprocess

        if isinstance(filters, str):
            self.filters = Expression(filters)
        elif isinstance(filters, (tuple, list)):
            self.filters = DnfFilters(filters)
        else:
            self.filters = None

        if select != "*":
            self.select = Evaluator(select)
        else:
            self.select = pass_thru

    def _create_line_reader(self):
        # get list of blobs handles as_at, by and frames
        blob_list = self.reader_class.get_list_of_blobs()

        # Handle stepping back if the option is set
        if self.freshness_limit > datetime.timedelta(seconds=1):
            while not bool(blob_list) and self.freshness_limit >= datetime.timedelta(
                days=self.reader_class.days_stepped_back
            ):
                self.reader_class.step_back_a_day()
                blob_list = self.reader_class.get_list_of_blobs()
            if self.freshness_limit < datetime.timedelta(
                days=self.reader_class.days_stepped_back
            ):
                message = f"No data found in last {self.freshness_limit} - aborting ({self.reader_class.dataset})"
                get_logger().warning(message)
                raise DataNotFoundError(message)
            if self.reader_class.days_stepped_back > 0:
                get_logger().warning(
                    f"Read looked back {self.reader_class.days_stepped_back} day(s) to {self.reader_class.start_date}, limit is {self.freshness_limit} ({self.reader_class.dataset})"
                )

        # Build lists of blobs we have handlers for, based on the file extensions
        supported_blobs = [
            b for b in blob_list if f".{b.split('.')[-1]}" in KNOWN_EXTENSIONS
        ]
        readable_blobs = [
            b
            for b in supported_blobs
            if KNOWN_EXTENSIONS[f".{b.split('.')[-1]}"][2] == EXTENSION_TYPE.DATA
        ]

        # Log debug information or an error if there's no blobs to read
        message = f"Reader found {len(readable_blobs)} sources to read data from in `{self.reader_class.dataset}`."
        if len(readable_blobs) == 0:
            get_logger().warning(message)
            raise DataNotFoundError(message)
        else:
            get_logger().debug(message)

        parallel = ParallelReader(
            reader=self.reader_class,
            columns=self.select,
            filters=self.filters or pass_thru,
            override_format=self.override_format,
        )

        use_multiprocess = all(
            [
                self.multiprocess,  # the user must have asked for it
                not self.cursor,  # we must not have a cursor
                len(readable_blobs) > 4,  # we must enough files to read
            ]
        )

        if not use_multiprocess:
            get_logger().debug(f"Serial Reader {self.cursor}")
            if not isinstance(self.cursor, Cursor):
                cursor = Cursor(readable_blobs=readable_blobs, cursor=self.cursor)
                self.cursor = cursor

            blob_to_read = self.cursor.next_blob()
            while blob_to_read:
                blob_reader = parallel(
                    blob_to_read,
                    [
                        idx
                        for idx in supported_blobs
                        if blob_to_read in idx and idx.endswith(".idx")
                    ],
                )
                location = self.cursor.skip_to_cursor(blob_reader)
                for self.cursor.location, record in enumerate(
                    blob_reader, start=location
                ):
                    yield record
                blob_to_read = self.cursor.next_blob(blob_to_read)

        else:
            get_logger().debug("Parallel Reader")
            yield from processed_reader(parallel, readable_blobs, supported_blobs)

    def __iter__(self):
        return self

    def __next__(self):
        if self._inner_line_reader is None:
            self._inner_line_reader = self._create_line_reader()

        # get the the next line from the reader
        return self._inner_line_reader.__next__()
