import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Arc, Polygon
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

plt.rcParams['font.family'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class PIDDrawer:
    def __init__(self, fig_size=(40, 24)):
        self.fig, self.ax = plt.subplots(1, 1, figsize=fig_size, dpi=150)
        self.ax.set_xlim(0, 40)
        self.ax.set_ylim(0, 24)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        self.colors = {
            'WT': '#4fc3f7',
            'TH': '#8D6E63',
            'EX': '#66BB6A',
            'FL': '#26C6DA',
            'BL': '#AB47BC',
            'HM': '#EC407A',
            'UH': '#EF5350',
            'PKG': '#FFA726',
            'CIP': '#78909C',
            'process': '#5a9ab8',
            'water': '#4fc3f7',
            'steam': '#EF5350',
            'cip': '#90A4AE',
        }

    def draw_tank(self, x, y, width, height, tag, name, color, params=None):
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                              boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor='#2a3d50', edgecolor=color, linewidth=2)
        self.ax.add_patch(box)

        if params and 'level' in params:
            level_h = height * params['level']
            liquid = patches.Rectangle(
                (x - width/2 + 0.05, y - height/2 + 0.05),
                width - 0.1, level_h,
                facecolor=color, alpha=0.4, edgecolor='none')
            self.ax.add_patch(liquid)

        self.ax.text(x, y, name, ha='center', va='center',
                     fontsize=8, color='white', fontweight='bold')
        self.ax.text(x, y - height/2 - 0.3, tag, ha='center', va='top',
                     fontsize=9, color=color, fontweight='bold')
        if params:
            for i, (k, v) in enumerate(params.items()):
                if k != 'level':
                    self.ax.text(x, y - height/2 - 0.5 - i*0.25, f"{k}: {v}",
                                 ha='center', va='top', fontsize=7, color='#aaaaaa')

    def draw_vessel(self, x, y, width, height, tag, name, color, interior=None):
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                              boxstyle="round,pad=0.02,rounding_size=0.1",
                              facecolor='#2a3d50', edgecolor=color, linewidth=2)
        self.ax.add_patch(box)

        if interior == 'filter':
            for i in range(3):
                line_y = y - height/4 + i * height/4
                self.ax.plot([x - width/3, x + width/3], [line_y, line_y],
                            color=color, linewidth=1, alpha=0.7)
        elif interior == 'active_carbon':
            for i in range(3):
                circle = Circle((x, y - height/4 + i * height/4), 0.08,
                               facecolor='none', edgecolor=color, linewidth=1)
                self.ax.add_patch(circle)
        elif interior == 'coil':
            for i in range(4):
                self.ax.plot([x - width/3, x + width/3],
                           [y - height/4 + i * height/5, y - height/4 + i * height/5],
                           color=color, linewidth=1.5, alpha=0.7)

        self.ax.text(x, y, name, ha='center', va='center',
                     fontsize=7, color='white', fontweight='bold')
        self.ax.text(x, y - height/2 - 0.2, tag, ha='center', va='top',
                     fontsize=9, color=color, fontweight='bold')

    def draw_centrifuge(self, x, y, size, tag, name, color):
        box = FancyBboxPatch((x - size/2, y - size/2), size, size,
                              boxstyle="round,pad=0.02,rounding_size=0.08",
                              facecolor='#2a3d50', edgecolor=color, linewidth=2)
        self.ax.add_patch(box)

        for r in [size/3, size/5, size/8]:
            circle = Circle((x, y), r, facecolor='none',
                           edgecolor=color, linewidth=1.5, alpha=0.8)
            self.ax.add_patch(circle)

        self.ax.text(x, y - size/2 - 0.2, tag, ha='center', va='top',
                     fontsize=9, color=color, fontweight='bold')
        self.ax.text(x, y - size/2 - 0.5, name, ha='center', va='top',
                     fontsize=7, color='#aaaaaa')

    def draw_heat_exchanger(self, x, y, width, height, tag, name, color):
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                              boxstyle="round,pad=0.02,rounding_size=0.05",
                              facecolor='#2a3d50', edgecolor=color, linewidth=2)
        self.ax.add_patch(box)

        xs = np.linspace(x - width/3, x + width/3, 10)
        ys = y + np.sin(np.linspace(0, 2*np.pi, 10)) * height/4
        self.ax.plot(xs, ys, color=color, linewidth=1.5, alpha=0.8)

        self.ax.text(x, y - height/2 - 0.2, tag, ha='center', va='top',
                     fontsize=9, color=color, fontweight='bold')
        self.ax.text(x, y - height/2 - 0.5, name, ha='center', va='top',
                     fontsize=7, color='#aaaaaa')

    def draw_pump(self, x, y, size, tag, name, color):
        box = FancyBboxPatch((x - size/2, y - size/2), size, size,
                              boxstyle="round,pad=0.02,rounding_size=0.05",
                              facecolor='#2a3d50', edgecolor=color, linewidth=1.5)
        self.ax.add_patch(box)

        self.ax.text(x, y, 'P', ha='center', va='center',
                     fontsize=10, color=color, fontweight='bold')

        self.ax.text(x, y - size/2 - 0.2, tag, ha='center', va='top',
                     fontsize=8, color=color, fontweight='bold')
        self.ax.text(x, y - size/2 - 0.45, name, ha='center', va='top',
                     fontsize=6, color='#aaaaaa')

    def draw_uht(self, x, y, width, height, tag, name, color):
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                              boxstyle="round,pad=0.02,rounding_size=0.12",
                              facecolor='#3d2020', edgecolor=color, linewidth=3)
        self.ax.add_patch(box)

        self.ax.text(x, y + 0.2, 'UHT', ha='center', va='center',
                     fontsize=12, color=color, fontweight='bold')
        self.ax.text(x, y - 0.3, '135°C/15s', ha='center', va='center',
                     fontsize=9, color=color)

        self.ax.text(x, y - height/2 - 0.25, tag, ha='center', va='top',
                     fontsize=10, color=color, fontweight='bold')
        self.ax.text(x, y - height/2 - 0.55, name, ha='center', va='top',
                     fontsize=7, color='#aaaaaa')

    def draw_filler(self, x, y, width, height, tag, name, color):
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                              boxstyle="round,pad=0.02,rounding_size=0.1",
                              facecolor='#2a3d50', edgecolor=color, linewidth=2)
        self.ax.add_patch(box)

        self.ax.text(x, y + 0.3, 'BLOW', ha='center', va='center',
                     fontsize=7, color=color, alpha=0.7)
        self.ax.text(x, y - 0.1, 'FILL', ha='center', va='center',
                     fontsize=9, color=color, fontweight='bold')
        self.ax.text(x, y - 0.5, '72HEAD', ha='center', va='center',
                     fontsize=6, color=color, alpha=0.7)

        self.ax.text(x, y - height/2 - 0.2, tag, ha='center', va='top',
                     fontsize=9, color=color, fontweight='bold')
        self.ax.text(x, y - height/2 - 0.5, name, ha='center', va='top',
                     fontsize=6, color='#aaaaaa')

    def draw_valve(self, x, y, size, tag, name, color, valve_type='angle'):
        if valve_type == 'angle':
            triangle = Polygon([(x, y + size/2), (x - size/2, y - size/3),
                               (x + size/2, y - size/3)],
                              facecolor=color, edgecolor='white', linewidth=1)
            self.ax.add_patch(triangle)
        else:
            circle = Circle((x, y), size/2, facecolor=color, edgecolor='white', linewidth=1)
            self.ax.add_patch(circle)

        self.ax.text(x, y - size/2 - 0.2, tag, ha='center', va='top',
                     fontsize=7, color=color)

    def draw_sensor(self, x, y, size, tag, sensor_type):
        circle = Circle((x, y), size/2, facecolor='#1a2535',
                       edgecolor='#f0ad4e', linewidth=1.5)
        self.ax.add_patch(circle)

        self.ax.text(x, y, tag[:2], ha='center', va='center',
                     fontsize=6, color='#f0ad4e', fontweight='bold')

    def draw_pipe(self, start, end, color, style='-', width=2, label=None):
        line_style = '--' if style == 'dashed' else '-'
        alpha = 0.6 if style == 'dashed' else 1.0

        self.ax.plot([start[0], end[0]], [start[1], end[1]],
                    color=color, linewidth=width, linestyle=line_style, alpha=alpha,
                    solid_capstyle='round')

        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            self.ax.text(mid_x, mid_y + 0.15, label, ha='center', va='bottom',
                        fontsize=6, color=color, alpha=0.8)

    def draw_cluster_box(self, x, y, width, height, title, color):
        box = FancyBboxPatch((x, y), width, height,
                              boxstyle="round,pad=0.02,rounding_size=0.2",
                              facecolor='#1a2535', edgecolor=color,
                              linewidth=1.5, alpha=0.5)
        self.ax.add_patch(box)

        self.ax.text(x + width/2, y + height + 0.3, title, ha='center', va='bottom',
                     fontsize=11, color=color, fontweight='bold')

    def add_title(self, title, subtitle):
        self.ax.text(20, 23.5, title, ha='center', va='center',
                     fontsize=18, color='white', fontweight='bold')
        self.ax.text(20, 22.9, subtitle, ha='center', va='center',
                     fontsize=10, color='#aaaaaa')

    def add_legend(self, x, y):
        legend_y = y
        items = [
            ('产品管道', self.colors['process'], '-'),
            ('纯水管', self.colors['water'], '-'),
            ('CIP管道', self.colors['cip'], '--'),
            ('蒸汽管道', self.colors['steam'], '--'),
        ]

        for i, (name, color, style) in enumerate(items):
            line = Line2D([0], [0], color=color, linewidth=2,
                         linestyle='--' if style == '--' else '-')
            self.ax.add_line(line)
            self.ax.text(x + i * 4, legend_y, name, fontsize=8, color='#cccccc')

    def save(self, filename):
        self.fig.savefig(filename, dpi=200, bbox_inches='tight',
                         facecolor='#0a0f1a', edgecolor='none',
                         format='png')
        print(f"流程图已保存: {filename}")

