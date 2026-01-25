# README
# 🏪 Junbot - 신준희 어시스턴트

**편의점같은 개발자** 신준희의 AI 포트폴리오 어시스턴트입니다.

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
- **RAG 검색 시스템**: Voyage AI voyage-3 임베딩 (MTEB #1)
- **실시간 Agent Actions**: 작업 과정 투명화
- **맞춤형 정보 제공**: 회사/직무별 특화 답변
