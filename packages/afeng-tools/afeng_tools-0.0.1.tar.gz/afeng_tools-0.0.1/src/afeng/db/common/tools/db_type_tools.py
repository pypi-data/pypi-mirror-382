import re


def is_postgresql(database_url:str) -> bool:
    """是否是postgresql"""
    return True if re.match('^postgresql', database_url) else False


def is_mysql(database_url:str) -> bool:
    """是否是mysql"""
    return True if re.match('^mysql', database_url) else False


def is_sqlite(database_url:str) -> bool:
    """是否是sqlite"""
    return True if re.match('^sqlite', database_url) else False


def is_oracle(database_url:str) -> bool:
    """是否是oracle"""
    return True if re.match('^oracle', database_url) else False


def is_mssql(database_url:str) -> bool:
    """是否是mssql"""
    return True if re.match('^mssql', database_url) else False


def is_mongodb(database_url:str) -> bool:
    """是否是mongodb"""
    return True if re.match('^mongodb', database_url) else False
