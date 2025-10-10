# bigtools

python 工具箱，实现了一些实用的函数、类和赋值了一批常用变量，方便调用，减少工程代码量。

## 安装

```
pip install bigtools
```
    

## 使用
每个函数、类、变量均有两种导入的方法，视不同情况选择适合的写法。为了更好的说明这个项目的情况，创建这个README我会尽量使用第二种写法。实际工程中我会使用第一种写法，简单直接。

```python3
# 例：
# 第一种写法，简单直接
from bigtools import generate_hash_value
# 第二种写法，包路径清晰
from bigtools.hash_tools import generate_hash_value
```

### 1. 使用函数或类
以生成hash值为例：
```python3
# 导入包
from bigtools import generate_hash_value
# 第二种写法
# from bigtools.hash_tools import generate_hash_value


hash_value = generate_hash_value('python工具箱')  # 默认使用md5，可选sha1、sha256 等等
print(hash_value)
```
### 2. 使用变量
2.1 以使用 headers 为例：
```python3
from bigtools import headers
# 第二种写法
# from bigtools.default_data import headers

print(headers)

import requests
url = ''
requests.get(url=url, headers=headers)
```
2.2 以使用 ContentType 为例：
大写字母开头的是类(type is class)，类里包含已赋值的变量，可用.来加载变量

```python3
from bigtools import ContentType

# 第二种写法
# from bigtools.default_data import ContentType
print(ContentType.app_json_headers)

# 发送post请求，获取数据
import requests
url = ''
data = ''
response = requests.post(url=url, data=data, headers=ContentType.app_json_headers)
print(response)
```
## 实现清单
```python3
"""加密验证工具"""
from bigtools.auth_tools import generate_api_key, compute_key_hmac, generate_hmac_signature, verify_hmac_signature
from bigtools.auth_tools import dict_to_urlsafe_b64, urlsafe_b64_to_dict, merge_method_dict, merge_str, SignatureGenerator
from bigtools.auth_tools import verify_signature, refresh_signature, build_jwt_token, build_and_encode_jwt_token
"""数据库工具"""
from bigtools.db_tools import mongo_client, async_mongo_client, MinioClinet, RedisClient
"""常用的一些数据"""
from bigtools.default_data import headers, random_headers, user_agents, ContentType, en_letter, numbers, DateType, RePattern
"""下载工具"""
from bigtools.download_tools import get_requests_session, download_stream_data, save_stream_data
from bigtools.download_tools import download_stream_data_async, save_stream_data_async
"""异常处理工具"""
from bigtools.exception_tools import RequestExceptionHandler, UniversalExceptionHandler
"""文件处理相关工具"""
from bigtools.file_tools import get_file_size, save_file, save_file_async, save_files_batch, load_file, load_file_async
"""hash工具"""
from bigtools.hash_tools import generate_hash_value, HASH_FUNCTIONS, HashGenerator
"""jieba工具"""
from bigtools.jieba_tools import get_keywords_from_text, get_keywords_from_text_async, jieba_tokenizer
"""json工具"""
from bigtools.json_tools import save_json_data, save_json_data_sync, save_json_data_async
from bigtools.json_tools import load_json_data, load_json_data_sync, load_json_data_async
from bigtools.json_tools import pretty_print_json, validate_json_schema, validate_json_string
from bigtools.json_tools import save_json_data_by_orjson, save_json_data_sync_by_orjson, save_json_data_async_by_orjson
from bigtools.json_tools import load_json_data_by_orjson, load_json_data_sync_by_orjson, load_json_data_async_by_orjson
from bigtools.json_tools import pretty_print_orjson, validate_orjson_string
"""日志工具"""
from bigtools.log_tools import set_log, SetLog
"""其他未分类的工具"""
from bigtools.more_tools import extract_ip, equally_split_list_or_str, load_config
from bigtools.more_tools import set_env, load_env, FuncTimer, time_sleep, count_str_start_or_end_word_num
from bigtools.more_tools import is_chinese, is_english, is_number, generate_random_string
"""路径处理工具"""
from bigtools.path_tools import check_make_dir, get_execution_dir, get_file_type, get_execution_file_name
"""相似度计算工具"""
from bigtools.similarity_tools import cosine_similarity, TfidfChineseRetriever, calculate_chinese_tfidf_similarity
from bigtools.similarity_tools import BM25ChineseRetriever, calculate_chinese_bm25_similarity
"""停用词大全"""
from bigtools.stop_words import stopwords
"""yaml工具"""
from bigtools.yaml_tools import load_yaml, load_all_yaml, write_yaml
```

