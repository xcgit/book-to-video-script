# book-to-video-script

把**已提取的书籍知识内容**（book-squeezer 榨取报告 / 读书笔记 / 要点清单）改写成**视频口播脚本文本**的 WorkBuddy 技能。

核心矛盾：视频要**吸引人**（钩子、节奏、故事），但知识类视频不能**偏离主题或夸大原意**。本技能用一套护栏 + 模板解决——让脚本抓人，但每一句话都能回溯到输入内容。

## 两条不可逾越的护栏

1. **不偏题**：每个段落都服务于输入内容的「核心论点（thesis）」，禁止为蹭热点把内容塞进无关叙事。
2. **不歪曲**：钩子可制造好奇，但不得编造书中没有的数据/结论/作者立场；增补的故事/类比必须明确标注 `[类比]`，不与作者原话混同。

## 安装

```bash
# 方式一：git clone 到 skills 目录
git clone https://github.com/xcgit/book-to-video-script.git ~/.workbuddy/skills/book-to-video-script

# 方式二：下载 zip 解压到 ~/.workbuddy/skills/book-to-video-script/
```

## 用法

- **触发词**：「把《XXX》做成 3 分钟视频脚本」「把这份读书笔记转成口播稿」「把提取内容转成 B 站风格长视频」。
- **可调参数**：视频类型（短 / 中 / 长）、时长、平台调性（抖音 / B站·YouTube / 视频号）、人称（第一/第三人称）、受众（小白 / 进阶 / 同行）。未指定时用默认值并显式说明。
- **辅助脚本**：`python scripts/build_script.py 报告.md --type short --platform douyin` 会抽取全书内核与知识点，生成带 `[画面]/[口播]/[时长]` 的骨架，钩子与故事留占位由你基于 `references/hook-story-bank.md` 填实。

## 目录结构

```
book-to-video-script/
├── SKILL.md                         # 主定义：7 步工作流 + 两条护栏
├── references/
│   ├── script-formats.md            # 短/中/长视频脚本模板与标注规范
│   └── hook-story-bank.md           # 钩子库 + 吸引力技法 + 故事增补规则 + 自检清单
└── scripts/
    └── build_script.py              # 骨架生成（仅标准库，无需联网）
```

## 与 book-squeezer 的关系

- **book-squeezer**：读书 → 结构化知识报告（分析阶段）。
- **book-to-video-script（本技能）**：知识报告 → 视频脚本（表达阶段）。
- 两者**独立**：本技能只读 book-squeezer 的输出，不反向修改它，也不重新榨取书。

## License

MIT
