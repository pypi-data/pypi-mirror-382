# KiCadFiles - Python Library for KiCad File Formats

A comprehensive Python library for parsing and manipulating KiCad file formats with complete S-expression and JSON token support.

## File Organization

### advanced_graphics.py - Complex Graphics Objects

```python
dimension              -> advanced_graphics.Dimension
format                 -> advanced_graphics.Format
fp_arc                 -> advanced_graphics.FpArc
fp_circle              -> advanced_graphics.FpCircle
fp_curve               -> advanced_graphics.FpCurve
fp_line                -> advanced_graphics.FpLine
fp_poly                -> advanced_graphics.FpPoly
fp_rect                -> advanced_graphics.FpRect
fp_text                -> advanced_graphics.FpText
at                     -> advanced_graphics.FpTextAt
fp_text_box            -> advanced_graphics.FpTextBox
gr_arc                 -> advanced_graphics.GrArc
gr_bbox                -> advanced_graphics.GrBbox
gr_circle              -> advanced_graphics.GrCircle
gr_curve               -> advanced_graphics.GrCurve
gr_line                -> advanced_graphics.GrLine
gr_poly                -> advanced_graphics.GrPoly
gr_rect                -> advanced_graphics.GrRect
gr_text                -> advanced_graphics.GrText
gr_text_box            -> advanced_graphics.GrTextBox
```

### base_element.py - Base Classes

```python
field_info             -> base_element.FieldInfo
field_type             -> base_element.FieldType
kicad_object           -> base_element.NamedObject
optional_flag          -> base_element.TokenFlag
parse_cursor           -> base_element.ParseCursor
parse_strictness       -> base_element.ParseStrictness
token_preference       -> base_element.TokenPreference
```

### base_types.py - Fundamental Types

```python
anchor                 -> base_types.Anchor
at                     -> base_types.At
at                     -> base_types.AtXY
layers                 -> base_types.BoardLayers
center                 -> base_types.Center
color                  -> base_types.Color
effects                -> base_types.Effects
end                    -> base_types.End
fill                   -> base_types.Fill
font                   -> base_types.Font
justify                -> base_types.Justify
layer                  -> base_types.Layer
layers                 -> base_types.Layers
mid                    -> base_types.Mid
                       -> base_types.NamedObject            # Base class
offset                 -> base_types.Offset
pos                    -> base_types.Pos
property               -> base_types.Property
pts                    -> base_types.Pts
size                   -> base_types.Size
start                  -> base_types.Start
stroke                 -> base_types.Stroke
text                   -> base_types.Text
type                   -> base_types.Type
uuid                   -> base_types.Uuid
xy                     -> base_types.Xy
xyz                    -> base_types.Xyz
```

### board_layout.py - PCB Board Design

```python
arc                    -> board_layout.BoardArc
footprint              -> board_layout.Footprint
general                -> board_layout.General
group                  -> board_layout.Group
kicad_pcb              -> board_layout.KicadPcb
net                    -> board_layout.Net
nets                   -> board_layout.Nets
pcbplotparams          -> board_layout.PcbPlotParams
private_layers         -> board_layout.PrivateLayers
segment                -> board_layout.Segment
setup                  -> board_layout.Setup
stackup                -> board_layout.Stackup
layer                  -> board_layout.StackupLayer
tenting                -> board_layout.Tenting
tracks                 -> board_layout.Tracks
via                    -> board_layout.Via
vias                   -> board_layout.Vias
zone                   -> board_layout.Zone
```

### design_rules.py - Design Rule Check Definitions

```python
max                    -> design_rules.ConstraintMax
min                    -> design_rules.ConstraintMin
opt                    -> design_rules.ConstraintOpt
rule                   -> design_rules.DesignRule
condition              -> design_rules.DesignRuleCondition
constraint             -> design_rules.DesignRuleConstraint
layer                  -> design_rules.DesignRuleLayer
priority               -> design_rules.DesignRulePriority
severity               -> design_rules.DesignRuleSeverity
kicad_dru              -> design_rules.KiCadDesignRules
```

