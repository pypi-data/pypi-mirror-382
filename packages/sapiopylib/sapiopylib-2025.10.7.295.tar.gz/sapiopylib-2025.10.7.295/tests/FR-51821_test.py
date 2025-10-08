import unittest

from sapiopylib.rest.pojo.datatype.DataTypeEnums import PreviewDisplayType, ComponentRelationType

from sapiopylib.rest.pojo.datatype.DataTypeComponent import HierarchyComponent, RecordImageComponent, \
    RelatedSideLinkLayoutComponent, RelatedRecordLayoutComponent

from sapiopylib.rest.DataTypeService import DataTypeManager

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.utils.autopaging import *

# Assume we have two data types
# F51821Test and F51821Test2
# F51821Test2 has a side link field to F51821Test
# F51821Test layout has:
# a hierarchy component called "Hierarchy Test" with data types to show = ["Directory"]
# a component "Side Link Test" reverse links of "F51821Test2" data type
# a record image component "Image Test" with size attribute "Default Size"
# a linked parent "Directory" component
# This must be created in data designer before test begins.

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
dt_man: DataTypeManager = DataMgmtServer.get_data_type_manager(user)

class FR51821Test(unittest.TestCase):
    def test_layouts(self):
        layout = next(dt_man.get_data_type_layout_list("F51821Test").__iter__())
        hierarchy_component: HierarchyComponent = layout.get_data_type_layout_component("Hierarchy Test")
        self.assertEqual(hierarchy_component.hierarchy_node_data_types, ["Directory"])
        image_component: RecordImageComponent = layout.get_data_type_layout_component("Image Test")
        self.assertEqual(image_component.preview_display_type, PreviewDisplayType.INITIAL)
        side_link_comp: RelatedSideLinkLayoutComponent = layout.get_data_type_layout_component("Side Link Test")
        self.assertEqual(side_link_comp.related_side_link_field_name, "SideLink")
        self.assertEqual(side_link_comp.related_data_type_name, "F51821Test2")
        parent_directory_comp: RelatedRecordLayoutComponent = layout.get_data_type_layout_component(
            "Directory")
        self.assertEqual(parent_directory_comp.related_data_type_name, "Directory")
        self.assertEqual(parent_directory_comp.component_relation_type, ComponentRelationType.Parent)
