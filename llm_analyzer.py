import json
import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIConnectionError, InternalServerError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import JOB_TITLE, JOB_DESCRIPTION, SCORING_CRITERIA, LLM_MODEL

load_dotenv()

_api_key = os.environ.get("OPENAI_API_KEY")
if not _api_key:
    raise ValueError(
        "Don't find OPENAI_API_KEY please create .env from .env.example "
        "then insert your API key"
    )

client = OpenAI(api_key=_api_key)


def _build_system_prompt() -> str:
    """
    create system prompt : LLM as AI Technical Recruiter, give scoring criteria, job description
    and instruction to return JSON only in Thai language 
    """
    criteria_text = "\n".join(
        f"- {key} (น้ำหนัก {value['weight']}%): {value['description']}"
        for key, value in SCORING_CRITERIA.items()
    )

    return f"""คุณคือ AI Technical Recruiter ผู้เชี่ยวชาญด้านการคัดกรอง Resume สำหรับตำแหน่ง "{JOB_TITLE}"

หน้าที่ของคุณคือวิเคราะห์ Resume ของผู้สมัคร เทียบกับ Job Description ด้านล่าง แล้วให้คะแนนตามเกณฑ์ 4 หมวด:

{criteria_text}

หมายเหตุสำคัญเรื่องภาษา:
- Resume ของผู้สมัครอาจเป็นภาษาไทยหรือภาษาอังกฤษก็ได้ ให้คุณอ่านและวิเคราะห์เนื้อหาได้ทั้งสองภาษาโดยไม่ลดทอนความแม่นยำ
- ไม่ว่า resume จะเป็นภาษาใด ให้ตอบกลับ reasoning, strengths, gaps, และ recommendation เป็น**ภาษาไทยเสมอ**

กติกาการให้คะแนน:
- แต่ละหมวดให้คะแนนเป็น 0-100 พร้อมเหตุผลประกอบที่อ้างอิงเนื้อหาจริงในเรซูเม่
- คำนวณ overall_score จากค่าเฉลี่ยถ่วงน้ำหนักตาม weight ของแต่ละหมวด
- ระบุจุดแข็ง (strengths) และจุดอ่อน (gaps) ที่พบจริงจาก resume เทียบกับ JD
- ให้ recommendation สั้นๆ ว่าผู้สมัครเหมาะสมกับตำแหน่งนี้ระดับใด (เช่น "เหมาะสมมาก", "เหมาะสมปานกลาง", "ควรพัฒนาเพิ่ม")
- ตอบกลับเป็น JSON เท่านั้น ห้ามมีข้อความอื่นนอกเหนือจาก JSON object ห้ามใส่ code block markdown

รูปแบบ JSON ที่ต้องตอบกลับ (ต้องตรงตาม schema นี้):
{{
  "position": "{JOB_TITLE}",
  "resume_language": "<th หรือ en ตามภาษาที่ตรวจพบใน resume>",
  "overall_score": <number 0-100>,
  "criteria_scores": {{
    "education_experience": {{"score": <0-100>, "reasoning": "<เหตุผลภาษาไทย>"}},
    "skills": {{"score": <0-100>, "reasoning": "<เหตุผลภาษาไทย>"}},
    "knowledge": {{"score": <0-100>, "reasoning": "<เหตุผลภาษาไทย>"}},
    "tools": {{"score": <0-100>, "reasoning": "<เหตุผลภาษาไทย>"}}
  }},
  "strengths": ["<จุดแข็ง 1>", "<จุดแข็ง 2>"],
  "gaps": ["<จุดอ่อน 1>", "<จุดอ่อน 2>"],
  "recommendation": "<คำแนะนำสรุปภาษาไทย>"
}}

Job Description:
{JOB_DESCRIPTION}
"""


@retry(
    # retry 3 times when OpenAI is unavailable
    # (rate limit / connection error / server error) don't retry on other errors (like invalid request, invalid JSON, etc.)
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),  # wait 2s, 4s, 8s between retries
    retry=retry_if_exception_type((RateLimitError, APIConnectionError, InternalServerError)),
    reraise=True,  # if still fails after 3 retries, raise the exception to caller
)
def _call_openai(system_prompt: str, resume_text: str):
    """split out the OpenAI API call to make it retryable with tenacity"""
    return client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,  # ต้องการผลลัพธ์ที่ consistent สำหรับการให้คะแนน ไม่ต้องการความ creative
        response_format={"type": "json_object"},  # บังคับ output เป็น JSON 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"นี่คือเนื้อหา Resume ของผู้สมัคร:\n\n{resume_text}"},
        ],
    )


def analyze_resume(resume_text: str) -> dict:
    """
    send resume text to LLM for analysis, return the result as a dict
    """
    system_prompt = _build_system_prompt()

    try:
        response = _call_openai(system_prompt, resume_text)
    except (RateLimitError, APIConnectionError, InternalServerError) as e:
        raise ValueError(
            f"OpenAI API ไม่พร้อมให้บริการชั่วคราว (ลองใหม่ 3 ครั้งแล้ว): {e}"
        )

    raw_content = response.choices[0].message.content

    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM ตอบกลับไม่ใช่ JSON ที่ถูกต้อง: {e}\nRaw response: {raw_content}")

    return result