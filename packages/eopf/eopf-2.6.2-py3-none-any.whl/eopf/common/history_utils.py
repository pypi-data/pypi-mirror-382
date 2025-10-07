from copy import deepcopy
from datetime import datetime, timezone
from re import match
from typing import Any, Dict, List, Optional, Tuple
from warnings import warn

from eopf import EOContainer, EOProduct, __version__
from eopf.common.constants import (
    PROCESSING_HISTORY_ADFS_FIELD,
    PROCESSING_HISTORY_ATTR,
    PROCESSING_HISTORY_EOPF_ASGARD_VERSION_FIELD,
    PROCESSING_HISTORY_EOPF_CPM_VERSION_FIELD,
    PROCESSING_HISTORY_EOPF_PYTHON_VERSION_FIELD,
    PROCESSING_HISTORY_EXECUTION_PARAMETERS_FIELD,
    PROCESSING_HISTORY_FACILITY_FIELD,
    PROCESSING_HISTORY_INPUTS_FIELD,
    PROCESSING_HISTORY_MANDATORY_FIELDS,
    PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN,
    PROCESSING_HISTORY_OUTPUTS_FIELD,
    PROCESSING_HISTORY_PROCESSOR_FIELD,
    PROCESSING_HISTORY_TIME_FIELD,
    PROCESSING_HISTORY_TIME_FORMAT,
    PROCESSING_HISTORY_UNKNOWN_MARKER,
    PROCESSING_HISTORY_UNKNOWN_TIME_MARKER,
    PROCESSING_HISTORY_VERSION_FIELD,
)
from eopf.common.date_utils import force_utc_iso8601
from eopf.config import EOConfiguration
from eopf.exceptions.errors import (
    ProcessingHistoryError,
    ProcessingHistoryInvalidEntry,
    ProcessingHistoryInvalidLevel,
    ProcessingHistoryMissingLevels,
)
from eopf.exceptions.warnings import ProcessingHistoryWarning
from eopf.logging import EOLogging

EOConfiguration().register_requested_parameter(
    "general__facility",
    "CS-SopraSteria",
    False,
    description="Organisation/Facility performing the conversion of legacy products",
)
EOConfiguration().register_requested_parameter(
    "general__title",
    "EOPF-CPM",
    False,
    description="Name of the Application",
)

_logger = EOLogging().get_logger("eopf.common.history_utils")


def init_history_entry(
    add_adfs_field: bool = False,
    add_cpm_version_field: bool = False,
    add_asgard_version_field: bool = False,
    add_python_version_field: bool = False,
    add_processing_parameters_field: bool = False,
) -> Dict[str, Any]:
    """
    Initialise a processing history entry with the mandatory fields; see PROCESSING_HISTORY_MANDATORY_FIELDS
    At user request the PROCESSING_HISTORY_OPTIONAL_FIELDS can also be initialised

    Parameters
    ----------
    add_adfs_field: bool
        initialises the optional ADFS field
    add_cpm_version_field: bool
        initialises the optional CPM version field
    add_asgard_version_field: bool
        initialises the optional ASGARD version field
    add_python_version_field: bool
        initialises the optional Python version field
    add_processing_parameters_field: bool
        initialises the optional Processing Parameters version field

    Returns
    -------
    Dict[str, Any]
    """

    entry: Dict[str, Any] = dict()

    entry[PROCESSING_HISTORY_PROCESSOR_FIELD] = PROCESSING_HISTORY_UNKNOWN_MARKER
    entry[PROCESSING_HISTORY_VERSION_FIELD] = PROCESSING_HISTORY_UNKNOWN_MARKER
    entry[PROCESSING_HISTORY_FACILITY_FIELD] = PROCESSING_HISTORY_UNKNOWN_MARKER
    entry[PROCESSING_HISTORY_TIME_FIELD] = PROCESSING_HISTORY_UNKNOWN_MARKER
    entry[PROCESSING_HISTORY_INPUTS_FIELD] = list()
    entry[PROCESSING_HISTORY_OUTPUTS_FIELD] = list()

    if add_adfs_field is True:
        entry[PROCESSING_HISTORY_ADFS_FIELD] = list()

    if add_cpm_version_field is True:
        entry[PROCESSING_HISTORY_EOPF_CPM_VERSION_FIELD] = PROCESSING_HISTORY_UNKNOWN_MARKER

    if add_asgard_version_field is True:
        entry[PROCESSING_HISTORY_EOPF_ASGARD_VERSION_FIELD] = PROCESSING_HISTORY_UNKNOWN_MARKER

    if add_python_version_field is True:
        entry[PROCESSING_HISTORY_EOPF_PYTHON_VERSION_FIELD] = PROCESSING_HISTORY_UNKNOWN_MARKER

    if add_processing_parameters_field is True:
        entry[PROCESSING_HISTORY_EXECUTION_PARAMETERS_FIELD] = dict()

    return entry


