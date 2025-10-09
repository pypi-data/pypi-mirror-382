# my_dict = {'a': 1, 'b': 2, 'c': 3}

# # 获取所有键
# keys = my_dict.keys()
# print(keys) # 输出：dict_keys(['a', 'b', 'c'])

# # 可以用 for 循环遍历
# for key in keys:
#     print(key)

# # 可以转换为列表
# key_list = list(keys)
# print(type(key_list))
# print(key_list) # 输出：['a', 'b', 'c']

###################################################################

# def test_function_1() -> int:
#     print("test function 1 called.")
#     return 3

# def condition() -> bool:
#     # Simulate a condition that can be True or False
#     print("condition called.")
#     return False

# def test_function_2() -> int:
#     print("test function 2 called.")
#     return 4

# print(test_function_1() if condition() else test_function_2())

##################################################################

# from ctypes import c_uint32
# from advantech.edge._internal._eapi._eapi_functions import _EApiStatus

# value_uint32 = c_uint32(0)
# status = _EApiStatus(value_uint32.value)
# print(status == _EApiStatus.SUCCESS)

# # Test condition
# print(3 if False else 4)

###################################################################

# import threading

# class TestClass:

#     __instance = None
#     __lock = threading.Lock()

#     def __new__(cls): 
#         with cls.__lock:
#             if cls.__instance is None:
#                 print(f"Creating instance of {cls.__name__}")
#                 cls.__instance = super(TestClass, cls).__new__(cls)
#             else:
#                 print(f"Return existing instance of {cls.__name__}")
#             return cls.__instance
    
#     def __init__(self):
        
#         print(f"Start initializing instance of {self.__class__.__name__}")        
        
#         # Check if the class is already initialized
#         if not hasattr(self, '_initialized'):

#             # Initialize the flag
#             self._initialized = True

#             print(f"Initializing instance of {self.__class__.__name__}")


# class1 = TestClass()
# class2 = TestClass()
# class3 = TestClass()
# class4 = TestClass()
# class5 = TestClass()
# class6 = TestClass()
# print(class1 is class2)  # True, both variables point to the same instance

###################################################################

# from enum import Enum

# class MyEnum(Enum):
#     VALUE1 = 1
#     VALUE2 = 2
#     VALUE3 = 3
    
# class MyEnumB(Enum):
#     VALUE1 = 1
#     VALUE2 = 2
    
# enumlist = list(MyEnum)

# print(1 not in enumlist)
# print(MyEnum.VALUE1 + MyEnum.VALUE2)
# print(MyEnum.VALUE1 in enumlist)

# x = MyEnum.VALUE1
# print(isinstance(x, MyEnum))
# print(isinstance(x, str))

# class Color(Enum):
#     RED = 1
#     GREEN = 2
#     BLUE = 3

# # 取得所有的 Enum 成員
# all_members = list(Color)
# print(all_members)

# # 只取出值（value）
# all_values = [member.value for member in Color]
# print(all_values)

# # 只取出名稱（name）
# all_names = [member.name for member in Color]
# print(all_names)

###################################################################

# import json

# json_str = '{"name": "Alice", "age": 25}'
# data = json.loads(json_str)
# print(isinstance(data, dict))  # Result : True

# dt = {
#     MyEnum.VALUE1: MyEnumB.VALUE2
# }

# for key in dt.values():
#     print(type(key))

###################################################################

# prop_value = "1.0"
# print(type(prop_value))
# print(float(prop_value))

# print(type("abc"))
# a = str("abc")
# print(type(str(a)))

###################################################################

# # 定義 : 直接指定
# person = {
#     "name": "Alice",
#     "age": 25,
#     "city": "Taipei"
# }

# # 定義 : 使用 dict 函數
# person = dict(name="Alice", age=25, city="Taipei")

###########################################################################

# # 操作 : 取得類型、長度
# print(type(person))            # Result : <class 'dict'>
# print(len(person))             # Result : 3

# # 操作 : 取得類型、長度
# print(type(person))            # Result : <class 'dict'>
# print(len(person))             # Result : 3

# # 操作 : 判斷鍵是否存在
# print("name" in person)        # Result : True
# print("email" not in person)   # Result : True

# # 操作 : 取值
# print(person["name"])          # Result : Alice

# # 操作 : 修改值
# person["age"] = 26

# # 操作 : 新增鍵值對
# person["job"] = "Engineer"

# # 操作 : 取得所有鍵
# print(person.keys()) # dict_keys(['name', 'age', 'city', 'job'])

# # 操作 : 取得所有值
# print(person.values()) # dict_values(['Alice', 26, 'Taipei', 'Engineer'])

# # 操作 : 取得所有鍵值對
# print(person.items()) # dict_items([('name', 'Alice'), ('age', 26), ...])

# # 使用 get() 安全取值（避免 key 不存在時報錯）
# print(person.get("email", "Not provided")) # Not provided

# # 刪除鍵值對
# del person["city"]

