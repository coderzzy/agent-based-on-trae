# 执行规则
- 严格按照步骤来进行，step by step 是为了细化任务提高任务完成成功率和质量，严禁一次完成多个 Step，跳步影响任务质量。

# 网络环境相关
- 如果网络环境有问题，bash命令执行卡住或者被人为打断，尝试设置代理后重试：export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890

# python 环境相关规则
### 激活环境：
- source .venv/bin/activate

### 安装依赖：
- 先激活环境后，再编辑 requirements.txt，再执行 "uv pip install -r requirements.txt"
- 必须按照 requirements.txt 安装依赖，严禁直接安装依赖包！！！

### 运行脚本：
- 先激活环境后，再执行 python xxx.py