def _extend_eop_history(
    eop: EOProduct,
    new_entry: Dict[str, Any],
    new_level: Optional[str],
) -> None:
    """
    Add processing history entry to EOProduct history in the highest processing level
    and after the latest entry

    Parameters
    ----------
    eop: EOProduct
        file system path to an existing product
    new_entry: Dict[str, Any]
        new processing history entry
    new_level: Optional[str]
        new processing history level

    Returns
    -------
    None
    """

    if PROCESSING_HISTORY_ATTR not in eop.attrs.keys():
        eop.attrs[PROCESSING_HISTORY_ATTR] = dict()

    existing_levels = [level for level in eop.attrs[PROCESSING_HISTORY_ATTR].keys()]
    if new_level in existing_levels:
        raise ProcessingHistoryError(f"Level {new_level} already exists in EOProduct Processing History {eop.name}")

    if new_level is None:
        if len(existing_levels) == 0:
            raise ProcessingHistoryMissingLevels(f"No level present and no new level defined for EOProduct {eop.name}")
        else:
            level_to_extend = existing_levels[-1]
    else:
        level_to_extend = new_level

    if len(existing_levels) == 0:
        # in case this is the first entry in the processing history
        last_entry_time = force_utc_iso8601(PROCESSING_HISTORY_UNKNOWN_TIME_MARKER)
    else:
        existing_last_level = existing_levels[-1]
        last_entry = eop.attrs[PROCESSING_HISTORY_ATTR][existing_last_level][-1]
        last_entry_time = force_utc_iso8601(last_entry[PROCESSING_HISTORY_TIME_FIELD])

    new_entry_time = force_utc_iso8601(new_entry[PROCESSING_HISTORY_TIME_FIELD])

    if new_entry_time >= last_entry_time:
        if level_to_extend in eop.attrs[PROCESSING_HISTORY_ATTR]:
            eop.attrs[PROCESSING_HISTORY_ATTR][level_to_extend].append(new_entry)
        else:
            eop.attrs[PROCESSING_HISTORY_ATTR][level_to_extend] = [new_entry]
    else:
        raise ProcessingHistoryError(
            f"New entry {new_entry_time} earlier than last entry {last_entry_time} in EOProduct {eop.name}",
        )


def _recursive_dict_check(val: Dict[str, Any]) -> Tuple[bool, str]:
    for k, v in val.items():
        if not isinstance(v, (str, list, dict)):
            message = f"Field: {k}; the value must be either a str, list or dict"
            return False, message
        if isinstance(v, list):
            ok, msg = _recursive_list_check(v)
            if ok is False:
                return ok, msg
        if isinstance(v, dict):
            ok, msg = _recursive_dict_check(v)
            if ok is False:
                return ok, msg

    message = "Valid processing history dict"
    return True, message


def _recursive_list_check(val: list[Any]) -> Tuple[bool, str]:
    for item in val:
        if not isinstance(item, (str, list, dict)):
            message = f"Field: {item}; the value must be either a str, list or dict"
            return False, message
        if isinstance(item, list):
            return _recursive_list_check(item)
        if isinstance(item, dict):
            return _recursive_dict_check(item)

    message = "Valid processing history list"
    return True, message


