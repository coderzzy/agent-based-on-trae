input 目录下已有若干 CSV 数据文件，你需要基于这些数据完成完整的数据分析，并生成一份可用于内容发布的数据分析报告。

你可以编写新的 Python 脚本进行数据处理、统计分析和可视化。

目标是生成一份 **图文并茂、具有洞察的数据分析报告**，内容质量达到可以发布到公众号或内容平台的长文水平。

---

# 输出文件

需要生成以下内容：

1️⃣ Markdown 长文报告

output/report.md

用于公众号文章。

2️⃣ HTML 图表浏览页

output/report.html

用于查看、下载图表。

3️⃣ Python 数据分析脚本

output/analysis.py

4️⃣ 图表图片

output/images/

---

# 项目目录结构

最终结构类似：

project_root/
│
├─ xxx/                # 原始 CSV 数据
│
├─ output/
│   ├─ images/
│   │   ├─ chart1_landscape.png
│   │   ├─ chart1_portrait.png
│   │   ├─ chart2_landscape.png
│   │   └─ chart2_portrait.png
│   │
│   ├─ analysis.py
│   ├─ report.md
│   └─ report.html
│
└─ requirements.txt    # 在项目根目录

---

# requirements.txt 规则

如果分析代码新增 Python 依赖：

请更新 **根目录的 requirements.txt**。

不要在 output 目录生成新的 requirements 文件。

---

# 数据分析要求

进行完整的数据探索与分析，包括但不限于：

* 数据概览
* 数据清洗
* 核心指标统计
* 趋势分析
* 分布分析
* Top / Ranking 分析
* 类别对比
* 相关性分析（如适用）
* 异常值
* 有趣现象
* 关键洞察（insight）

不要只描述数据，要解释：

* 为什么会这样
* 有什么含义
* 能得出什么结论

---

# 图表生成要求

每一个重要分析都要生成图表。

每张图生成 **两种比例版本**：

公众号横版图：

1600 × 900

文件名：

xxx_landscape.png

小红书竖版图：

1080 × 1920

文件名：

xxx_portrait.png

图片输出到：

output/images/

---

# 图表 UI 设计要求（非常重要）

图表必须视觉美观，适合内容传播。

不要使用 matplotlib 默认样式。

要求：

统一风格
简洁配色
清晰字体
适合移动端阅读

推荐做法：

使用 seaborn theme

例如：

seaborn whitegrid / ticks

字体大小建议：

标题 28+
轴标签 18+
刻度 14+

---

# 中文字体要求

图表必须正确显示中文。

优先使用以下字体：

Noto Sans CJK SC
PingFang SC
Microsoft YaHei
SimHei

先检查系统已安装的字体，决定使用现有字体还是额外安装。

Python 示例：
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC','PingFang SC','Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

---

# 图表风格要求

图表应类似：

科技媒体 / 数据媒体 / 咨询报告

例如：

36氪
晚点
麦肯锡报告
数据新闻

建议：

* 高对比色
* 大标题
* 留白
* 数据标签
* 清晰图例

---

# Insight 图（重要）

在关键发现部分额外生成 **Insight 卡片图**：

尺寸：

1080 × 1080

内容：

一句总结洞察
+
关键数字

示例：

"2024 年用户增长 230%，创历史新高"

这种图适合：

小红书
社交媒体传播

---

# 图表数量

建议：

8 — 15 张核心图表

不要生成大量无意义图表。

---

# report.md（公众号长文）

生成一篇完整 Markdown 报告。

结构建议：

标题

导语

数据来源说明

数据概览

关键发现

深度分析（多个章节）

图表解读

Insight 总结

结论

---

# Markdown 图表引用

示例：

![用户增长趋势](images/user_growth_landscape.png)

每张图下方必须配说明。

---

# report.html（图表浏览页）

生成一个 HTML 页面用于：

浏览所有图表
下载图片

页面内容：

标题

使用说明

图表列表

每个图表模块包含：

图表标题
图表说明

公众号横图

小红书竖图

Insight 卡片（如果有）

所有图片支持：

右键保存下载。

---

# HTML 页面顶部说明

如何使用图片：

公众号

使用横版图（landscape）

小红书

使用竖版图（portrait）

社交媒体

可以使用 Insight 卡片

下载方式：

右键图片保存。

---

# Python 脚本要求

编写脚本完成：

数据读取

数据清洗

数据分析

图表生成

图片导出

脚本可重复运行。

---

# 代码规范

* 结构清晰
* 有必要注释
* 输出路径统一使用 output/
* 图表生成逻辑模块化

---

# 最终目标

生成一套完整的数据报告资产：

公众号长文

小红书竖版图

公众号横版图

Insight 卡片

HTML 图表下载页

分析脚本

所有内容结构清晰、分析深入、图表美观。
