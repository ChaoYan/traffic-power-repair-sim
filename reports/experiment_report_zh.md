# 协同抢修实验报告（自动生成）

## 1. 运行信息
- Run URL: https://wandb.ai/chaoyan/traffic-power-repair-sim/runs/s8ulen8z
- 实验对象：交通-电网协同抢修策略（S1~S4）

## 2. 关键结论
- 最优策略：**S4**（AUC=8997.50）
- 最弱策略：**S1**（AUC=4777.50）
- 最终恢复负荷：**1400.0 kW**

## 3. 指标总表
| 策略 | AUC | 工期(h) | 最终恢复负荷(kW) |
|---|---:|---:|---:|
| S4 | 8997.50 | 11.25 | 1400.0 |
| S3 | 8182.50 | 10.00 | 1400.0 |
| S2 | 5517.50 | 9.00 | 1400.0 |
| S1 | 4777.50 | 15.00 | 1400.0 |

## 4. 各图表解释
### 4.1 LSD 恢复曲线
![ch8_lsd_curves_zh.png](https://i.ibb.co/nMRb05tr/ch8-lsd-curves-zh-png.png)

### 4.2 AUC 柱状图
![ch8_auc_bar_zh.png](https://i.ibb.co/QF35swFS/ch8-auc-bar-zh-png.png)

### 4.3 路网拓扑
![ch6_road_topology_zh.png](https://i.ibb.co/27YCjkdg/ch6-road-topology-zh-png.png)

### 4.4 电网拓扑
![ch6_power_topology_zh.png](https://i.ibb.co/nMSjvXXC/ch6-power-topology-zh-png.png)

### 4.5 双网并列总览
![ch6_joint_topology_overview_zh.png](https://i.ibb.co/gMwGgH2p/ch6-joint-topology-overview-zh-png.png)

### 4.6 道路-电网叠加图
![ch6_road_power_overlay_zh.png](https://i.ibb.co/Nd6YL6ZZ/ch6-road-power-overlay-zh-png.png)

- `ch8_lsd_curves_*.png`：展示恢复负荷的阶梯增长过程，越早抬升意味着越高 AUC。
- `ch8_auc_bar_*.png`：直接对比各策略累计恢复收益；可快速定位最优策略。
- `ch6_road_topology_*.png`：识别受损道路与关键接入点，解释可达性约束来源。
- `ch6_power_topology_*.png`：展示农村树状配电网中故障线位置与关键设施节点。
- `ch6_joint_topology_overview_*.png`：双图并列用于说明道路与电网的空间耦合关系。
- `ch6_road_power_overlay_*.png`：同图叠加更直观地解释“道路可达性 → 电力任务顺序”的影响链。

## 5. 解释性分析（业务视角）
- **早期恢复优先性**：S3/S4 在关键负荷（医院/安置点/指挥中心）上更早恢复，因而 AUC 明显领先。
- **可达性约束传导**：道路层受损边会推迟电力任务启动时刻，直接影响恢复曲线前半段斜率。
- **策略差异本质**：S1 偏顺序执行，安全但慢；S2 并行改善中期效率；S3/S4 强调关键任务优先，提升早期收益。

## 6. 图件清单
- `ch8_lsd_curves_zh.png`
- `ch8_auc_bar_zh.png`
- `ch6_road_topology_zh.png`
- `ch6_power_topology_zh.png`
- `ch6_joint_topology_overview_zh.png`
- `ch6_road_power_overlay_zh.png`
