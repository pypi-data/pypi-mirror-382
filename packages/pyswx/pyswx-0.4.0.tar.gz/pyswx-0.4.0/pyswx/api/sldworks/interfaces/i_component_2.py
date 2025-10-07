"""
IComponent2 Interface Members

Reference:
https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2_members.html

Status: 🔴
"""

from pathlib import Path
from typing import TYPE_CHECKING
from typing import List

from pythoncom import VT_ARRAY
from pythoncom import VT_BOOL
from pythoncom import VT_BSTR
from pythoncom import VT_DISPATCH
from pythoncom import VT_I4
from pythoncom import VT_NULL
from pythoncom import VT_R8
from win32com.client import VARIANT

from pyswx.api.base_interface import BaseInterface
from pyswx.api.sldworks.interfaces.i_custom_property_manager import ICustomPropertyManager
from pyswx.api.sldworks.interfaces.i_enum_bodies_2 import IEnumBodies2
from pyswx.api.sldworks.interfaces.i_math_transform import IMathTransform
from pyswx.api.swconst.enumerations import SWBodyTypeE
from pyswx.api.swconst.enumerations import SWComponentSolvingOptionE
from pyswx.api.swconst.enumerations import SWComponentSuppressionStateE
from pyswx.api.swconst.enumerations import SWDocumentTypesE
from pyswx.api.swconst.enumerations import SWInConfigurationOptsE

if TYPE_CHECKING:
    from pyswx.api.sldworks.interfaces.i_model_doc_2 import IModelDoc2


