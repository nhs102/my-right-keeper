"""
Intelligent query processing using Generative AI
사용자의 자연어 표현을 법적 키워드로 변환하는 모듈
"""

import logging
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
try:
    from .config import config
except ImportError:
    from config import config

logger = logging.getLogger(__name__)

def rephrase_query_with_ai(user_query: str) -> List[str]:
    """
    Use AI to convert natural language expressions into legal keywords
    사용자의 자연어 표현을 법적 키워드로 변환
    """
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.3,
        )
        
        # Create prompt for query rephrasing
        prompt = f"""
당신은 한국 노동법 전문가입니다. 사용자의 자연어 표현을 분석하여 관련된 법적 키워드들을 추출해주세요.

사용자 표현: "{user_query}"

다음과 같은 상황들을 고려하여 관련 법적 키워드들을 추출해주세요:

**성희롱/괴롭힘 관련:**
- 신체 접촉, 성적 언동 → "성희롱", "직장내괴롭힘", "성폭력"
- 욕설, 폭언, 따돌림 → "직장내괴롭힘", "인격모독"

**임금/근로조건 관련:**
- 급여, 월급, 돈 → "임금", "급여"
- 야근, 초과근무 → "연장근로", "근로시간"
- 연차, 휴가 → "연차", "휴가"

**해고/퇴사 관련:**
- 해고, 잘림, 퇴사 → "해고", "부당해고"
- 퇴직금 → "퇴직금", "퇴직급여"

**기타 근로조건:**
- 계약서, 근로계약 → "근로계약"
- 산재, 사고 → "산업재해", "안전보건"

응답 형식: 관련 키워드들을 쉼표로 구분하여 나열해주세요.
예시: "성희롱, 직장내괴롭힘, 성폭력"

관련 키워드:
"""

        # Generate response
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        
        # Extract keywords from response
        keywords_text = response.content.strip()
        keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
        
        logger.info(f"AI rephrased '{user_query}' to keywords: {keywords}")
        return keywords
        
    except Exception as e:
        logger.error(f"Failed to rephrase query with AI: {e}")
        return []


def enhance_query_understanding(user_query: str) -> List[str]:
    """
    Enhanced query understanding combining AI rephrasing with existing methods
    """
    all_keywords = []
    
    # 1. Try AI rephrasing first
    ai_keywords = rephrase_query_with_ai(user_query)
    if ai_keywords:
        all_keywords.extend(ai_keywords)
    
    # 2. Add original query as fallback
    all_keywords.append(user_query)
    
    # Remove duplicates while preserving order
    unique_keywords = []
    for keyword in all_keywords:
        if keyword not in unique_keywords:
            unique_keywords.append(keyword)
    
    return unique_keywords