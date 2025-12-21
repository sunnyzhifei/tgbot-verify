import random
import base64
import os
from datetime import datetime
from typing import Dict, Any

# 尝试引用 AcaGenProvider 以共享学校数据
try:
    from .acagen_provider import AcaGenProvider
except ImportError:
    AcaGenProvider = None

# 嵌入的大学数据 (源自 student-card-generator/js/universities.js)
UNIVERSITY_DATA = {
    "USA": [
        {
            "name": "Massachusetts Institute of Technology",
            "shortName": "MIT",
            "domain": "mit.edu",
            "logo": "https://upload.wikimedia.org/wikipedia/commons/0/0c/MIT_logo.svg", # 使用在线URL替代本地路径
            "color": "#A31F34",
            "layout": "horizontal",
            "address": "77 Massachusetts Ave, Cambridge, MA 02139, USA",
            "majors": ["Computer Science", "Mechanical Engineering", "Physics", "Mathematics", "Electrical Engineering"]
        },
        {
            "name": "Harvard University",
            "shortName": "Harvard",
            "domain": "harvard.edu",
            "logo": "https://upload.wikimedia.org/wikipedia/commons/7/70/Harvard_University_logo.svg",
            "color": "#A51C30",
            "layout": "vertical",
            "address": "Cambridge, MA 02138, USA",
            "majors": ["Law", "Medicine", "Business", "Political Science", "Economics"]
        },
        {
            "name": "Stanford University",
            "shortName": "Stanford",
            "domain": "stanford.edu",
            "logo": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Stanford_University_logo_2012.svg", # 替换为可靠的在线Logo
            "color": "#8C1515",
            "layout": "vertical",
            "address": "450 Serra Mall, Stanford, CA 94305, USA",
            "majors": ["Computer Science", "Engineering", "Business", "Law", "Medicine"]
        }
    ],
    "UK": [
        {
            "name": "University of Oxford",
            "shortName": "Oxford",
            "domain": "ox.ac.uk",
            "logo": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Oxford-University-Circlet.svg",
            "color": "#002147",
            "layout": "vertical",
            "address": "Wellington Square, Oxford OX1 2JD, UK",
            "majors": ["Philosophy, Politics and Economics", "Law", "Medicine", "History", "Mathematics"]
        },
        {
            "name": "University of Cambridge",
            "shortName": "Cambridge",
            "domain": "cam.ac.uk",
            "logo": "https://upload.wikimedia.org/wikipedia/commons/c/c3/University_of_Cambridge_logo.svg",
            "color": "#A3C1AD",
            "layout": "horizontal",
            "address": "The Old Schools, Trinity Ln, Cambridge CB2 1TN, UK",
            "majors": ["Natural Sciences", "Engineering", "Medicine", "Law", "Computer Science"]
        }
    ],
    "Singapore": [
         {
            "name": "National University of Singapore",
            "shortName": "NUS",
            "domain": "nus.edu.sg",
            "logo": "https://upload.wikimedia.org/wikipedia/en/b/b9/NUS_coat_of_arms.svg",
            "color": "#EF7C00",
            "layout": "horizontal",
            "address": "21 Lower Kent Ridge Rd, Singapore 119077",
            "majors": ["Computer Science", "Engineering", "Business", "Medicine", "Law"]
        }
    ]
}

# 默认头像 (使用 RandomUser.me 获取真人头像)
# 注意：RandomUser 提供的是真实人脸素材，更适合 ID 卡
# 为了保证男女比例平衡，可以随机选择性别
def get_random_avatar_url(gender=None):
    """获取随机真人头像 URL"""
    # 随机性别
    if not gender:
        gender = random.choice(["men", "women"])
    
    # RandomUser.me 提供了几十张男女头像，ID范围 0-99
    # 例如: https://randomuser.me/api/portraits/men/1.jpg
    img_id = random.randint(0, 99)
    return f"https://randomuser.me/api/portraits/{gender}/{img_id}.jpg"

