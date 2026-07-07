#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_script.py — 把书籍/知识提取稿快速生成「视频脚本骨架」。

用法：
  python build_script.py "报告.md" --type medium --platform bilibili
  python build_script.py "笔记.md" --type short --person first --out ./out

说明：
  - 仅用标准库，无需联网、无需第三方依赖。
  - 从输入 markdown 中启发式抽取：标题、核心论点(thesis)、知识点列表。
  - 套用 book-to-video-script 的模板，生成带 [画面]/[口播]/[时长] 标注的骨架。
  - 钩子与故事为「占位 + 提示」，由人工/AI 基于 hook-story-bank.md 精修填充。
  - 本脚本不替代创作，只把重复的结构搭建自动化，避免每次重写模板。

依赖抽取质量：输入越接近 book-squeezer 报告格式（含「第 0 层：全书内核」「### 知识点 N」），
抽取越准；纯笔记也能兜底（取首标题为 thesis，取各级标题为知识点）。
"""
import argparse
import re
import sys
from pathlib import Path

TYPE_DEFAULTS = {
    "short": {"label": "短视频", "dur": "约 75s", "pts": 1},
    "medium": {"label": "中视频", "dur": "约 6min", "pts": 4},
    "long": {"label": "长视频", "dur": "约 20min", "pts": 8},
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def extract_title(md: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    if m:
        t = m.group(1).strip()
        t = t.replace("《", "").replace("》", "").strip()
        # 去掉「深度榨取报告」等后缀
        t = re.sub(r"深度榨取报告|榨取报告|报告$", "", t).strip()
        if t:
            return t
    return fallback


def extract_thesis(md: str) -> str:
    # 优先匹配 book-squeezer 报告的「全书内核」
    m = re.search(r"全书内核\**\s*[:：]\s*(.+)", md)
    if m:
        return m.group(1).strip().strip("。").strip()
    # 其次匹配「核心论点 / 一句话」
    m = re.search(r"(核心论点|全书主张|核心主张)\**\s*[:：]\s*(.+)", md)
    if m:
        return m.group(2).strip().strip("。").strip()
    # 兜底：取第一个非空段落（去掉 markdown 标记）
    for line in md.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and len(line) > 8:
            return re.sub(r"[*_`#]", "", line)[:60]
    return "（请从输入中归纳一句话核心论点，作为不偏题锚点）"


def extract_points(md: str, limit: int) -> list:
    pts = []
    # book-squeezer 风格：### 知识点 N：名称
    for m in re.finditer(r"^###\s*知识点\s*\d*\s*[:：]?\s*(.+)$", md, re.MULTILINE):
        name = m.group(1).strip()
        name = re.sub(r"\s*[🟥🟧🟨🟦].*$", "", name).strip()
        if name:
            pts.append(name)
    # 兜底：用二级标题
    if not pts:
        for m in re.finditer(r"^##\s+(.+)$", md, re.MULTILINE):
            name = m.group(1).strip()
            if "层" not in name and "元信息" not in name and "总结" not in name:
                pts.append(re.sub(r"[*_`]", "", name))
    # 再兜底：三级标题
    if not pts:
        for m in re.finditer(r"^###\s+(.+)$", md, re.MULTILINE):
            pts.append(re.sub(r"[*_`]", "", m.group(1).strip()))
    # 去重保序
    seen, out = set(), []
    for p in pts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out[:limit] if limit else out


def build(out_type: str, platform: str, person: str, title: str, thesis: str, points: list) -> str:
    cfg = TYPE_DEFAULTS.get(out_type, TYPE_DEFAULTS["medium"])
    person_word = "我" if person == "first" else ("咱们" if person == "third" else "你")
    L = []
    L.append(f"# 《{title}》{cfg['label']}脚本（{platform} 风 / {cfg['dur']}）")
    L.append("")
    L.append(f"> 核心论点(thesis，不偏题锚点)：{thesis}")
    L.append(">")
    L.append("> ⚠️ 钩子与故事为占位，请基于 references/hook-story-bank.md 精修：")
    L.append("> - 钩子必须来自内容，禁止虚构；")
    L.append("> - 增补故事/类比加 [类比] 标注，不冒充原书。")
    L.append("")
    L.append("---")
    L.append("")

    if out_type == "short":
        L.append("[画面] 黑屏，大字标题弹出：[在此填钩子式提问，来自内容]")
        L.append(f"[口播] [钩子 5s：{person_word}先抛一个内容里最反直觉的点，不剧透结论]")
        L.append("[时长] 5s")
        L.append("[BGM] 第 4 秒节奏点切入")
        L.append("")
        pt = points[0] if points else "（核心观点）"
        L.append(f"[画面] 博主出镜 / 「{pt}」字卡")
        L.append(f"[口播] [核心观点 20s：用大白话讲清「{pt}」]")
        L.append("[时长] 20s")
        L.append("")
        L.append("[画面] 生活化画面 / 动画示意")
        L.append(f"[口播] [故事或[类比]：把「{pt}」落到具体场景 40s]")
        L.append("[时长] 40s")
        L.append("")
        L.append("[画面] 金句定格")
        L.append(f"[口播] [反转/金句 10s：把观点收成一句能截图的话，回扣：{thesis}]")
        L.append("[时长] 10s")
        L.append("")
        L.append("[画面] 结尾卡片：关注 + 下期预告")
        L.append(f"[口播] [CTA 10s：关注 / 评论区聊聊你对「{pt}」的看法]")
        L.append("[时长] 10s")
    else:
        L.append("## 片头 Hook")
        L.append("[画面] [强视觉开场]")
        L.append(f"[口播] [钩子 30s：用内容里最反直觉的一点开场，不剧透结论]")
        L.append("[时长] 30s")
        L.append("[BGM] 主旋律进入")
        L.append("")
        L.append("## 第一幕：立论")
        L.append(f"[口播] [抛出 thesis：这支视频想说清楚——{thesis}]")
        L.append("[画面] 论点字卡")
        L.append("[时长] 60s")
        L.append("")
        L.append("## 第二幕：主体")
        chosen = points[: cfg["pts"]] if points else [f"（知识点 {i+1}）" for i in range(cfg["pts"])]
        for i, pt in enumerate(chosen, 1):
            L.append(f"### 知识点 {i}：{pt}")
            L.append(f"[画面] [对应画面]")
            L.append(f"[口播] [观点 45s：大白话定义「{pt}」+ 为什么重要]")
            L.append(f"[口播] [故事/案例：书里真实案例 或 [类比] 增补类比 60s]")
            L.append(f"[口播] [回扣 thesis：这点如何支撑「{thesis}」15s]")
            L.append("[时长] 120s")
            L.append("")
        L.append("## 第三幕：升华与收尾")
        L.append(f"[口播] [把各点串成一句话行动建议 / 认知升级，回扣 {thesis}]")
        L.append("[画面] 总结字卡")
        L.append("[时长] 60s")
        L.append(f"[口播] [CTA：关注 + 评论区提问 + 下期预告]")
        L.append("[时长] 30s")
        if out_type == "long":
            L.append("")
            L.append("> 注：长视频建议按子论点拆章，每章复用上述三幕结构，章间用 callback 衔接。")

    L.append("")
    L.append("---")
    L.append("生成说明：本骨架由 build_script.py 自动生成，钩子/故事需人工基于 hook-story-bank.md 精修并通过护栏自检。")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="把提取稿生成视频脚本骨架")
    ap.add_argument("input", help="输入 markdown（榨取报告 / 笔记）")
    ap.add_argument("--type", choices=["short", "medium", "long"], default="medium")
    ap.add_argument("--platform", default="bilibili/YouTube")
    ap.add_argument("--person", choices=["first", "third", "you"], default="first",
                    help="first=我/博主视角, third=咱们/解说, you=你/对话体")
    ap.add_argument("--out", default=None, help="输出路径（默认 当前目录/{标题}-视频脚本-{type}.md）")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"[错误] 找不到输入文件：{src}", file=sys.stderr)
        sys.exit(2)

    md = read_text(src)
    title = extract_title(md, src.stem)
    thesis = extract_thesis(md)
    points = extract_points(md, TYPE_DEFAULTS[args.type]["pts"])

    script = build(args.type, args.platform, args.person, title, thesis, points)

    out_path = Path(args.out) if args.out else Path(f"{title}-视频脚本-{args.type}.md")
    out_path.write_text(script, encoding="utf-8")
    print(f"[完成] 已生成脚本骨架：{out_path}")
    print(f"  标题={title}")
    print(f"  核心论点={thesis}")
    print(f"  抽取知识点={len(points)} 个：{points if points else '（未抽到，请检查输入格式）'}")


if __name__ == "__main__":
    main()