class IComponent2(BaseInterface):
    def __init__(self, com_object):
        super().__init__()
        self.com_object = com_object

    def __repr__(self) -> str:
        return f"IComponent2({self.com_object})"

    @property
    def component_reference(self) -> str:
        """
        Gets the component reference for this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~ComponentReference.html
        """
        return self.com_object.ComponentReference

    @component_reference.setter
    def component_reference(self, value: str):
        self.com_object.ComponentReference = value

    def custom_property_manager(self, config_name: str) -> ICustomPropertyManager:
        """
        Gets the custom property information for this configuration.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~CustomPropertyManager.html

        Note:
        In the api definition this is a property, but in the python implementation it is a method, because python
        does not support properties with parameters. The parameter is the configuration name.
        """
        return ICustomPropertyManager(self.com_object.CustomPropertyManager(config_name))

    @property
    def display_title(self) -> str:
        """
        Gets the display title of this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~DisplayTitle.html
        """
        return self.com_object.DisplayTitle

    @display_title.setter
    def display_title(self, value: str):
        self.com_object.DisplayTitle = value

    @property
    def i_material_property_values(self) -> List[float]:
        """
        Gets the material property values for this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~IMaterialPropertyValues.html
        """
        com_object = self.com_object.IMaterialPropertyValues
        return [float(i) for i in com_object]

    @i_material_property_values.setter
    def i_material_property_values(self, values: List[float]) -> None:
        in_values = VARIANT(VT_ARRAY | VT_R8, values)
        self.com_object.IMaterialPropertyValues = in_values

    @property
    def is_graphics_only(self) -> bool:
        """
        Gets whether this component is graphics only.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~IsGraphicsOnly.html
        """
        return bool(self.com_object.IsGraphicsOnly)

    @is_graphics_only.setter
    def is_graphics_only(self, value: bool) -> None:
        in_value = VARIANT(VT_BOOL, value)
        self.com_object.IsGraphicsOnly = in_value

    @property
    def is_speedpak(self) -> bool:
        """
        Gets whether this component is SpeedPak.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~IsSpeedPak.html
        """
        return bool(self.com_object.IsSpeedPak)

    @is_speedpak.setter
    def is_speedpak(self, value: bool) -> None:
        in_value = VARIANT(VT_BOOL, value)
        self.com_object.IsSpeedPak = in_value

    @property
    def is_virtual(self) -> bool:
        """
        Gets whether this component is a virtual component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~IsVirtual.html
        """
        return bool(self.com_object.IsVirtual)

    @property
    def material_property_values(self) -> List[float] | None:
        """
        Gets the material property values for this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~MaterialPropertyValues.html
        """
        com_object = self.com_object.MaterialPropertyValues
        if com_object is None:
            return None
        return [float(i) for i in com_object]

    @material_property_values.setter
    def material_property_values(self, values: List[float]) -> None:
        in_values = VARIANT(VT_ARRAY | VT_R8, values)
        self.com_object.MaterialPropertyValues = in_values

    @property
    def name2(self) -> str:
        """
        Gets the name of this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~Name2.html
        """
        return self.com_object.Name2

    @name2.setter
    def name2(self, value: str):
        self.com_object.Name2 = value

    @property
    def presentation_transform(self) -> IMathTransform:
        """
        Gets or sets the component transform.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~PresentationTransform.html
        """
        com_object = self.com_object.PresentationTransform
        return IMathTransform(com_object)

    @presentation_transform.setter
    def presentation_transform(self, value: IMathTransform) -> None:
        in_value = VARIANT(VT_DISPATCH, value.com_object)
        self.com_object.PresentationTransform = in_value

    @property
    def referenced_configuration(self) -> str:
        """
        Gets or sets the active configuration used by this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~ReferencedConfiguration.html
        """
        return self.com_object.ReferencedConfiguration

    @referenced_configuration.setter
    def referenced_configuration(self, value: str) -> None:
        self.com_object.referenced_configuration = value

    @property
    def referenced_display_state2(self) -> str:
        """
        Gets or sets the active display state of this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~ReferencedDisplayState2.html
        """
        return self.com_object.ReferencedDisplayState2

    @referenced_display_state2.setter
    def referenced_display_state2(self, value: str) -> None:
        self.com_object.ReferencedDisplayState2 = value

    @property
    def solving(self) -> SWComponentSolvingOptionE | int:
        """
        Gets the Solve as option (rigid or flexible) of this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~Solving.html
        """
        com_object = self.com_object.Solving
        if isinstance(com_object, int):
            return com_object
        return SWComponentSolvingOptionE(com_object)

    @solving.setter
    def solving(self, value: SWComponentSolvingOptionE) -> None:
        in_value = VARIANT(VT_I4, value.value)
        self.com_object.Solving = in_value

    @property
    def transform2(self) -> IMathTransform:
        """
        Gets or sets the component transform.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~Transform2.html
        """
        com_object = self.com_object.Transform2
        return IMathTransform(com_object)

    @transform2.setter
    def transform2(self, value: IMathTransform) -> None:
        in_value = VARIANT(VT_DISPATCH, value.com_object)
        self.com_object.Transform2 = in_value

    @property
    def use_named_configuration(self) -> bool:
        """
        Gets whether a specified configuration or the in-use/last active configuration is used.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~UseNamedConfiguration.html
        """
        return bool(self.com_object.UseNamedConfiguration)

    @use_named_configuration.setter
    def use_named_configuration(self, value: bool) -> None:
        in_value = VARIANT(VT_BOOL, value)
        self.com_object.UseNamedConfiguration = in_value

    @property
    def visible(self) -> bool:
        """
        Gets or sets the visibility state of this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~Visible.html
        """
        return bool(self.com_object.Visible)

    @visible.setter
    def visible(self, value: bool) -> None:
        in_value = VARIANT(VT_BOOL, value)
        self.com_object.Visible = in_value

    def add_property_extension(self, property_extension: int | float | str) -> int:
        """
        Adds a property extension to this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~AddPropertyExtension.html
        """
        in_property_extension = VARIANT(VT_I4 | VT_R8 | VT_BSTR, property_extension)
        com_object = self.com_object.AddPropertyExtension(in_property_extension)
        return int(com_object)

    def de_select(self) -> bool:
        """
        Deselects this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~DeSelect.html
        """
        return bool(self.com_object.DeSelect)

    def enum_bodies3(self, body_type: SWBodyTypeE, visible_only: bool) -> IEnumBodies2:
        """
        Gets the bodies in the component in a multibody part.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~EnumBodies3.html
        """
        in_body_type = VARIANT(VT_I4, body_type.value)
        in_visible_only = VARIANT(VT_BOOL, visible_only)

        com_object = self.com_object.EnumBodies3(in_body_type, in_visible_only)
        return IEnumBodies2(com_object)

    def get_children(self) -> List["IComponent2"]:
        """
        Gets all of the children components of this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~GetChildren.html
        """
        com_object = self.com_object.GetChildren
        return [IComponent2(i) for i in com_object]

    def get_exclude_from_bom2(self, config_opt: SWInConfigurationOptsE, config_names: List[str] | None) -> List[bool]:
        """
        Gets whether this component is excluded from the bills of materials (BOMs) in the specified configurations.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~GetExcludeFromBOM2.html
        """
        in_config_opt = VARIANT(VT_I4, config_opt.value)
        in_config_names = (
            VARIANT(VT_BSTR | VT_ARRAY, [str(i) for i in config_names]) if config_names else VARIANT(VT_NULL, None)
        )

        com_object = self.com_object.GetExcludeFromBOM2(in_config_opt, in_config_names)
        return [bool(i) for i in com_object]

    def get_id(self) -> int:
        """
        Gets the component ID for this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~GetID.html
        """
        return int(self.com_object.GetID)

    def get_model_doc2(self) -> "IModelDoc2 | None":
        """
        Gets the model document for this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~GetModelDoc2.html
        """
        from pyswx.api.sldworks.interfaces.i_model_doc_2 import IModelDoc2

        com_object = self.com_object.GetModelDoc2
        return IModelDoc2(com_object) if com_object else None

    def get_parent(self) -> "IComponent2 | None":
        """
        Gets the parent component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~GetParent.html
        """
        com_object = self.com_object.GetParent
        return IComponent2(com_object) if com_object else None

    def get_path_name(self) -> Path:
        """
        Gets the full path name for this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~GetPathName.html
        """
        return Path(self.com_object.GetPathName)

    def get_suppression2(self) -> SWComponentSuppressionStateE:
        """
        Gets the suppression state of this component.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~GetSuppression2.html
        """
        return SWComponentSuppressionStateE(self.com_object.GetSuppression2)

    def get_type(self) -> SWDocumentTypesE:
        """
        Gets this lightweight assembly component's document type.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~GetType.html
        """
        return SWDocumentTypesE(self.com_object.GetType)

    def is_envelope(self) -> bool:
        """
        Gets whether this component is an envelope.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/solidworks.interop.sldworks~solidworks.interop.sldworks.icomponent2~isenvelope.html
        """
        return bool(self.com_object.IsEnvelope)

    def is_hidden(self, consider_suppressed: bool) -> bool:
        """
        Gets whether this component is hidden or suppressed.

        Reference:
        https://help.solidworks.com/2024/english/api/sldworksapi/solidworks.interop.sldworks~solidworks.interop.sldworks.icomponent2~ishidden.html
        """
        in_consider_suppressed = VARIANT(VT_BOOL, consider_suppressed)
        return bool(self.com_object.IsHidden(in_consider_suppressed))
