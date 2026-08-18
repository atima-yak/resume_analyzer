# Resume Analyzer — Resume · JD Matching Analyzer

เครื่องมือวิเคราะห์เรซูเม่ผู้สมัครเทียบกับ Job Description ด้วย LLM รองรับ Resume ทั้งภาษาไทยและภาษาอังกฤษ คืนผลเป็นคะแนนพร้อมเหตุผลประกอบในรูปแบบ JSON

โปรเจกต์นี้พัฒนาขึ้นสำหรับตำแหน่ง **AI & Data Solution Intern** เป็นตัวอย่าง end-to-end AI application ตั้งแต่รับไฟล์ดิบ, ควบคุม LLM output, จนถึงห่อเป็น API และหน้าเว็บใช้งานจริง

## Demo

เปิดหน้าเว็บแล้วลากไฟล์ PDF resume มาวาง กด "วิเคราะห์เรซูเม่" จะเห็นคะแนนรวมเป็นเกจวงกลม คะแนนแยกตาม 4 หมวด พร้อมจุดแข็ง/ช่องว่างที่พบ

## Features

- **รองรับ Resume ทั้งไทยและอังกฤษ** — วิเคราะห์ได้ทั้งสองภาษา แต่บังคับผลลัพธ์ (reasoning, strengths, gaps, recommendation) เป็นภาษาไทยเสมอ
- **ให้คะแนนแบบมีเหตุผลประกอบ** — แบ่งเป็น 4 หมวด: ประสบการณ์/การศึกษา, ทักษะ, ความรู้, เครื่องมือ พร้อม weighted average
- **บังคับ output เป็น JSON schema ที่แน่นอน** — ผ่าน `response_format={"type": "json_object"}` ของ OpenAI
- **Retry อัตโนมัติ** — เมื่อเจอปัญหาชั่วคราวฝั่ง LLM provider (rate limit, connection error, server error) ด้วย exponential backoff สูงสุด 3 ครั้ง
- **หน้าเว็บ UI พร้อมใช้** — ลากไฟล์วาง, เกจคะแนนวงกลม
- **เซฟผลวิเคราะห์อัตโนมัติ** (เมื่อรันในเครื่อง) พร้อม endpoint ดูประวัติย้อนหลัง
- **REST API มาตรฐาน** พร้อม Swagger UI (`/docs`) สำหรับทดสอบ

## Tech Stack

| ส่วนประกอบ | เทคโนโลยี |
|---|---|
| Backend | FastAPI + Uvicorn |
| LLM | OpenAI API (`gpt-4o-mini`) |
| PDF Parsing | pdfplumber |
| Retry Logic | tenacity |
| Frontend | HTML/CSS/JS (single-file, ไม่มี framework) |
| Deployment | Vercel (serverless) |

## โครงสร้างโปรเจกต์

```
resume_analyzer/
├── api.py                 # FastAPI app: endpoints ทั้งหมด
├── config.py               # JD, เกณฑ์การให้คะแนน, ตั้งค่า LLM
├── llm_analyzer.py         # เรียก LLM วิเคราะห์ + retry logic
├── resume_parser.py        # แกะข้อความจาก PDF
├── static/
│   └── index.html           # หน้าเว็บ UI
├── requirements.txt
├── vercel.json              # config สำหรับ deploy บน Vercel
├── pyproject.toml           # entrypoint config สำหรับ Vercel
├── .env.example
└── .gitignore
```

## วิธีติดตั้งและรันในเครื่อง

### 1. Clone และสร้าง virtual environment

```bash
git clone https://github.com/<username>/resume_analyzer.git
cd resume_analyzer
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
```

### 2. ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

### 3. ตั้งค่า API Key

```bash
cp .env.example .env
```

เปิดไฟล์ `.env` แล้วใส่ OpenAI API key ของคุณ:

```
OPENAI_API_KEY=sk-your-key-here
```

### 4. รันเซิร์ฟเวอร์

```bash
python -m uvicorn api:app --reload
```

เปิดเบราว์เซอร์ไปที่:
- `http://127.0.0.1:8000/` — หน้าเว็บ UI
- `http://127.0.0.1:8000/docs` — Swagger UI สำหรับทดสอบ API

## API Endpoints

| Method | Endpoint | คำอธิบาย |
|---|---|---|
| `GET` | `/` | หน้าเว็บ UI |
| `POST` | `/analyze-resume` | อัปโหลด PDF resume → คืนผลวิเคราะห์เป็น JSON |
| `GET` | `/results` | รายการผลวิเคราะห์ทั้งหมด (เฉพาะรันในเครื่อง) |
| `GET` | `/results/{filename}` | ดึงผลวิเคราะห์ฉบับเต็มตามชื่อไฟล์ |
| `GET` | `/health` | เช็คสถานะเซิร์ฟเวอร์ |

### ตัวอย่าง Response จาก `/analyze-resume`

```json
{
  "position": "AI & Data Solution Intern",
  "resume_language": "th",
  "overall_score": 78,
  "criteria_scores": {
    "education_experience": { "score": 75, "reasoning": "..." },
    "skills": { "score": 82, "reasoning": "..." },
    "knowledge": { "score": 76, "reasoning": "..." },
    "tools": { "score": 78, "reasoning": "..." }
  },
  "strengths": ["...", "..."],
  "gaps": ["...", "..."],
  "recommendation": "เหมาะสมมาก"
}
```

## Deploy ขึ้น Vercel

โปรเจกต์นี้ตั้งค่าให้ deploy บน Vercel ได้ทันทีผ่าน `vercel.json` และ `pyproject.toml`

1. Push โค้ดขึ้น GitHub
2. เชื่อม repo กับ [Vercel](https://vercel.com)
3. ตั้งค่า Environment Variable `OPENAI_API_KEY` ใน Vercel Dashboard (Settings → Environment Variables)
4. Deploy

## แนวคิดการออกแบบ

- **แยก concern เป็นโมดูล** — parsing, LLM logic, API layer, config แยกไฟล์กันชัดเจน
- **Prompt Engineering** — JD ถูกฝังในระบบ prompt ตรง ๆ เพราะรองรับตำแหน่งเดียว
- **Fail-fast** — เช็ค API key ตั้งแต่ตอน import โมดูล ไม่ปล่อยให้พังตอนเรียก API จริง
- **Exception translation** — แปลง exception เฉพาะทางของ LLM provider ให้เป็น `ValueError` กลางๆ ที่ทั้งระบบเข้าใจตรงกัน
