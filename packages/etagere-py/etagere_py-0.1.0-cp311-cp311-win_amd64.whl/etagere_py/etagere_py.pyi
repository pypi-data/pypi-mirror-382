"""Python bindings for the etagere texture atlas allocator library.

This module provides a Python interface to etagere, a 2D rectangle packing
library commonly used for texture atlas allocation in graphics applications.
"""

class Allocation:
    """Represents a successful allocation in the texture atlas.

    Attributes:
        id: Unique identifier for this allocation. Use this ID to
            deallocate the space later.
        x: X-coordinate of the top-left corner of the allocated
            rectangle.
        y: Y-coordinate of the top-left corner of the allocated
            rectangle.
        width: Width of the allocated rectangle in pixels.
        height: Height of the allocated rectangle in pixels.
    """

    id: int
    x: int
    y: int
    width: int
    height: int

class AtlasAllocator:
    """A 2D texture atlas allocator using bucketed allocation strategy.

    This allocator manages a fixed-size 2D space and allows efficient
    packing of rectangles. It uses a bucketed approach to optimize for
    common allocation sizes.

    Example:
        >>> atlas = AtlasAllocator(1024, 1024)
        >>> alloc = atlas.allocate(256, 128)
        >>> if alloc:
        ...     print(f"Allocated at ({alloc.x}, {alloc.y})")
        ...     atlas.deallocate(alloc.id)
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize a new texture atlas allocator.

        Args:
            width: Total width of the atlas in pixels. Must be positive.
            height: Total height of the atlas in pixels. Must be
                positive.

        Raises:
            ValueError: If width or height is not positive.
        """

    def clear(self) -> None:
        """Remove all allocations and reset the atlas to empty state.

        This operation invalidates all previously returned allocation
        IDs. After calling clear(), the atlas is ready to accept new
        allocations as if it was newly created.
        """

    def total_size(self) -> tuple[int, int]:
        """Get the total dimensions of the atlas.

        Returns:
            A tuple of (width, height) representing the total atlas
            dimensions in pixels.
        """

    def is_empty(self) -> bool:
        """Check if the atlas has no active allocations.

        Returns:
            True if no space is currently allocated, False otherwise.
        """

    def allocate(self, width: int, height: int) -> Allocation | None:
        """Allocate a rectangle of the specified size in the atlas.

        Attempts to find space for a rectangle with the given
        dimensions. If successful, returns an Allocation object
        containing the position and ID of the allocated space.

        Args:
            width: Width of the rectangle to allocate. Must be
                positive.
            height: Height of the rectangle to allocate. Must be
                positive.

        Returns:
            An Allocation object if space was found, None if the atlas
            is too full to accommodate the requested size.

        Raises:
            ValueError: If width or height is not positive.
        """

    def deallocate(self, allocation_id: int) -> None:
        """Free a previously allocated rectangle.

        Marks the space occupied by the allocation as available for
        future allocations. The allocation ID becomes invalid after
        this call.

        Args:
            allocation_id: The ID returned by a previous allocate()
                call.

        Note:
            Deallocating an invalid or already-deallocated ID is safe
            but has no effect.
        """

    def allocated_space(self) -> int:
        """Get the total area currently allocated in the atlas.

        Returns:
            The sum of all allocated rectangle areas in square pixels.
        """

    def free_space(self) -> int:
        """Get the total available space remaining in the atlas.

        Returns:
            The amount of unallocated space in square pixels.

        Note:
            Due to fragmentation, the actual largest allocatable
            rectangle may be smaller than this value suggests.
        """

    def to_svg(self) -> str:
        """Generate an SVG visualization of the current atlas state.

        Creates an SVG document fragment showing all allocated
        rectangles in the atlas. Useful for debugging and
        visualization purposes.

        Returns:
            A string containing SVG markup representing the atlas
            layout.

        Raises:
            IOError: If SVG generation fails.
            ValueError: If the generated SVG contains invalid UTF-8.

        Note:
            The returned SVG is a fragment without <svg> wrapper tags,
            allowing it to be embedded in larger documents.
        """