# DEFAULT_AVATAR_TEMPLATE 已弃用，改用动态生成

def get_random_university():
    """随机获取一个大学配置 (仅限美国)"""
    # 强制只选择 USA
    country = "USA"
    if country in UNIVERSITY_DATA:
        uni = random.choice(UNIVERSITY_DATA[country])
        return uni
    
    # Fallback (理论上不会发生，除非数据为空)
    return random.choice(UNIVERSITY_DATA["USA"])

def generate_student_id():
    """生成学生ID: YYYY + 5位随机数"""
    year = datetime.now().year
    rand_suffix = random.randint(10000, 99999)
    return f"{year}{rand_suffix}"

def generate_dates(birth_date_str=None):
    """生成相关日期 (DOB, Issued, Valid Thru)
    闭环逻辑：以 API 提交的生日为基准，确保证件当前在有效期内且至少还有一年过期。
    """
    now = datetime.now()
    
    # 0. 确定生日 (Source of Truth)
    if birth_date_str:
        try:
            dob = datetime.strptime(birth_date_str, "%Y-%m-%d")
        except ValueError:
            dob = datetime(2002, 1, 1)
    else:
        # 只有在没有传入时才随机，确保 20-25 岁
        dob_year = now.year - random.randint(20, 25)
        dob = datetime(dob_year, random.randint(1, 12), random.randint(1, 28))

    # 1. 计算默认毕业年份 (按 18 岁入学 + 4 年学制 = 22 岁毕业)
    default_exit_year = dob.year + 22
    
    # 2. 闭环修正：如果按 18 岁算已经毕业了，或者即将毕业（不满一年）
    # 我们将其模拟为“在读研究生”或者“晚入学的本科生”
    if default_exit_year < now.year + 1:
        # 强制有效期在未来 1.5 - 2.5 年后
        valid_thru_year = now.year + random.randint(1, 2)
    else:
        # 如果还没毕业，就按正常的 22 岁毕业逻辑
        valid_thru_year = default_exit_year

    # 3. 细化有效期 (设置为毕业月 5/6 月)
    valid_thru_month = 5 if random.random() > 0.5 else 6
    valid_thru_day = random.randint(15, 30)
    valid_thru = datetime(valid_thru_year, valid_thru_month, valid_thru_day)
    
    # 4. 签发日期 (Issued): 有效期前推 4 年，固定在秋季 8/9 月入学
    issued_year = valid_thru.year - 4
    issued = datetime(issued_year, random.randint(8, 9), random.randint(1, 28))
    
    return {
        "dob": dob.strftime("%d/%m/%Y"), # 图片显示格式 DD/MM/YYYY
        "issued": issued.strftime("%d/%m/%Y"),
        "valid_thru": valid_thru.strftime("%d/%m/%Y")
    }

def _get_logo_base64(logo_name):
    """从 assets/logos 读取并返回 base64"""
    if not logo_name or logo_name.startswith("http"):
        return logo_name
        
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logos", logo_name)
    if os.path.exists(logo_path):
        try:
            ext = os.path.splitext(logo_name)[1].lower().replace('.', '')
            mime = 'image/svg+xml' if ext == 'svg' else f'image/{ext}'
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                return f"data:{mime};base64,{encoded}"
        except Exception:
            return logo_name
    return logo_name

