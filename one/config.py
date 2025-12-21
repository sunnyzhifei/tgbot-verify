# SheerID 验证配置文件

# SheerID API 配置
PROGRAM_ID = '67c8c14f5f17a83b745e3f82'
SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'
# 尝试从全局配置导入代理设置
try:
    import config as root_config
    PROXY_URL = getattr(root_config, 'PROXY_URL', None)
except ImportError:
    PROXY_URL = None  # 代理配置，可在 root config.py 或环境变量中设置

# 验证码配置（留空关闭）
HCAPTCHA_SECRET = ''  # 留空关闭 hCaptcha 验证
TURNSTILE_SECRET = ''  # 留空关闭 Turnstile 验证

# 文件大小限制
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# 主要美国大学配置 (SheerID 官方 ID)
SCHOOLS = {
    '650865': {
        'id': 650865,
        'idExtended': '650865',
        'name': 'Arizona State University',
        'city': 'Tempe',
        'state': 'AZ',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'ASU.EDU'
    },
    '2652': {
        'id': 2652,
        'idExtended': '2652',
        'name': 'University of Central Florida',
        'city': 'Orlando',
        'state': 'FL',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'UCF.EDU',
        'latitude': 28.6024,
        'longitude': -81.2001
    },
    '2516': {
        'id': 2516,
        'idExtended': '2516',
        'name': 'The Ohio State University',
        'city': 'Columbus',
        'state': 'OH',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'OSU.EDU',
        'latitude': 40.0067,
        'longitude': -83.0305
    },
    '2686': {
        'id': 2686,
        'idExtended': '2686',
        'name': 'University of Texas at Austin',
        'city': 'Austin',
        'state': 'TX',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'UTEXAS.EDU',
        'latitude': 30.2849,
        'longitude': -97.7341
    },
    '2197': {
        'id': 2197,
        'idExtended': '2197',
        'name': 'Georgia Institute of Technology',
        'city': 'Atlanta',
        'state': 'GA',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'GATECH.EDU',
        'latitude': 33.7756,
        'longitude': -84.3963
    }
}

# 默认学校 (ASU)
DEFAULT_SCHOOL_ID = '650865'

# UTM 参数（营销追踪参数）
# 如果 URL 中没有这些参数，会自动添加
DEFAULT_UTM_PARAMS = {
    'utm_source': 'gemini',
    'utm_medium': 'paid_media',
    'utm_campaign': 'students_pmax_bts-slap'
}

