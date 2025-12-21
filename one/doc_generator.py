import os
import random
import base64
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

class DocGenerator:
    COMMON_STYLE = '''
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    body {
        margin: 0;
        padding: 0;
        background-color: #f3f4f6;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 50px 0;
        font-family: 'Inter', sans-serif;
    }
    
    .paper {
        width: 794px;
        min-height: 1123px;
        background: white;
        padding: 60px 70px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        position: relative;
        box-sizing: border-box;
        color: #1a1a1a;
        margin-bottom: 40px;
    }
    
    .serif { font-family: 'Crimson Pro', serif; }
    
    .header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .uni-logo {
        width: 70px;
        height: 70px;
        margin-bottom: 10px;
    }
    
    .uni-name {
        font-size: 24px;
        color: #1e3a8a;
        font-weight: 700;
        text-transform: uppercase;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    .divider {
        border-bottom: 1px solid #e5e7eb;
        margin: 20px 0;
    }
    
    .doc-title {
        text-align: center;
        font-size: 20px;
        font-weight: 700;
        text-decoration: underline;
        margin: 30px 0;
        text-transform: uppercase;
    }
    '''

    @staticmethod
    def _get_logo_base64(logo_name):
        """将本地 Logo 转换为 Base64，如果失败则返回原始名称(可能是 URL)"""
        if not logo_name or logo_name.startswith("http"):
            return logo_name
            
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logos", logo_name)
        if os.path.exists(logo_path):
            try:
                ext = os.path.splitext(logo_name)[1].lower().replace('.', '')
                if ext == 'svg':
                    mime = 'image/svg+xml'
                else:
                    mime = f'image/{ext}'
                    
                with open(logo_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    return f"data:{mime};base64,{encoded}"
            except Exception:
                return logo_name
        return logo_name

    @staticmethod
    def generate_admission_letter_html(data):
        university = data.get("university", "Hachimi University")
        # 处理本地 Logo
        raw_logo = data.get("logo", "asu.png")
        uni_logo = DocGenerator._get_logo_base64(raw_logo)
        full_name = data.get("fullName", "Grimes Kelton")
        term = data.get("term", "Fall 2024")
        student_id = data.get("studentId", "511355-7318")
        passport_no = data.get("passportNo", "Z6PZKOC6B")
        program = data.get("program", "Bachelor of Business Admin")
        major = data.get("major", "Marketing")
        college = data.get("college", f"College of {major.split()[-1]}")
        issue_date = data.get("issueDate", "09/26/2024")
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                {DocGenerator.COMMON_STYLE}
                .admission-body {{ font-family: 'Crimson Pro', serif; font-size: 17px; line-height: 1.6; }}
                .info-box {{ background: #f9fafb; border-left: 4px solid #1e3a8a; padding: 20px; margin: 30px 0; display: grid; grid-template-columns: 140px 1fr; gap: 8px; font-family: 'Inter', sans-serif; font-size: 14px; }}
                .info-label {{ color: #6b7280; font-weight: 600; }}
                .official-seal {{ position: absolute; bottom: 80px; right: 80px; width: 110px; height: 110px; border: 3px solid #b91c1c; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: #b91c1c; font-weight: 700; opacity: 0.5; transform: rotate(-15deg); }}
            </style>
        </head>
        <body>
            <div class="paper admission-body">
                <div class="header">
                    <img src="{uni_logo}" class="uni-logo">
                    <h1 class="uni-name">{university}</h1>
                    <div style="font-style: italic; color: #4b5563;">Office of Admissions</div>
                </div>
                <div class="divider"></div>
                <div class="doc-title" style="text-decoration: none;">LETTER OF ADMISSION</div>
                <div style="font-weight: 600; margin-bottom: 20px;">Date: {issue_date}</div>
                <div style="font-weight: 700; font-size: 18px; margin-bottom: 20px;">Dear {full_name},</div>
                <p>We are pleased to inform you that you have been admitted to <b>{university}</b> for the <b>{term}</b> semester. The Admissions Committee was impressed by your academic achievements and believes you will make a significant contribution to our university community.</p>
                <div class="info-box">
                    <div class="info-label">Student ID:</div><div>{student_id}</div>
                    <div class="info-label">Passport No:</div><div>{passport_no}</div>
                    <div class="info-label">Program:</div><div>{program}</div>
                    <div class="info-label">Major:</div><div>{major}</div>
                    <div class="info-label">College:</div><div>{college}</div>
                </div>
                <p>Your program is expected to commence soon. Please report to the International Student Office upon arrival to finalize your registration. This offer is contingent upon verification of final transcripts.</p>
                <div style="margin-top: 60px;">
                    <div style="width: 180px; border-top: 1px solid #000; margin-bottom: 5px;"></div>
                    <b>O'Keefe, Uriah (PhD)</b><br><span style="font-size: 14px; color: #666;">Dean of Admissions</span>
                </div>
                <div class="official-seal">OFFICIAL<br>SEAL</div>
            </div>
        </body>
        </html>
        '''
        return html

    @staticmethod
    def generate_enrollment_cert_html(data):
        university = data.get("university", "Hachimi University")
        # 处理本地 Logo
        raw_logo = data.get("logo", "asu.png")
        uni_logo = DocGenerator._get_logo_base64(raw_logo)
        
        full_name = data.get("fullName", "Grimes Kelton")
        student_id = data.get("studentId", "511355-7318")
        term = data.get("term", "Fall 2024")
        major = data.get("major", "Marketing")
        grad_date = data.get("validUntil", "May 2028")
        issue_date = data.get("issueDate", datetime.now().strftime("%m/%d/%Y"))

        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                {DocGenerator.COMMON_STYLE}
                .cert-body {{ font-family: 'Inter', sans-serif; font-size: 15px; line-height: 1.8; color: #374151; }}
                .cert-title {{ font-size: 22px; font-weight: 800; border-bottom: 2px solid #000; display: inline-block; padding-bottom: 5px; }}
            </style>
        </head>
        <body>
            <div class="paper cert-body">
                <div class="header" style="text-align: left; display: flex; align-items: center; gap: 15px;">
                    <img src="{uni_logo}" style="width: 50px; height: 50px; object-fit: contain;">
                    <h1 class="uni-name" style="font-size: 20px;">{university}</h1>
                </div>
                <div class="divider"></div>
                <div style="text-align: center; margin: 40px 0;">
                    <div class="cert-title">CERTIFICATE OF ENROLLMENT</div>
                </div>
                <div style="text-align: right; font-weight: 700; margin-bottom: 40px;">Date Issued: {issue_date}</div>
                <p>To Whom It May Concern:</p>
                <p>This letter is to certify that <b>{full_name}</b> (Student ID: <b>{student_id}</b>) is currently enrolled as a full-time student at {university}.</p>
                <p>The student is pursuing a degree in <b>{major}</b>. The student is currently registered for the <b>{term}</b> academic term.</p>
                <p><b>Anticipated Graduation Date:</b> {grad_date}<br><b>Academic Standing:</b> Good Standing</p>
                <p style="margin-top: 40px;">This certificate is issued upon the request of the student for whatever legal purpose it may serve.</p>
                <div style="margin-top: 80px;">
                    <div style="width: 220px; border-top: 1px solid #999; margin-bottom: 5px;"></div>
                    <b>Waters, Misael</b><br>University Registrar
                </div>
                <div style="position: absolute; bottom: 60px; right: 70px; font-size: 11px; color: #999; text-align: right; width: 200px; font-style: italic;">
                    This document is electronically generated and valid without a physical signature if verified online.
                </div>
            </div>
        </body>
        </html>
        '''
        return html

    @staticmethod
    def generate_transcript_html(data):
        university = data.get("university", "Hachimi University")
        # 处理本地 Logo
        raw_logo = data.get("logo", "asu.png")
        uni_logo = DocGenerator._get_logo_base64(raw_logo)

        full_name = data.get("fullName", "Grimes Kelton")
        student_id = data.get("studentId", "511355-7318")
        major = data.get("major", "Marketing")
        college = data.get("college", f"College of {major.split()[-1]}")
        
        courses = [
            {"code": "MKT 3358", "desc": "Professional Selling", "grade": "A", "hours": "3.00", "pts": "12.00"},
            {"code": "QMST 2333", "desc": "Business Statistics", "grade": "B", "hours": "3.00", "pts": "9.00"},
            {"code": "ENG 1310", "desc": "College Writing I", "grade": "A", "hours": "3.00", "pts": "12.00"},
            {"code": "COMM 1310", "desc": "Fund. of Human Communication", "grade": "A", "hours": "3.00", "pts": "12.00"},
            {"code": "ENG 1320", "desc": "College Writing II", "grade": "A", "hours": "3.00", "pts": "12.00"}
        ]

        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                {DocGenerator.COMMON_STYLE}
                .ts-header {{ display: grid; grid-template-columns: 100px 1fr 100px 1fr; gap: 10px; font-size: 13px; background: #fff; padding: 15px; border: 1px solid #eee; margin-bottom: 20px; }}
                .ts-label {{ font-weight: 700; color: #444; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }}
                th {{ background: #e5e7eb; padding: 8px; text-align: left; font-weight: 700; }}
                td {{ padding: 8px; border-bottom: 1px solid #f3f4f6; }}
                .term-header {{ background: #f3f4f6; padding: 5px 10px; font-weight: 700; font-size: 14px; border-top: 1px solid #ddd; }}
                .totals {{ display: flex; justify-content: space-between; font-weight: 700; padding: 5px 10px; background: #fff; border-bottom: 2px solid #ddd; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="paper">
                <div class="header" style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px;">
                    <img src="{uni_logo}" style="width: 45px; height: 45px; object-fit: contain;">
                    <div>
                        <div class="uni-name" style="font-size: 16px;">{university}</div>
                        <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: #666;">Office of the University Registrar</div>
                    </div>
                </div>
                <div class="ts-header">
                    <div class="ts-label">Name:</div><div>{full_name}</div>
                    <div class="ts-label">Student ID:</div><div>{student_id}</div>
                    <div class="ts-label">College:</div><div>{college}</div>
                    <div class="ts-label">Major:</div><div>{major}</div>
                </div>

                <div class="term-header">Fall 2024</div>
                <table>
                    <thead><tr><th>Course</th><th>Description</th><th>Grade</th><th>Hours</th><th>Quality Pts</th></tr></thead>
                    <tbody>
                        {" ".join([f"<tr><td>{c['code']}</td><td>{c['desc']}</td><td>{c['grade']}</td><td>{c['hours']}</td><td>{c['pts']}</td></tr>" for c in courses])}
                    </tbody>
                </table>
                <div class="totals">
                    <div>Term Totals:</div><div>Attempted: 15.00</div><div>Earned: 15.00</div><div>GPA Hours: 15.00</div><div>GPA: 3.80</div>
                </div>

                <div class="term-header" style="margin-top: 20px;">Spring 2025</div>
                <table>
                    <thead><tr><th>Course</th><th>Description</th><th>Grade</th><th>Hours</th><th>Quality Pts</th></tr></thead>
                    <tbody>
                        {" ".join([f"<tr><td>{c['code']}</td><td>{c['desc']}</td><td>{c['grade']}</td><td>{c['hours']}</td><td>{c['pts']}</td></tr>" for c in courses])}
                    </tbody>
                </table>
                <div class="totals">
                    <div>Term Totals:</div><div>Attempted: 15.00</div><div>Earned: 15.00</div><div>GPA: 3.80</div>
                </div>

                <div style="margin-top: 40px; border-top: 2px solid #000; padding-top: 10px; font-weight: 700; display: flex; justify-content: space-between;">
                    <div>Cumulative Totals:</div><div>GPA: 3.75</div><div>Status: Good Standing</div>
                </div>
            </div>
        </body>
        </html>
        '''
        return html

    @staticmethod
    def generate_statement_html(data):
        university = data.get("university", "Hachimi University")
        # 处理本地 Logo
        raw_logo = data.get("logo", "asu.png")
        uni_logo = DocGenerator._get_logo_base64(raw_logo)
        
        full_name = data.get("fullName", "Grimes Kelton")
        student_id = data.get("studentId", "511355-7318")
        term = data.get("term", "Fall 2024")
        address = data.get("address", "585 O'Conner Rapids, Missouri")
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                {DocGenerator.COMMON_STYLE}
                .stmt-header {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 30px; }}
                .student-addr {{ line-height: 1.5; margin-bottom: 20px; font-size: 14px; }}
                .bill-table {{ width: 100%; border-collapse: collapse; }}
                .bill-table th {{ border-bottom: 2px solid #333; padding: 10px; text-align: left; }}
                .bill-table td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .amount {{ text-align: right; }}
                .total-row {{ font-weight: 700; font-size: 16px; margin-top: 20px; text-align: right; }}
            </style>
        </head>
        <body>
            <div class="paper">
                <div class="stmt-header" style="align-items: center;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <img src="{uni_logo}" style="width: 40px; height: 40px; object-fit: contain;">
                        <div style="font-weight: 800; font-size: 18px; color: #1e3a8a;">{university}</div>
                    </div>
                    <div style="text-align: right;">Statement Date: 08/30/2025<br>Due Date: 09/22/2025</div>
                </div>
                <div class="student-addr">
                    <b>{full_name}</b><br>{address}<br>ID: {student_id}<br>Term: {term}
                </div>
                <div class="doc-title" style="text-decoration: none; text-align: left; border-bottom: 1px solid #eee; padding-bottom: 10px;">ACCOUNT STATEMENT</div>
                <table class="bill-table">
                    <thead><tr><th>Description</th><th class="amount">Amount</th></tr></thead>
                    <tbody>
                        <tr><td>Undergraduate (Non-Resident) - 15 Hours</td><td class="amount">$9,484.00</td></tr>
                        <tr><td>Tuition - College of Business</td><td class="amount">$1,100.00</td></tr>
                        <tr><td>Technology Fee</td><td class="amount">$340.00</td></tr>
                        <tr><td>Student Service Fee</td><td class="amount">$210.00</td></tr>
                        <tr><td>Student Health Insurance</td><td class="amount">$1,650.00</td></tr>
                    </tbody>
                </table>
                <div class="total-row">
                    <div>Total Charges: $12,784.00</div>
                    <div style="color: #059669; margin-top: 5px;">Payments/Credits: ($12,784.00)</div>
                    <div style="border-top: 2px solid #000; display: inline-block; padding-top: 5px; margin-top: 10px; font-size: 20px; color: #b91c1c;">BALANCE DUE: $0.00</div>
                </div>
                <div style="margin-top: 60px; font-size: 12px; color: #666; text-align: center;">
                    Thank you for your payment. This statement reflects account activity as of the date indicated.
                </div>
            </div>
        </body>
        </html>
        '''
        return html

    @staticmethod
    def generate_all_docs(data, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        gen = DocGenerator()
        docs = [
            ("admission_letter", gen.generate_admission_letter_html(data)),
            ("enrollment_cert", gen.generate_enrollment_cert_html(data)),
            ("academic_transcript", gen.generate_transcript_html(data)),
            ("account_statement", gen.generate_statement_html(data))
        ]
        
        output_paths = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 850, 'height': 1200})
            
            for name, html in docs:
                page.set_content(html, wait_until='networkidle')
                path = os.path.join(output_dir, f"{name}.png")
                page.locator('.paper').screenshot(path=path)
                output_paths.append(path)
                print(f"Generated {name} saved to: {path}")
            
            browser.close()
        return output_paths

    @staticmethod
    def generate_image(html, output_path):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 850, 'height': 1200})
            page.set_content(html, wait_until='networkidle')
            page.locator('.paper').screenshot(path=output_path)
            browser.close()
        return output_path

if __name__ == "__main__":
    from acagen_provider import AcaGenProvider
    provider = AcaGenProvider()
    student_data = provider.generate_student()
    
    DocGenerator.generate_all_docs(student_data, "output_docs")
