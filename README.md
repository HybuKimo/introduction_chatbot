# 🏪 Junbot - 신준희 어시스턴트
<p align="center">
  <img src="https://github.com/user-attachments/assets/f51c3c75-9841-4efd-8917-f19e22579dca" width="500"/>
  <img src="https://github.com/user-attachments/assets/b74e0185-f303-45f7-9e15-56c00e40596e" width="500"/>
</p>

---
## 📆 프로젝트 기간

- 2026년 1월 20일 ~ 진행 중

## ☑️ 프로젝트 개요
취준생 입장에서 다양한 기업, 직무를 항상 확인하고 원하는 역량에 맞춰 자기소개서를 작성해야한다. 매번 찾아서 검색하기 많은 스트레스와 시간을 보낸다.
기업(HR팀) 입장에서 수많은 


## 🏗️ 마이크로서비스 아키텍처

```
personal-chatbot/
├── frontend/             # Next.js + TypeScript
├── backend/             # FastAPI (API Gateway)
├── rag-service/         # RAG + LangChain + Voyage AI
└── docker-compose.yml   # 전체 서비스 오케스트레이션
```

### 🔧 기술 스택

| 서비스 | 기술 스택 | 포트 |
|--------|-----------|------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS | 3000 |
| **Backend** | FastAPI, Pydantic (API 게이트웨이) | 8000 |
| **RAG Service** | LangChain, Voyage AI, XAI, ChromaDB | 8001 |

### 🌟 핵심 기능

- **4단계 지능형 응답**: general → company → position → company_position
- **RAG 검색 시스템**: Voyage AI voyage-3 임베딩
- **실시간 Agent Actions**: 작업 과정 투명화
- **맞춤형 정보 제공**: 회사/직무별 특화 답변
