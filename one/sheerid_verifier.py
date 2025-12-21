"""SheerID 学生验证主程序"""
import re
import random
import logging
import httpx
from typing import Dict, Optional, Tuple

from . import config
from .name_generator import NameGenerator, generate_birth_date
from .img_generator import generate_image, generate_psu_email

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """SheerID 学生身份验证器"""

    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # 配置代理
        if config.PROXY_URL:
            self.http_client = httpx.Client(timeout=30.0, proxy=config.PROXY_URL)
        else:
            self.http_client = httpx.Client(timeout=30.0)
    
    def __del__(self):
        if hasattr(self, "http_client"):
            self.http_client.close()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        chars = '0123456789abcdef'
        return ''.join(random.choice(chars) for _ in range(32))

    @staticmethod
    def normalize_url(url: str) -> str:
        """规范化 URL（保留原样）"""
        return url

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def verify_hcaptcha(self, token: str) -> bool:
        if not config.HCAPTCHA_SECRET or not token:
            return not config.HCAPTCHA_SECRET
        try:
            response = self.http_client.post(
                "https://hcaptcha.com/siteverify",
                data={"response": token, "secret": config.HCAPTCHA_SECRET},
            )
            result = response.json()
            return result.get("success", False)
        except Exception as e:
            logger.error(f"hCaptcha 验证失败: {e}")
            return False

    def verify_turnstile(self, token: str) -> bool:
        if not config.TURNSTILE_SECRET or not token:
            return not config.TURNSTILE_SECRET
        try:
            response = self.http_client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={"secret": config.TURNSTILE_SECRET, "response": token},
            )
            result = response.json()
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Turnstile 验证失败: {e}")
            return False

    def _sheerid_request(
        self, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """发送 SheerID API 请求"""
        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = self.http_client.request(
                method=method, url=url, json=body, headers=headers
            )
            try:
                data = response.json()
            except Exception:
                data = response.text
            return data, response.status_code
        except Exception as e:
            logger.error(f"SheerID 请求失败: {e}")
            raise

    def _upload_to_s3(self, upload_url: str, img_data: bytes) -> bool:
        """上传 PNG 到 S3"""
        try:
            headers = {"Content-Type": "image/png"}
            response = self.http_client.put(
                upload_url, content=img_data, headers=headers, timeout=60.0
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"S3 上传失败: {e}")
            return False

    def submit_student_info(
        self,
        first_name: str,
        last_name: str,
        email: str,
        birth_date: str,
        school_id: str,
        hcaptcha_token: str = None,
        turnstile_token: str = None
    ) -> Dict:
        """步骤 1: 提交学生个人信息并初始化验证会话"""
        if config.HCAPTCHA_SECRET:
            logger.info("验证 hCaptcha...")
            if not self.verify_hcaptcha(hcaptcha_token):
                raise Exception("hCaptcha 验证失败")
            logger.info("✅ hCaptcha 验证成功")

        if config.TURNSTILE_SECRET:
            logger.info("验证 Turnstile...")
            if not self.verify_turnstile(turnstile_token):
                raise Exception("Turnstile 验证失败")
            logger.info("✅ Turnstile 验证成功")

        school = config.SCHOOLS[school_id]
        logger.info(f"正在提交学生信息: {first_name} {last_name} ({email})")
        
        step2_body = {
            "firstName": first_name,
            "lastName": last_name,
            "birthDate": birth_date,
            "email": email,
            "phoneNumber": "",
            "organization": {
                "id": int(school_id),
                "idExtended": school["idExtended"],
                "name": school["name"],
            },
            "deviceFingerprintHash": self.device_fingerprint,
            "locale": "zh",
            "metadata": {
                "marketConsentValue": False,
                "refererUrl": f"{config.SHEERID_BASE_URL}/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}",
                "verificationId": self.verification_id,
                "flags": '{"doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","include-cvec-field-france-student":"not-labeled-optional","org-search-overlay":"default","org-selected-display":"default"}',
                "submissionOptIn": "提交上述个人信息即表示，本人知悉并同意 SheerID 将其披露、传输及存储在中国大陆境外，用于对本人的身份验证。关于 SheerID 的更多信息。",
            },
        }

        step2_data, step2_status = self._sheerid_request(
            "POST",
            f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectStudentPersonalInfo",
            step2_body,
        )

        if step2_status != 200:
            raise Exception(f"提交学生信息失败 (状态码 {step2_status}): {step2_data}")
        if step2_data.get("currentStep") == "error":
            error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
            raise Exception(f"提交学生信息错误: {error_msg}")

        logger.info(f"✅ 学生信息提交成功, 当前步骤: {step2_data.get('currentStep')}")
        
        # 处理 SSO 状态
        if step2_data.get("currentStep") in ["sso", "collectStudentPersonalInfo"]:
            logger.info("正在跳过 SSO 验证...")
            step3_data, _ = self._sheerid_request(
                "DELETE",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso",
            )
            return step3_data
            
        return step2_data

    def upload_documents(self, document_list: list) -> Dict:
        """步骤 2: 上传证件材料 (Admission Letter, Transcript, etc.)"""
        if not document_list:
            raise Exception("未提供要上传的文档列表")

        logger.info(f"准备上传 {len(document_list)} 个证件文档...")

        # 构造请求体，限制最多3个文件
        files_meta = []
        for doc in document_list[:3]:
            files_meta.append({
                "fileName": doc["name"],
                "mimeType": "image/png",
                "fileSize": len(doc["data"])
            })

        step4_data, step4_status = self._sheerid_request(
            "POST",
            f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
            {"files": files_meta}
        )

        if not step4_data.get("documents"):
            raise Exception(f"未能获取上传 URL: {step4_data}")

        # 逐个上传到 S3
        for i, remote_doc in enumerate(step4_data["documents"]):
            upload_url = remote_doc["uploadUrl"]
            local_data = document_list[i]["data"]
            logger.info(f"正在上传 {document_list[i]['name']} ({i+1}/{len(document_list)})...")
            if not self._upload_to_s3(upload_url, local_data):
                raise Exception(f"文档 {document_list[i]['name']} 上传失败")
        
        logger.info("✅ 所有文档上传成功，正在确认订单...")

        # 完成上传
        step6_data, _ = self._sheerid_request(
            "POST",
            f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
        )
        logger.info(f"✅ 证件提交完成，进入审核阶段")
        
        return {
            "success": True,
            "pending": True,
            "message": "文档已提交，等待审核",
            "verification_id": self.verification_id,
            "redirect_url": step6_data.get("redirectUrl"),
            "status": step6_data,
        }

    def verify(self, **kwargs) -> Dict:
        """兼容旧版本的统一验证接口"""
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        if not first_name or not last_name:
            name = NameGenerator.generate()
            first_name = name["first_name"]
            last_name = name["last_name"]

        school_id = kwargs.get("school_id") or config.DEFAULT_SCHOOL_ID
        email = kwargs.get("email") or generate_psu_email(first_name, last_name)
        birth_date = kwargs.get("birth_date") or generate_birth_date()

        info_res = self.submit_student_info(
            first_name, last_name, email, birth_date, school_id,
            hcaptcha_token=kwargs.get("hcaptcha_token"),
            turnstile_token=kwargs.get("turnstile_token")
        )

        if info_res.get("currentStep") != "docUpload":
            return {"success": False, "message": f"状态异常: {info_res.get('currentStep')}", "status": info_res}

        # 准备文档
        document_list = kwargs.get("document_list")
        if not document_list:
            school = config.SCHOOLS[school_id]
            img_data = generate_image(first_name, last_name, school_name=school['name'], birth_date=birth_date)
            document_list = [{"name": "student_card.png", "data": img_data}]

        return self.upload_documents(document_list)


def main():
    """主函数 - 命令行界面"""
    import sys

    print("=" * 60)
    print("SheerID 学生身份验证工具 (Python版)")
    print("=" * 60)
    print()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入 SheerID 验证 URL: ").strip()

    if not url:
        print("❌ 错误: 未提供 URL")
        sys.exit(1)

    verification_id = SheerIDVerifier.parse_verification_id(url)
    if not verification_id:
        print("❌ 错误: 无效的验证 ID 格式")
        sys.exit(1)

    print(f"✅ 解析到验证 ID: {verification_id}")
    print()

    verifier = SheerIDVerifier(verification_id)
    result = verifier.verify()

    print()
    print("=" * 60)
    print("验证结果:")
    print("=" * 60)
    print(f"状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
    print(f"消息: {result['message']}")
    if result.get("redirect_url"):
        print(f"跳转 URL: {result['redirect_url']}")
    print("=" * 60)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
