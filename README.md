# Agent Based On TRAE | 基于 TRAE 的 Agent 任务
```
思路：
1、使用 TRAE 里 LLM 的 Agent 能力
2、配置好通用的 rules、MCP、Skills
3、完成主要基于代码能力的各种 Agent 任务（如数据分析、图文视频剪辑等）

使用：
1、在 TRAE 里打开项目
2、使用 uv 配置基础 python 环境，并设置 TRAE 的开发环境为 .venv/bin/python
3、把 输入文件 放到 input/ 目录下
4、TRAE 调整到 Build / SOLO 模式，输入 prompt 指令
5、等待 TRAE 完成，生成产物
6、让 Agent 总结本次任务为 prompt_templates/skills 等，放到libs目录下
```


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

# 运行脚本
python xxx.py

# uv 依赖 跟 requirements.txt 保持一致
uv pip list --format=freeze > requirements.txt
```
