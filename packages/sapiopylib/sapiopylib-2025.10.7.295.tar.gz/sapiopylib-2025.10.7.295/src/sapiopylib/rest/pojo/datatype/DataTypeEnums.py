from enum import Enum


class ViewDetailsType(Enum):
    """
    Different pojo subclasses for View Details, used for JSON conversion into concrete subclasses.
    """
    CALENDAR = 0
    FORM_CYCLER = 1
    KANBAN = 2


class DisplayType(Enum):
    """
    Representing the different ways a list of records or search results can be displayed to the user in a component.
    """
    Table = 'Table'
    FormCycler = 'Form Cycler'
    IdvCycler = 'IDV Cycler'
    Tile = 'Tile'
    AttachmentCycler = 'Attachment Cycler'
    Kanban = 'Kanban'
    Calendar = 'Calendar'

    display_name: str

    def __init__(self, display_name: str):
        self.display_name = display_name

class PreviewDisplayType(Enum):
    """
    How shall preview display content be resized.
    """
    CONTAIN = "Fit Image", "contain"
    COVER = "Center Scale Image", "cover"
    INITIAL = "Natural Image Size", "initial"

    display_name: str
    css: str

    def __init__(self, display_name: str, css: str):
        self.display_name = display_name
        self.css = css


class DataTypeLayoutComponentTypes(Enum):
    """
    Enum class containing all possible layout components that can be used in webservices.
    """
    FORM_COMPONENT = 0
    TAB_COMPONENT = 1
    ATTACHMENT_PREVIEW_COMPONENT = 2
    CLIENT_PLUGIN_COMPONENT = 3
    TEMP_DATA_COMPONENT = 4
    DASHBOARD_COMPONENT = 5
    PROCESS_VIEW_COMPONENT = 6
    CALENDAR_COMPONENT = 7
    FEED_COMPONENT = 8
    NEWS_FEED_COMPONENT = 9
    HIERARCHY_COMPONENT = 10
    RELATED_RECORDS_COMPONENT = 11
    SEARCH_COMPONENT = 12
    RELATED_NOTEBOOK_EXPERIMENTS = 13
    RECORD_IMAGE_COMPONENT = 14
    RELATED_SIDE_LINK_COMPONENT = 15


class AggregationType(Enum):
    """
    The types of aggregation that can be done in a Kanban view.
    """
    Total = True
    Average = True
    Minimum = True
    Maximum = True
    Count = False

    is_field_required: bool

    def __init__(self, is_field_required: bool):
        self.is_field_required = is_field_required


class RecordImagePlacement(Enum):
    """
    Specifies how the record's image should be displayed in the form cycler.
    """
    NONE = 0, 'No Image'
    LEFT = 1, 'Left Image'
    RIGHT = 2, 'Right Image'

    placement_id: int
    display_name: str

    def __init__(self, placement_id: int, display_name: str):
        self.placement_id = placement_id
        self.display_name = display_name


class ComponentRelationType(Enum):
    """
    How data of this component is related to the current record.
    """
    Child = 1
    Parent = 2
    Descendant = 3
    Ancestor = 4


class PreviewDisplayType(Enum):
    """
    How shall (attachment) preview display content be resized.
    """
    CONTAIN = "Fit Image", "contain"
    COVER = "Center Scale Image", "cover"
    INITIAL = "Natural Image Size", "initial"

    display_name: str
    css_Value: str

    def __init__(self, display_name: str, css_value: str):
        self.display_name = display_name
        self.css_Value = css_value


class CalendarDataSourceType(Enum):
    """
    Enum that represents the different types of data source that can back the calendar.
    """
    REPORT = "Search"
    ALL_RECS_OF_TYPE = "All Records of Type"

    text: str

    def __init__(self, text: str):
        self.text = text


class CalendarView(Enum):
    """
    Enum representing the different types of calendar views.
    """
    MONTH = 0
    WEEK = 1
    DAY = 2
    LIST_DAY = 3
    LIST_WEEK = 4
