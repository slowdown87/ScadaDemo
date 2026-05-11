GENERATORS = {
    "PLC_Arch": {
        "script": "plc_arch_generator.py",
        "desc": "PLC架构文档",
        "output": "02_Arch/茶饮料_PLC架构_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "TagCode": {
        "script": "tag_code_generator.py",
        "desc": "位号编码规则",
        "output": "03_Device/茶饮料_位号编码规则_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "DeviceParam": {
        "script": "device_param_generator.py",
        "desc": "设备参数表",
        "output": "03_Device/茶饮料_设备参数表_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "MonitorPoint": {
        "script": "monitor_point_generator.py",
        "desc": "监控点表",
        "output": "03_Device/茶饮料_监控点表_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "SCADA_Spec": {
        "script": "scada_spec_generator.py",
        "desc": "SCADA系统功能规格说明书",
        "output": "01_Spec/茶饮料_SCADA功能规格_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "HMI_Spec": {
        "script": "hmi_generator.py",
        "desc": "HMI画面规格说明书",
        "output": "01_Spec/茶饮料_HMI画面规格_auto.md",
        "input": "01_Spec/configs/hmi_config.yaml"
    },
    "FB_Spec": {
        "script": "fb_spec_generator.py",
        "desc": "PLC功能块规格说明书",
        "output": "02_Arch/auto/茶饮料_PLC功能块规格_auto.md",
        "input": "01_Spec/configs/fb_spec_config.yaml"
    },
    "Process_Flow": {
        "script": "process_flow_generator.py",
        "desc": "生产线工艺配置",
        "output": "02_Arch/auto/茶饮料_生产线工艺配置_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "Process_Recipe": {
        "script": "process_recipe_generator.py",
        "desc": "工艺配方",
        "output": "04_Process/auto/茶饮料_工艺配方_auto.md",
        "input": "01_Spec/configs/process_recipe_templates.yaml"
    },
    "Index": {
        "script": "index_generator.py",
        "desc": "文档索引清单",
        "output": "00_Index/auto/文档索引清单_auto.md",
        "input": "01_Spec/configs/index_config.yaml"
    },
    "Interlock": {
        "script": "interlock_generator.py",
        "desc": "联锁逻辑说明书",
        "output": "04_Process/auto/茶饮料_联锁逻辑说明书_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "CIP_Spec": {
        "script": "cip_spec_generator.py",
        "desc": "CIP清洗程序规格书",
        "output": "04_Process/auto/茶饮料_CIP清洗程序规格书_auto.md",
        "input": "01_Spec/configs/process_recipe_templates.yaml"
    },
    "Comm_Spec": {
        "script": "comm_spec_generator.py",
        "desc": "通讯接口规格书",
        "output": "04_Process/auto/茶饮料_通讯接口规格书_auto.md",
        "input": "01_Spec/configs/comm_templates.yaml"
    },
    "CIP_Recipe": {
        "script": "cip_recipe_generator.py",
        "desc": "CIP清洗配方",
        "output": "05_Product/auto/CIP配方_auto.md",
        "input": "05_Product/configs/cip_recipe_templates.yaml"
    },
    "Product_Recipe": {
        "script": "product_recipe_generator.py",
        "desc": "产品配方",
        "output": "05_Product/auto/产品配方_auto.md",
        "input": "05_Product/configs/product_recipe_templates.yaml"
    },
}