### enums.py - Common Enumeration Types

```python
clearance_type         -> enums.ClearanceType
constraint_type        -> enums.ConstraintType
fill_type              -> enums.FillType
footprint_text_type    -> enums.FootprintTextType
hatch_style            -> enums.HatchStyle
justify_horizontal     -> enums.JustifyHorizontal
justify_vertical       -> enums.JustifyVertical
label_shape            -> enums.LabelShape
layer_type             -> enums.LayerType
pad_shape              -> enums.PadShape
pad_type               -> enums.PadType
pin_electrical_type    -> enums.PinElectricalType
pin_graphic_style      -> enums.PinGraphicStyle
severity_level         -> enums.SeverityLevel
smoothing_style        -> enums.SmoothingStyle
stroke_type            -> enums.StrokeType
via_type               -> enums.ViaType
zone_connection        -> enums.ZoneConnection
zone_fill_mode         -> enums.ZoneFillMode
zone_keepout_setting   -> enums.ZoneKeepoutSetting
```

### footprint_library.py - Footprint Management

```python
attr                   -> footprint_library.Attr
file                   -> footprint_library.EmbeddedFile
embedded_files         -> footprint_library.EmbeddedFiles
data                   -> footprint_library.FileData
footprints             -> footprint_library.Footprints
model                  -> footprint_library.Model
at                     -> footprint_library.ModelAt
offset                 -> footprint_library.ModelOffset
rotate                 -> footprint_library.ModelRotate
scale                  -> footprint_library.ModelScale
net_tie_pad_groups     -> footprint_library.NetTiePadGroups
```

### json_base_element.py - JSON Base Classes

```python
json_object            -> json_base_element.JsonObject
```

### library_tables.py - Library Table Management

```python
fp_lib_table           -> library_tables.FpLibTable
lib                    -> library_tables.LibraryEntry
sym_lib_table          -> library_tables.SymLibTable
```

### pad_and_drill.py - Pad and Drill Elements

```python
chamfer                -> pad_and_drill.Chamfer
drill                  -> pad_and_drill.Drill
net                    -> pad_and_drill.Net
options                -> pad_and_drill.Options
pad                    -> pad_and_drill.Pad
pads                   -> pad_and_drill.Pads
primitives             -> pad_and_drill.Primitives
shape                  -> pad_and_drill.Shape
teardrops              -> pad_and_drill.Teardrops
zone_connect           -> pad_and_drill.ZoneConnect
```

### primitive_graphics.py - Basic Graphics Primitives

```python
arc                    -> primitive_graphics.Arc
bezier                 -> primitive_graphics.Bezier
circle                 -> primitive_graphics.Circle
line                   -> primitive_graphics.Line
polygon                -> primitive_graphics.Polygon
polyline               -> primitive_graphics.Polyline
rect                   -> primitive_graphics.Rect
rectangle              -> primitive_graphics.Rectangle
```

### project_settings.py - JSON Project Settings

```python
board_defaults         -> project_settings.BoardDefaults
board_settings         -> project_settings.BoardSettings
cvpcb_settings         -> project_settings.CvpcbSettings
design_settings        -> project_settings.DesignSettings
erc_settings           -> project_settings.ERCSettings
ipc2581_settings       -> project_settings.IPC2581Settings
kicad_project          -> project_settings.KicadProject
library_settings       -> project_settings.LibrarySettings
net_class              -> project_settings.NetClass
net_settings           -> project_settings.NetSettings
pcbnew_settings        -> project_settings.PcbnewSettings
project_meta           -> project_settings.ProjectMeta
schematic_bom_settings -> project_settings.SchematicBOMSettings
schematic_settings     -> project_settings.SchematicSettings
```

### schematic_system.py - Schematic Drawing

