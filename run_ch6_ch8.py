from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from sim.ch6_ch8 import export_ch6_ch8_dataset_csv, run_ch6_ch8_experiment
from sim.wandb_reporting import (
    create_wandb_report,
    render_markdown_report_en,
    render_markdown_report_zh,
    save_text,
    summarize_results,
    upload_images_to_imgbb,
)

FONT_DIR = Path("assets/fonts")
ZH_FONT_PATH = FONT_DIR / "NotoSansSC-Regular.otf"
ZH_FONT_URL = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"


def _ensure_chinese_font() -> str:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    if not ZH_FONT_PATH.exists():
        urllib.request.urlretrieve(ZH_FONT_URL, ZH_FONT_PATH)
    fm.fontManager.addfont(str(ZH_FONT_PATH))
    return fm.FontProperties(fname=str(ZH_FONT_PATH)).get_name()


def _labels(lang: str) -> Dict[str, str]:
    if lang == "zh":
        return {
            "time": "时间 (小时)",
            "restored": "LSD(t): 已恢复负荷 (kW)",
            "strategy": "策略",
            "lsd_title": "策略对比：LSD恢复阶梯曲线",
            "auc_title": "策略对比：AUC 指标",
            "road_title": "交通网络拓扑（含环路）",
            "power_title": "农村配电网拓扑（树状）",
            "joint_title": "协同抢修案例拓扑总览",
            "overlay_title": "交通-电网同图叠加拓扑",
            "open_road": "可通行道路",
            "damaged_road": "受损道路",
            "road_junc": "普通路口",
            "road_key": "关键接入/基地",
            "healthy_line": "正常线路",
            "fault_line": "故障线路",
            "substation": "变电站",
            "feeder": "馈线节点",
            "rural_load": "农村负荷节点",
            "facility": "关键设施",
            "x": "X 坐标 (km)",
            "y": "Y 坐标 (km)",
        }
    return {
        "time": "Time (hour)",
        "restored": "LSD(t): Restored load (kW)",
        "strategy": "Strategy",
        "lsd_title": "Strategy comparison: LSD(t) restoration curve",
        "auc_title": "Strategy comparison: AUC metric",
        "road_title": "Transport network topology (with cycles)",
        "power_title": "Rural distribution grid topology (radial tree)",
        "joint_title": "Joint topology overview for coordinated repair case",
        "overlay_title": "Overlay topology: transport + power",
        "open_road": "Open road",
        "damaged_road": "Damaged road",
        "road_junc": "Road junction",
        "road_key": "Critical access/depot",
        "healthy_line": "Healthy line",
        "fault_line": "Faulted line",
        "substation": "Substation",
        "feeder": "Feeder node",
        "rural_load": "Rural load node",
        "facility": "Critical facility",
        "x": "X coordinate (km)",
        "y": "Y coordinate (km)",
    }


def _apply_font(lang: str) -> None:
    if lang == "zh":
        name = _ensure_chinese_font()
        plt.rcParams["font.family"] = [name]
    plt.rcParams["axes.unicode_minus"] = False


def _plot_lsd(results, outdir: Path, lang: str) -> Path:
    plt.style.use("seaborn-v0_8-whitegrid")
    _apply_font(lang)
    t = _labels(lang)
    plt.figure(figsize=(9, 5.5))
    palette = {"S1": "#4c78a8", "S2": "#f58518", "S3": "#54a24b", "S4": "#b279a2"}
    for res in results:
        xs = [x for x, _ in res["history"]]
        ys = [y for _, y in res["history"]]
        plt.step(xs, ys, where="post", linewidth=2.5, color=palette[res["strategy"]], label=f"{res['strategy']}  AUC={res['auc']:.0f}")
    plt.xlabel(t["time"])
    plt.ylabel(t["restored"])
    plt.title(t["lsd_title"])
    plt.legend(title=t["strategy"], frameon=True)
    out = outdir / f"ch8_lsd_curves_{lang}.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close()
    return out


def _plot_auc(results, outdir: Path, lang: str) -> Path:
    plt.style.use("seaborn-v0_8-whitegrid")
    _apply_font(lang)
    t = _labels(lang)
    plt.figure(figsize=(8, 4.8))
    names = [r["strategy"] for r in results]
    aucs = [r["auc"] for r in results]
    bars = plt.bar(names, aucs, color=["#4c78a8", "#f58518", "#54a24b", "#b279a2"])
    for b, v in zip(bars, aucs):
        plt.text(b.get_x() + b.get_width() / 2, v + 30, f"{v:.0f}", ha="center", va="bottom", fontsize=9)
    plt.ylabel("AUC")
    plt.title(t["auc_title"])
    out = outdir / f"ch8_auc_bar_{lang}.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close()
    return out


