# fastmongo
![](https://img.shields.io/badge/Python-3.8.6-green.svg)
![](https://img.shields.io/badge/pymongo-3.11.2-green.svg)

#### 介绍
快速使用pymongo

#### 软件架构
软件架构说明


#### 安装教程

1.  pip安装
```shell script
pip3 install fastmongo
```
2.  pip安装（使用阿里云镜像加速）
```shell script
pip3 install fastmongo -i https://mirrors.aliyun.com/pypi/simple
```

#### 使用说明

1.  demo
```python
import fastmongo
query_res = fastmongo.safe_find(db='test', collection='test')
```

2. 环境文件
- 默认文件名：local.mongo.env
- 文件构成：
  - connect_str=XXX：连接字符串，若有此字段，将优先使用，否则将使用下面字段拼接connect_str；
  - host=XXX：若不填，默认值为localhost，将自动拼接connect_str；
  - port=XXX：若不填，默认值为27017，将自动拼接connect_str；
  - username=XXX：若不填，默认值为root，将自动拼接connect_str；
  - password=XXX：若不填，默认值为''，将自动拼接connect_str；
