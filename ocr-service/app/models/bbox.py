"""
Bounding Box Model
Represents position and size of detected text
"""
from pydantic import BaseModel, Field


class BBox(BaseModel):
    """Bounding box for text element"""
    x: int = Field(..., description="X coordinate (left)")
    y: int = Field(..., description="Y coordinate (top)")
    w: int = Field(..., description="Width")
    h: int = Field(..., description="Height")
    
    @property
    def right(self) -> int:
        """Right edge X coordinate"""
        return self.x + self.w
    
    @property
    def bottom(self) -> int:
        """Bottom edge Y coordinate"""
        return self.y + self.h
    
    @property
    def center(self) -> tuple:
        """Center point (x, y)"""
        return (self.x + self.w // 2, self.y + self.h // 2)
    
    @property
    def area(self) -> int:
        """Area in pixels"""
        return self.w * self.h
