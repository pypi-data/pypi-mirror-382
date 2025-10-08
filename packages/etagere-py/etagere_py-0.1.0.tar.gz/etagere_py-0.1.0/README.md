# etagere-py

Python bindings for the Rust [`etagere`](https://crates.io/crates/etagere) 2D rectangle packing library, built with PyO3.

---

## Features

- Fast, efficient 2D rectangle packing for texture atlas allocation.
- Ideal for graphics applications and game development.
- Allocation, deallocation, and space management.
- SVG visualization for debugging and analysis.
- Unicode-aware and memory-safe implementation.

---

## Installation

Install directly from PyPI:

```bash
pip install etagere-py
```

---

## Example

```python
from etagere_py import AtlasAllocator

# Create a new atlas allocator with dimensions 1024x1024
atlas = AtlasAllocator(1024, 1024)

# Allocate a rectangle of size 256x128
allocation = atlas.allocate(256, 128)

if allocation:
    print(f"Allocated at position ({allocation.x}, {allocation.y})")
    print(f"Allocation ID: {allocation.id}")
    
    # Deallocate the rectangle when no longer needed
    atlas.deallocate(allocation.id)

# Check current space usage
print(f"Allocated space: {atlas.allocated_space()} pixels")
print(f"Free space: {atlas.free_space()} pixels")
```

---

## Visualization

You can visualize the current state of the atlas using the `to_svg()` method:

```python
from etagere_py import AtlasAllocator

atlas = AtlasAllocator(512, 512)

# Make some allocations
alloc1 = atlas.allocate(100, 100)
alloc2 = atlas.allocate(200, 150)

# Generate SVG visualization
svg_content = atlas.to_svg()

# Save to file or display in an SVG viewer
with open("atlas.svg", "w") as f:
    f.write(svg_content)
```