def _road_pos_role(dataset):
    return ({n.node_id: (n.x_km, n.y_km) for n in dataset["road_nodes"]}, {n.node_id: n.role for n in dataset["road_nodes"]})


def _power_pos_kind(dataset):
    pos = {
        "P1": (0, 0), "P2": (10, 0), "P3": (20, 6), "P4": (20, -6), "P5": (30, 10), "P6": (30, 3),
        "P7": (30, -3), "P8": (30, -10), "P9": (40, 12), "P10": (40, 4), "P11": (40, -4), "P12": (40, -12),
    }
    return pos, {n.node_id: n.kind for n in dataset["power_nodes"]}


def _plot_road_topology(dataset, outdir: Path, lang: str) -> Path:
    plt.style.use("seaborn-v0_8-white")
    _apply_font(lang)
    t = _labels(lang)
    pos, role = _road_pos_role(dataset)
    plt.figure(figsize=(10, 6))
    for e in dataset["road_edges"]:
        x1, y1 = pos[e.u]
        x2, y2 = pos[e.v]
        plt.plot([x1, x2], [y1, y2], color="#d62728" if e.is_damaged else "#7f7f7f", linewidth=3.0 if e.is_damaged else 2.0, alpha=0.92)

    for nid, (x, y) in pos.items():
        marker = "s" if role[nid] == "depot" else "o"
        size = 70 if role[nid] != "junction" else 40
        color = "#1f77b4" if role[nid] == "junction" else "#2ca02c"
        plt.scatter([x], [y], marker=marker, s=size, color=color, edgecolors="black", linewidths=0.6, zorder=3)
        plt.text(x + 0.35, y + 0.2, nid, fontsize=8)

    legend_items = [
        Line2D([0], [0], color="#7f7f7f", lw=2, label=t["open_road"]),
        Line2D([0], [0], color="#d62728", lw=3, label=t["damaged_road"]),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#1f77b4", markeredgecolor="black", markersize=7, label=t["road_junc"]),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#2ca02c", markeredgecolor="black", markersize=8, label=t["road_key"]),
    ]
    plt.legend(handles=legend_items, loc="upper left", frameon=True)
    plt.title(t["road_title"])
    plt.xlabel(t["x"])
    plt.ylabel(t["y"])
    plt.grid(alpha=0.25, linestyle="--")
    out = outdir / f"ch6_road_topology_{lang}.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close()
    return out


def _plot_power_topology(dataset, outdir: Path, lang: str) -> Path:
    plt.style.use("seaborn-v0_8-white")
    _apply_font(lang)
    t = _labels(lang)
    pos, _ = _power_pos_kind(dataset)
    plt.figure(figsize=(10, 5.8))
    for l in dataset["power_lines"]:
        x1, y1 = pos[l.u]
        x2, y2 = pos[l.v]
        plt.plot([x1, x2], [y1, y2], color="#d62728" if l.is_fault else "#1f77b4", linewidth=3.0 if l.is_fault else 2.0, alpha=0.95)

    node_style = {
        "substation": ("#9467bd", "s", 120),
        "feeder": ("#17becf", "o", 80),
        "village_load": ("#2ca02c", "o", 60),
        "hospital": ("#e377c2", "^", 95),
        "shelter": ("#ff7f0e", "^", 95),
        "command_center": ("#bcbd22", "^", 95),
        "school": ("#8c564b", "^", 95),
    }
    for n in dataset["power_nodes"]:
        x, y = pos[n.node_id]
        c, m, s = node_style[n.kind]
        plt.scatter([x], [y], color=c, marker=m, s=s, edgecolors="black", linewidths=0.7, zorder=3)
        plt.text(x + 0.5, y + 0.3, n.node_id, fontsize=8)

    legend_items = [
        Line2D([0], [0], color="#1f77b4", lw=2, label=t["healthy_line"]),
        Line2D([0], [0], color="#d62728", lw=3, label=t["fault_line"]),
        Patch(facecolor="#9467bd", edgecolor="black", label=t["substation"]),
        Patch(facecolor="#17becf", edgecolor="black", label=t["feeder"]),
        Patch(facecolor="#2ca02c", edgecolor="black", label=t["rural_load"]),
        Patch(facecolor="#e377c2", edgecolor="black", label=t["facility"]),
    ]
    plt.legend(handles=legend_items, loc="upper left", frameon=True)
    plt.title(t["power_title"])
    plt.axis("off")
    out = outdir / f"ch6_power_topology_{lang}.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close()
    return out