def check_history_entry(entry: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Perform validity checks on processing history entry and returns invalidity reason

    Parameters
    ----------
    entry: EOProduct
        Dict[str, Any]


    Returns
    -------
    Tuple[bool, str]
    """
    try:
        # check the type of values to be str, list or dict
        ok, message = _recursive_dict_check(entry)
        if ok is False:
            return ok, message

        # check the existence of mandatory fields and their values
        for mandatory_field in PROCESSING_HISTORY_MANDATORY_FIELDS:
            if mandatory_field not in entry.keys():
                message = f"Missing mandatory field: {mandatory_field}"
                return False, message

        try:
            force_utc_iso8601(entry[PROCESSING_HISTORY_TIME_FIELD])
        except Exception as err:
            message = f"{PROCESSING_HISTORY_TIME_FIELD} can not be converted to datetime due to: {err}"
            return False, message

        message = "Valid processing history entry"
        return True, message

    except Exception as err:
        message = f"Invalid processing history due to: {err}"
        return False, message


def _extend_history(
    root_eoobj: EOProduct | EOContainer,
    new_entry: Dict[str, Any],
    new_level: Optional[str] = None,
) -> None:
    """
    Traverse EOObject hierarchy and call EOProduct extend history

    Note
    This will add the new entry to all EOProducts under the EOContainer

    Parameters
    ----------
    root_eoobj: EOProduct | EOContainer
        root EOObject
    new_entry: Dict[str, Any]
        new processing history entry
    new_level: Optional[str]
        new level to be added

    Returns
    -------
    None
    """
    if isinstance(root_eoobj, EOProduct):
        _extend_eop_history(root_eoobj, new_entry, new_level)
    elif isinstance(root_eoobj, EOContainer):
        for child_eoobj in root_eoobj:
            _extend_history(root_eoobj[child_eoobj], new_entry, new_level)
    else:
        # do not explore lower that EOProducts
        pass


def extend_history(
    root_eoobj: EOProduct | EOContainer,
    new_entry: Dict[str, Any],
    new_level: Optional[str] = None,
) -> None:
    """
    Add processing history entry to EOProduct history (recursively) in the highest processing level
    or given new level. The new entry is added after the existing last entry

    Note
    This will add the new entry to all EOProducts under the EOContainer

    Parameters
    ----------
    root_eoobj: EOProduct | EOContainer
        root EOObject
    new_entry: Dict[str, Any]
        new processing history entry
    new_level: Optional[str]
        new level to be added

    Raises
    ------
    ProcessingHistoryInvalidEntry
    ProcessingHistoryInvalidLevel

    Returns
    -------
    None
    """
    # check new entry validity
    entry_is_valid, message = check_history_entry(new_entry)
    if entry_is_valid is False:
        raise ProcessingHistoryInvalidEntry(f"Invalid new entry due to: {message}")

    # check new level format
    if new_level is not None:
        m = match(PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN, new_level)
        if m is None:
            raise ProcessingHistoryInvalidLevel(
                f"New level: {new_level} does not match the format: {PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN}",
            )

    _extend_history(root_eoobj, new_entry, new_level)


def _update_safe_history(root_eoobj: EOProduct | EOContainer, safe_output: str) -> None:
    """
    As the legacy metadata files do not contain the name of the SAFE product (S01) or are hard to extract (S02, S03)
    We will add the output of the highest level processor (the safe file) during conversion

    Note
    This will update the new entry to all EOProducts under the EOContainer

    Parameters
    ----------
    root_eoobj: EOProduct | EOContainer
        root EOObject
    safe_output: str
        output generated by legacy SAFE processors

    Returns
    -------
    None
    """
    if isinstance(root_eoobj, EOProduct):
        existing_levels = [level for level in root_eoobj.attrs[PROCESSING_HISTORY_ATTR].keys()]
        highest_level = existing_levels[-1]
        root_eoobj.attrs[PROCESSING_HISTORY_ATTR][highest_level][-1][PROCESSING_HISTORY_OUTPUTS_FIELD] = [safe_output]
    if isinstance(root_eoobj, EOContainer):
        for child_path in root_eoobj:
            _update_safe_history(root_eoobj[child_path], safe_output)


def add_eopf_cpm_entry_to_history(
    root_eoobj: EOProduct | EOContainer,
    safe_output: str,
    cpm_output: str,
) -> None:
    """
    Add EOPF-CPM processing history entry to EOProduct history (recursively)
    in the highest processing level and after the latest entry

    Note
    This will add the new entry to all EOProducts under the EOContainer

    Parameters
    ----------
    root_eoobj: EOProduct | EOContainer
        root EOObject
    safe_output: str
        output generated by legacy SAFE processors
    cpm_output: str
        output generated by EOPF-CPM

    Returns
    -------
    None
    """

    _update_safe_history(root_eoobj, safe_output)
    cpm_history_entry = init_history_entry()
    cpm_history_entry[PROCESSING_HISTORY_VERSION_FIELD] = __version__
    cpm_history_entry[PROCESSING_HISTORY_FACILITY_FIELD] = EOConfiguration().get("general__facility")
    cpm_history_entry[PROCESSING_HISTORY_PROCESSOR_FIELD] = EOConfiguration().get("general__title")
    utc_now = datetime.now().replace(tzinfo=timezone.utc)
    cpm_history_entry[PROCESSING_HISTORY_TIME_FIELD] = utc_now.strftime(PROCESSING_HISTORY_TIME_FORMAT)
    cpm_history_entry[PROCESSING_HISTORY_INPUTS_FIELD] = [safe_output]
    cpm_history_entry[PROCESSING_HISTORY_OUTPUTS_FIELD] = [cpm_output]
    extend_history(root_eoobj, cpm_history_entry)


def _get_eop_history_entry(
    eop: EOProduct,
    level_id: str | int,
    entry_id: str | int,
    level_entries: list[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    entry: Dict[str, Any]
    if isinstance(entry_id, str):
        for entry in level_entries:
            # we suppose the processors are unique, thus we retrieve only the first occurrence
            if entry[PROCESSING_HISTORY_PROCESSOR_FIELD] == entry_id:
                return entry
        msg = f"Entry: {entry_id} is not present under EOProduct: {eop.name} processing history level: {level_id}"  # noqa: E501
        warn(msg, ProcessingHistoryWarning)
        _logger.warning(msg)
        return None
    else:
        return level_entries[entry_id]


def _get_eop_history_level(eop: EOProduct, level_id: str | int) -> list[Dict[str, Any]]:
    level_entries: list[Dict[str, Any]]
    if isinstance(level_id, int):
        existing_levels = [level for level in eop.attrs[PROCESSING_HISTORY_ATTR].keys()]
        level_entries = eop.attrs[PROCESSING_HISTORY_ATTR][existing_levels[level_id]]
    else:
        level_entries = eop.attrs[PROCESSING_HISTORY_ATTR][level_id]

    return level_entries


def _get_eop_history(
    eop: EOProduct,
    level_id: Optional[str | int] = None,
    entry_id: Optional[str | int] = None,
) -> Optional[Dict[str, List[dict[str, Any]]] | List[dict[str, Any]] | dict[str, Any]]:
    """
    Retrieve entire processing history, level or entry from an EOProduct

    Note
    ----
    The level id can be an index or the exact name
    The entry id can be the name of the processor or an index
    When providing an entry id it is mandatory to provide an level id

    Parameters
    ----------
    eop: EOProduct
    level_id: Optional[str|int]
    entry_id: Optional[str|int]

    Warnings
    --------
    ProcessingHistoryWarning

    Returns
    -------
    Optional[Dict[str, List[dict[str, Any]]] | List[dict[str, Any]] | dict[str, Any]]
    """

    if PROCESSING_HISTORY_ATTR not in eop.attrs:
        msg = f"No processing history under EOProduct: {eop.name}"
        warn(msg, ProcessingHistoryWarning)
        _logger.warning(msg)
        return None

    if level_id is None:
        return eop.attrs[PROCESSING_HISTORY_ATTR]

    try:
        level_entries = _get_eop_history_level(eop, level_id)
    except Exception as err:
        msg = f"Level: {str(level_id)} not present under EOProduct: {eop.name}, see error: {err}"  # noqa: E501

        warn(msg, ProcessingHistoryWarning)
        _logger.warning(msg)
        return None

    if entry_id is None:
        return level_entries

    try:
        return _get_eop_history_entry(eop, level_id, entry_id, level_entries)
    except Exception as err:
        msg = f"No processor with id: {str(entry_id)} is present under EOProduct: {eop.name} processing history level: {str(level_id)}, see error: {err}"  # noqa: E501
        warn(msg, ProcessingHistoryWarning)
        _logger.warning(msg)
        return None


def _filter_history_result(
    result: Dict[str, Any],
    eop_id: Optional[str] = None,
) -> Dict[str, Any]:
    # remove None results
    none_filtered_product: Dict[str, Any] = dict()
    for k, v in result.items():
        if v is not None:
            none_filtered_product[k] = v

    # remove results according to eop_id
    product_filtered_result: Dict[str, Any] = deepcopy(none_filtered_product)
    if eop_id is not None:
        for k, v in result.items():
            if eop_id not in k:
                product_filtered_result.pop(k)

    return product_filtered_result


def get_history(
    root_eoobj: EOProduct | EOContainer,
    level_id: Optional[str | int] = None,
    entry_id: Optional[str | int] = None,
    eop_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve entire processing history, level or entry from an EOProduct or EOContainer
    When retrieving history for an EOContainer there will be multiple results,
    one for each EOProduct under the EOCOntainer hierarchy.
    To easily identify results for each EOProduct you the top level key will display the path to the EOProduct
    inside the root EOContainer.

    Note
    ----
    The level id can be an index or the exact name
    The entry id can be the name of the processor or an index
    The eop id can be any part of the path (as str) to the EOProduct inside the EOContainer
    When providing an entry id it is mandatory to provide an level id

    Examples
    ----------
    - Retrieve the entire history
    >>> get_history(eop)
    The EOProduct will automatically sort the processor history in asceding manner,
    from oldest to newest level and entry
    - Retrieve the latest processing level in a generic way, via level index
    >>> get_history(eop, level_id=-1)
    - Retrieve the latest processing level, via level name
    >>> get_history(eop, level_id="Level-1 Product")
    - Retrieve the latest entry in a generic way, via level and entry index
    >>> get_history(eop, level_id=-1, entry_id=-1)
    - Retrieve the latest entry, via level index and processor name
    >>> get_history(eop, level_id=-1, entry_id="L1.2 processor")
    - One can filter the results on EOContainer based on the EOP path by passing an eop_id
    >>> get_history(eoc, level_id=-1, entry_id=-1, eop_id="rvl")

    Parameters
    ----------
    root_eoobj : EOProduct | EOContainer
    level_id: Optional[str|int]
    entry_id: Optional[str|int]
    eop_id: Optional[str] = None,


    Returns
    -------
    Optional[Dict[str, Any]]
    """

    try:
        result: Dict[str, Any] = {}
        if isinstance(root_eoobj, EOProduct):
            eop_res = _get_eop_history(root_eoobj, level_id, entry_id)
            result = {root_eoobj.name: eop_res}
        else:
            for child_path in root_eoobj:
                eoc_res = get_history(root_eoobj[child_path], level_id, entry_id)
                if eoc_res is not None:
                    for k, v in eoc_res.items():
                        abs_path = root_eoobj.name + "/" + k
                        result[abs_path] = v

        product_filtered_result = _filter_history_result(result, eop_id)

        if len(product_filtered_result) == 0:
            return None
        return product_filtered_result

    except Exception as err:
        msg = f"Can not retrieve processing history due to {str(err)}"  # noqa: E501
        warn(msg, ProcessingHistoryWarning)
        _logger.warning(msg)
        return None
