import graphviz
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')

dot = graphviz.Digraph(
    'flowsheet_p&id',
    format='svg',
    engine='dot',
    directory='.',
)

dot.attr(
    rankdir='LR',
    splines='ortho',
    nodesep='0.8',
    ranksep='1.2',
    pad='0.5',
    dpi='300',
    fontname='SimHei',
    fontsize='12',
    bgcolor='transparent',
    size='30,20',
    ratio='fill',
    compound='true',
    newrank='true',
)

dot.attr('node', shape='box', style='rounded,filled', fillcolor='#E3F2FD',
         color='#1565C0', fontname='SimHei', fontsize='10',
         penwidth='2', width='2.0', height='0.8')

dot.attr('edge', color='#5a9ab8', penwidth='2', arrowsize='0.8',
         fontname='SimHei', fontsize='9', fontcolor='#333333')

with dot.subgraph(name='cluster_wt') as c:
    c.attr(label='WT 水处理系统', style='rounded,filled',
           fillcolor='#E3F2FD', color='#4fc3f7', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('WT101', 'WT-101\n原水箱 10m³', fillcolor='#B3E5FC', color='#4fc3f7')
    c.node('WT102', 'WT-102\n多介质过滤器', fillcolor='#B3E5FC', color='#4fc3f7')
    c.node('WT103', 'WT-103\n活性炭过滤器', fillcolor='#B3E5FC', color='#4fc3f7')
    c.node('WT104', 'WT-104\nRO反渗透', fillcolor='#B3E5FC', color='#4fc3f7')
    c.node('WT105', 'WT-105\n离子交换柱', fillcolor='#B3E5FC', color='#4fc3f7')
    c.node('WT106', 'WT-106\nUV杀菌器', fillcolor='#E1BEE7', color='#9370db')
    c.node('WT107', 'WT-107\n纯水储罐 10m³', fillcolor='#B3E5FC', color='#4fc3f7')

with dot.subgraph(name='cluster_th') as c:
    c.attr(label='TH 茶叶前处理', style='rounded,filled',
           fillcolor='#EFEBE9', color='#8D6E63', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('TH101', 'TH-101\n茶叶储罐 2m³', fillcolor='#D7CCC8', color='#8D6E63')
    c.node('TH102', 'TH-102\n茶叶粉碎机', fillcolor='#D7CCC8', color='#8D6E63')

with dot.subgraph(name='cluster_ex') as c:
    c.attr(label='EX 萃取系统(三级逆流)', style='rounded,filled',
           fillcolor='#E8F5E9', color='#66BB6A', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('EX101', 'EX-101\n萃取罐1 95°C', fillcolor='#C8E6C9', color='#66BB6A')
    c.node('EX102', 'EX-102\n萃取罐2 90°C', fillcolor='#C8E6C9', color='#66BB6A')
    c.node('EX103', 'EX-103\n萃取罐3 85°C', fillcolor='#C8E6C9', color='#66BB6A')
    c.node('EX104', 'EX-104\n茶渣分离器', fillcolor='#C8E6C9', color='#66BB6A')
    c.node('EX105', 'EX-105\n茶汁冷却器', fillcolor='#C8E6C9', color='#66BB6A')
    c.node('EX106', 'EX-106\n萃取液储罐', fillcolor='#C8E6C9', color='#66BB6A')

with dot.subgraph(name='cluster_fl') as c:
    c.attr(label='FL 过滤净化', style='rounded,filled',
           fillcolor='#E0F7FA', color='#26C6DA', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('FL101', 'FL-101\n碟式离心机', fillcolor='#B2EBF2', color='#26C6DA')
    c.node('FL102', 'FL-102\n超滤膜组件', fillcolor='#B2EBF2', color='#26C6DA')

with dot.subgraph(name='cluster_bl') as c:
    c.attr(label='BL 调配系统', style='rounded,filled',
           fillcolor='#F3E5F5', color='#AB47BC', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('BL101', 'BL-101\n调配罐1 5m³', fillcolor='#E1BEE7', color='#AB47BC')
    c.node('BL102', 'BL-102\n调配罐2 5m³', fillcolor='#E1BEE7', color='#AB47BC')
    c.node('BL103', 'BL-103\n糖浆溶解罐', fillcolor='#FCE4EC', color='#EC407A')
    c.node('BL104', 'BL-104\n糖浆储罐', fillcolor='#FCE4EC', color='#EC407A')
    c.node('BL105', 'BL-105\n酸液罐', fillcolor='#FFF9C4', color='#F9A825')

with dot.subgraph(name='cluster_hm') as c:
    c.attr(label='HM 均质系统', style='rounded,filled',
           fillcolor='#FCE4EC', color='#EC407A', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('HM101', 'HM-101\n高压均质机\n20-25MPa', fillcolor='#F8BBD9', color='#EC407A')

with dot.subgraph(name='cluster_uh') as c:
    c.attr(label='UH UHT杀菌系统', style='rounded,filled',
           fillcolor='#FFEBEE', color='#EF5350', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('UH102', 'UH-102\n预热器 80°C', fillcolor='#FFCDD2', color='#EF5350')
    c.node('UH101', 'UH-101\nUHT杀菌锅\n135°C/15s', fillcolor='#FFCDD2', color='#EF5350')
    c.node('UH103', 'UH-103\n保温管 30m', fillcolor='#FFCDD2', color='#EF5350')
    c.node('UH104', 'UH-104\n冷却器 25°C', fillcolor='#B2EBF2', color='#26C6DA')
    c.node('UH105', 'UH-105\n无菌储罐 3m³', fillcolor='#FFCDD2', color='#EF5350')

with dot.subgraph(name='cluster_pkg') as c:
    c.attr(label='PKG 包装系统', style='rounded,filled',
           fillcolor='#FFF8E1', color='#FFA726', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('BF101', 'BF-101\n吹瓶机', fillcolor='#FFE0B2', color='#FFA726')
    c.node('PF101', 'PF-101\n吹灌一体机\n54000B/H', fillcolor='#FFE0B2', color='#FFA726')
    c.node('CG101', 'CG-101\n旋盖机', fillcolor='#FFE0B2', color='#FFA726')
    c.node('LI101', 'LI-101\n视觉灯检机', fillcolor='#B2EBF2', color='#26C6DA')
    c.node('CI101', 'CI-101\n激光喷码机', fillcolor='#FFE0B2', color='#FFA726')
    c.node('LB101', 'LB-101\n贴标机', fillcolor='#C8E6C9', color='#66BB6A')
    c.node('CA101', 'CA-101\n装箱机', fillcolor='#E1BEE7', color='#AB47BC')
    c.node('PK101', 'PK-101\n冷却隧道', fillcolor='#C8E6C9', color='#66BB6A')
    c.node('PK108', 'PK-108\n码垛机', fillcolor='#C8E6C9', color='#66BB6A')
    c.node('PK110', 'PK-110\n缠绕机', fillcolor='#C8E6C9', color='#66BB6A')

with dot.subgraph(name='cluster_cip') as c:
    c.attr(label='CIP 清洗系统', style='rounded,filled',
           fillcolor='#ECEFF1', color='#78909C', fontname='SimHei',
           fontsize='12', penwidth='2', margin='20')
    c.node('CP101', 'CP-101\nCIP碱液罐\n2m³ 85°C', fillcolor='#CFD8DC', color='#78909C')
    c.node('CP102', 'CP-102\nCIP酸液罐\n1m³ 60°C', fillcolor='#CFD8DC', color='#78909C')
    c.node('CP103', 'CP-103\nCIP热水罐\n3m³ 85°C', fillcolor='#CFD8DC', color='#78909C')

dot.edge('WT101', 'WT102', color='#4fc3f7')
dot.edge('WT102', 'WT103', color='#4fc3f7')
dot.edge('WT103', 'WT104', color='#4fc3f7')
dot.edge('WT104', 'WT105', color='#4fc3f7')
dot.edge('WT105', 'WT106', color='#4fc3f7')
dot.edge('WT106', 'WT107', color='#4fc3f7')

dot.edge('TH101', 'TH102', color='#8D6E63')

dot.edge('EX101', 'EX102', color='#66BB6A', style='dashed')
dot.edge('EX102', 'EX103', color='#66BB6A', style='dashed')
dot.edge('EX103', 'EX104', color='#66BB6A')
dot.edge('EX104', 'EX105', color='#66BB6A')
dot.edge('EX105', 'EX106', color='#66BB6A')

dot.edge('FL101', 'FL102', color='#26C6DA')

dot.edge('BL101', 'BL102', color='#AB47BC')
dot.edge('BL103', 'BL104', color='#EC407A')
dot.edge('BL104', 'BL105', color='#F9A825')

dot.edge('UH102', 'UH101', color='#EF5350')
dot.edge('UH101', 'UH103', color='#EF5350')
dot.edge('UH103', 'UH104', color='#26C6DA')
dot.edge('UH104', 'UH105', color='#EF5350')

dot.edge('PF101', 'CG101', color='#FFA726')
dot.edge('CG101', 'LI101', color='#26C6DA')
dot.edge('LI101', 'CI101', color='#FFA726')
dot.edge('CI101', 'LB101', color='#66BB6A')
dot.edge('LB101', 'CA101', color='#AB47BC')
dot.edge('CA101', 'PK101', color='#66BB6A')
dot.edge('PK101', 'PK108', color='#66BB6A')
dot.edge('PK108', 'PK110', color='#66BB6A')

dot.edge('TH102', 'EX101', color='#8D6E63', style='dashed', label='茶叶粉')
dot.edge('WT107', 'BL101', color='#4fc3f7', style='dashed', label='纯水')
dot.edge('EX105', 'FL101', color='#66BB6A')
dot.edge('FL102', 'BL101', color='#66BB6A', style='dashed', label='净化茶汁')
dot.edge('BL102', 'HM101', color='#AB47BC')
dot.edge('HM101', 'UH102', color='#EC407A')
dot.edge('UH105', 'PF101', color='#EF5350', style='dashed', label='UHT产品')
dot.edge('BF101', 'PF101', color='#FFA726', style='dashed', label='空瓶')

output = dot.render('flowsheet_pro', cleanup=True)
print(f"流程图已生成: {output}")