def _plot_joint_topology(dataset, outdir: Path, lang: str) -> Path:
    plt.style.use("seaborn-v0_8-whitegrid")
    _apply_font(lang)
    t = _labels(lang)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2))

    pos_r, _ = _road_pos_role(dataset)
    for e in dataset["road_edges"]:
        x1, y1 = pos_r[e.u]
        x2, y2 = pos_r[e.v]
        axes[0].plot([x1, x2], [y1, y2], color="#d62728" if e.is_damaged else "#7f7f7f", linewidth=2.2)
    axes[0].scatter([v[0] for v in pos_r.values()], [v[1] for v in pos_r.values()], s=20, c="#1f77b4")
    axes[0].set_title(t["road_title"])
    axes[0].set_xlabel(t["x"])
    axes[0].set_ylabel(t["y"])

    pos_p, _ = _power_pos_kind(dataset)
    for l in dataset["power_lines"]:
        x1, y1 = pos_p[l.u]
        x2, y2 = pos_p[l.v]
        axes[1].plot([x1, x2], [y1, y2], color="#d62728" if l.is_fault else "#1f77b4", linewidth=2.2)
    axes[1].scatter([v[0] for v in pos_p.values()], [v[1] for v in pos_p.values()], s=24, c="#2ca02c")
    axes[1].set_title(t["power_title"])
    axes[1].axis("off")

    fig.suptitle(t["joint_title"])
    out = outdir / f"ch6_joint_topology_overview_{lang}.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close()
    return out


def _normalize(points: List[Tuple[float, float]], x_range: Tuple[float, float], y_range: Tuple[float, float]):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    nx = [(x - xmin) / (xmax - xmin) * (x_range[1] - x_range[0]) + x_range[0] for x in xs]
    ny = [(y - ymin) / (ymax - ymin) * (y_range[1] - y_range[0]) + y_range[0] for y in ys]
    return list(zip(nx, ny))


def _plot_overlay_topology(dataset, outdir: Path, lang: str) -> Path:
    plt.style.use("seaborn-v0_8-white")
    _apply_font(lang)
    t = _labels(lang)
    plt.figure(figsize=(11, 7))

    rpos, _ = _road_pos_role(dataset)
    road_x = [x for x, _ in rpos.values()]
    road_y = [y for _, y in rpos.values()]
    xlim = (min(road_x), max(road_x))
    ylim = (min(road_y), max(road_y))

    for e in dataset["road_edges"]:
        x1, y1 = rpos[e.u]
        x2, y2 = rpos[e.v]
        plt.plot([x1, x2], [y1, y2], color="#b0b0b0" if not e.is_damaged else "#d62728", linewidth=2.8 if e.is_damaged else 2.0, zorder=1)
    plt.scatter(road_x, road_y, s=26, c="#1f77b4", edgecolors="white", linewidths=0.4, zorder=2)

    ppos, _ = _power_pos_kind(dataset)
    p_items = list(ppos.items())
    pcoords_norm = _normalize([xy for _, xy in p_items], xlim, ylim)
    pmap = {nid: xy for (nid, _), xy in zip(p_items, pcoords_norm)}

    for l in dataset["power_lines"]:
        x1, y1 = pmap[l.u]
        x2, y2 = pmap[l.v]
        plt.plot([x1, x2], [y1, y2], color="#1f77b4" if not l.is_fault else "#ff7f0e", linewidth=2.6 if l.is_fault else 1.8, linestyle="--", alpha=0.95, zorder=3)
    plt.scatter([xy[0] for xy in pmap.values()], [xy[1] for xy in pmap.values()], s=28, c="#2ca02c", marker="^", edgecolors="black", linewidths=0.4, zorder=4)

    legend_items = [
        Line2D([0], [0], color="#b0b0b0", lw=2, label=t["open_road"]),
        Line2D([0], [0], color="#d62728", lw=3, label=t["damaged_road"]),
        Line2D([0], [0], color="#1f77b4", lw=2, ls="--", label=t["healthy_line"]),
        Line2D([0], [0], color="#ff7f0e", lw=3, ls="--", label=t["fault_line"]),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#1f77b4", label=t["road_junc"], markersize=7),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#2ca02c", markeredgecolor="black", label=t["facility"], markersize=8),
    ]
    plt.legend(handles=legend_items, loc="upper left", frameon=True)
    plt.title(t["overlay_title"])
    plt.xlabel(t["x"])
    plt.ylabel(t["y"])
    plt.grid(alpha=0.2, linestyle=":")
    out = outdir / f"ch6_road_power_overlay_{lang}.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close()
    return out


