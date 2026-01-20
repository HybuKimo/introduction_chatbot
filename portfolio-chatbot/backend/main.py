from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
import logging
from datetime import datetime
import uuid
import re
import asyncio
from playwright.async_api import async_playwright
import aiohttp
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Portfolio Agent", version="2.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터 모델
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    company: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    detected_company: Optional[str] = None
    agent_actions: Optional[List[str]] = None

@dataclass
class CompanyInfo:
    name: str
    job_postings: List[Dict]
    company_culture: Dict
    tech_requirements: List[str]
    hiring_process: str

# Agent Tools
class WebScrapingAgent:
    def __init__(self):
        self.playwright = None
        self.browser = None
        
    async def initialize(self):
        """Playwright 브라우저 초기화"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            logger.info("Agent browser initialized")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
    
    async def close(self):
        """브라우저 종료"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def search_job_postings(self, company_name: str) -> List[Dict]:
        """채용 정보 크롤링"""
        if not self.browser:
            await self.initialize()
            
        actions = []
        job_postings = []
        
        try:
            page = await self.browser.new_page()
            actions.append(f"🔍 {company_name} 채용정보 검색 시작")
            
            # 사람인 검색
            search_url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&searchword={company_name}"
            await page.goto(search_url, wait_until="domcontentloaded")
            actions.append("📊 사람인 채용공고 분석")
            
            await page.wait_for_timeout(2000)  # 페이지 로딩 대기
            
            # 채용공고 정보 추출
            job_elements = await page.query_selector_all('.item_recruit')
            
            for i, element in enumerate(job_elements[:3]):  # 상위 3개만
                try:
                    title_elem = await element.query_selector('.job_tit a')
                    company_elem = await element.query_selector('.corp_name a')
                    condition_elem = await element.query_selector('.job_condition')
                    
                    if title_elem and company_elem:
                        title = await title_elem.inner_text()
                        company = await company_elem.inner_text()
                        condition = await condition_elem.inner_text() if condition_elem else ""
                        
                        if company_name.lower() in company.lower():
                            job_postings.append({
                                'title': title.strip(),
                                'company': company.strip(),
                                'condition': condition.strip(),
                                'source': '사람인'
                            })
                except Exception as e:
                    logger.warning(f"Failed to extract job posting {i}: {e}")
                    continue
            
            await page.close()
            actions.append(f"✅ {len(job_postings)}개 채용공고 수집 완료")
            
        except Exception as e:
            logger.error(f"Job scraping failed: {e}")
            actions.append(f"❌ 채용정보 수집 실패: {str(e)}")
            
        return job_postings, actions
    
    async def get_company_culture(self, company_name: str) -> Dict:
        """회사 문화/정보 크롤링"""
        if not self.browser:
            await self.initialize()
            
        culture_info = {}
        actions = []
        
        try:
            page = await self.browser.new_page()
            actions.append(f"🏢 {company_name} 기업정보 수집")
            
            # 잡플래닛에서 회사 정보 검색
            search_url = f"https://www.jobplanet.co.kr/search?query={company_name}"
            await page.goto(search_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # 기업 문화 정보 추출 (간단한 예시)
            try:
                # 첫 번째 검색 결과 클릭
                first_company = await page.query_selector('.company_name a')
                if first_company:
                    await first_company.click()
                    await page.wait_for_timeout(2000)
                    
                    # 기업 개요 정보 추출
                    overview_elem = await page.query_selector('.company_overview')
                    if overview_elem:
                        overview_text = await overview_elem.inner_text()
                        culture_info['overview'] = overview_text[:300]  # 300자 제한
                    
                    actions.append("✅ 기업 문화 정보 수집 완료")
                else:
                    culture_info['overview'] = f"{company_name}는 혁신적인 기업으로 알려져 있습니다."
                    actions.append("⚠️ 기본 기업정보 사용")
                    
            except Exception as e:
                culture_info['overview'] = f"{company_name}에서 함께 성장할 기회를 기대합니다."
                actions.append(f"⚠️ 기업정보 수집 제한적: {str(e)}")
            
            await page.close()
            
        except Exception as e:
            logger.error(f"Company culture scraping failed: {e}")
            actions.append(f"❌ 기업정보 수집 실패")
            culture_info['overview'] = f"{company_name}와 함께 성장하고 싶습니다."
            
        return culture_info, actions

# 전역 Agent 인스턴스
web_agent = WebScrapingAgent()

# 데이터 로드 함수들
def load_resume_data():
    with open('data/resume.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_company_name(message: str) -> Optional[str]:
    company_patterns = {
        '네이버': ['네이버', 'naver', 'NAVER', 'Naver'],
        '카카오': ['카카오', 'kakao', 'KAKAO', 'Kakao'],
        '쿠팡': ['쿠팡', 'coupang', 'COUPANG', 'Coupang'],
        '토스': ['토스', 'toss', 'TOSS', 'Toss'],
        '삼성': ['삼성', 'samsung', 'SAMSUNG', 'Samsung'],
        'LG': ['LG', 'lg', '엘지'],
        '현대': ['현대', 'hyundai', 'HYUNDAI']
    }
    
    message_lower = message.lower()
    
    for company, patterns in company_patterns.items():
        for pattern in patterns:
            if pattern.lower() in message_lower:
                return company
    
    return None

async def generate_agent_response(message: str, company: str = None) -> tuple[str, List[str]]:
    """AI Agent 기반 응답 생성"""
    resume_data = load_resume_data()
    all_actions = []
    
    if not company:
        company = extract_company_name(message)
    
    if company:
        all_actions.append(f"🎯 {company} 관련 질문 감지")
        
        # Agent 실행: 실시간 정보 수집
        job_postings, job_actions = await web_agent.search_job_postings(company)
        company_culture, culture_actions = await web_agent.get_company_culture(company)
        
        all_actions.extend(job_actions)
        all_actions.extend(culture_actions)
        
        # 분석 및 개인화 답변 생성
        all_actions.append("🧠 개인 이력과 기업정보 매칭 분석")
        
        # 간단한 매칭 로직 (나중에 XAI API로 대체)
        my_skills = [skill['name'] for skill in resume_data['skills']['backend']]
        
        if job_postings:
            relevant_jobs = [job for job in job_postings if any(skill.lower() in job['condition'].lower() for skill in my_skills)]
            
            if relevant_jobs:
                response = f"""🎯 {company} 맞춤 분석 결과:

📋 **최신 채용정보** (실시간 수집):
{relevant_jobs[0]['title']}
• 요구사항: {relevant_jobs[0]['condition'][:100]}...

🤝 **저와의 매칭도**:
• 제가 보유한 {', '.join(my_skills[:3])} 기술이 해당 포지션과 적합합니다
• {resume_data['experience'][0]['achievements'][0]} 경험이 도움이 될 것 같습니다

💡 **지원 이유**:
편의점같은 개발자로서 {company}의 사용자들에게 24/7 편리함을 제공하고 싶습니다. 특히 {company_culture.get('overview', '혁신적인 기업문화')}와 제 가치관이 일치한다고 생각합니다.

더 구체적인 질문이 있으시면 언제든 물어보세요! 🚀"""
            else:
                response = f"""🎯 {company}에 대한 관심 감사합니다!

실시간으로 채용정보를 확인했지만, 현재 공개된 포지션과 제 기술스택의 직접적인 매칭은 제한적입니다. 

하지만 편의점같은 개발자로서:
• **편리함 추구**: 사용자 중심의 서비스 개발 
• **의로움 실천**: 올바른 가치관으로 개발
• **지속 성장**: 새로운 기술 학습에 적극적

{company}와 함께 성장하며 기여할 준비가 되어 있습니다! 💪"""
        else:
            response = f"""🎯 {company}에 관심 가져주셔서 감사합니다!

현재 공개된 채용정보 수집에 일시적인 제한이 있지만, 편의점같은 개발자로서 {company}에 기여할 수 있는 방법들:

🛠 **기술적 기여**:
• {', '.join(my_skills[:3])} 등의 기술로 안정적인 서비스 구축
• {resume_data['projects'][0]['description'][:50]}... 경험 활용

🤝 **가치 연결**:
편의점처럼 항상 준비된 개발자로서 {company}의 사용자들에게 편리하고 신뢰할 수 있는 서비스를 제공하겠습니다.

구체적인 포지션이나 프로젝트에 대해 더 궁금한 점이 있으시면 언제든 물어보세요! 🚀"""
        
        all_actions.append("✅ 맞춤형 답변 생성 완료")
        
    else:
        # 일반적인 질문 처리
        message_lower = message.lower()
        
        if '경력' in message_lower or 'experience' in message_lower:
            experience = resume_data['experience'][0]
            response = f"**경력 소개**:\n{experience['position']}로 {experience['duration']} 근무하며 {', '.join(experience['achievements'])} 등의 성과를 달성했습니다. 편의점같은 개발자로서 항상 사용자에게 편리함을 제공하려 노력합니다."
        
        elif '프로젝트' in message_lower:
            project = resume_data['projects'][0]
            response = f"**프로젝트 경험**:\n{project['name']} - {project['description']} 특히 {project['role']}로서 {project['challenges'][:100]}..."
            
        elif '기술' in message_lower or 'tech' in message_lower:
            skills = resume_data['skills']['backend']
            tech_list = [f"{skill['name']}({skill['level']})" for skill in skills[:3]]
            response = f"**기술 스택**:\n주요 기술은 {', '.join(tech_list)} 등입니다. 편의점같은 개발자로서 사용자가 필요할 때 언제든 도움이 되는 기술을 보유하고 있습니다."
            
        else:
            response = f"""안녕하세요! 편의점같은 개발자 **신준희**입니다! 🏪

{resume_data['personal_info']['intro']}

💡 **궁금한 점이 있으시면**:
• "네이버에 지원하는 이유는?" (실시간 기업 분석)
• "프로젝트 경험을 알려주세요"
• "어떤 기술 스택을 사용하나요?"

언제든 편하게 물어보세요! 24/7 준비된 개발자입니다 🚀"""
        
        all_actions.append("💬 일반 질문 응답 완료")
    
    return response, all_actions

# 로그 저장
def save_chat_log(session_id: str, message: str, response: str, company: str = None, agent_actions: List[str] = None):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "company": company,
        "user_message": message,
        "bot_response": response,
        "agent_actions": agent_actions or []
    }
    
    date_str = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/chat_{date_str}.json"
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

@app.get("/")
async def root():
    return {"message": "AI Portfolio Agent v2.0", "status": "running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        detected_company = request.company or extract_company_name(request.message)
        
        # Agent 기반 응답 생성
        response, agent_actions = await generate_agent_response(request.message, detected_company)
        
        # 로그 저장
        save_chat_log(
            session_id=session_id,
            message=request.message,
            response=response,
            company=detected_company,
            agent_actions=agent_actions
        )
        
        logger.info(f"Agent processed - Session: {session_id}, Company: {detected_company}, Actions: {len(agent_actions)}")
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            detected_company=detected_company,
            agent_actions=agent_actions
        )
        
    except Exception as e:
        logger.error(f"Agent processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Agent processing failed")

@app.get("/admin/logs/{date}")
async def get_logs(date: str):
    try:
        log_file = f"logs/chat_{date}.json"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            return {"logs": logs}
        else:
            return {"logs": [], "message": "No logs found for this date"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/analytics")
async def get_analytics():
    try:
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = f"logs/chat_{date_str}.json"
        
        if not os.path.exists(log_file):
            return {"message": "No data for today"}
            
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        total_chats = len(logs)
        companies = {}
        agent_usage = sum(1 for log in logs if log.get('agent_actions'))
        
        for log in logs:
            if log.get('company'):
                companies[log['company']] = companies.get(log['company'], 0) + 1
        
        return {
            "total_chats_today": total_chats,
            "agent_activations": agent_usage,
            "companies": companies,
            "most_active_company": max(companies.items(), key=lambda x: x[1])[0] if companies else None,
            "agent_usage_rate": f"{(agent_usage/total_chats*100):.1f}%" if total_chats > 0 else "0%"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    await web_agent.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