```python
bus                    -> schematic_system.Bus
bus_entry              -> schematic_system.BusEntry
cells                  -> schematic_system.Cells
column_widths          -> schematic_system.ColumnWidths
global_label           -> schematic_system.GlobalLabel
hierarchical_label     -> schematic_system.HierarchicalLabel
junction               -> schematic_system.Junction
kicad_sch              -> schematic_system.KicadSch
label                  -> schematic_system.Label
netclass_flag          -> schematic_system.NetclassFlag
no_connect             -> schematic_system.NoConnect
path                   -> schematic_system.Path
pin                    -> schematic_system.PinRef
project                -> schematic_system.Project
row_heights            -> schematic_system.RowHeights
rule_area              -> schematic_system.RuleArea
symbol                 -> schematic_system.SchematicSymbol
sheet                  -> schematic_system.Sheet
path                   -> schematic_system.SheetInstance
sheet_instances        -> schematic_system.SheetInstances
instances              -> schematic_system.SheetLocalInstances
pin                    -> schematic_system.SheetPin
instances              -> schematic_system.SymbolInstances
table                  -> schematic_system.Table
border                 -> schematic_system.TableBorder
table_cell             -> schematic_system.TableCell
margins                -> schematic_system.TableMargins
separators             -> schematic_system.TableSeparators
span                   -> schematic_system.TableSpan
wire                   -> schematic_system.Wire
```

### symbol_library.py - Symbol Management

```python
arc                    -> symbol_library.Arc
bezier                 -> symbol_library.Bezier
circle                 -> symbol_library.Circle
instances              -> symbol_library.Instances
kicad_symbol_lib       -> symbol_library.KicadSymbolLib
lib_symbols            -> symbol_library.LibSymbols
line                   -> symbol_library.Line
number                 -> symbol_library.Number
pin                    -> symbol_library.Pin
name                   -> symbol_library.PinName
pin_names              -> symbol_library.PinNames
pin_numbers            -> symbol_library.PinNumbers
pintype                -> symbol_library.Pintype
polygon                -> symbol_library.Polygon
polyline               -> symbol_library.Polyline
rectangle              -> symbol_library.Rectangle
symbol                 -> symbol_library.Symbol
```

### text_and_documents.py - Text and Document Elements

```python
bitmap                 -> text_and_documents.Bitmap
comment                -> text_and_documents.Comment
data                   -> text_and_documents.Data
image                  -> text_and_documents.Image
kicad_wks              -> text_and_documents.KicadWks
members                -> text_and_documents.Members
paper                  -> text_and_documents.Paper
pngdata                -> text_and_documents.Pngdata
tbtext                 -> text_and_documents.Tbtext
textsize               -> text_and_documents.Textsize
title_block            -> text_and_documents.TitleBlock
line                   -> text_and_documents.WksLine
rect                   -> text_and_documents.WksRect
setup                  -> text_and_documents.WksSetup
tbtext                 -> text_and_documents.WksTbText
textsize               -> text_and_documents.WksTextsize
```

### zone_system.py - Zone and Copper Filling

```python
connect_pads           -> zone_system.ConnectPads
copperpour             -> zone_system.Copperpour
fill_segments          -> zone_system.FillSegments
filled_polygon         -> zone_system.FilledPolygon
filled_segments        -> zone_system.FilledSegments
hatch                  -> zone_system.Hatch
hatch_orientation      -> zone_system.HatchOrientation
keepout                -> zone_system.Keepout
mode                   -> zone_system.Mode
smoothing              -> zone_system.Smoothing
fill                   -> zone_system.ZoneFill
```

## Class Naming Convention

Each S-expression token gets a corresponding class with the pattern:

- Token name in lowercase -> CamelCase ClassName
- Examples: `at`       -> `At`, `fp_line`              -> `FpLine`, `zone_connect`         -> `ZoneConnect`

## Implementation Notes

1. **Dependency-Based Structure**: Classes organized by dependencies to eliminate TYPE_CHECKING
2. **Nested Elements**: When tokens contain other tokens, they reference classes from appropriate modules
3. **File Organization**: Tokens grouped by functional area and dependency level
4. **Inheritance**: All classes inherit from a base `NamedObject` class

