from typing import Optional, TypeVar, List, Sequence, Union, Tuple, Type, Dict, Any

from pydantic import BaseModel
from sqlalchemy import delete as db_delete, select, Column, BinaryExpression, func, Select, Result, \
    ColumnExpressionArgument, text, Row, \
    RowMapping, inspect, distinct
from sqlalchemy.engine.result import RMKeyView
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Load, joinedload, class_mapper

from afeng.db.common.schemas.page_schemas import PageParams, PageResponse
from .base_models import DBModel

# 定义类型变量
ModelType = TypeVar("ModelType", bound=DBModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def filter_dict_key(value_schema_data:dict, model_class: type[ModelType]) -> dict[str, Any]:
    schema_data = dict()
    field_info_dict = {c.name: c for c in model_class.__table__.columns}
    for key, value in value_schema_data.items():
        if key in field_info_dict:
            schema_data[key] = value
    return schema_data


def get_primary_key_name(model_class: type[ModelType]) -> str:
    """
    获取主键字段名称
    :param model_class: 模型类
    :return:  主键字段名称
    """
    mapper = class_mapper(model_class)
    primary_key_columns = mapper.primary_key
    if primary_key_columns:
        return primary_key_columns[0].name
    return "id"


def create_query(model_class: type[ModelType], *criteria: ColumnExpressionArgument[bool]) -> Select:
    """
    创建查询语句
    :param model_class: 模型类
    :param criteria: 查询条件
    :return: 查询语句
    """
    return select(model_class).filter(*criteria)


async def execute(db: AsyncSession, stmt: Select) -> Result:
    """
    执行查询语句
    :param db: 数据库会话
    :param stmt: 查询语句
    :return: 查询结果
    """
    return await db.execute(stmt)


async def scalar_one(db: AsyncSession, stmt: Select):
    """
    执行查询语句，返回单个结果
    :param db: 数据库会话
    :param stmt: 查询语句
    :return: 结果项
    """
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def scalar_all(db: AsyncSession, stmt: Select, unique: bool = False) -> Sequence:
    """
    执行查询语句，返回所有结果
    :param db: 数据库会话
    :param stmt: 查询语句
    :param unique: 是否需要去重，默认False
    :return: 结果序列
    """
    result = await db.execute(stmt)
    scalars = result.scalars()
    if unique:
        return scalars.unique().all()
    return scalars.all()

async def get_one(db: AsyncSession, model_class:type[ModelType],
                  *criteria: ColumnExpressionArgument[bool]) -> Optional[ModelType]:
    """
    获取单个记录
    :param db: 数据库会话
    :param model_class: 模型类，继承自DBModel
    :param criteria: 查询条件
    :return: 模型实例，如果不存在则返回None
    """
    stmt = select(model_class).where(*criteria)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get(db: AsyncSession, model_class:type[ModelType], key_value: int|str, key_name:str='id') -> Optional[ModelType]:
    """
    获取记录（通常是通过id查询）
    :param db: 数据库会话
    :param model_class: 模型类，继承自DBModel
    :param key_value: 主键值，通常为id的值
    :param key_name: 主键字段名称，默认为'id'
    :return: 模型实例，如果不存在则返回None
    """
    if key_name == 'id':
        key_value = int(key_value)
    primary_key_column:Column = getattr(model_class, key_name)
    stmt = select(model_class).where(primary_key_column == key_value)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def query_list(db: AsyncSession, model_class:type[ModelType],
               filters: Optional[List[BinaryExpression]|tuple[BinaryExpression]] = None,
               load_options: Optional[List[Union[Load, selectinload, joinedload]]] = None,
                order_by: Optional[Union[Column, List[Column], Tuple[Column]]] = None  # 可选排序
            )  -> Sequence[ModelType]:
    """
    获取记录列表
    :param db: 数据库会话
    :param model_class: 模型类，继承自DBModel
    :param filters:  查询条件，可以是多个条件，也可以是单个条件
    :param load_options: 关系加载选项，如 [selectinload(User.creator)]  # 预加载creator关系
    :param order_by: 排序条件
    :return:  模型实例列表
    """
    stmt = select(model_class)
    if load_options:
        for option in load_options:
            stmt = stmt.options(option)
    if filters:
        for filter_condition in filters:
            stmt = stmt.where(filter_condition)
    # 处理排序
    if order_by:
        if isinstance(order_by, (list, tuple)):
            stmt = stmt.order_by(*order_by)
        else:
            stmt = stmt.order_by(order_by)
    else:
        # 默认按创建时间降序排序
        stmt = stmt.order_by(model_class.created_at.desc())

    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def query_page(
        db: AsyncSession,
        model_class: type[ModelType],
        page_params: PageParams,
        filters: Optional[Union[List[BinaryExpression], tuple[BinaryExpression]]] = None,
        load_options: Optional[List[Union[Load, selectinload, joinedload]]] = None,  # 新增加载选项
        order_by: Optional[Union[Column, List[Column], Tuple[Column]]] = None,  # 可选排序
        join_relations: Optional[List[Any]] = None,  # 新增：明确的 JOIN 关系列表
    ) -> PageResponse[ModelType]:
    """
    分页查询记录，支持关系预加载
    :param db: 数据库会话
    :param model_class: 模型类
    :param page_params: 分页参数
    :param filters: 查询条件
    :param load_options: 关系加载选项，如 [selectinload(User.creator), joinedload(User.creator)]  # 预加载creator关系
    :param order_by: 排序条件
    :param join_relations: 明确的 JOIN 关系列表，可选
    :return: 分页响应对象
    """
    # 构建基础查询
    base_stmt = select(model_class)

    # 添加明确的 JOIN（如果提供了）
    if join_relations:
        for join_relation in join_relations:
            base_stmt = base_stmt.join(join_relation)

    # 添加过滤条件
    if filters:
        for filter_condition in filters:
            base_stmt = base_stmt.where(filter_condition)

    # 构建 COUNT 查询
    count_base_stmt = select(model_class)

    # 为 COUNT 查询添加相同的 JOIN（如果提供了）
    if join_relations:
        for join_relation in join_relations:
            count_base_stmt = count_base_stmt.join(join_relation)

    # 为 COUNT 查询添加相同的过滤条件
    if filters:
        for filter_condition in filters:
            count_base_stmt = count_base_stmt.where(filter_condition)

    # 使用 DISTINCT COUNT 主键
    try:
        primary_key = inspect(model_class).primary_key[0]
        count_stmt = select(func.count(distinct(primary_key))).select_from(count_base_stmt.subquery())
    except (IndexError, AttributeError):
        count_stmt = select(func.count()).select_from(count_base_stmt.subquery())

    # 执行 COUNT 查询
    total = await db.scalar(count_stmt)

    # 构建完整查询（用于获取数据）
    stmt = base_stmt

    # 添加关系加载选项
    if load_options:
        for option in load_options:
            stmt = stmt.options(option)

    # 处理排序
    if order_by:
        if isinstance(order_by, (list, tuple)):
            stmt = stmt.order_by(*order_by)
        else:
            stmt = stmt.order_by(order_by)
    else:
        # 默认按创建时间降序排序
        stmt = stmt.order_by(model_class.created_at.desc())

    # 添加分页
    offset = page_params.offset if page_params.offset is not None else (page_params.page_num - 1) * page_params.page_size
    stmt = stmt.offset(offset).limit(page_params.page_size)

    # 执行查询
    result = await db.execute(stmt)
    items = result.scalars().unique().all()

    # 计算总页数
    total_pages = (total + page_params.page_size - 1) // page_params.page_size if total > 0 else 0

    return PageResponse(
        items=items,
        total=total,
        page_num=page_params.page_num,
        page_size=page_params.page_size,
        total_page=total_pages
    )

async def add(db: AsyncSession,model_class: type[ModelType], create_schema: CreateSchemaType|dict,
              auto_commit: bool = True) -> ModelType:
    """
    添加记录
    :param db: 数据库会话
    :param model_class: 模型类
    :param create_schema: 创建数据Schema
    :param auto_commit: 是否自动提交，默认为True
    :return: 添加后的模型实例
    """
    if not isinstance(create_schema, dict):
        # 将Pydantic模型转换为字典，排除未设置的字段
        create_schema_data = create_schema.model_dump(exclude_unset=True)
    else:
        create_schema_data = create_schema

    # 创建模型实例
    db_obj = model_class(**filter_dict_key(create_schema_data, model_class))
    db.add(db_obj)
    if auto_commit:
        await db.commit()
        await db.refresh(db_obj)
    return db_obj


async def add_db_obj(db: AsyncSession,db_obj: ModelType,
              auto_commit: bool = True) -> ModelType:
    """
    添加记录
    :param db: 数据库会话
    :param db_obj: 模型实例
    :param auto_commit: 是否自动提交，默认为True
    :return: 添加后的模型实例
    """
    db.add(db_obj)
    if auto_commit:
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update(db: AsyncSession, model_class: Type[ModelType],
                        update_schema: Union[UpdateSchemaType, Dict[str, Any]],
                        key_value: Union[int, str], key_name: str = 'id',
                        auto_commit: bool = True, exclude_none: bool = True) -> ModelType:
    """
    更新记录
    :param db: 数据库会话
    :param model_class: 模型类
    :param update_schema: 更新数据Schema或字典
    :param key_value: 主键值，通常为id的值
    :param key_name: 主键字段名称，默认为'id'
    :param auto_commit: 是否自动提交，默认为True
    :param exclude_none: 是否排除None值，默认为True
    :return: 更新后的模型实例
    """
    if key_name == 'id':
        key_value = int(key_value)
    # 1. 先查询获取要更新的对象
    db_obj = await get(db, model_class, key_value, key_name)
    if not db_obj:
        raise ValueError(f"[{key_name}={key_value}]的{model_class.__name__}数据不存在！")
    return await update_db_obj(db=db, db_obj=db_obj, update_schema=update_schema,
                               auto_commit=auto_commit, exclude_none=exclude_none)


async def update_db_obj(db: AsyncSession, db_obj: ModelType, update_schema: UpdateSchemaType|Dict[str, Any],
                         auto_commit: bool = True, exclude_none: bool = True) -> ModelType:
    """
    更新记录
    :param db: 数据库会话
    :param db_obj: 模型实例对象
    :param update_schema: 更新数据Schema
    :param auto_commit: 是否自动提交，默认为True
    :param exclude_none: 是否排除None值，默认为True
    :return: 更新后的模型实例
    """
    # 获取更新数据
    if isinstance(update_schema, dict):
        update_data = update_schema
    else:
        update_data = update_schema.model_dump(exclude_unset=True)

    # 更新对象属性
    for field, value in update_data.items():
        if exclude_none and value is None:
            continue
        if hasattr(db_obj, field):
            setattr(db_obj, field, value)

    db.add(db_obj)
    if auto_commit:
        # 3. 提交事务并刷新对象
        await db.commit()
        await db.refresh(db_obj)
    return db_obj


async def delete(db: AsyncSession, model_class: Type[ModelType],
                 key_value: Union[int, str], key_name: str = 'id',
                 auto_commit: bool = True) -> bool:
    """
    删除记录
    :param db: 数据库会话
    :param model_class: 模型类
    :param key_value: 主键值，通常为id的值
    :param key_name: 主键字段名称，默认为'id'
    :param auto_commit: 是否自动提交，默认为True
    :return: True表示删除成功，False表示删除失败
    """
    if key_name == 'id':
        key_value = int(key_value)
    primary_key_column: Column = getattr(model_class, key_name)
    stmt = select(model_class).where(primary_key_column == key_value)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()

    if obj:
        await db.delete(obj)
        if auto_commit:
            await db.commit()
        return obj
    return False

async def batch_delete(db: AsyncSession, model_class: Type[ModelType],
                 key_value_list: list[Union[int, str]], key_name: str = 'id',
                 auto_commit: bool = True) -> int:
    """
    批量删除记录
    :param db: 数据库会话
    :param model_class: 模型类
    :param key_value_list: 主键值列表，通常为id的值
    :param key_name: 主键字段名称，默认为'id'
    :param auto_commit: 是否自动提交，默认为True
    :return: 删除的记录数
    """
    if key_name == 'id':
        key_value_list = [int(key_value) for key_value in key_value_list]
    primary_key_column: Column = getattr(model_class, key_name)
    stmt = db_delete(model_class).where(primary_key_column.in_(key_value_list))
    result = await db.execute(stmt)
    row_count = result.rowcount
    if auto_commit:
        await db.commit()
    return row_count

async def get_max_value(db: AsyncSession, model_class: Type[ModelType], model_column: Column) -> int:
    """
    获取最大ID
    :param db: 数据库会话
    :param model_class: 模型类
    :param model_column: 模型属性, 如: User.id
    :return: 最大值
    """
    stmt = select(func.max(model_column)).select_from(model_class)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def execute_sql(db: AsyncSession, sql: str,
                      params: dict = None,
                      is_mapping_result: bool = False) -> tuple[RMKeyView, Sequence[Row[tuple[Any, ...] | Any]]]|Sequence[RowMapping]:
    """
     执行sql语句
    :param db: 数据库会话
    :param sql: sql语句
    :param params: sql参数
    :param is_mapping_result: 是否返回字典结果
    :return: 执行结果 (行数据列表, 字段名列表) or 字典列表结果
    """
    cursor = await db.execute(text(sql), params)
    if is_mapping_result:
        return cursor.mappings().all()
    return cursor.keys(), cursor.fetchall()

