# Junbot - 이력서 어시스턴트
<p align="center">
  <img src="https://github.com/user-attachments/assets/93c4e1bc-a91a-4078-8876-2b822893c5f9" width="500"/>
  <img src="https://github.com/user-attachments/assets/cc9cf2d8-fd93-47e7-9bdb-26bdc81b8166" width="500"/><br/>
  <img src="https://github.com/user-attachments/assets/f51c3c75-9841-4efd-8917-f19e22579dca" width="500"/>
</p>

---
## 📆 프로젝트 기간

- 2026년 1월 20일 ~ 진행 중

## ☑️ 프로젝트 개요
취준생 입장에서는 다양한 기업, 직무를 항상 확인하고 원하는 역량에 맞춰 이력서를 작성해야 한다. 여러 사이트를 매번 찾아서 채용 관련 정보를 찾는데 많은 시간을 쓰게된다. 반복적인 작업으로 피로할 것이다.
기업(HR팀) 입장에서는 수많은 지원자들의 이력서를 열람해야 한다. 많은 글들을 보면서 피로도가 상당할 것이다.
이를 해소하기 위해 대화를 통해 agent가 기업과 직무를 파악하고, RAG를 활용하여 vectorDB에 저장한 지원자(본인)의 이력서을 바탕으로 맞춤형 답변을 제공하는 챗봇 프로젝트를 구상했다.

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