## Class Implementation Specification

### Standard Pattern

```python
from dataclasses import dataclass, field
from typing import Optional

from .base_element import NamedObject
from .enums import SomeEnum  # Import required enums
from . import other_module   # Import other modules as needed

@dataclass
class ClassName(NamedObject):
    """S-expression token description.

    The 'token_name' token defines... in the format::

        (token_name PARAM1 [OPTIONAL_PARAM])

    Args:
        param1: Description of required parameter
        optional_param: Description of optional parameter
    """
    __token_name__: ClassVar[str] = "token_name"

    # Follow exact documentation order
    param1: type = field(default=default_value, metadata={"description": "Description"})
    optional_param: Optional[type] = field(default=None, metadata={"description": "Description", "required": False})
```

### Implementation Rules

**Types & Defaults:**

- Basic: `str`, `int`, `float`, `bool` with defaults `""`, `0`, `0.0`, `False`
- Optional: `Optional[type]` with `default=None` and `metadata={"required": False}`
- Nested Objects: Use `default_factory=lambda: ClassName()` for required nested objects
- Enums: Direct enum values as defaults (e.g., `default=PadShape.RECT`)
- Lists: `List[module.Type]` with `default_factory=list` or `None` for optional

**Field Order (CRITICAL):**

- Must follow exact KiCad documentation parameter order
- If required primitives after optional fields: add `# TODO: Fix field order`

**Metadata & Documentation:**

- All fields need `metadata={"description": "..."}`
- Optional fields add `"required": False`
- Docstrings: PEP 257/287 compliant with Sphinx format
- Use `Args:` section (no `Attributes:` - dataclass fields are self-documenting)
- Code blocks with `::` for S-expression format examples

### Example: Field Order Conflicts

```python
@dataclass
class Example(NamedObject):
    """Token with field order conflict - follows documentation order.

    Note:
        Field order follows KiCad documentation, not dataclass conventions.
        Required fields after optional fields violate dataclass ordering.

    Args:
        optional1: First parameter (optional)
        required_str: Required parameter after optional
        optional2: Last parameter (optional)
    """
    __token_name__: ClassVar[str] = "example"

    optional1: Optional[str] = field(default=None, metadata={"description": "First param", "required": False})
    required_str: str = field(default="", metadata={"description": "Required after optional"})  # TODO: Fix field order
    optional2: Optional[int] = field(default=None, metadata={"description": "Last param", "required": False})
```

### Example: Complete Implementation

```python
from dataclasses import dataclass, field
from typing import Optional

from .base_element import NamedObject
from .enums import StrokeType

@dataclass
class Stroke(NamedObject):
    """Stroke definition token.

    The 'stroke' token defines how the outlines of graphical objects are drawn in the format:
    (stroke
        (width WIDTH)
        (type TYPE)
        (color R G B A)
    )

    This represents the nested structure exactly as it appears in the S-expression files.

    Args:
        width: Line width specification
        type: Stroke line style specification
        color: Line color specification (optional)
    """

    __token_name__: ClassVar[str] = "stroke"

    width: NamedFloat = field(
        default_factory=lambda: NamedFloat("width", 0.0),
        metadata={"description": "Line width specification"},
    )
    type: Type = field(
        default_factory=lambda: Type(value=StrokeType.SOLID.value),
        metadata={"description": "Stroke line style specification"},
    )
    color: Color = field(
        default_factory=lambda: Color(),
        metadata={"description": "Line color specification", "required": False},
    )
```

## Core Principles

1. **Mirror S-expression structure exactly** - nested tokens become nested objects
2. **Follow KiCad documentation parameter order** - mark dataclass conflicts with TODO
3. **Type safety** - explicit types, metadata, `mypy --strict` compatible
4. **Consistent naming** - `snake_case` → `PascalCase`, exact field names, `__token_name__`