def generate_html(first_name: str, last_name: str, photo_url: str = None, university_name: str = None, birth_date: str = None, **kwargs) -> str:
    """生成学生证 HTML (完全复刻 AcaGen 设计)
    Args:
        first_name: 名
        last_name: 姓
        photo_url: 头像URL
        university_name: 学校名称 (用于匹配)
        birth_date: 生日 (YYYY-MM-DD)
        **kwargs: 包含 studentId, major, college 等额外字段
    """
    
    # 1. 尝试从 AcaGenProvider 匹配
    uni = None
    if AcaGenProvider and university_name:
        for u in AcaGenProvider.UNIVERSITIES:
            if u["name"].lower() == university_name.lower() or u["short"].lower() == university_name.lower():
                # 转换为 img_generator 兼容格式
                uni = {
                    "name": u["name"],
                    "shortName": u["short"],
                    "domain": u["domain"],
                    "logo": _get_logo_base64(u["logo"]),
                    "color": "#1e3a8a", # 默认蓝色
                    "layout": "horizontal",
                    "majors": ["Computer Science", "Engineering", "Business"]
                }
                break
    
    # 2. 如果没匹配到，尝试匹配内置 UNIVERSITY_DATA
    if not uni and university_name:
        for u in UNIVERSITY_DATA.get("USA", []):
            if u["name"].lower() == university_name.lower() or u["shortName"].lower() == university_name.lower():
                uni = u.copy()
                break
    
    if not uni:
        # 如果没找到匹配的配置，或者没传，就随机给一个 (注意：这可能导致不一致，但在 verifier 调用时应确保能匹配)
        # 即使没匹配到配置，也可以根据传入 accessor 的 university_name 动态构造一个基础配置
        if university_name:
            uni = {
                 "name": university_name,
                 "shortName": "".join([w[0] for w in university_name.split() if w[0].isupper()]), # 简单的缩写生成
                 "color": "#003366", # 默认深蓝
                 "layout": "horizontal",
                 "logo": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Education%2C_Studying%2C_University%2C_Alumni_-_icon.png", # 通用Logo
                 "majors": ["Information Technology", "Computer Science"]
            }
        else:
            uni = get_random_university()

    full_name = f"{first_name} {last_name}"
    
    # 数据生成
    student_id = kwargs.get("studentId", "047794-7940") if kwargs else generate_student_id()
    dates = generate_dates(birth_date)
    major = kwargs.get("major", "College of Business") if kwargs else random.choice(uni["majors"])
    college = kwargs.get("college", f"McCoy {major}") if kwargs else f"{major}"
    
    # 处理头像
    if not photo_url:
        photo_url = get_random_avatar_url()

    # 样式定义 (精确复刻 AcaGen 截图)
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        body {{
            margin: 0;
            padding: 0;
            background-color: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}

        .id-card {{
            width: 750px;
            height: 480px;
            background-color: white;
            border-radius: 24px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
        }}

        .header {{
            background: #FBBF24; /* AcaGen 橙黄色 Header */
            color: white;
            padding: 0 30px;
            display: flex;
            align-items: center;
            gap: 22px;
            height: 135px;
            flex-shrink: 0;
        }}

        .logo-container {{
            width: 112px;
            height: 112px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}

        .logo-img {{
            width: 90px;
            height: 90px;
            object-fit: contain;
        }}

        .uni-info {{
            flex: 1;
        }}

        .uni-name {{
            font-size: 40px;
            font-weight: 700;
            margin: 0;
            line-height: 1.1;
        }}

        .card-type {{
            font-size: 18px;
            text-transform: uppercase;
            opacity: 1;
            margin-top: 5px;
            letter-spacing: 1px;
            font-weight: 500;
        }}

        .body {{
            flex: 1;
            padding: 30px;
            display: flex;
            gap: 30px;
            background: #fdfdfd;
        }}

        .photo-box {{
            width: 150px;
            height: 190px;
            background: #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #e5e7eb;
            flex-shrink: 0;
            margin-top: 10px;
        }}

        .student-photo {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .info-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 10px 0;
        }}

        .field {{
            margin-bottom: 5px;
        }}

        .label {{
            font-size: 15px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
            margin-bottom: 2px;
        }}

        .value {{
            font-size: 28px;
            font-weight: 600;
            color: #333;
        }}

        .footer {{
            height: 90px;
            padding: 0 40px;
            background: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #f3f3f3;
        }}

        .footer-item {{
            text-align: left;
        }}

        .footer-item.right {{
            text-align: right;
        }}

        .footer-label {{
            font-size: 13px;
            color: #999;
            text-transform: uppercase;
            font-weight: 500;
            margin-bottom: 3px;
        }}

        .footer-value {{
            font-size: 20px;
            font-weight: 600;
            color: #333;
        }}
    </style>
    """

    # 构建 HTML (按截图字段顺序: NAME -> STUDENT ID -> FACULTY)
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        {css}
    </head>
    <body>
        <div class="id-card">
            <!-- Header Section -->
            <div class="header">
                <div class="logo-container">
                    <img src="{uni['logo']}" class="logo-img">
                </div>
                <div class="uni-info">
                    <div class="uni-name">{uni['name']}</div>
                    <div class="card-type">International Student ID Card</div>
                </div>
            </div>
            
            <!-- Body Section -->
            <div class="body">
                <div class="photo-box">
                    <img src="{photo_url}" class="student-photo">
                </div>
                <div class="info-panel">
                    <div class="field">
                        <div class="label">NAME</div>
                        <div class="value">{full_name}</div>
                    </div>
                    <div class="field">
                        <div class="label">STUDENT ID</div>
                        <div class="value" style="font-family: inherit;">{student_id}</div>
                    </div>
                    <div class="field">
                        <div class="label">FACULTY</div>
                        <div class="value">{college}</div>
                    </div>
                </div>
            </div>
            
            <!-- Footer Section -->
            <div class="footer">
                <div class="footer-item">
                    <div class="footer-label">ISSUE DATE</div>
                    <div class="footer-value">{dates['issued']}</div>
                </div>
                <div class="footer-item right">
                    <div class="footer-label">VALID UNTIL</div>
                    <div class="footer-value">{dates['valid_thru']}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def generate_image(first_name, last_name, school_name=None, birth_date=None, **kwargs):
    """
    生成学生证图片
    
    Args:
        first_name: 名字
        last_name: 姓氏
        school_name: 学校全名 (用于选择模板)
        birth_date: 生日字符串 (YYYY-MM-DD)
    """
    try:
        from playwright.sync_api import sync_playwright

        html_content = generate_html(
            first_name, 
            last_name, 
            university_name=school_name,
            birth_date=birth_date,
            **kwargs
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # 设置透明背景
            page = browser.new_page(viewport={'width': 600, 'height': 600}, device_scale_factor=2)
            page.set_content(html_content, wait_until='networkidle') 
            
            # 定位到 .id-card 元素进行截图
            card_locator = page.locator('.id-card')
            screenshot_bytes = card_locator.screenshot(type='png', omit_background=True)
            
            browser.close()

        return screenshot_bytes

    except ImportError:
        raise Exception("Playwright not installed. Run: pip install playwright && playwright install chromium")
    except Exception as e:
        raise Exception(f"Generate image failed: {str(e)}")

# For backward compatibility with existing verifier code
def generate_psu_email(first_name, last_name):
    # 保留这个辅助函数，虽然新的卡片不一定显示邮箱，但验证逻辑可能需要
    return f"{first_name.lower()}.{last_name.lower()}@student.edu"

if __name__ == '__main__':
    # 测试生成的代码
    import os
    print("Testing Image Generator...")
    
    # 测试数据
    test_first = "Alice"
    test_last = "Wonderland"
    test_school = "Massachusetts Institute of Technology"
    test_dob = "2002-05-20"
    
    print(f"Generating ID Card for:")
    print(f"Name: {test_first} {test_last}")
    print(f"School: {test_school}")
    print(f"DOB: {test_dob}")
    
    try:
        data = generate_image(
            test_first, 
            test_last, 
            school_name=test_school,
            birth_date=test_dob
        )
        
        output_file = f"test_{test_school.lower().replace(' ', '_')}.png"
        with open(output_file, "wb") as f:
            f.write(data)
            
        print(f"Success! Generated image saved to: {os.path.abspath(output_file)}")
        print("Please open the image to verify: Name, School Logo, DOB, and Realistic Avatar.")
        
    except Exception as e:
        print(f"Failed: {e}")
