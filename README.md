# llm-data-analysis
摸索使用大模型进行数据分析
- 思路：
    - 1. 大模型生成中间代码
    - 2. 由中间代码完成最终的数据分析和报告产出
- 工具
    - TRAE + MCP + Skills


## 环境与启动（python项目）
```
# 安装uv，方法一
curl -Ls https://astral.sh/uv/install.sh | bash
uv --version

# 创建虚拟环境
uv venv         
# 激活虚拟环境
source .venv/bin/activate  
# 安装依赖
uv pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 运行服务
python run.py  
```
