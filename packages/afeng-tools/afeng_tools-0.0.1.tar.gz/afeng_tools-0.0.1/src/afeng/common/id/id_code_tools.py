"""
id和编码工具
"""
import random
import hashlib
import string
from typing import Literal


def get_code_by_id(id_value: int, begin_value=100000) -> int:
    """通过id获取编码"""
    return begin_value + id_value


def get_id_by_code(code: int, begin_value=100000) -> int:
    """通过编码获取id"""
    return code - begin_value


def get_tmp_code(length:int=4, base_code: int=None, ) -> str:
    """获取临时编码(当有base_code时，每次获取到的编码一样)"""
    if base_code is not None:
        # 从现有编码中获取临时编码
        return str(int(str(base_code)[::-1]) + base_code + 10**length-1)[:length]
    else:
        # 随机生成一个编码
        return str(random.randint(10**(length-1), 10**length-1))



def get_unique_code(source_text: str, length: int=4,
                    char_type:Literal['digits', 'uppercase', 'lowercase', 'mixed'] = 'mixed') -> str:
    """
    生成唯一码
    :param source_text: 用于生成哈希值的源字符串(相同的源字符串，生成的唯一码相同)
    :param length: 生成的唯一码的长度
    :param char_type: 唯一码的字符类型，mixed:大小写字母和数字，lowercase:小写字母，uppercase:大写字母，digits:数字
    :return: 唯一码
    """
    # 使用SHA-256生成哈希值
    hash_object = hashlib.sha256(source_text.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    # 定义字符集
    if char_type == 'digits':
        # 纯数字
        char_set = string.digits
    elif char_type == 'uppercase':
        # 纯大写
        char_set = string.ascii_uppercase
    elif char_type == 'lowercase':
        # 纯小写
        char_set = string.ascii_lowercase
    else:
        # 混合字符集
        char_set = string.ascii_letters + string.digits
    # 提取所需的字符
    return ''.join(char_set[int(hash_hex[i:i+2], 16) % len(char_set)] for i in range(0, length * 2, 2))


if __name__ == '__main__':
    print(get_tmp_code(6))
    print()