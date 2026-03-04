from __future__ import annotations

import base64
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class StrategyMetric:
    strategy: str
    auc: float
    makespan: float
    restored_kw: float


@dataclass(frozen=True)
class ReportSummary:
    best_strategy: str
    best_auc: float
    worst_strategy: str
    worst_auc: float
    restored_kw: float
    strategy_rows: List[StrategyMetric]


def summarize_results(results: List[Dict[str, object]]) -> ReportSummary:
    ranked = sorted(results, key=lambda x: float(x["auc"]), reverse=True)
    rows = [
        StrategyMetric(
            strategy=str(r["strategy"]),
            auc=float(r["auc"]),
            makespan=float(r["makespan"]),
            restored_kw=float(r["final_restored_kw"]),
        )
        for r in ranked
    ]
    return ReportSummary(
        best_strategy=rows[0].strategy,
        best_auc=rows[0].auc,
        worst_strategy=rows[-1].strategy,
        worst_auc=rows[-1].auc,
        restored_kw=rows[0].restored_kw,
        strategy_rows=rows,
    )


def upload_images_to_imgbb(image_paths: List[Path], api_key: str) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for p in image_paths:
        raw = p.read_bytes()
        payload = urllib.parse.urlencode(
            {"key": api_key, "image": base64.b64encode(raw).decode("ascii"), "name": p.name}
        ).encode("utf-8")
        req = urllib.request.Request("https://api.imgbb.com/1/upload", data=payload, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data.get("success"):
            raise RuntimeError(f"imgbb upload failed for {p.name}: {data}")
        out[p.name] = {
            "url": data["data"]["url"],
            "display_url": data["data"]["display_url"],
            "delete_url": data["data"]["delete_url"],
        }
    return out


def _table_zh(summary: ReportSummary) -> str:
    lines = ["| 策略 | AUC | 工期(h) | 最终恢复负荷(kW) |", "|---|---:|---:|---:|"]
    for r in summary.strategy_rows:
        lines.append(f"| {r.strategy} | {r.auc:.2f} | {r.makespan:.2f} | {r.restored_kw:.1f} |")
    return "\n".join(lines)


def _table_en(summary: ReportSummary) -> str:
    lines = ["| Strategy | AUC | Makespan(h) | Final Restored(kW) |", "|---|---:|---:|---:|"]
    for r in summary.strategy_rows:
        lines.append(f"| {r.strategy} | {r.auc:.2f} | {r.makespan:.2f} | {r.restored_kw:.1f} |")
    return "\n".join(lines)


def _figure_explanations_zh() -> str:
    return """- `ch8_lsd_curves_*.png`：展示恢复负荷的阶梯增长过程，越早抬升意味着越高 AUC。
- `ch8_auc_bar_*.png`：直接对比各策略累计恢复收益；可快速定位最优策略。
- `ch6_road_topology_*.png`：识别受损道路与关键接入点，解释可达性约束来源。
- `ch6_power_topology_*.png`：展示农村树状配电网中故障线位置与关键设施节点。
- `ch6_joint_topology_overview_*.png`：双图并列用于说明道路与电网的空间耦合关系。
- `ch6_road_power_overlay_*.png`：同图叠加更直观地解释“道路可达性 → 电力任务顺序”的影响链。"""


def _figure_explanations_en() -> str:
    return """- `ch8_lsd_curves_*.png`: step-wise restored-load trajectory; earlier jumps imply larger AUC.
- `ch8_auc_bar_*.png`: direct cumulative-benefit comparison across strategies.
- `ch6_road_topology_*.png`: damaged roads and key access nodes explain accessibility constraints.
- `ch6_power_topology_*.png`: radial rural grid with faulted branches and critical facilities.
- `ch6_joint_topology_overview_*.png`: side-by-side topology coupling view (transport vs power).
- `ch6_road_power_overlay_*.png`: single-map overlay to explain accessibility-to-repair-order causality."""


def _img_md(name: str, links: Optional[Dict[str, Dict[str, str]]]) -> str:
    if not links or name not in links:
        return f"`{name}`"
    return f"![{name}]({links[name]['display_url']})"


def render_markdown_report_zh(
    summary: ReportSummary,
    run_url: str,
    figure_paths: List[Path],
    hosted_links: Optional[Dict[str, Dict[str, str]]] = None,
) -> str:
    figs = "\n".join([f"- `{p.name}`" for p in figure_paths])
    picks = {
        "lsd": "ch8_lsd_curves_zh.png",
        "auc": "ch8_auc_bar_zh.png",
        "road": "ch6_road_topology_zh.png",
        "power": "ch6_power_topology_zh.png",
        "joint": "ch6_joint_topology_overview_zh.png",
        "overlay": "ch6_road_power_overlay_zh.png",
    }
    return f"""# 协同抢修实验报告（自动生成）

## 1. 运行信息
- Run URL: {run_url}
- 实验对象：交通-电网协同抢修策略（S1~S4）

## 2. 关键结论
- 最优策略：**{summary.best_strategy}**（AUC={summary.best_auc:.2f}）
- 最弱策略：**{summary.worst_strategy}**（AUC={summary.worst_auc:.2f}）
- 最终恢复负荷：**{summary.restored_kw:.1f} kW**

## 3. 指标总表
{_table_zh(summary)}

## 4. 各图表解释
### 4.1 LSD 恢复曲线
{_img_md(picks['lsd'], hosted_links)}

### 4.2 AUC 柱状图
{_img_md(picks['auc'], hosted_links)}

### 4.3 路网拓扑
{_img_md(picks['road'], hosted_links)}

### 4.4 电网拓扑
{_img_md(picks['power'], hosted_links)}

### 4.5 双网并列总览
{_img_md(picks['joint'], hosted_links)}

### 4.6 道路-电网叠加图
{_img_md(picks['overlay'], hosted_links)}

{_figure_explanations_zh()}

## 5. 解释性分析（业务视角）
- **早期恢复优先性**：S3/S4 在关键负荷（医院/安置点/指挥中心）上更早恢复，因而 AUC 明显领先。
- **可达性约束传导**：道路层受损边会推迟电力任务启动时刻，直接影响恢复曲线前半段斜率。
- **策略差异本质**：S1 偏顺序执行，安全但慢；S2 并行改善中期效率；S3/S4 强调关键任务优先，提升早期收益。

## 6. 图件清单
{figs}
"""


def render_markdown_report_en(
    summary: ReportSummary,
    run_url: str,
    figure_paths: List[Path],
    hosted_links: Optional[Dict[str, Dict[str, str]]] = None,
) -> str:
    figs = "\n".join([f"- `{p.name}`" for p in figure_paths])
    picks = {
        "lsd": "ch8_lsd_curves_en.png",
        "auc": "ch8_auc_bar_en.png",
        "road": "ch6_road_topology_en.png",
        "power": "ch6_power_topology_en.png",
        "joint": "ch6_joint_topology_overview_en.png",
        "overlay": "ch6_road_power_overlay_en.png",
    }
    return f"""# Coordinated Repair Experiment Report (Auto-generated)

## 1. Run information
- Run URL: {run_url}
- Scope: road-power coordinated repair strategy comparison (S1~S4)

## 2. Key findings
- Best strategy: **{summary.best_strategy}** (AUC={summary.best_auc:.2f})
- Lowest strategy: **{summary.worst_strategy}** (AUC={summary.worst_auc:.2f})
- Final restored load: **{summary.restored_kw:.1f} kW**

## 3. Metrics table
{_table_en(summary)}

## 4. Figure-by-figure interpretation
### 4.1 LSD restoration curves
{_img_md(picks['lsd'], hosted_links)}

### 4.2 AUC comparison
{_img_md(picks['auc'], hosted_links)}

### 4.3 Road topology
{_img_md(picks['road'], hosted_links)}

### 4.4 Power topology
{_img_md(picks['power'], hosted_links)}

### 4.5 Side-by-side joint overview
{_img_md(picks['joint'], hosted_links)}

### 4.6 Overlay topology
{_img_md(picks['overlay'], hosted_links)}

{_figure_explanations_en()}

## 5. Explainability notes (operational view)
- **Early restoration priority**: S3/S4 recover critical facilities earlier, yielding larger AUC gains.
- **Accessibility propagation**: damaged transport links delay power task start times and flatten early LSD growth.
- **Strategy trade-off**: S1 is conservative and slower; S2 improves parallelism; S3/S4 prioritize critical tasks for earlier gains.

## 6. Figure list
{figs}
"""


def save_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _markdown_report_block(wr, text: str):
    """Use MarkdownBlock for report blocks."""
    return wr.MarkdownBlock(text)


def create_wandb_report(
    *,
    entity: str,
    project: str,
    run_url: str,
    summary: ReportSummary,
    report_title: str,
    markdown_zh: str = "",
    markdown_en: str = "",
) -> Optional[str]:
    """Create a W&B report page that syncs only Chinese markdown block as requested."""
    try:
        from wandb.apis import reports as wr

        report = wr.Report(
            project=project,
            entity=entity,
            title=report_title,
            description=f"Run URL: {run_url}",
            blocks=[
                wr.H1("Traffic-Power Coordinated Repair Report (ZH Synced)"),
                wr.MarkdownBlock(markdown_zh or "_No Chinese markdown provided._"),
            ],
        )
        report.save(draft=False)
        return getattr(report, "url", None)
    except Exception:
        return None
