# 使用命令 
## 初次使用（准备）
### 创建环境
```python
conda create -n paper_extract 'python=3.12' -y
conda activate paper_extract
```
### 安装依赖
```
pip install -U magic-pdf[full] -i https://mirrors.aliyun.com/pypi/simple
pip install -r requirements.txt

```
### 下载MinerU预训练模型
方法一：从 Hugging Face 下载模型
```
pip install huggingface_hub
wget https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/scripts/download_models_hf.py -O download_models_hf.py
python download_models_hf.py
```
方法二：从 ModelScope 下载模型
```
pip install modelscope
wget https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/scripts/download_models.py -O download_models.py
python download_models.py
```
## 直接使用
### 第一步：初步处理pdf
```
magic-pdf -p 待处理pdf路径 -o 输出结果路径
```
### 第二步：医药分子论文信息处理
这一步需要将项目根目录下的main.py内的参数进行设置
```
ROOT_DIRS = "第一步处理后的文件最外层根目录"
MODE = "normal"
```
执行处理命令
```
python main.py
```
## ！！！注意事项
### 1.部分权重信息未提供
医药分子处理部分的yolo模型是未有提供的，有兴趣可以自己再训练，根据yolo11的预训练模型。
### 2.部分文件路径需要根据自己实际进行修改
processor.py的部分内容，比如提示词的路径，需要自己根据需求再修改，此处项目文件内不提供prompts文件。
### 3.env文件部分内容空白
调用llm的api_key和base_url需要根据自己的情况进行补充填写
