use etagere::{AllocId, BucketedAtlasAllocator, Size};
use pyo3::prelude::*;

#[pyclass]
#[derive(Clone)]
struct Allocation {
    #[pyo3(get)]
    id: u32,
    #[pyo3(get)]
    x: i32,
    #[pyo3(get)]
    y: i32,
    #[pyo3(get)]
    width: i32,
    #[pyo3(get)]
    height: i32,
}

#[pyclass]
struct AtlasAllocator {
    allocator: BucketedAtlasAllocator,
}

#[pymethods]
impl AtlasAllocator {
    #[new]
    fn new(width: i32, height: i32) -> PyResult<Self> {
        if width <= 0 || height <= 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Width and height must be positive",
            ));
        }

        Ok(Self {
            allocator: BucketedAtlasAllocator::new(Size::new(width, height)),
        })
    }

    fn clear(&mut self) {
        self.allocator.clear()
    }

    fn total_size(&self) -> (i32, i32) {
        let size = self.allocator.size();
        (size.width, size.height)
    }

    fn is_empty(&self) -> bool {
        self.allocator.is_empty()
    }

    fn allocate(&mut self, width: i32, height: i32) -> PyResult<Option<Allocation>> {
        if width <= 0 || height <= 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Width and height must be positive",
            ));
        }

        let size = Size::new(width, height);
        match self.allocator.allocate(size) {
            Some(allocation) => {
                let rect = allocation.rectangle;
                Ok(Some(Allocation {
                    id: allocation.id.serialize(),
                    x: rect.min.x,
                    y: rect.min.y,
                    width: rect.width(),
                    height: rect.height(),
                }))
            }
            None => Ok(None),
        }
    }

    fn deallocate(&mut self, allocation_id: u32) {
        self.allocator
            .deallocate(AllocId::deserialize(allocation_id));
    }

    fn allocated_space(&self) -> i32 {
        self.allocator.allocated_space()
    }

    fn free_space(&self) -> i32 {
        self.allocator.free_space()
    }

    fn to_svg(&self) -> PyResult<String> {
        let mut buffer = Vec::new();
        self.allocator
            .dump_into_svg(None, &mut buffer)
            .map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("Failed to generate SVG: {}", e))
            })?;

        String::from_utf8(buffer)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid UTF-8: {}", e)))
    }
}

#[pymodule]
fn etagere_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Allocation>()?;
    m.add_class::<AtlasAllocator>()?;
    Ok(())
}
