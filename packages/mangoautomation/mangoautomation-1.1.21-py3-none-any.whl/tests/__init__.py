# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-07 23:25
# @Author : 毛鹏
import random

data_list = [{'exp': 2, 'loc': 'get_by_role("textbox", name="请输入1密码")'},
             {'exp': 0, 'loc': '//input[@type="password"]'}]
print(random.randint(0, len(data_list) - 1), len(data_list))
