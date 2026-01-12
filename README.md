# ASC Framing Decision List (FDL) - Python API

A Python library for creating, manipulating, and processing
[ASC Framing Decision Lists (FDLs)](https://theasc.com/society/ascmitc/asc-framing-decision-list). 
This implementation provides a high-level API for working with framing intents, canvas 
transformations, and framing decisions in professional video production workflows.

## About FDL

The **Framing Decision List (FDL)** specification is developed and maintained by the 
[American Society of Cinematographers (ASC)](https://theasc.com/). The FDL specification, 
concepts, and related intellectual property are owned by ASC.

This library provides an independent Python implementation of the FDL specification and is 
not officially affiliated with or endorsed by ASC unless explicitly stated.

## Features

- **Comprehensive FDL Support**: Full implementation of the [ASC FDL v2.0 specification](https://github.com/ascmitc/fdl/blob/main/Specification/ASCFDL_Specification_v2.0.pdf)
- **Type-Safe API**: Built with Pydantic v2 for robust validation and type checking
- **Framing Calculations**: Automatic computation such as framing geometry, anchor points, 
  protection regions, and more
- **Serialization**: Load and save FDL documents in standard JSON format
- **Validation**: Built-in uniqueness constraints and semantic validation for all FDL components
- **Canvas Template Processing**: Apply CanvasTemplate transformations to derive new canvases with
 proper dimension scaling and framing decision inheritance

## Installation

Install the ASC FDL Python library using pip:

```bash
pip install fdl-python
```

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Clone the repository
git clone https://github.com/eden-annn/fdl-python.git
cd fdl-python

# Install dependencies (including dev dependencies)
uv sync

# Run tests
uv run pytest
```

## Quick Start

### Creating an FDL from Scratch

```python
import fdl

# Initialize an FDL document
asc_fdl = fdl.AscFramingDecisionList(fdl_creator="ASC FDL Committee")

# Define a Framing Intent
framing_intent = fdl.FramingIntent(
    label="2:1 Framing",
    id=fdl.FdlId("FDLSMP01"),
    aspect_ratio=fdl.DimensionsInt(width=2, height=1),
    protection=0.05,  # 5% protection area
)

# Add Framing Intent to FDL document
asc_fdl.add_framing_intent(framing_intent)

# Create a Canvas representing your source media
canvas = fdl.Canvas(
    label="Open Gate Vignette",
    id=fdl.FdlId("20260101"),
    source_canvas_id=fdl.FdlId("20260101"),
    dimensions=fdl.DimensionsInt(width=4448, height=3096),
    anamorphic_squeeze=1.0
)

# Add Framing Decision to Canvas
framing_decision = canvas.add_framing_decision(framing_intent)

# Create a Context and add the Canvas
context = fdl.Context(
    label="ArriLF",
    context_creator="ASC FDL Committee",
    clip_id=fdl.ClipId(clip_name="A001_C001", file="A001_C001.ari"),
    canvases=[canvas]
)

# Add Context to FDL document
asc_fdl.add_context(context)

# Save to file
asc_fdl.to_file("output.fdl")
```

### Loading and Processing an Existing FDL

```python
import fdl

# Load an FDL document
asc_fdl = fdl.AscFramingDecisionList.from_file("input.fdl")

# Print full FDL structure
print(asc_fdl.to_json())

# Access framing intents
for framing_intent in asc_fdl.iter_framing_intents():
    print(f"FramingIntent: {framing_intent}")

# Access contexts and canvases
for context in asc_fdl.iter_contexts():
    print(f"Context: {context.label}")
    for canvas in context.iter_canvases():
        print(f"  Canvas: {canvas.label} - {canvas.dimensions}")
```

### Canvas Template Processing

Apply transformations to create derived canvases:

```python
import fdl

# Define a canvas template for VFX delivery
template = fdl.CanvasTemplate(
    label="VFX PULL",
    id=fdl.FdlId("VFXPULL"),
    target_dimensions=fdl.DimensionsInt(width=3840, height=2160),
    fit_source=fdl.FitSource.framing_decision_dimensions,
    fit_method=fdl.FitMethod.width,
    preserve_from_source_canvas=fdl.PreserveFromSourceCanvas.canvas_dimensions,
    maximum_dimensions=fdl.DimensionsInt(width=5000, height=2700),
    pad_to_maximum=True,
    round=fdl.Round(even=fdl.Even.even, mode=fdl.Mode.up),
)

# Create processor and derive new canvas
processor = fdl.CanvasTemplateProcessor(template)
new_canvas = processor.create_canvas(
    source_canvas=canvas,
    framing_decision_id=framing_decision.id
)

print(f"New canvas dimensions: {new_canvas.dimensions}")
print(f"Effective dimensions: {new_canvas.effective_dimensions}")
```

## Core Concepts

### FDL Document Structure

An FDL document consists of:

- **Framing Intents**: Target aspect ratios and delivery specifications
- **Contexts**: Groups of related canvases (e.g., per camera, per scene)
- **Canvases**: Representations of media with specific dimensions and framing decisions
- **Framing Decisions**: Computed geometry showing how intents map to canvases
- **Canvas Templates**: Transformation rules for deriving new canvases

### FDL Model Hierarchy

```
AscFramingDecisionList
├── framing_intents[]
├── contexts[]
│   └── canvases[]
│       └── framing_decisions[]
└── canvas_templates[]
```

### Framing Decision Calculation

When you add a framing decision to a canvas, the library automatically computes:

- **Dimensions**: The frame dimensions for the target aspect ratio
- **Anchor Point**: Position of the frame within the canvas
- **Protection Area**: Optional safe zone around the creative framing
- **Protection Anchor Point**: Position of the protection frame

### Canvas Template Processing

Canvas templates enable transformations like:

- **Fit Methods**: Width, height, fit-all, or fill
- **Source Selection**: Use canvas dimensions, effective dimensions, or framing decisions
- **Anamorphic Desqueeze**: Apply anamorphic desqueeze transformation after source selection
- **Preservation Rules**: Maintain canvas dimensions while fitting framing decisions
- **Maximum/Padding**: Enforce size limits and pad to fixed dimensions
- **Rounding**: Apply even/odd pixel constraints

The processor automatically:
- Selects source dimensions based on fit_source configuration
- Applies anamorphic desqueeze (if specified in template)
- Computes target dimensions and scale factors
- Rescales framing decisions (dimensions, anchors, protection)
- Calculates effective dimensions for padded outputs
- Applies rounding rules

## API Reference

### Core Classes

#### `AscFramingDecisionList`

Main FDL document class with convenience methods:

```python
# Creation and loading
fdl = AscFramingDecisionList()
fdl = AscFramingDecisionList.from_file("path.fdl")
fdl = AscFramingDecisionList.from_json(json_string)
fdl = AscFramingDecisionList.from_dict(dict_data)

# Adding components
fdl.add_context(context)
fdl.add_framing_intent(framing_intent)
fdl.add_canvas_template(template)

# Querying
framing_intent = fdl.get_framing_intent_by_id(id)
canvas = fdl.get_canvas_by_id(id, context=None)

# Iteration
for framing_intents in fdl.iter_framing_intents(): ...
for context in fdl.iter_contexts(): ...
for template in fdl.iter_canvas_templates(): ...

# Serialization
fdl.to_file("output.fdl", indent=2)
json_str = fdl.to_json(indent=2)
dict_data = fdl.to_dict()
```

#### `Canvas`

Represents a media canvas with dimensions and framing decisions:

```python
canvas = Canvas(
    label="My Canvas",
    id=FdlId("canvas_001"),
    source_canvas_id=FdlId("source_001"),
    dimensions=DimensionsInt(width=4096, height=2160),
    effective_dimensions=DimensionsInt(width=3840, height=2160),
    anamorphic_squeeze=1.0,
)

# Add framing decisions
framing_decision = canvas.add_framing_decision(framing_intent, label="Hero Frame")
```

**Important**: Canvas IDs must be unique within a context. Attempting to add duplicate IDs 
raises `ValueError`.

#### `FramingIntent`

Defines a target aspect ratio and delivery specification:

```python
intent = FramingIntent(
    label="16:9 HD",
    id=FdlId("HD_16x9"),
    aspect_ratio=DimensionsInt(width=16, height=9),
    protection=0.10,  # 10% protection border
)
```

**Important**: Framing intent IDs must be unique across the FDL document.

#### `Context`

Groups related canvases:

```python
context = Context(
    label="Camera A",
    context_creator="DIT Team",
    clip_id=ClipId(clip_name="A001_C001", file="A001_C001.MOV"),
    canvases=[canvas1, canvas2],
)

# Add canvases
context.add_canvas(canvas)

# Query canvases
canvas = context.get_canvas_by_id(canvas_id)
```

#### `CanvasTemplate`

Defines transformation rules:

```python
template = CanvasTemplate(
    label="UHD Deliverable",
    id=FdlId("UHD_TEMPLATE"),
    target_dimensions=DimensionsInt(width=3840, height=2160),
    fit_source=FitSource.framing_decision_dimensions,
    fit_method=FitMethod.width,
    preserve_from_source_canvas=PreserveFromSourceCanvas.none,
    round=Round(even=Even.even, mode=Mode.round),
)
```

**Fit Source Options**:
- `FitSource.framing_decision_dimensions`: Use a specific framing decision
- `FitSource.effective_dimensions`: Use canvas effective dimensions
- `FitSource.canvas_dimensions`: Use full canvas dimensions

**Fit Methods**:
- `FitMethod.width`: Scale to match target width
- `FitMethod.height`: Scale to match target height
- `FitMethod.fit_all`: Scale to fit entire source (letterbox/pillarbox)
- `FitMethod.fill`: Scale to fill target (crop source)

#### `CanvasTemplateProcessor`

Applies templates to generate derived canvases:

```python
processor = CanvasTemplateProcessor(template)

new_canvas = processor.create_canvas(
    source_canvas=canvas,
    framing_decision_id=FdlIdFramingDecision("canvas_001-intent_001"),
    new_canvas_id=FdlId("derived_001"),
    new_canvas_label="Derived Canvas",
)
```

The processor automatically:
- Computes target dimensions and scale
- Rescales all framing decisions
- Calculates effective dimensions when padding is applied
- Applies rounding rules

### Schema Types

Key data types from the FDL schema:

```python
# Identifiers
FdlId("unique_id")
FdlIdFramingDecision("canvas_id-intent_id")

# Dimensions
DimensionsInt(width=1920, height=1080)
DimensionsFloat(width=1920.5, height=1080.25)

# Points
PointFloat(x=960.0, y=540.0)

# Rounding
Round(even=Even.even, mode=Mode.up)
Round(even=Even.whole, mode=Mode.down)

# Enums
FitSource
FitMethod
PreserveFromSourceCanvas
Mode
Even
AlignmentMethodHorizontal
AlignmentMethodVertical
```

## Additional validations and implementations

### Validations

All models include validation respecting FDL guideline:

```python
# Duplicate canvas IDs raise ValueError
try:
    context.add_canvas(canvas_with_duplicate_id)
except ValueError as e:
    print(f"Canvas ID must be unique in a Context: {e}")

# Invalid maximum_dimensions raise ValueError
try:
    template = CanvasTemplate(
        target_dimensions=DimensionsInt(width=3840, height=2160),
        maximum_dimensions=DimensionsInt(width=1920, height=1080),  # Too small!
    )
except ValueError as e:
    print(f"maximum_dimensions must be greater or equal to the target_dimensions: {e}")
```

### Working with Effective Dimensions

Canvases can specify effective dimensions (active pixel region):

```python
canvas = Canvas(
    dimensions=DimensionsInt(width=4096, height=2160),
    effective_dimensions=DimensionsInt(width=3840, height=2160),
    # effective_anchor_point is computed automatically if not provided
)

# When processing with pad_to_maximum=True, effective dimensions track active pixels
processor = CanvasTemplateProcessor(template_with_padding)
new_canvas = processor.create_canvas(source_canvas)
print(f"Total dimensions: {new_canvas.dimensions}")
print(f"Active region: {new_canvas.effective_dimensions}")
```

### Framing Decision and Scaling via CanvasTemplate

When CanvasTemplate creates derived canvases, framing decisions are rescaled accordingly:

```python
processor = CanvasTemplateProcessor(template)
new_canvas = processor.create_canvas(source_canvas, framing_decision_id=fd_id)

# Original framing decisions remain unchanged
# New canvas has scaled copies with:
# - Dimensions scaled by computed scale factor
# - Anchor points scaled proportionally
# - Protection dimensions and anchors scaled
# - IDs and labels preserved
```

## Schema Generation

The schema types are generated from the official ASC FDL v2.0 JSON Schema. While the generated 
models are used as-is, some models have been extended with custom validation and convenience
methods in separate modules, for instance:

- `Canvas` (extends `_Canvas`)
- `Context` (extends `_Context`)
- `CanvasTemplate` (extends `_CanvasTemplate`)

This approach maintains schema compatibility while providing enhanced Python ergonomics.

## Requirements

- Python 3.10+
- pydantic >= 2.0

## Development

```bash
# Install development dependencies
pip install pydantic mypy ruff pytest

# Run tests
pytest tests/

# Type checking
mypy python/fdl/

# Format code
ruff format python/
```

## Contributing

Contributions are welcome! Please ensure:

- Code follows the existing style (100-character line limit)
- All tests pass
- Type hints are provided
- Docstrings follow the project conventions

## License

### FDL Specification
The Framing Decision List (FDL) specification, concepts, and related intellectual property 
are owned by the **American Society of Cinematographers (ASC)**.

- **Website**: https://theasc.com/
- **Specification Repository**: https://github.com/ascmitc/fdl

### Python Implementation
This Python implementation is licensed under the **BSD 3-Clause License**.

See the [LICENSE](LICENSE) and [NOTICE](NOTICE) files for full details.

This implementation is independent and not officially affiliated with or endorsed by 
the American Society of Cinematographers (ASC) unless explicitly stated.

## References

- [ASC FDL Specification v2.0](https://github.com/ascmitc/fdl/blob/main/Specification/ASCFDL_Specification_v2.0.pdf)
- [ASC FDL User Guide](https://github.com/ascmitc/fdl/blob/main/ASCFDL_UserGuide_v1.0.pdf)
- [ASC Framing Decision List (Github)](https://github.com/ascmitc/fdl)

## Acknowledgments

This Python library is a project developed in adherence to the official ASC Framing 
Decision List specification. Special thanks to the American Society of Cinematographers (ASC) 
Motion Imaging Technology Council (MITC) for developing and maintaining the FDL standard.
