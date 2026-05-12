from diagrams import Diagram, Cluster, Edge
from diagrams.programming.framework import Django
from diagrams.onprem.workflow import Airflow
from diagrams.generic.storage import Storage
from diagrams.azure.storage import BlobStorage
from diagrams.gcp.compute import KubernetesEngine
from diagrams.gcp.iot import IotCore
from diagrams.aws.compute import Lambda
from diagrams.azure.database import SQLDatabase
from diagrams.ibm.security import KeyProtect
from diagrams.ibm.storage import CloudObjectStorage
from diagrams.azure.iot import IotHub
from diagrams.azure.ml import MachineLearningService
from diagrams.digitalocean.network import LoadBalancer
from diagrams.huawei.obs import OBS
from diagrams.oci.security import Vault
from diagrams.oci.compute import Compute
from diagrams.openstack.orchestration import Heat
from diagrams.eq import assess
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

graph_attrs = {
    "dpi": "300",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.6",
    "ranksep": "1.0",
    "fontname": "SimHei",
    "fontsize": "12",
    " bgcolor": "transparent",
    "fontcolor": "#333333",
    "size": "20,15",
    "ratio": "fill",
    "rankdir": "LR",
    "compound": "true",
}

node_attrs = {
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "#E3F2FD",
    "color": "#1565C0",
    "fontname": "SimHei",
    "fontsize": "10",
    "penwidth": "2",
    "width": "2.2",
    "height": "1.0",
}

edge_attrs = {
    "color": "#5a9ab8",
    "penwidth": "2",
    "arrowsize": "0.8",
    "fontname": "SimHei",
    "fontsize": "9",
    "fontcolor": "#333333",
}

cluster_attrs = {
    "style": "rounded,filled",
    "fillcolor": "#F5F5F5",
    "color": "#90A4AE",
    "fontname": "SimHei",
    "fontsize": "11",
    "penwidth": "1.5",
    "margin": "25",
}

with Diagram(
    "茶饮料生产线 P&ID (50000 B/H)",
    filename="flowsheet_pro",
    format="png",
    outformat="png",
    graph_attr=graph_attrs,
    node_attr=node_attrs,
    edge_attr=edge_attrs,
    show=False,
    direction="LR",
):
    with Cluster("WT\n水处理系统", graph_attr={"label": "WT 水处理系统", **cluster_attrs}):
        wt101 = Storage("WT-101\n原水箱 10m³")
        wt102 = Storage("WT-102\n多介质过滤器")
        wt103 = Storage("WT-103\n活性炭过滤器")
        wt104 = Storage("WT-104\nRO反渗透")
        wt105 = Storage("WT-105\n离子交换柱")
        wt106 = Storage("WT-106\nUV杀菌器")
        wt107 = Storage("WT-107\n纯水储罐 10m³")

        wt101 >> wt102 >> wt103 >> wt104 >> wt105 >> wt106 >> wt107

    with Cluster("TH\n茶叶前处理", graph_attr={"label": "TH 茶叶前处理", **cluster_attrs}):
        th101 = Storage("TH-101\n茶叶储罐 2m³")
        th102 = Storage("TH-102\n茶叶粉碎机")
        th101 >> th102

    with Cluster("EX\n萃取系统", graph_attr={"label": "EX 萃取系统(三级逆流)", **cluster_attrs}):
        ex101 = Storage("EX-101\n萃取罐1 95°C")
        ex102 = Storage("EX-102\n萃取罐2 90°C")
        ex103 = Storage("EX-103\n萃取罐3 85°C")
        ex104 = Storage("EX-104\n茶渣分离器")
        ex105 = Storage("EX-105\n茶汁冷却器")

        ex101 >> ex102 >> ex103 >> ex104 >> ex105

    with Cluster("FL\n过滤净化", graph_attr={"label": "FL 过滤净化系统", **cluster_attrs}):
        fl101 = Storage("FL-101\n碟式离心机")
        fl102 = Storage("FL-102\n超滤膜组件 0.1μm")

        fl101 >> fl102

    with Cluster("BL\n调配系统", graph_attr={"label": "BL 调配系统", **cluster_attrs}):
        bl101 = Storage("BL-101\n调配罐1 5m³")
        bl102 = Storage("BL-102\n调配罐2 5m³")
        bl103 = Storage("BL-103\n糖浆溶解罐 2m³")
        bl104 = Storage("BL-104\n糖浆储罐 2m³")
        bl105 = Storage("BL-105\n酸液罐")

        bl101 >> bl102
        bl103 >> bl104 >> bl105
        bl101 - bl102

    with Cluster("HM\n均质系统", graph_attr={"label": "HM 均质系统", **cluster_attrs}):
        hm101 = Storage("HM-101\n高压均质机 20-25MPa")

    with Cluster("UH\nUHT杀菌", graph_attr={"label": "UH UHT杀菌系统", **cluster_attrs}):
        uh102 = Storage("UH-102\n预热器 80°C")
        uh101 = Storage("UH-101\nUHT杀菌锅 135°C/15s")
        uh103 = Storage("UH-103\n保温管 30m")
        uh104 = Storage("UH-104\n冷却器 25°C")
        uh105 = Storage("UH-105\n无菌储罐 3m³")

        uh102 >> uh101 >> uh103 >> uh104 >> uh105

    with Cluster("PKG\n包装系统", graph_attr={"label": "PKG 包装系统", **cluster_attrs}):
        pf101 = Storage("PF-101\n吹灌一体机 54000B/H")
        cg101 = Storage("CG-101\n旋盖机")
        li101 = Storage("LI-101\n视觉灯检机")
        ci101 = Storage("CI-101\n激光喷码机")
        lb101 = Storage("LB-101\n贴标机")
        ca101 = Storage("CA-101\n装箱机")
        pk101 = Storage("PK-101\n冷却隧道")
        pk108 = Storage("PK-108\n码垛机")
        pk110 = Storage("PK-110\n缠绕机")

        pf101 >> cg101 >> li101 >> ci101 >> lb101 >> ca101 >> pk101 >> pk108 >> pk110

    with Cluster("CIP\n清洗系统", graph_attr={"label": "CIP 清洗系统", **cluster_attrs}):
        cp101 = Storage("CP-101\nCIP碱液罐 2m³")
        cp102 = Storage("CP-102\nCIP酸液罐 1m³")
        cp103 = Storage("CP-103\nCIP热水罐 3m³")

    wt107 >> Edge(color="#4fc3f7", label="纯水 5m³/h") >> bl101
    th102 >> Edge(color="#8B4513", label="茶叶粉 200kg/h") >> ex101
    ex105 >> fl101
    fl102 >> Edge(color="#90EE90", label="净化茶汁") >> bl101
    bl102 >> hm101
    hm101 >> uh102
    uh105 >> Edge(color="#90EE90", label="UHT产品") >> pf101

print("流程图已生成: flowsheet_pro.png")