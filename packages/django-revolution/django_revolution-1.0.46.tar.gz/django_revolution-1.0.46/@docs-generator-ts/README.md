# Django Revolution TypeScript Generator Documentation

> Python-based TypeScript client generator with 100% output parity to `@hey-api/openapi-ts`

## 🎯 What is This?

A pure Python implementation of TypeScript client generation that produces **identical output** to the popular `@hey-api/openapi-ts` npm package, eliminating Node.js dependencies while maintaining full compatibility.

### Key Features

✅ **Zero Node.js Dependencies** - Pure Python implementation
✅ **100% Output Parity** - Generates identical TypeScript as @hey-api/openapi-ts
✅ **Type-Safe** - Built with Pydantic 2, no `dict` or `Any` types
✅ **Fetch API Support** - Modern HTTP client (no axios/angular)
✅ **Plugin System** - Modular architecture for extensibility
✅ **Django Integration** - Seamless integration with Django Revolution

## 📚 Documentation Structure

```
@docs/
├── README.md                          # You are here
├── index.md                          # Overview & quick start
├── ROADMAP.md                        # 13-day development plan
├── API_DESIGN.md                     # API design & examples
│
├── architecture/
│   ├── index.md                      # Architecture overview
│   ├── parser.md                     # OpenAPI parser details
│   ├── plugins.md                    # Plugin system design
│   └── ir-models.md                  # IR Pydantic models
│
├── api/
│   ├── generator.md                  # TypeScriptGenerator API
│   ├── config.md                     # Configuration models
│   └── plugins.md                    # Plugin API reference
│
├── guides/
│   ├── getting-started.md            # Installation & setup
│   ├── custom-plugins.md             # Creating plugins
│   └── migration.md                  # From @hey-api/openapi-ts
│
└── examples/
    ├── basic-usage.md                # Simple examples
    ├── django-integration.md         # Django Revolution integration
    └── advanced.md                   # Advanced use cases
```

## 🚀 Quick Start

### Installation

```bash
pip install django-revolution-ts
```

### Basic Usage

```python
from django_revolution_ts import TypeScriptGenerator
from pathlib import Path

# Generate TypeScript client
generator = TypeScriptGenerator(
    input_path=Path("openapi.json"),
    output_path=Path("src/client")
)

result = generator.generate()
print(f"Generated {result.files_count} files")
```

### Django Revolution Integration

```python
from django_revolution.openapi import NativeTypeScriptGenerator

# Drop-in replacement for HeyAPITypeScriptGenerator
generator = NativeTypeScriptGenerator(config, logger)
result = generator.generate_client(zone_name, schema_path)
```

## 📖 Core Documentation

### For Users

- **[Overview & Quick Start](./index.md)** - Start here
- **[API Design](./API_DESIGN.md)** - Public API & usage examples
- **[Getting Started Guide](./guides/getting-started.md)** - Installation & setup

### For Developers

- **[Architecture Overview](./architecture/index.md)** - System architecture
- **[Development Roadmap](./ROADMAP.md)** - 13-day implementation plan
- **[Parser Details](./architecture/parser.md)** - OpenAPI parsing
- **[Plugin System](./architecture/plugins.md)** - Plugin architecture
- **[IR Models](./architecture/ir-models.md)** - Pydantic 2 models

### Advanced Topics

- **[Custom Plugins](./guides/custom-plugins.md)** - Creating plugins
- **[Migration Guide](./guides/migration.md)** - From @hey-api/openapi-ts
- **[Advanced Examples](./examples/advanced.md)** - Complex use cases

## 🏗️ Architecture at a Glance

```
┌──────────────────┐
│  OpenAPI Spec    │  (YAML/JSON)
└────────┬─────────┘
         ↓
┌─────────────────────────────────┐
│  Layer 1: Parser                │
│  OpenAPI → IR (Pydantic 2)      │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Layer 2: Plugin System         │
│  IR → Enhanced IR               │
│  - @hey-api/typescript          │
│  - @hey-api/sdk                 │
│  - @hey-api/client-fetch        │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Layer 3: Generator             │
│  Enhanced IR → TypeScript       │
│  - Jinja2 templates             │
│  - Prettier formatting          │
└────────┬────────────────────────┘
         ↓
┌──────────────────┐
│  Generated Files │  (.ts)
└──────────────────┘
```

## 🎯 Design Goals

1. **Output Parity**: Generates **identical** TypeScript as @hey-api/openapi-ts
2. **Type Safety**: 100% typed with Pydantic 2, no `Any` or `dict`
3. **No Node.js**: Pure Python implementation
4. **Modularity**: Plugin-based architecture for extensibility

## 📊 Development Status

**Current Phase**: Design & Documentation ✅
**Next Phase**: Implementation (13 days)
**Target**: Production release v1.0.0

See [ROADMAP.md](./ROADMAP.md) for detailed timeline.

## 🔗 Related Projects

- [@hey-api/openapi-ts](https://heyapi.dev/openapi-ts/) - Reference implementation
- [Django Revolution](https://github.com/markolofsen/django-revolution) - Django API framework
- [Pydantic 2](https://docs.pydantic.dev/latest/) - Data validation library

## 💡 Why This Project?

### Problems Solved

❌ **Node.js Dependency** in Python projects
❌ **Process Spawning** overhead (npx)
❌ **Installation Complexity** (npm + Python)
❌ **Integration Friction** with Django

### Solution

✅ **Pure Python** - No Node.js required
✅ **Native Integration** - Direct Python API
✅ **Type Safety** - Pydantic 2 validation
✅ **Output Parity** - Identical to @hey-api/openapi-ts

## 📝 Contributing

Contributions welcome! See [ROADMAP.md](./ROADMAP.md) for current development phase.

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-repo/django-revolution-ts
cd django-revolution-ts

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## 📄 License

MIT License - See LICENSE file for details

## 🏷️ Metadata

**Tags**: `typescript, openapi, codegen, pydantic, django`
**Status**: %%EXPERIMENTAL%%
**Version**: 0.1.0
**Python**: >=3.10
**Dependencies**: `pydantic>=2.0`, `jinja2>=3.0`, `pyyaml>=6.0`

---

**Built with ❤️ for Django Revolution**
