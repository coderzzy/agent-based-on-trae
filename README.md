# llm-data-analysis 基于 AI IDE 的数据分析
```
思路：
1、使用 AI IDE 里 LLM 的 Agent 能力
2、配置好通用的 rules、MCP、Skills
3、完成生成代码，分析数据，产出报告

使用：
1、在 AI IDE 里打开项目
2、配置基础 python 环境
3、IDE 调整到 Agent 模式，输入 prompt 指令
4、等待 Agent 完成，生成最终报告
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
```
