# 시니어 프로젝트 실행 가이드

## 🚀 프로젝트 실행 방법

### 1. 가상환경 활성화
```powershell
& "C:\Users\Shawn\OneDrive - BYU-Idaho\Seinor Project\venv\Scripts\Activate.ps1"
```

### 2. 애플리케이션 실행
```powershell
# Streamlit 웹 애플리케이션 실행
cd app
streamlit run web_app.py
```

### 3. 테스트 실행
```powershell
# 모든 테스트 실행
python -m pytest tests/ -v

# 커버리지와 함께 테스트 실행
python -m pytest tests/ --cov=app --cov-report=html
```

## 🧹 코드 품질 확인

### 코드 포맷팅
```powershell
# Black을 사용한 코드 포맷팅
black app/ tests/

# Flake8을 사용한 린팅
flake8 app/ --max-line-length=100
```

## 📁 프로젝트 구조

```
📦 시니어 프로젝트/
├── app/                    # 애플리케이션 소스 코드
│   ├── __init__.py
│   ├── web_app.py         # Streamlit 웹 애플리케이션
│   ├── rag_pipeline.py    # RAG 파이프라인 로직
│   ├── api_connector.py   # 법제처 API 연결
│   ├── cache_utils.py     # 캐싱 유틸리티
│   └── config.py          # 설정 관리
├── tests/                  # 테스트 파일
│   ├── conftest.py
│   ├── test_api_connector.py
│   └── test_cache_utils.py
├── docs/                   # 문서
├── venv/                   # 가상환경
├── requirements.txt        # 패키지 의존성
├── pytest.ini            # 테스트 설정
├── .env                   # 환경 변수
└── README.md              # 프로젝트 설명

```

## ✅ 현재 상태

- ✅ **가상환경**: 정상 설정 및 활성화됨
- ✅ **패키지 설치**: 모든 필수 패키지 설치 완료
- ✅ **테스트**: 26개 테스트 모두 통과
- ✅ **코드 품질**: Black으로 포맷팅 완료
- ✅ **환경변수**: API 키 설정 완료
- ✅ **Import 문제**: 상대/절대 import 이슈 해결

## 🔧 주요 기능

1. **법제처 API 연동**: 노동법 관련 법령해석 검색
2. **RAG 파이프라인**: LangChain을 활용한 문서 검색 및 답변 생성
3. **벡터 캐싱**: 성능 향상을 위한 쿼리 캐싱 시스템
4. **Streamlit UI**: 사용자 친화적인 웹 인터페이스
5. **종합 테스트**: API, 캐싱, 핵심 로직 테스트 포함

## 📈 성능 최적화

- Chroma DB를 활용한 벡터 스토어
- LRU 캐싱으로 중복 요청 최소화  
- Google Gemini를 활용한 효율적인 AI 답변 생성
- 재시도 로직과 타임아웃 처리로 안정성 확보