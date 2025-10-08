from collections import defaultdict
from string import ascii_uppercase
from typing import List, Iterator, Tuple, Optional

from sapiopylib.rest import User
from sapiopylib.rest.CustomReportService import CustomReportManager
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.DataTypeService import DataTypeManager
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.pojo.CustomReport import RawReportTerm, RawTermOperation, CustomReportCriteria, \
    ReportColumn
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, FieldType
from sapiopylib.rest.utils.Protocols import ElnExperimentProtocol, ElnEntryStep
from sapiopylib.rest.utils.plates.MultiLayerPlating import MultiLayerPlateLayer, MultiLayerPlateConfig
from sapiopylib.rest.utils.plates.PlatingUtils import PlatingOrder


class MultiLayerPlatingManager:
    protocol: ElnExperimentProtocol
    user: User
    data_record_manager: DataRecordManager
    eln_manager: ElnManager
    custom_report_manager: CustomReportManager
    data_type_manager: DataTypeManager

    @staticmethod
    def get_entry_prefs_json(layers: List[MultiLayerPlateLayer]) -> str:
        layer1 = layers[0]

        string = '{'
        string += '    "dataTypeShownInDataTypePanel": "' + ','.join(
            map(lambda layer: layer.data_type_config.data_type_name, layers)) + '",'
        string += '    "modeType": "DILUTION",'
        string += '    "dataTypePreferencesJSONMap": {'
        string += '    },'
        string += '    "fillByOrientationType": '
        if layer1.plating_orientation == PlatingOrder.FillBy.BY_ROW:
            string += '"FILL_BY_ROW",'
        else:
            string += '"FILL_BY_COLUMN",'
        string += '    "fillByDirectionType": "SE",'
        concentration = layer1.dilution_config.starting_concentration
        if concentration is not None:
            string += '    "dilutionTopConcentration": ' + str(concentration) + ','
        else:
            string += '    "dilutionTopConcentration": null,'
        string += '    "dilutionConcentrationUnits": "ng/µL",'
        factor = layer1.dilution_config.dilution_factor
        if factor is not None:
            string += '    "dilutionScheme": ' + str(factor) + ','
        else:
            string += '    "dilutionScheme": null,'
        string += '    "volume": null,'
        string += '    "concentration": null,'
        string += '    "concentrationUnits": null,'
        string += '    "AnnotationText": null,'
        string += '    "sourceVolumeToRemove": null,'
        string += '    "updateSourceVolumeToRemove": false,'
        string += '    "targetMass": null,'
        string += '    "updateTargetMass": false,'
        string += '    "isDisablePromptModeOptions": false,'
        string += '    "isUpdateConcentration": false,'
        string += '    "isUpdateConcentrationUnits": false,'
        string += '    "numReplicates": ' + str(layer1.replicate_config.number_of_replicates) + ','
        string += '    "fillByMethodType": false,'
        string += '    "isDataTypePanelCollapsed": false,'
        string += '    "isStackAssignments": false,'
        string += '    "shouldViewSourcePlate": false,'
        string += '    "isUpdateVolume": false,'
        string += '    "isShowTopLevel": false'
        string += '}'
        # print(string)
        return string

    @staticmethod
    def get_plate_configs_json(config: MultiLayerPlateConfig) -> str:
        string = '{'
        string += '    "plateSize": {'
        string += '        "iscircular": false,'
        string += '        "numCols": ' + str(config.plate_cols) + ','
        string += '        "numRows": ' + str(config.plate_rows)
        string += '    },'
        string += '    "controlTypesAllowed": ['
        string += '"' + '","'.join(config.allowed_control_types) + '"'
        string += '    ],'
        string += '    "dataTypesWhereReplicatesNotAllowed": ['
        string += '    ],'
        string += '    "outputSampleType": "* Same as Input *",'
        string += '    "plateSourceType": "BLANK_PLATE",'
        string += '    "layerSinkingDisabled": true,'
        string += '    "numberOfPlatesToCreate": 1,'
        string += '    "isHideResultTables": false,'
        string += '    "isReplicatesDisabled": false,'
        string += '    "isAutoAccessionPlateId": true,'
        string += '    "isControlsDisabled": false,'
        string += '    "normalization": {'
        string += '        "TargetVolume": null,'
        string += '        "TargetConcentration": null,'
        string += '        "TargetMass": null,'
        string += '        "SourceVolumeToRemove": null'
        string += '    }'
        string += '}'
        return string

    def __init__(self, protocol: ElnExperimentProtocol):
        self.protocol = protocol
        self.user = protocol.user
        self.data_record_manager = DataMgmtServer.get_data_record_manager(self.user)
        self.eln_manager = DataMgmtServer.get_eln_manager(self.user)
        self.custom_report_manager = DataMgmtServer.get_custom_report_manager(self.user)
        self.data_type_manager = DataMgmtServer.get_data_type_manager(self.user)

    def create_well_positions(self, config: MultiLayerPlateConfig,
                              layers: List[MultiLayerPlateLayer],
                              existing_plates=None) -> Tuple[List[DataRecord], List[DataRecord]]:
        # create Well Elements and Plates before we actually create the GUI step, so we can set the options
        # iterate through the layers provided
        if existing_plates is None:
            existing_plates = []
        used_wells = []
        plates: List[DataRecord] = existing_plates
        well_elements: List[DataRecord] = []
        for layer in layers:
            # get records from the experiment - break early if none are found
            records_for_step = self.get_records_for_layer(layer)
            if records_for_step is None or len(records_for_step) == 0:
                continue

            tracker = _PlateRecordTracker(plates, records_for_step, config, layer, self.user)

            # swap index lists depending on if we are iterating row or col wise
            if layer.plating_orientation == PlatingOrder.FillBy.BY_ROW:
                index1_list = ascii_uppercase[:config.plate_rows]
                index2_list = range(1, config.plate_cols + 1)
            else:
                index2_list = ascii_uppercase[:config.plate_rows]
                index1_list = range(1, config.plate_cols + 1)

            concentration = layer.dilution_config.starting_concentration

            # loop until we have exhausted all records, or we break due to not getting another plate
            while tracker.has_more_records():
                plate = tracker.get_next_plate()
                if plate is None:
                    break

                if plate not in plates:
                    plates.append(plate)

                # iterate over positions
                for index1 in index1_list:
                    for index2 in index2_list:
                        record = tracker.get_next_record()
                        # print(str(tracker.current_record_index) + "," + str(tracker.current_replicate_count))
                        if record is None:
                            break
                        # reset concentration
                        if tracker.is_different_record():
                            concentration = layer.dilution_config.starting_concentration
                        # continue to the next column instead of the next row if this is flagged to restart,
                        # unless we are already on a new row
                        if layer.replicate_config.restart_on_next_item \
                                and tracker.is_different_record() and index2_list.index(index2) > 0:
                            # backspace so we don't lose our current place after calling next_record
                            tracker.backspace()
                            break

                        # check if this well needs to be occupied by a previous layer
                        if layer.replicate_config.apply_to_only_occupied_wells:
                            if layer.plating_orientation == PlatingOrder.FillBy.BY_ROW:
                                position = str(index1) + str(index2)
                            else:
                                position = str(index2) + str(index1)

                            # check if this plate and position was added to on a previous layer, if not, skip
                            if not (str(plate.get_record_id()) + "::" + position) in used_wells:
                                break

                        # create a new Plate Designer Well Element record
                        well_element = self.data_record_manager.add_data_record("PlateDesignerWellElement")
                        # set Plate, Row, and Col
                        well_element.set_field_value("PlateRecordId", plate.get_record_id())

                        if layer.plating_orientation == PlatingOrder.FillBy.BY_ROW:
                            well_element.set_field_value("RowPosition", index1)
                            well_element.set_field_value("ColPosition", index2)
                            used_wells.append(str(plate.get_record_id()) + "::" + str(index1) + str(index2))
                        else:
                            well_element.set_field_value("RowPosition", index2)
                            well_element.set_field_value("ColPosition", index1)
                            used_wells.append(str(plate.get_record_id()) + "::" + str(index2) + str(index1))

                        # set the Layer based on the order provided
                        well_element.set_field_value("Layer", layers.index(layer) + 1)
                        # associate this Well Element with the current record
                        well_element.set_field_value("SourceDataTypeName", record.get_data_type_name())
                        well_element.set_field_value("SourceRecordId", record.get_record_id())
                        well_element.set_field_value("Concentration", concentration)
                        well_element.set_field_value("ConcentrationUnits", record.get_field_value("ConcentrationUnits"))

                        # divide concentration by dilution factor for the next loop
                        if layer.dilution_config.dilution_factor is not None and \
                                layer.dilution_config.starting_concentration is not None:
                            concentration = concentration / layer.dilution_config.dilution_factor

                        well_elements.append(well_element)
        return plates, well_elements

    def get_records_for_layer(self, layer: MultiLayerPlateLayer) -> List[DataRecord]:
        if layer.data_type_config.records is not None:
            return self.filter_for_valid_records(layer, layer.data_type_config.records)

        is_consumable = self.is_data_type_consumable(layer)
        if is_consumable:
            records_for_step: List[DataRecord] = self.get_records_for_consumable_type(layer)
            if len(records_for_step) > 0:
                return self.filter_for_valid_records(layer, records_for_step)

        # get the records from the experiment, somewhere prior to where the entry was added
        data_type_step = self.protocol.get_last_step_of_type(layer.data_type_config.data_type_name)
        # wrap record iterators in tracker for retrieval
        records_for_step = data_type_step.get_records()

        return self.filter_for_valid_records(layer, records_for_step)

    @staticmethod
    def filter_for_valid_records(layer: MultiLayerPlateLayer, records_for_step: List[DataRecord]) -> List[DataRecord]:
        # filter to valid records
        if layer.data_type_config.identifierField is not None:
            valid_keys = layer.data_type_config.identifierValues
            return [rec for rec in records_for_step if
                    rec.get_field_value(layer.data_type_config.identifierField) in valid_keys]
        return records_for_step

    def is_data_type_consumable(self, layer: MultiLayerPlateLayer) -> bool:

        exemplar_config: DataRecord = self.data_record_manager.query_all_records_of_type("ExemplarConfig").result_list[
            0]
        consumable_data_types: str = exemplar_config.get_field_value("ConsumableDataTypes")

        for consumable_family in consumable_data_types.split("\n"):
            item_level = consumable_family.split(":::")[1]
            item_level = item_level.strip()
            if item_level.upper() == layer.data_type_config.data_type_name.upper():
                return True

        return False

    def get_records_for_consumable_type(self, layer: MultiLayerPlateLayer) -> List[DataRecord]:
        # this is a consumable type, so check for ELN tables
        tag_key = "CONSUMABLE TRACKING"
        tag_value = "ITEM DATA TYPE: "
        steps = self.protocol.get_sorted_step_list()
        for step in steps:
            step_options = step.get_options()
            tag_value: str = step_options.get(tag_key)
            if tag_value is not None and tag_value in tag_value and layer.data_type_config.data_type_name in tag_value:
                consumable_step = step
                break
        else:
            # no step found, or else we'd have hit the break
            return []

        consumable_lot_field, consumable_type_field = self._get_consumable_type_and_lot_for_eln_type(consumable_step)
        if consumable_lot_field is None:
            return []

        # consumable_type_field = "ConsumableType"
        # consumable_lot_field = "ConsumableLot"

        # map the consumable types to lot numbers for later
        records: List[DataRecord] = consumable_step.get_records()
        type_to_lot_map = defaultdict(list)
        consumable_types = []
        for record in records:
            consumable_type = record.get_field_value(consumable_type_field)
            consumable_lot = record.get_field_value(consumable_lot_field)
            type_to_lot_map[consumable_type].append(consumable_lot)
            consumable_types.append(consumable_type)

        # retrieve the proper fields to query for based on the field tags of the data type
        record_consumable_type_field_name, record_consumable_lot_field_name = self. \
            _get_consumable_type_and_lot_for_data_type(layer.data_type_config.data_type_name)

        # query for type, lot, record id - we are querying only by consumable type,
        # as we can't check both fields in the report term
        consumable_type_term_value = "{" + (",".join(consumable_types)) + "}"
        consumable_type_term = RawReportTerm(layer.data_type_config.data_type_name, record_consumable_type_field_name,
                                             RawTermOperation.EQUAL_TO_OPERATOR,
                                             consumable_type_term_value)
        report_columns = [ReportColumn(layer.data_type_config.data_type_name,
                                       record_consumable_type_field_name, FieldType.STRING),
                          ReportColumn(layer.data_type_config.data_type_name,
                                       record_consumable_lot_field_name, FieldType.STRING),
                          ReportColumn(layer.data_type_config.data_type_name, "RecordId", FieldType.LONG)]
        custom_report_criteria: CustomReportCriteria = CustomReportCriteria(report_columns, consumable_type_term)
        result_table = self.custom_report_manager.run_custom_report(custom_report_criteria).result_table

        # check the custom report results, get record ID for valid type/lot pairs
        record_id_list = []
        for row in result_table:
            consumable_type = row[0]
            consumable_lot = row[1]
            record_id = row[2]
            valid_lots_for_type = type_to_lot_map[consumable_type]
            if consumable_lot in valid_lots_for_type:
                record_id_list.append(record_id)

        # return the actual records
        return self.data_record_manager.query_data_records_by_id(
            layer.data_type_config.data_type_name, record_id_list).result_list

    def _get_consumable_type_and_lot_for_data_type(self, name: str) -> Tuple[Optional[str], Optional[str]]:
        data_field_definitions: List[AbstractVeloxFieldDefinition] = self.data_type_manager.get_field_definition_list(
            name)
        for definition in data_field_definitions:
            field_tag = definition.tag
            if "<!-- MATERIALS MANAGEMENT: TYPE -->" in field_tag:
                consumable_type_record_field = definition.get_data_field_name()
                break
        else:
            # no consumable type field found, return early
            return None, None
        for definition in data_field_definitions:
            field_tag = definition.tag
            # check that this is not a double, as the Quantity field appears to use the same tag
            if definition.data_field_type != FieldType.DOUBLE and \
                    "<!-- MATERIALS MANAGEMENT: LOT -->" in field_tag:
                consumable_lot_record_field = definition.get_data_field_name()
                break
        else:
            # no consumable type field found, return early
            return None, None
        return consumable_type_record_field, consumable_lot_record_field

    def _get_consumable_type_and_lot_for_eln_type(self, consumable_step: ElnEntryStep) -> \
            Tuple[Optional[str], Optional[str]]:
        field_definitions: List[AbstractVeloxFieldDefinition] = self.eln_manager.get_experiment_entry(
            self.protocol.get_id(),
            consumable_step.get_id(), True).field_definition_list
        for definition in field_definitions:
            field_tag = definition.tag
            if "CONSUMABLE TYPES LIST WITH IGNORABLE VALUES" in field_tag:
                consumable_type_field = definition.get_data_field_name()
                break
        else:
            # no type found, return early
            return None, None

        for definition in field_definitions:
            field_tag = definition.tag
            # check that this is not a double, as the Quantity field appears to use the same tag
            if definition.data_field_type != FieldType.DOUBLE and \
                    ("CONSUMABLE TRACKING MAP TO " + consumable_type_field) in field_tag:
                consumable_lot_field = definition.get_data_field_name()
                break
        else:
            # no lot found, return None
            return None, None
        return consumable_lot_field, consumable_type_field


