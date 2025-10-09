from typing import Generic, TypeVar, Optional, Sequence

from pydantic import BaseModel, Field

T = TypeVar('T')

class PageParams(BaseModel):
    """分页参数"""
    page_num: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=10000, description="每页大小")
    # 当有offset时，page_num失效，直接从offset开始取page_size条数据
    offset: Optional[int] = Field(default=None, ge=0, description="跳过的记录数")

class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: Sequence[T] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页大小")
    total_page: int = Field(default=0, description="总页数")
    
    class Config:
        from_attributes = True

    @property
    def has_next(self):
        """是否有下一页"""
        return self.page_num < self.total_page

    @property
    def has_previous(self):
        """是否有上一页"""
        return self.page_num > 1

    @property
    def has_more(self):
        """是否有更多数据"""
        return self.total > self.page_size * self.page_num

    @property
    def records(self):
        """返回总记录数"""
        return self.items



