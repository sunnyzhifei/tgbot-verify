"""
Verify AcaGen Local - 采用 AcaGen 风格闭环资料的本地验证脚本
1. 自动生成 AcaGen 风格的学生资料
2. 生成对应的录取通知书/成绩单图片
3. 调用 SheerID 接口提交验证
4. 轮询验证状态
"""
import asyncio
import os
import sys
import logging
import time
import httpx
from typing import Dict, Optional

# 导入 AcaGen 组件
from one.acagen_provider import AcaGenProvider
from one.doc_generator import DocGenerator
from one.sheerid_verifier import SheerIDVerifier
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

async def poll_status(verification_id: str, max_wait: int = 1200, interval: int = 5):
    """轮询 SheerID 验证状态"""
    start_time = time.time()
    proxies = config.PROXY_URL
    
    async with httpx.AsyncClient(timeout=30.0, proxies=proxies) as client:
        logger.info(f"开始轮询验证状态... (最多等待 {max_wait/60:.1f} 分钟)")
        while True:
            elapsed = int(time.time() - start_time)
            if elapsed >= max_wait:
                return {"status": "timeout", "message": "超过最大等待时间"}

            try: 
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                ) 

                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")
                    logger.info(f"当前状态: {current_step} (已耗时 {elapsed}s)")

                    if current_step == "success":
                        return {
                            "status": "success",
                            "message": "验证成功",
                            "reward_code": data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode"),
                            "redirect_url": data.get("redirectUrl")
                        }
                    elif current_step == "error":
                        error_ids = data.get("errorIds", [])
                        return {
                            "status": "error",
                            "message": ", ".join(error_ids) if error_ids else "未知错误"
                        }
                    elif current_step == "docUpload":
                         # 如果还在 docUpload 阶段，说明提交可能还没被处理
                         pass
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.warning(f"轮询出错: {e}")
                await asyncio.sleep(interval)

async def main():
    if len(sys.argv) < 2:
        print("使用方法: python verify_acagen_local.py <SheerID_URL>")
        return

    url = sys.argv[1]
    verification_id = SheerIDVerifier.parse_verification_id(url)
    
    if not verification_id:
        print("Error: Could not parse verificationId from URL")
        return

    print("="*60)
    print(f"Starting AcaGen Closed-Loop Verification")
    print(f"Verification ID: {verification_id}")
    print("="*60)

    # 1. 生成 AcaGen 风格闭环资料
    print("Step 1: Generating AcaGen closed-loop student data...")
    provider = AcaGenProvider()
    student_data = provider.generate_student(university_name="Arizona State University")
    
    print(f"   [Name]: {student_data['fullName']}")
    print(f"   [DOB]: {student_data['birthDate']}")
    print(f"   [School]: {student_data['university']}")
    
    # 2. 执行 SheerID 信息提交 (Step 1 of interaction)
    print("Step 2: Submitting student information to SheerID...")
    verifier = SheerIDVerifier(verification_id)
    loop = asyncio.get_event_loop()
    
    try:
        # 先提交基本信息，确认 SheerID 接受资料后再渲染图片
        submit_res = await loop.run_in_executor(None, lambda: verifier.submit_student_info(
            first_name=student_data['firstName'],
            last_name=student_data['lastName'],
            email=student_data['email'],
            birth_date=student_data['birthDate'],
            school_id="650865" # ASU
        ))
        
        if submit_res.get("currentStep") != "docUpload":
            print(f"❌ 提交资料后状态异常: {submit_res.get('currentStep')}")
            return

        print(f"✅ Information accepted! Current step: {submit_res.get('currentStep')}")

        # 3. 只有信息提交成功后，才开始耗时的渲染工作
        print("Step 3: Rendering closed-loop documents (Four-set)...")
        output_dir = "temp_verify"
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        
        from one.img_generator import generate_image as generate_id_card
        doc_gen = DocGenerator()
        
        # 存储所有生成的文档对象
        all_generated_docs = []
        
        # A. 生成官网版三件套
        doc_templates = [
            ("admission_letter.png", doc_gen.generate_admission_letter_html(student_data)),
            ("academic_transcript.png", doc_gen.generate_transcript_html(student_data)),
            ("enrollment_cert.png", doc_gen.generate_enrollment_cert_html(student_data))
        ]
        
        for filename, html in doc_templates:
            img_path = os.path.abspath(os.path.join(output_dir, filename))
            await loop.run_in_executor(None, doc_gen.generate_image, html, img_path)
            with open(img_path, "rb") as f:
                all_generated_docs.append({"name": filename, "data": f.read()})
            print(f"   [Generated]: {filename}")

        # B. 生成带人像的学生证
        id_card_filename = "student_id_card.png"
        id_card_path = os.path.abspath(os.path.join(output_dir, id_card_filename))
        id_card_bytes = await loop.run_in_executor(
            None, 
            lambda: generate_id_card(
                student_data['firstName'], 
                student_data['lastName'], 
                school_name=student_data['university'],
                birth_date=student_data['birthDate'],
                studentId=student_data['studentId'],
                major=student_data['major'],
                college=student_data.get('college', student_data['major'])
            )
        )
        with open(id_card_path, "wb") as f:
            f.write(id_card_bytes)
        all_generated_docs.append({"name": id_card_filename, "data": id_card_bytes})
        print(f"   [Generated]: {id_card_filename}")

        # C. 随机挑选 3 个进行上传
        import random
        document_list = random.sample(all_generated_docs, 3)
        picked_names = [d['name'] for d in document_list]
        print(f"Step 4: Randomly picked 3 documents for submission: {', '.join(picked_names)}")

        # 4. 执行文档上传
        print(f"Step 5: Uploading {len(document_list)} documents to SheerID...")
        result = await loop.run_in_executor(None, lambda: verifier.upload_documents(document_list))

        if not result.get("success"):
             print(f"Error submitting data: {result.get('message')}")
             return

        print("Data submitted successfully! Entering polling phase...")
        
        # 4. 轮询状态
        poll_result = await poll_status(verification_id)
        
        print("\n" + "="*50)
        if poll_result["status"] == "success":
            print("SUCCESS! Verification complete.")
            print(f"Reward Code: {poll_result.get('reward_code')}")
            print(f"Redirect URL: {poll_result.get('redirect_url')}")
        elif poll_result["status"] == "error":
            print(f"FAILED: Verification rejected: {poll_result.get('message')}")
        else:
            print(f"WAITING: {poll_result.get('message')}")
        print("="*50)

    except Exception as e:
        print(f"❌ 运行异常: {e}")

if __name__ == "__main__":
    asyncio.run(main())