def _print_summary(results, csv_paths: List[Path], figure_paths: List[Path], lang: str) -> None:
    if lang == "zh":
        print("=== 按 AUC 排序 ===")
        for r in sorted(results, key=lambda x: x["auc"], reverse=True):
            print(f"{r['strategy']}: AUC={r['auc']:.2f}, 工期={r['makespan']:.2f}, 恢复负荷={r['final_restored_kw']:.1f}")
        print("保存的CSV：")
    else:
        print("=== Strategy ranking by AUC ===")
        for r in sorted(results, key=lambda x: x["auc"], reverse=True):
            print(f"{r['strategy']}: AUC={r['auc']:.2f}, makespan={r['makespan']:.2f}, restored={r['final_restored_kw']:.1f}")
        print("Saved CSV files:")
    for p in csv_paths:
        print(f"  - {p}")
    print(f"Saved figures ({lang}):")
    for p in figure_paths:
        print(f"  - {p}")


def maybe_log_wandb(results, figures: List[Path], enabled: bool, entity: str, project: str) -> tuple[str | None, str | None]:
    if not enabled:
        return None, None
    import wandb

    run = wandb.init(entity=entity, project=project, config={"experiment": "ch6_ch8_bilingual_overlay_topology"})
    for res in results:
        run.log({"strategy_auc": res["auc"], "strategy_makespan": res["makespan"], "strategy": res["strategy"], "final_restored_kw": res["final_restored_kw"]})
    for fig in figures:
        run.log({fig.stem: wandb.Image(str(fig))})
    run_url = run.url
    run_path = f"{entity}/{project}/{run.id}"
    run.finish()
    return run_url, run_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Chapter 6-8 synthetic data, bilingual visualizations, and reports.")
    parser.add_argument("--outdir", default="artifacts", help="Output folder for charts.")
    parser.add_argument("--data-outdir", default="data/ch6_ch8", help="Output folder for CSV tables tracked in git.")
    parser.add_argument("--wandb", action="store_true", help="Log results and figures to Weights & Biases.")
    parser.add_argument("--wandb-report", action="store_true", help="Create W&B Report page with interpretation blocks.")
    parser.add_argument("--report-outdir", default="reports", help="Output folder for local markdown reports.")
    parser.add_argument("--entity", default="chaoyan")
    parser.add_argument("--project", default="traffic-power-repair-sim")
    parser.add_argument("--imgbb-api-key", default="", help="Optional imgbb API key for uploading generated images.")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    payload = run_ch6_ch8_experiment()
    dataset = payload["dataset"]
    results = payload["results"]

    csv_paths = export_ch6_ch8_dataset_csv(dataset, Path(args.data_outdir))

    figures: List[Path] = []
    zh_figs: List[Path] = []
    en_figs: List[Path] = []
    for lang in ["zh", "en"]:
        lang_figures = [
            _plot_lsd(results, outdir, lang),
            _plot_auc(results, outdir, lang),
            _plot_road_topology(dataset, outdir, lang),
            _plot_power_topology(dataset, outdir, lang),
            _plot_joint_topology(dataset, outdir, lang),
            _plot_overlay_topology(dataset, outdir, lang),
        ]
        _print_summary(results, csv_paths, lang_figures, lang)
        figures.extend(lang_figures)
        if lang == "zh":
            zh_figs = lang_figures
        else:
            en_figs = lang_figures

    run_url, _ = maybe_log_wandb(results, figures, args.wandb, args.entity, args.project)
    summary = summarize_results(results)
    default_run_url = run_url or f"https://wandb.ai/{args.entity}/{args.project}"

    report_outdir = Path(args.report_outdir)
    hosted_links = None
    links_path = report_outdir / "imgbb_links.json"
    if args.imgbb_api_key:
        hosted_links = upload_images_to_imgbb(figures, args.imgbb_api_key)
        save_text(links_path, json.dumps(hosted_links, ensure_ascii=False, indent=2))
        print(f"Uploaded {len(hosted_links)} images to imgbb and saved links file.")
    elif links_path.exists():
        hosted_links = json.loads(links_path.read_text(encoding="utf-8"))
        print(f"Loaded existing imgbb links from {links_path}.")

    zh_text = render_markdown_report_zh(summary, default_run_url, zh_figs, hosted_links)
    en_text = render_markdown_report_en(summary, default_run_url, en_figs, hosted_links)
    zh_report = save_text(report_outdir / "experiment_report_zh.md", zh_text)
    en_report = save_text(report_outdir / "experiment_report_en.md", en_text)
    print(f"Local reports saved: {zh_report}, {en_report}")

    if args.wandb_report:
        report_url = create_wandb_report(
            entity=args.entity,
            project=args.project,
            run_url=default_run_url,
            summary=summary,
            report_title="Traffic-Power Coordinated Repair Experiment Report",
            markdown_zh=zh_text,
            markdown_en=en_text,
        )
        if report_url:
            print(f"W&B report created (ZH markdown only): {report_url}")
        else:
            print("W&B report creation skipped/failed (check permissions and reports API).")


if __name__ == "__main__":
    main()
