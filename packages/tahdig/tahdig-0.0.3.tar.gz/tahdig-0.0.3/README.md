# 🍚 Tahdig - Configuration with a Crispy Layer

[![Development Status](https://img.shields.io/badge/status-under%20development-orange.svg)](https://github.com/fardin/tahdig)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-390%20passed-brightgreen.svg)](tests/)

> ⚠️ **Under Development** - This library is currently in active development. API may change before v1.0 release.

> Like the golden, crispy crust of Persian rice (تهدیگ), Tahdig provides a delightful foundation for your Python configuration needs.

## 🌟 What is Tahdig?

Tahdig is a powerful yet elegant configuration management system for Python applications. Inspired by Detectron2's configuration system, it provides:

- **Hierarchical Configuration** with intuitive dot notation access
- **Component Registry** with automatic parameter injection
- **Configuration Inheritance** using the `extends` keyword
- **Environment Variable Substitution** with sensible defaults
- **Comprehensive Debugging Tools** including validation, linting, and visualization
- **Type Safety** with schema validation

## 🚀 Quick Start

### Installation

```bash
pip install tahdig
```

### Basic Usage

```python
from tahdig import Config

# Create a configuration
config = Config({
    'database': {
        'host': 'localhost',
        'port': 5432,
        'name': 'myapp'
    },
    'api': {
        'version': 'v1',
        'timeout': 30
    }
})

# Access with dot notation
print(config.database.host)  # 'localhost'
print(config.api.timeout)    # 30

# Freeze configuration to prevent modifications
config.freeze()
```

### Component Registry

```python
from tahdig import Registry, Config

# Create a registry
registry = Registry("services")

# Register components with automatic parameter injection
@registry.register()
class DatabaseService:
    def __init__(self, host, port, database, cfg=None):
        self.host = host
        self.port = port
        self.database = database

# Create configuration
config = Config({
    'host': 'localhost',
    'port': 5432,
    'database': 'myapp'
})

# Instantiate with automatic parameter injection
ServiceFactory = registry.get("DatabaseService")
service = ServiceFactory(cfg=config)
print(service.host)  # 'localhost'
```

### Configuration Files with Inheritance

**base_config.yaml:**
```yaml
model:
  name: resnet50
  layers: 50
  pretrained: false

training:
  epochs: 100
  batch_size: 32
```

**production_config.yaml:**
```yaml
extends: base_config.yaml

model:
  pretrained: true  # Override base value

training:
  epochs: 200       # Override base value
  # batch_size: 32 is inherited from base
```

```python
from tahdig import Config

config = Config.from_file('production_config.yaml')
print(config.model.name)       # 'resnet50' (inherited)
print(config.model.pretrained) # True (overridden)
print(config.training.epochs)  # 200 (overridden)
```

### Environment Variables

**config.yaml:**
```yaml
database:
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  password: ${DB_PASSWORD}  # Required, no default
```

```python
import os
from tahdig import Config

os.environ['DB_HOST'] = 'production.db.com'
os.environ['DB_PASSWORD'] = 'secret'

config = Config.from_file('config.yaml')
print(config.database.host)  # 'production.db.com'
print(config.database.port)  # '5432' (default used)
```

## 🎯 Key Features

### 1. **Hierarchical Configuration**
Access nested configurations naturally with dot notation:
```python
config.model.layers.conv1.filters  # Deep nesting supported
```

### 2. **Configuration Freezing**
Prevent accidental modifications:
```python
config.freeze()
config.new_key = 'value'  # Raises ConfigKeyError
```

### 3. **Schema Validation**
Validate your configuration against schemas:
```python
from tahdig import validate_config

schema = {
    'database': {
        'host': str,
        'port': int,
        'timeout': lambda x: x > 0  # Custom validator
    }
}

is_valid = validate_config(config, schema)
```

### 4. **Configuration Linting**
Check for best practices and common issues:
```python
from tahdig import lint_config

errors = lint_config(config)
for error in errors:
    print(f"{error.severity}: {error}")
```

### 5. **Interactive Explorer**
Explore your configuration interactively:
```python
from tahdig import ConfigDebugger

debugger = ConfigDebugger(config)
debugger.explore()  # Opens interactive REPL
```

### 6. **Visualization**
Visualize configuration structure as a tree:
```python
from tahdig import visualize_config

tree = visualize_config(config)
print(tree)
# Output:
# ├── database/
# │   ├── host: localhost
# │   ├── port: 5432
# │   └── timeout: 30
# └── api/
#     └── version: v1
```

## 📦 Architecture

Tahdig consists of several key components:

- **`Config`** - Main configuration class with file I/O
- **`ConfigNode`** - Nested configuration container
- **`Registry`** - Component registration and retrieval
- **`ConfigDebugger`** - Comprehensive debugging tools

### Debug Tools (Modular)

- **`validators`** - Schema validation and type checking
- **`linters`** - Best practice checking
- **`analyzers`** - Performance profiling and comparison
- **`visualizers`** - Tree visualization and interactive exploration
- **`generators`** - Documentation and IDE support generation

## 🔧 Advanced Usage

### Custom Config Transformations

```python
from tahdig import Registry

registry = Registry("transformers")

def custom_transformer(cfg):
    return {
        'host': cfg.host.upper(),
        'port': cfg.port * 2
    }

@registry.register("service", config_fn=custom_transformer)
class Service:
    def __init__(self, host, port):
        self.host = host
        self.port = port
```

### Hierarchical Class Instantiation

The registry can automatically instantiate classes from configuration using the `type` field:

#### Option 1: Build Directly from Config

Use `registry.build()` when your config specifies the top-level class:

```python
from tahdig import Registry, Config

registry = Registry("app")

@registry.register()
class Database:
    def __init__(self, host, port, cfg=None):
        self.host = host
        self.port = port

@registry.register()
class RedisCache:
    def __init__(self, host, port, cfg=None):
        self.host = host
        self.port = port

@registry.register()
class Application:
    def __init__(self, database, cache, debug=False, cfg=None):
        self.database = database
        self.cache = cache
        self.debug = debug

# Config specifies what to build at the top level
config = Config({
    'type': 'Application',  # ✅ Build Application from this config
    'database': {
        'type': 'Database',  # ✅ Nested instantiation
        'host': 'localhost',
        'port': 5432
    },
    'cache': {
        'type': 'RedisCache',  # ✅ Parameter name doesn't need to match
        'host': 'localhost',
        'port': 6379
    },
    'debug': True
})

# Build directly from config - fully config-driven!
app = registry.build(cfg=config)

assert isinstance(app, Application)
assert isinstance(app.database, Database)
assert isinstance(app.cache, RedisCache)
```

This is ideal for:
- **Configuration files** (YAML/JSON) that define the entire application
- **Plugin systems** where configs specify components
- **ML experiments** where configs define model architectures

**Example with YAML config file:**

```yaml
# app_config.yaml
type: Application
database:
  type: Database
  host: localhost
  port: 5432
cache:
  type: RedisCache
  host: localhost
  port: 6379
debug: true
```

```python
# Load and build from YAML
config = Config.from_file('app_config.yaml')
app = registry.build(cfg=config)
```

#### Option 2: Get Factory and Instantiate

Use `registry.get()` when you know the class name in code:

```python
# Get the factory function
AppFactory = registry.get("Application")

# Config only has parameters, not top-level type
config = Config({
    'database': {
        'type': 'Database',
        'host': 'localhost',
        'port': 5432
    },
    'cache': {
        'type': 'RedisCache',
        'host': 'localhost',
        'port': 6379
    },
    'debug': True
})

app = AppFactory(cfg=config)
```

**🎯 Two Ways to Specify Types:**

1. **✅ Recommended: Use `type` field in config** (Most flexible)
   ```python
   config = Config({
       'database': {
           'type': 'Database',  # ✅ Explicit and clear
           'host': 'localhost',
           'port': 5432
       }
   })
   ```
   
   **Benefits:**
   - **Explicit**: No ambiguity about which class to instantiate
   - **Flexible**: Parameter names don't need to match class names  
   - **Polymorphic**: Easily swap implementations in config files
   - **Config-driven**: Change behavior without touching code
   - **Best Practice**: Same pattern used by Detectron2, MMDetection, Hydra
   
   **Use this approach for:**
   - Configuration files (YAML/JSON)
   - Plugin systems
   - ML experiments with different architectures
   - Any time you want full config control

2. **Alternative: Use type hints** (When type safety is priority)
   ```python
   def __init__(self, database: Database, cache: RedisCache, cfg=None):
       ...
   ```
   
   **Benefits:**
   - **Type safety**: Works with mypy and other static type checkers
   - **IDE support**: Better autocomplete and inline documentation
   - **Clear intent**: Self-documenting code
   
   **Use this approach for:**
   - Internal components with fixed types
   - When you want type checking
   - Simpler cases where config-driven isn't needed

**💡 You can combine both approaches:** Use type hints in code for type safety, but allow `type` field in config to override when needed for flexibility.

### Configuration Comparison

```python
from tahdig import ConfigDebugger

debugger = ConfigDebugger(config1)
diff = debugger.diff_with_file('config2.yaml')

for key, change in diff.items():
    if key.startswith('+'):
        print(f"Added: {key}")
    elif key.startswith('-'):
        print(f"Removed: {key}")
    elif key.startswith('~'):
        print(f"Modified: {key}")
```

### Performance Profiling

```python
from tahdig import ConfigDebugger

debugger = ConfigDebugger(config)
metrics = debugger.profile()

print(f"Config size: {metrics['config_size']} bytes")
print(f"Max depth: {metrics['config_depth']}")
print(f"Total keys: {metrics['total_keys']}")
```

### Real-World Example: Object Detection System

Here's a complete example showing how to build a configurable object detection system with swappable components:

```python
from tahdig import Registry, Config

# Create registry for model components
model_registry = Registry("detection")

# 1. Backbone Networks (Feature Extraction)
@model_registry.register()
class ResNet50:
    """ResNet-50 backbone for high accuracy."""
    def __init__(self, pretrained=True, freeze_layers=0, cfg=None):
        self.name = "ResNet-50"
        self.pretrained = pretrained
        self.freeze_layers = freeze_layers
        self.out_channels = 2048

@model_registry.register()
class MobileNetV2:
    """MobileNet-V2 backbone for mobile deployment."""
    def __init__(self, pretrained=True, width_mult=1.0, cfg=None):
        self.name = "MobileNet-V2"
        self.pretrained = pretrained
        self.width_mult = width_mult
        self.out_channels = 1280

# 2. Neck Networks (Multi-scale Features)
@model_registry.register()
class FPN:
    """Feature Pyramid Network."""
    def __init__(self, in_channels, out_channels=256, num_levels=5, cfg=None):
        self.name = "FPN"
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_levels = num_levels

# 3. Detection Heads
@model_registry.register()
class RetinaNetHead:
    """RetinaNet detection head with focal loss."""
    def __init__(self, num_classes, in_channels=256, num_anchors=9, cfg=None):
        self.name = "RetinaNet"
        self.num_classes = num_classes
        self.in_channels = in_channels
        self.num_anchors = num_anchors

@model_registry.register()
class YOLOv5Head:
    """YOLOv5 detection head."""
    def __init__(self, num_classes, in_channels=256, cfg=None):
        self.name = "YOLOv5"
        self.num_classes = num_classes
        self.in_channels = in_channels

# 4. Dataset Configuration
@model_registry.register()
class COCODataset:
    """COCO dataset loader."""
    def __init__(self, root_dir, split='train', img_size=640, cfg=None):
        self.name = "COCO"
        self.root_dir = root_dir
        self.split = split
        self.img_size = img_size
        self.num_classes = 80

@model_registry.register()
class CustomDataset:
    """Custom dataset loader."""
    def __init__(self, root_dir, annotations, num_classes, img_size=640, cfg=None):
        self.name = "Custom"
        self.root_dir = root_dir
        self.annotations = annotations
        self.num_classes = num_classes
        self.img_size = img_size

# 5. Complete Detection Model
@model_registry.register()
class ObjectDetector:
    """Complete object detection model."""
    def __init__(self, backbone, neck, head, dataset, 
                 img_size=(640, 640), batch_size=16, cfg=None):
        self.backbone = backbone
        self.neck = neck
        self.head = head
        self.dataset = dataset
        self.img_size = img_size
        self.batch_size = batch_size
    
    def summary(self):
        return f"""
╔══════════════════════════════════════════════════════════╗
║           Object Detection Model Summary                 ║
╠══════════════════════════════════════════════════════════╣
║ Backbone:    {self.backbone.name:<30} ({self.backbone.out_channels} channels)
║ Neck:        {self.neck.name:<30} ({self.neck.out_channels} channels)
║ Head:        {self.head.name:<30} ({self.head.num_classes} classes)
║ Dataset:     {self.dataset.name:<30} ({self.dataset.num_classes} classes)
║ Image Size:  {str(self.img_size):<43}
║ Batch Size:  {self.batch_size:<43}
╚══════════════════════════════════════════════════════════╝
"""
```

**Config #1: High-Accuracy RetinaNet (retinanet_coco.yaml)**

```yaml
type: ObjectDetector
img_size: [640, 640]
batch_size: 16

backbone:
  type: ResNet50
  pretrained: true
  freeze_layers: 2

neck:
  type: FPN
  in_channels: 2048  # Must match backbone output
  out_channels: 256
  num_levels: 5

head:
  type: RetinaNetHead
  num_classes: 80
  in_channels: 256   # Must match neck output
  num_anchors: 9

dataset:
  type: COCODataset
  root_dir: /data/coco
  split: train
  img_size: 640
```

**Config #2: Fast Mobile YOLO (yolo_mobile.yaml)**

```yaml
type: ObjectDetector
img_size: [416, 416]  # Smaller for speed
batch_size: 32         # Larger batch with smaller model

backbone:
  type: MobileNetV2     # Swap to lightweight backbone
  pretrained: true
  width_mult: 0.75      # Even lighter

neck:
  type: FPN
  in_channels: 1280     # MobileNetV2 output
  out_channels: 128     # Smaller for mobile
  num_levels: 3         # Fewer pyramid levels

head:
  type: YOLOv5Head      # Swap to YOLO head
  num_classes: 80
  in_channels: 128

dataset:
  type: COCODataset
  root_dir: /data/coco
  split: train
  img_size: 416
```

**Config #3: Custom Dataset (custom_detector.yaml)**

```yaml
type: ObjectDetector
img_size: [512, 512]
batch_size: 8

backbone:
  type: ResNet50
  pretrained: true
  freeze_layers: 0

neck:
  type: FPN
  in_channels: 2048
  out_channels: 256
  num_levels: 4

head:
  type: RetinaNetHead
  num_classes: 20       # Custom number of classes
  in_channels: 256
  num_anchors: 9

dataset:
  type: CustomDataset   # Use custom dataset
  root_dir: /data/my_dataset
  annotations: annotations.json
  num_classes: 20
  img_size: 512
```

**Usage: Build Different Models from Config**

```python
# Load and build RetinaNet model
retinanet_config = Config.from_file('retinanet_coco.yaml')
retinanet = model_registry.build(cfg=retinanet_config)
print(retinanet.summary())

# Output:
# ╔══════════════════════════════════════════════════════════╗
# ║           Object Detection Model Summary                 ║
# ╠══════════════════════════════════════════════════════════╣
# ║ Backbone:    ResNet-50                      (2048 channels)
# ║ Neck:        FPN                            (256 channels)
# ║ Head:        RetinaNet                      (80 classes)
# ║ Dataset:     COCO                           (80 classes)
# ║ Image Size:  (640, 640)
# ║ Batch Size:  16
# ╚══════════════════════════════════════════════════════════╝

# Build mobile YOLO - completely different architecture!
yolo_config = Config.from_file('yolo_mobile.yaml')
yolo = model_registry.build(cfg=yolo_config)
print(yolo.summary())

# Output:
# ╔══════════════════════════════════════════════════════════╗
# ║           Object Detection Model Summary                 ║
# ╠══════════════════════════════════════════════════════════╣
# ║ Backbone:    MobileNet-V2                   (1280 channels)
# ║ Neck:        FPN                            (128 channels)
# ║ Head:        YOLOv5                         (80 classes)
# ║ Dataset:     COCO                           (80 classes)
# ║ Image Size:  (416, 416)
# ║ Batch Size:  32
# ╚══════════════════════════════════════════════════════════╝

# Build custom detector
custom_config = Config.from_file('custom_detector.yaml')
custom = model_registry.build(cfg=custom_config)
print(custom.summary())
```

**🎯 Key Benefits:**

1. **🔄 Swappable Components**
   - Change `backbone.type: ResNet50` → `MobileNetV2` without touching code
   - Swap `head.type: RetinaNetHead` → `YOLOv5Head` instantly
   
2. **📝 Fully Config-Driven**
   - Entire model architecture defined in YAML
   - Version control your experiments
   - Share configs with team members

3. **🔬 Easy Experimentation**
   ```bash
   # Try different architectures
   python train.py --config retinanet_coco.yaml
   python train.py --config yolo_mobile.yaml
   python train.py --config custom_detector.yaml
   ```

4. **🏗️ Modular & Testable**
   - Each component is independent
   - Easy to add new backbones/heads/datasets
   - Just register and use!

5. **🌍 Environment-Specific Configs**
   ```yaml
   # dev_config.yaml
   dataset:
     root_dir: /local/small_dataset
     split: train
   batch_size: 4
   
   # prod_config.yaml
   dataset:
     root_dir: ${DATA_ROOT}/full_dataset
     split: train
   batch_size: 64
   ```

6. **📊 Perfect for ML/AI**
   - Same pattern used by Detectron2, MMDetection, Hydra
   - Track experiments with config files
   - Reproduce results easily

## 📚 Documentation

- **[API Reference](docs/api.md)** - Complete API documentation
- **[User Guide](docs/guide.md)** - Comprehensive user guide
- **[Examples](examples/)** - Example configurations and use cases
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines

## 🧪 Testing

Tahdig has comprehensive test coverage:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=tahdig --cov-report=html
```

**Test Statistics:**
- **390 tests** - 100% passing ✅
- **Coverage** - 95%+
- **Test categories:** Config, Registry, Inheritance, Validation, Integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Detectron2's configuration system](https://github.com/facebookresearch/detectron2)
- Named after the delicious crispy rice crust from Persian cuisine (تهدیگ)

## 🌟 Why "Tahdig"?

Tahdig (تهدیگ) is the crispy, golden crust that forms at the bottom of the pot when cooking Persian rice. It's considered a delicacy - the best part of the meal. Like this beloved dish:

- **Layered** - Your configuration has hierarchical layers
- **Carefully crafted** - Tahdig requires skill and attention, like good configuration
- **The foundation** - It's the base that holds everything together  
- **Something special** - Not just any config library, but the delightful layer that makes everything better

---

Made with ❤️ by [Fardin](https://github.com/fardin)

**Star ⭐ this repo if you find it useful!**