def create_tea_production_flowsheet():
    pid = PIDDrawer(fig_size=(45, 28))

    pid.add_title('茶饮料生产线 P&ID (50000 B/H)',
                  '纯茶饮料 · PET瓶UHT无菌灌装 · 54000B/H(最大)')

    y_base = 22

    pid.draw_cluster_box(1, 2, 10, 19, 'WT 水处理系统', pid.colors['WT'])
    pid.draw_tank(3, 18, 1.5, 2.5, 'WT-101', '原水箱\n10m³', pid.colors['WT'],
                  {'LT': '75%'})
    pid.draw_vessel(5, 18, 1.2, 2, 'WT-102', '多介质\n过滤器', pid.colors['WT'], 'filter')
    pid.draw_vessel(7, 18, 1.2, 2, 'WT-103', '活性炭\n过滤器', pid.colors['WT'], 'active_carbon')
    pid.draw_vessel(9, 18, 1.3, 2.2, 'WT-104', 'RO\n反渗透', pid.colors['WT'])
    pid.draw_vessel(4, 14, 1.0, 1.5, 'WT-105', '离子\n交换柱', pid.colors['WT'], 'filter')
    pid.draw_vessel(6, 14, 1.0, 1.5, 'WT-106', 'UV\n杀菌器', '#9370db')
    pid.draw_tank(8.5, 14, 1.5, 2.5, 'WT-107', '纯水储罐\n10m³', pid.colors['WT'],
                  {'LT': '80%', 'CT': '8μS/cm'})
    pid.draw_pump(3, 11, 0.8, 'P-WT01', '原水泵', pid.colors['WT'])
    pid.draw_pump(6, 11, 0.8, 'P-WT02', '纯水泵', pid.colors['WT'])

    pid.draw_pipe((3, 16.8), (4.4, 16.8), pid.colors['water'])
    pid.draw_pipe((5.6, 17), (6.4, 17), pid.colors['water'])
    pid.draw_pipe((7.6, 17), (8.35, 17.1), pid.colors['water'])
    pid.draw_pipe((9.65, 16.9), (9.65, 15.5), pid.colors['water'])
    pid.draw_pipe((3, 10.2), (3, 5), pid.colors['water'])

    pid.draw_cluster_box(13, 2, 3, 6, 'TH 茶叶前处理', pid.colors['TH'])
    pid.draw_tank(14.5, 6, 1.3, 2, 'TH-101', '茶叶储罐\n2m³', pid.colors['TH'],
                  {'LT': '60%'})
    pid.draw_vessel(14.5, 3.5, 1.3, 1.5, 'TH-102', '茶叶\n粉碎机', pid.colors['TH'])

    pid.draw_cluster_box(17.5, 2, 7, 19, 'EX 萃取系统 (三级逆流)', pid.colors['EX'])
    pid.draw_tank(19, 18, 1.5, 2.8, 'EX-101', '萃取罐1\n95°C', pid.colors['EX'],
                  {'TT': '95°C', 'LT': '85%'})
    pid.draw_tank(21.5, 18, 1.5, 2.8, 'EX-102', '萃取罐2\n90°C', pid.colors['EX'],
                  {'TT': '90°C', 'LT': '80%'})
    pid.draw_tank(24, 18, 1.5, 2.8, 'EX-103', '萃取罐3\n85°C', pid.colors['EX'],
                  {'TT': '85°C', 'LT': '75%'})
    pid.draw_vessel(19, 13.5, 1.3, 2, 'EX-104', '茶渣\n分离器', pid.colors['EX'], 'filter')
    pid.draw_heat_exchanger(21.5, 13.5, 1.3, 2, 'EX-105', '茶汁\n冷却器', pid.colors['EX'])
    pid.draw_tank(24, 13.5, 1.5, 2.5, 'EX-106', '萃取液\n储罐 3m³', pid.colors['EX'],
                  {'LT': '70%'})

    pid.draw_pipe((19, 16.6), (19, 14.5), pid.colors['EX'])
    pid.draw_pipe((21.5, 16.6), (21.5, 14.5), pid.colors['EX'], 'dashed')
    pid.draw_pipe((24, 16.6), (24, 14.5), pid.colors['EX'], 'dashed')
    pid.draw_pipe((20.2, 17), (20.8, 17), pid.colors['EX'])
    pid.draw_pipe((22.7, 17), (23.3, 17), pid.colors['EX'])
    pid.draw_pipe((19, 12.5), (20.4, 12.5), pid.colors['EX'])
    pid.draw_pipe((22.6, 12.5), (23.4, 12.5), pid.colors['EX'])

    pid.draw_cluster_box(26, 2, 4, 10, 'FL 过滤净化', pid.colors['FL'])
    pid.draw_centrifuge(28, 9, 1.8, 'FL-101', '碟式\n离心机', pid.colors['FL'])
    pid.draw_vessel(28, 5.5, 1.5, 2, 'FL-102', '超滤膜\n0.1μm', pid.colors['FL'])
    pid.draw_pipe((28, 8.1), (28, 6.5), pid.colors['FL'])

    pid.draw_cluster_box(26, 13, 4.5, 8, 'HM 均质', pid.colors['HM'])
    pid.draw_uht(28, 17, 2.2, 2.5, 'HM-101', '高压均质机\n20-25MPa', pid.colors['HM'])

    pid.draw_cluster_box(32, 2, 5.5, 19, 'UH UHT杀菌系统', pid.colors['UH'])
    pid.draw_heat_exchanger(34.5, 18, 1.5, 2.2, 'UH-102', '预热器\n80°C', pid.colors['UH'])
    pid.draw_uht(34.5, 14, 2.2, 2.5, 'UH-101', 'UHT杀菌锅\n135°C/15s', pid.colors['UH'])
    pid.draw_vessel(37, 18, 1.2, 1.8, 'UH-103', '保温管\n30m', pid.colors['UH'], 'coil')
    pid.draw_heat_exchanger(37, 14, 1.5, 2.2, 'UH-104', '冷却器\n25°C', '#26C6DA')
    pid.draw_tank(39.5, 16, 1.5, 2.8, 'UH-105', '无菌储罐\n3m³', pid.colors['UH'],
                  {'LT': '65%', 'TT': '25°C'})

    pid.draw_pipe((34.5, 16.9), (34.5, 15.3), pid.colors['UH'])
    pid.draw_pipe((35.6, 17.9), (36.4, 17.9), pid.colors['UH'])
    pid.draw_pipe((37.6, 17.1), (37.6, 15.3), pid.colors['UH'])
    pid.draw_pipe((37, 12.5), (38.7, 12.5), pid.colors['UH'])
    pid.draw_pipe((38.2, 14.7), (39.2, 15.5), pid.colors['UH'])

    pid.draw_cluster_box(1, 12, 8, 8, 'BL 调配系统', pid.colors['BL'])
    pid.draw_tank(3, 18, 1.8, 2.8, 'BL-101', '调配罐1\n5m³', pid.colors['BL'],
                  {'pH': '5.5', 'Brix': '10°'})
    pid.draw_tank(6, 18, 1.8, 2.8, 'BL-102', '调配罐2\n5m³', pid.colors['BL'],
                  {'pH': '5.5', 'Brix': '10°'})
    pid.draw_tank(3, 14, 1.3, 2, 'BL-103', '糖浆\n溶解罐', '#EC407A',
                  {'Brix': '65°'})
    pid.draw_tank(6, 14, 1.3, 2, 'BL-104', '糖浆\n储罐', '#EC407A',
                  {'Brix': '65°'})
    pid.draw_tank(8.5, 16, 1.0, 1.5, 'BL-105', '酸液罐\n0.5m³', '#F9A825')

    pid.draw_pipe((4.8, 18), (4.2, 18), pid.colors['BL'])
    pid.draw_pipe((3, 12.6), (3, 11), pid.colors['BL'])

    pid.draw_cluster_box(12, 12, 3, 8, 'CIP 清洗', pid.colors['CIP'])
    pid.draw_tank(13.5, 18, 1.3, 2, 'CP-101', 'CIP碱液罐\n2m³ 85°C', pid.colors['CIP'])
    pid.draw_tank(13.5, 15, 1.3, 2, 'CP-102', 'CIP酸液罐\n1m³ 60°C', pid.colors['CIP'])
    pid.draw_tank(13.5, 12, 1.3, 2, 'CP-103', 'CIP热水罐\n3m³ 85°C', pid.colors['CIP'])

    pid.draw_cluster_box(1, 1, 38, 9, 'PKG 包装系统', pid.colors['PKG'])
    pid.draw_vessel(5, 7, 1.8, 2.2, 'BF-101', '吹瓶机\nSBL-FG', pid.colors['PKG'])
    pid.draw_filler(10, 7, 2.2, 2.5, 'PF-101', '吹灌一体机\n54000B/H', pid.colors['PKG'])
    pid.draw_vessel(15, 7, 1.5, 2, 'CG-101', '旋盖机', pid.colors['PKG'])
    pid.draw_centrifuge(19, 7, 1.6, 'LI-101', '视觉\n灯检机', '#26C6DA')
    pid.draw_vessel(23, 7, 1.5, 1.8, 'CI-101', '激光\n喷码机', pid.colors['PKG'])
    pid.draw_vessel(27, 7, 1.5, 1.8, 'LB-101', '贴标机', '#66BB6A')
    pid.draw_vessel(31, 7, 1.5, 1.8, 'CA-101', '装箱机', '#AB47BC')
    pid.draw_vessel(35, 7, 2, 1.8, 'PK-101', '冷却\n隧道', '#66BB6A')
    pid.draw_vessel(38, 7, 1.5, 1.8, 'PK-108', '码垛机', '#66BB6A')

    pid.draw_pipe((5, 5.9), (5, 5), pid.colors['PKG'])
    pid.draw_pipe((6.9, 7), (8.9, 7), pid.colors['PKG'])
    pid.draw_pipe((11.1, 7), (14.2, 7), pid.colors['PKG'])
    pid.draw_pipe((15.7, 7), (18.2, 7), pid.colors['PKG'])
    pid.draw_pipe((19.8, 7), (22.2, 7), '#26C6DA')
    pid.draw_pipe((23.7, 7), (26.2, 7), pid.colors['PKG'])
    pid.draw_pipe((27.7, 7), (30.2, 7), '#66BB6A')
    pid.draw_pipe((31.7, 7), (34, 7), '#AB47BC')
    pid.draw_pipe((36, 7), (37.2, 7), '#66BB6A')
    pid.draw_pipe((38.7, 7), (39, 7), '#66BB6A')

    pid.draw_pipe((14.5, 3.5), (19, 5.5), pid.colors['TH'])
    pid.draw_pipe((8.5, 12.6), (28, 6.5), pid.colors['water'], 'dashed', 1.5, '纯水→BL')
    pid.draw_pipe((28, 4.5), (28, 3), pid.colors['FL'])
    pid.draw_pipe((28, 2), (3, 10.2), pid.colors['FL'], 'dashed', 1.5, '净化茶汁')
    pid.draw_pipe((28, 17), (28, 12), pid.colors['HM'])
    pid.draw_pipe((28, 12), (34.5, 19.1), pid.colors['HM'])
    pid.draw_pipe((39.5, 14.6), (39.5, 8), pid.colors['UH'], 'dashed', 2, 'UHT产品')

    pid.draw_pipe((5, 8.1), (8.9, 8.1), pid.colors['PKG'], 'dashed', 1.5, '空瓶→PF')

    pid.save('flowsheet_professional.png')

create_tea_production_flowsheet()