import os
# 定义默认图片资源目录路径
DEFAULT_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "images")

DEFAULT_COMPANY_INFO = {
    "name": "无锡谱视界科技有限公司",
    "address": "江苏省无锡市新吴区菱湖大道200号E2-111",
    "email": "company@specvision.com.cn",
    "phone": "0510-85290662",
    "logo_path": os.path.join(DEFAULT_IMAGES_DIR, "logo.png"),
    "watermark_path": os.path.join(DEFAULT_IMAGES_DIR, "waterpicture.png"),
    "profile": """无锡谱视界科技有限公司于2021年成立于无锡，由江苏双利合谱科技有限公司、长春长光辰谱科技有限公司和核心团队共同出资组建。公司目前员工40余人，研发团队占比2/3，核心团队来自中国科学院长春光学精密机械与物理研究所、北京卓立汉光仪器有限公司（上市公司）等国内顶尖的研究机构和相关龙头企业。
    无锡谱视界科技有限公司拥有基于像元级镀膜分光技术开发的快照式光谱遥感成像和AI大模型光谱数据解析两大核心技术。其中像元级镀膜技术是由中国科学院长春光学精密机械与物理研究所成果转化而来，曾应用于珠海一号、吉林一号等多型号遥感卫星。在水环境监测领域，无锡谱视界科技有限公司基于像元级镀膜核心技术开发了可用于水生态环境监测的机载快照式光谱成像指数分析仪、智能小型机载光谱指数分析基站、岸基高光谱水质监测仪、全天候光谱水质监测仪、高光谱塔基水质监测仪和手持式高光谱智水仪等多个产品，是国内唯一一家将像元级镀膜技术产品化并成功应用于水生态环境监测的企业。公司目前授权专利11项（其中发明专利8项，实用新型3项），软件著作权15个，与多家研究单位进行产学研合作，获2022年中国产学研合作创新与促进奖（产学研合作创新奖）。""",
    # Spire.Doc水印配置
    "watermark_enabled": True,           # 是否启用水印
    "watermark_text": "无锡谱视界科技有限公司",        # 水印文本
    "watermark_size": 65,                # 水印字体大小
    "watermark_color": (200, 0, 0),      # 水印颜色，RGB格式
    "watermark_diagonal": True,          # 是否使用对角线布局
    "watermark_use_spire": True          # 是否使用Spire.Doc添加水印
}