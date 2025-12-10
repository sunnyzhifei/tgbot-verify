"""通用学生证生成模块 (复刻 student-card-generator)"""
import random
import base64
from datetime import datetime
from typing import Dict, Any

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

# 默认头像 (Dicebear Adventurer)
DEFAULT_AVATAR_TEMPLATE = "https://api.dicebear.com/7.x/adventurer/svg?seed={}"

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

def generate_dates():
    """生成相关日期 (DOB, Issued, Valid Thru)"""
    now = datetime.now()
    
    # 年龄 18-26
    age = 18 + random.randint(0, 8)
    dob_year = now.year - age
    dob = datetime(dob_year, random.randint(1, 12), random.randint(1, 28))
    
    # 入学年份 (DOB + 18)
    enrollment_year = dob_year + 18
    # 签发日期 (入学当年随机)
    issued = datetime(enrollment_year, random.randint(1, 12), random.randint(1, 28))
    
    # 有效期 (签发 + 4年)
    valid_thru = datetime(issued.year + 4, issued.month, issued.day)
    
    return {
        "dob": dob.strftime("%d/%m/%Y"),
        "issued": issued.strftime("%d/%m/%Y"),
        "valid_thru": valid_thru.strftime("%d/%m/%Y")
    }

def generate_html(first_name: str, last_name: str, photo_url: str = None) -> str:
    """生成学生证 HTML (完全复刻前端)"""
    
    uni = get_random_university()
    full_name = f"{first_name} {last_name}"
    
    # 数据生成
    student_id = generate_student_id()
    dates = generate_dates()
    major = random.choice(uni["majors"]) if "majors" in uni else "Information Technology"
    
    # 处理头像
    if not photo_url:
        seed = full_name.replace(" ", "")
        photo_url = DEFAULT_AVATAR_TEMPLATE.format(seed)

    # 样式定义 (从 style.css 和 JS 内联样式提取)
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {
            margin: 0;
            padding: 0;
            background-color: transparent;
            font-family: 'Inter', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .id-card {
            width: 480px; /* 略微放大以便截图清晰 */
            height: 300px;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            overflow: hidden;
            position: relative;
            display: flex;
            flex-direction: column;
        }

        /* 垂直布局 */
        .id-card.vertical-card {
            width: 300px;
            height: 480px;
        }

        .glass-overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 100%);
            pointer-events: none;
            z-index: 2;
        }

        .card-header {
            padding: 20px;
            display: flex;
            align-items: center;
            color: white;
            position: relative;
            z-index: 1;
        }

        .vertical-card .card-header {
            flex-direction: column;
            text-align: center;
            padding-bottom: 30px;
        }

        .university-logo {
            width: 60px;
            height: 60px;
            object-fit: contain;
            background: rgba(255,255,255,0.9);
            border-radius: 50%;
            padding: 5px;
            margin-right: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        .vertical-card .university-logo {
            margin-right: 0;
            margin-bottom: 10px;
            width: 70px;
            height: 70px;
        }

        .university-info {
            flex: 1;
        }

        .university-name {
            font-size: 20px;
            font-weight: 800;
            margin: 0;
            line-height: 1.2;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .university-full-name {
            font-size: 10px;
            opacity: 0.9;
            margin: 4px 0 0 0;
            font-weight: 400;
        }

        .card-content {
            flex: 1;
            padding: 20px;
            display: flex;
            gap: 20px;
            background: #fff;
            position: relative;
            z-index: 1;
            align-items: center;
        }

        .vertical-card .card-content {
            flex-direction: column;
            text-align: center;
            padding-top: 5px;
        }

        .photo-container {
            flex-shrink: 0;
        }

        .student-photo {
            width: 100px;
            height: 120px;
            object-fit: cover;
            border-radius: 8px;
            border: 3px solid #f0f0f0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .vertical-card .student-photo {
            width: 110px;
            height: 110px;
            border-radius: 50%;
            border: 4px solid #fff;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            margin-top: -50px; /* Pull up into header */
            position: relative;
            z-index: 3;
            background: #fff;
        }

        .student-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 6px;
            width: 100%;
        }

        .info-row {
            display: flex;
            font-size: 11px;
            border-bottom: 1px solid #f5f5f5;
            padding-bottom: 3px;
        }

        .vertical-card .info-row {
            justify-content: space-between;
        }

        .label {
            color: #888;
            font-weight: 600;
            width: 75px;
        }

        .value {
            color: #333;
            font-weight: 500;
            flex: 1;
        }
        
        .id-number {
            font-family: 'Courier New', monospace;
            font-weight: 700;
            letter-spacing: 1px;
            color: #000;
        }

        .card-footer {
            padding: 15px 20px;
            border-top: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #fcfcfc;
        }

        .signature {
            display: flex;
            flex-direction: column;
        }

        .signature-text {
            font-family: 'Brush Script MT', cursive;
            font-size: 20px;
            color: #000;
        }

        .signature-label {
            font-size: 8px;
            color: #999;
            text-transform: uppercase;
        }

        .barcode {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }

        .barcode-svg {
            height: 25px;
            width: 100px;
            opacity: 0.7;
        }
        
        .barcode-number {
            font-size: 9px;
            color: #555;
            font-family: monospace;
            letter-spacing: 2px;
        }
    </style>
    """

    # 构建 HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        {css}
    </head>
    <body>
        <div class="id-card {uni['layout']}-card" style="border-top: 4px solid {uni['color']}">
            <div class="glass-overlay"></div>
            
            <!-- Header -->
            <div class="card-header" style="background: linear-gradient(135deg, {uni['color']}, {uni['color']}dd)">
                <img src="{uni['logo']}" alt="Logo" class="university-logo">
                <div class="university-info">
                    <h2 class="university-name">{uni['shortName']}</h2>
                    <p class="university-full-name">{uni['name']}</p>
                </div>
            </div>
            
            <!-- Content -->
            <div class="card-content">
                <div class="photo-container">
                    <img src="{photo_url}" alt="Student Photo" class="student-photo">
                </div>
                <div class="student-info">
                    <div class="info-row"><span class="label">Full Name:</span><span class="value">{full_name}</span></div>
                    <div class="info-row"><span class="label">Student ID:</span><span class="value id-number">{student_id}</span></div>
                    <div class="info-row"><span class="label">DOB:</span><span class="value">{dates['dob']}</span></div>
                    <div class="info-row"><span class="label">Major:</span><span class="value">{major}</span></div>
                    <div class="info-row"><span class="label">Issued:</span><span class="value">{dates['issued']}</span></div>
                    <div class="info-row"><span class="label">Valid Thru:</span><span class="value">{dates['valid_thru']}</span></div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="card-footer">
                <div class="signature">
                    <span class="signature-text">{full_name}</span>
                    <span class="signature-label">Student Signature</span>
                </div>
                <div class="barcode">
                    <svg viewBox="0 0 120 40" class="barcode-svg">
                       <rect x="0" y="0" width="4" height="40" fill="#000"/><rect x="6" y="0" width="2" height="40" fill="#000"/><rect x="10" y="0" width="4" height="40" fill="#000"/><rect x="16" y="0" width="2" height="40" fill="#000"/><rect x="20" y="0" width="6" height="40" fill="#000"/><rect x="28" y="0" width="2" height="40" fill="#000"/><rect x="32" y="0" width="4" height="40" fill="#000"/><rect x="38" y="0" width="2" height="40" fill="#000"/><rect x="42" y="0" width="4" height="40" fill="#000"/><rect x="48" y="0" width="6" height="40" fill="#000"/><rect x="56" y="0" width="2" height="40" fill="#000"/><rect x="60" y="0" width="4" height="40" fill="#000"/><rect x="66" y="0" width="2" height="40" fill="#000"/><rect x="70" y="0" width="6" height="40" fill="#000"/><rect x="78" y="0" width="2" height="40" fill="#000"/><rect x="82" y="0" width="4" height="40" fill="#000"/><rect x="88" y="0" width="2" height="40" fill="#000"/><rect x="92" y="0" width="4" height="40" fill="#000"/><rect x="98" y="0" width="6" height="40" fill="#000"/><rect x="106" y="0" width="2" height="40" fill="#000"/><rect x="110" y="0" width="4" height="40" fill="#000"/><rect x="116" y="0" width="2" height="40" fill="#000"/>
                    </svg>
                    <span class="barcode-number">{student_id}</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def generate_image(first_name, last_name, school_id=None):
    """
    生成学生证图片
    
    Args:
        first_name: 名字
        last_name: 姓氏
        school_id: (已弃用，随机选择) 
    """
    try:
        from playwright.sync_api import sync_playwright

        html_content = generate_html(first_name, last_name)

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
    data = generate_image("Alex", "Chen")
    with open("test_new_card.png", "wb") as f:
        f.write(data)
    print("Test card generated: test_new_card.png")
