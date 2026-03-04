# Coordinated Repair Experiment Report (Auto-generated)

## 1. Run information
- Run URL: https://wandb.ai/chaoyan/traffic-power-repair-sim/runs/s8ulen8z
- Scope: road-power coordinated repair strategy comparison (S1~S4)

## 2. Key findings
- Best strategy: **S4** (AUC=8997.50)
- Lowest strategy: **S1** (AUC=4777.50)
- Final restored load: **1400.0 kW**

## 3. Metrics table
| Strategy | AUC | Makespan(h) | Final Restored(kW) |
|---|---:|---:|---:|
| S4 | 8997.50 | 11.25 | 1400.0 |
| S3 | 8182.50 | 10.00 | 1400.0 |
| S2 | 5517.50 | 9.00 | 1400.0 |
| S1 | 4777.50 | 15.00 | 1400.0 |

## 4. Figure-by-figure interpretation
### 4.1 LSD restoration curves
![ch8_lsd_curves_en.png](https://i.ibb.co/hRppXL4X/ch8-lsd-curves-en-png.png)

### 4.2 AUC comparison
![ch8_auc_bar_en.png](https://i.ibb.co/XPzf39q/ch8-auc-bar-en-png.png)

### 4.3 Road topology
![ch6_road_topology_en.png](https://i.ibb.co/B2n8K8GV/ch6-road-topology-en-png.png)

### 4.4 Power topology
![ch6_power_topology_en.png](https://i.ibb.co/S4yp6vrF/ch6-power-topology-en.png)

### 4.5 Side-by-side joint overview
![ch6_joint_topology_overview_en.png](https://i.ibb.co/99DdMMtK/ch6-joint-topology-overview-en-png.png)

### 4.6 Overlay topology
![ch6_road_power_overlay_en.png](https://i.ibb.co/0RgBv005/ch6-road-power-overlay-en-png.png)

- `ch8_lsd_curves_*.png`: step-wise restored-load trajectory; earlier jumps imply larger AUC.
- `ch8_auc_bar_*.png`: direct cumulative-benefit comparison across strategies.
- `ch6_road_topology_*.png`: damaged roads and key access nodes explain accessibility constraints.
- `ch6_power_topology_*.png`: radial rural grid with faulted branches and critical facilities.
- `ch6_joint_topology_overview_*.png`: side-by-side topology coupling view (transport vs power).
- `ch6_road_power_overlay_*.png`: single-map overlay to explain accessibility-to-repair-order causality.

## 5. Explainability notes (operational view)
- **Early restoration priority**: S3/S4 recover critical facilities earlier, yielding larger AUC gains.
- **Accessibility propagation**: damaged transport links delay power task start times and flatten early LSD growth.
- **Strategy trade-off**: S1 is conservative and slower; S2 improves parallelism; S3/S4 prioritize critical tasks for earlier gains.

## 6. Figure list
- `ch8_lsd_curves_en.png`
- `ch8_auc_bar_en.png`
- `ch6_road_topology_en.png`
- `ch6_power_topology_en.png`
- `ch6_joint_topology_overview_en.png`
- `ch6_road_power_overlay_en.png`