class _PlateRecordTracker:
    plates: Iterator[DataRecord]
    records: List[DataRecord]
    plate_config: MultiLayerPlateConfig
    layer_config: MultiLayerPlateLayer
    number_of_replicates: int
    restart_on_next_item: bool
    create_first_plate: bool
    repeat_until_all_plates: bool

    current_replicate_count: int
    current_record_index: int
    current_record: Optional[DataRecord]
    previous_record: Optional[DataRecord]
    user: User
    dataRecordManager: DataRecordManager

    def __init__(self, plates: List[DataRecord], records: List[DataRecord], plate_config: MultiLayerPlateConfig,
                 layer_config: MultiLayerPlateLayer, user: User):
        self.plates = iter(plates)
        self.records = records
        self.plate_config = plate_config
        self.layer_config = layer_config
        self.number_of_replicates = layer_config.replicate_config.number_of_replicates
        self.restart_on_next_item = layer_config.replicate_config.restart_on_next_item
        self.repeat_until_all_plates = layer_config.replicate_config.repeat_until_all_plates

        self.current_replicate_count = 0
        self.current_record_index = 0
        self.current_record = records[0]
        self.previous_record = None

        self.user = user
        self.dataRecordManager = DataMgmtServer.get_data_record_manager(user)

        if len(plates) == 0:
            self.create_first_plate = True
        else:
            self.create_first_plate = False

    def get_next_record(self) -> DataRecord:
        self.previous_record = self.current_record
        if self.current_replicate_count == self.number_of_replicates:
            self.current_replicate_count = 1
            self.current_record_index += 1
            if self.current_record_index >= len(self.records):
                # we have reached the end of our records
                if not self.repeat_until_all_plates:
                    # if not repeating, return None
                    self.current_record = None
                else:
                    # otherwise, restart the counters
                    self.current_record_index = 0
                    self.current_record = self.records[self.current_record_index]
            else:
                self.current_record = self.records[self.current_record_index]
        else:
            self.current_replicate_count += 1

        return self.current_record

    def backspace(self) -> None:
        self.current_replicate_count -= 1

    def is_different_record(self) -> bool:
        return (self.previous_record != self.current_record) and self.previous_record is not None

    def get_next_plate(self) -> DataRecord:
        next_plate = next(self.plates, None)
        # create a plate if we are out of plates, we are allowed to overflow, and this layer is not set to repeat for
        # all current plates
        if (next_plate is None and self.plate_config.overflow_to_new_plate and not self.repeat_until_all_plates) \
                or self.create_first_plate:
            self.create_first_plate = False
            return self.create_plate(self.plate_config)
        else:
            return next_plate

    """
       Create a new plate based on the plate config
       """

    def create_plate(self, config: MultiLayerPlateConfig) -> DataRecord:
        plate: DataRecord = self.dataRecordManager.add_data_record('Plate')
        plate.set_field_value('PlateRows', config.plate_rows)
        plate.set_field_value('PlateColumns', config.plate_cols)

        return plate

    def has_more_records(self) -> bool:
        # if repeat is on, we will always have more records
        if self.repeat_until_all_plates:
            return True
        # initialization state, return true
        if self.current_record_index == 0 and self.current_replicate_count == 0:
            return len(self.records) > 0
        # the get_next_records has already checked and pulled None
        if self.current_record is None:
            return False
        # the next time get_next_records is called, it will return None
        if (self.current_record_index + 1) <= len(
                self.records) and self.current_replicate_count == self.number_of_replicates:
            return False
        return True
