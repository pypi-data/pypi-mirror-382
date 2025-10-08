from typing import List

from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.utils.plates.PlatingUtils import PlatingOrder


class MultiLayerReplicateConfig:
    number_of_replicates: int
    restart_on_next_item: bool
    apply_to_only_occupied_wells: bool
    repeat_until_all_plates: bool

    def __init__(self, number_of_replicates=1, restart_on_next_item=False, apply_to_only_occupied_wells=False,
                 repeat_until_all_plates=False):
        """
        :param number_of_replicates: The number of replicates that should be added before moving to the next record.
        :param restart_on_next_item: Whether to restart at the next row/col once all replicates have been plated.
        :param apply_to_only_occupied_wells: If True, records on this layer will only be applied to wells that already
                                                have a record on a lower layer.
        :param repeat_until_all_plates: If True, records will be applied until all wells are filled for existing plates,
                                        restarting at the beginning of the list once all records are applied.
                                        New plates will not be created while applying records from this layer.
        """
        self.number_of_replicates = number_of_replicates
        self.restart_on_next_item = restart_on_next_item
        self.apply_to_only_occupied_wells = apply_to_only_occupied_wells
        self.repeat_until_all_plates = repeat_until_all_plates


class MultiLayerDilutionConfig:
    dilution_factor: float
    starting_concentration: float

    def __init__(self, dilution_factor=1, starting_concentration=None):
        """
        :param dilution_factor: The factor by which subsequent replicates should have their concentration divided.
        :param starting_concentration: The starting concentration of the first replicate.
        """
        self.dilution_factor = dilution_factor
        self.starting_concentration = starting_concentration


class MultiLayerDataTypeConfig:
    data_type_name: str
    records: List[DataRecord]
    identifierField: str
    identifierValues: List[str]

    def __init__(self, data_type_name: str, records: List[DataRecord] = None,
                 id_field: str = None, id_values: List[str] = None):
        """

        :param data_type_name: The data type name of the records to apply to this layer
        :param records: A fixed list of records to use. If None, records will be pulled from the experiment.
        :param id_field: The field to check when filtering records based on the identifierValues parameter.
        :param id_values: Whitelist of values that should be used when retrieving records for this layer. Checks
                                    the field passed as identifierField.
        """
        self.data_type_name = data_type_name
        self.records = records
        self.identifierField = id_field
        self.identifierValues = id_values


class MultiLayerPlateLayer:
    data_type_config: MultiLayerDataTypeConfig
    plating_orientation: PlatingOrder.FillBy
    replicate_config: MultiLayerReplicateConfig
    dilution_config: MultiLayerDilutionConfig

    def __init__(self, data_type_config: MultiLayerDataTypeConfig, plating_orientation: PlatingOrder.FillBy,
                 replicate_config: MultiLayerReplicateConfig, dilution_config: MultiLayerDilutionConfig):
        self.data_type_config = data_type_config
        self.plating_orientation = plating_orientation
        self.replicate_config = replicate_config
        self.dilution_config = dilution_config


class MultiLayerPlateConfig:
    allowed_control_types: List[str]
    overflow_to_new_plate: bool
    plate_rows: int
    plate_cols: int

    def __init__(self, plate_rows=8, plate_cols=12, overflow_to_new_plate=True,
                 allowed_controls=None):
        """
        Create a 3D Plating Config
        :param plate_rows: The number of rows to be plated, and the default row count of new plates.
        :param plate_cols: The number of columns to be plated, and the default column count of new plates
        :param overflow_to_new_plate: Whether to create new plates if plating records reaches the end of the last
        provided plate, or the end of the first plate no existing plates are provided.
        :param allowed_controls: The controls that should be available to apply.
        """

        if allowed_controls is None:
            allowed_controls = ["Positive", "Negative"]
        self.plate_rows = plate_rows
        self.plate_cols = plate_cols
        self.overflow_to_new_plate = overflow_to_new_plate
        self.allowed_control_types = allowed_controls
