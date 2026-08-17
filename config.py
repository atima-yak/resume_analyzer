JOB_TITLE = "AI & Data Solution Intern"

JOB_DESCRIPTION = """
หน้าที่รับผิดชอบ:
1. ทำงานร่วมกับผู้ใช้งานหรือทีมพัฒนาธุรกิจ เพื่อรวบรวมและทำความเข้าใจความต้องการของระบบ
2. ออกแบบ พัฒนา และปรับแต่งคำสั่ง prompt เพื่อเพิ่มประสิทธิภาพการทำงานของ AI
3. ออกแบบโครงสร้างระบบ กระบวนการทำงาน และการใช้งานของ AI application
4. ใช้ Large Language Models (LLMs) เพื่อพัฒนา AI application
5. ทดสอบการทำงานและประเมินประสิทธิภาพของ AI application
6. ทำงานร่วมกับทีมวิศวกรซอฟต์แวร์อย่างใกล้ชิด เพื่อนำ AI application ไปใช้ในระบบจริง

คุณสมบัติที่ต้องการ:
- ชำนาญในการเขียนโปรแกรมด้วย Python, prompt engineering, และ context engineering
- มีทักษะในการคิดวิเคราะห์และแก้ไขปัญหาได้อย่างดีเยี่ยม
- มีความเข้าใจในด้าน AI ระบบอัตโนมัติ (automation) และ data-driven solutions
- มีความเข้าใจเกี่ยวกับ Natural Language Processing (NLP) และแนวคิดของ machine learning
- มีประสบการณ์ในการทำงานกับ API, JSON หรือ automation pipelines
- (พิจารณาพิเศษ) มีประสบการณ์กับ n8n, SQL, Docker หรือแพลตฟอร์ม Cloud
"""

# เกณฑ์การให้คะแนน แบ่งเป็น 4 หมวด คือ ประสบการณ์/การศึกษา, ทักษะ, ความรู้, เครื่องมือ
SCORING_CRITERIA = {
    "education_experience": {
        "weight": 25,
        "description": "ประสบการณ์การทำงาน/ฝึกงาน และพื้นฐานการศึกษาที่เกี่ยวข้องกับ AI, Data, CS",
    },
    "skills": {
        "weight": 30,
        "description": "ทักษะการเขียนโปรแกรม Python, prompt engineering, context engineering, การคิดวิเคราะห์",
    },
    "knowledge": {
        "weight": 25,
        "description": "ความรู้ด้าน AI, LLM, NLP, Machine Learning, automation, data-driven solutions",
    },
    "tools": {
        "weight": 20,
        "description": "เครื่องมือ/เทคโนโลยีที่ใช้งาน เช่น API, JSON, automation pipelines, n8n, SQL, Docker, Cloud",
    },
}

# กำหนด LLM 
LLM_PROVIDER = "openai"       
LLM_MODEL = "gpt-4o-mini"    

## LLM_PROVIDER = "gemini"      
## LLM_MODEL = "gemini-flash-latest"  