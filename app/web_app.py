import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

try:
    # Try relative imports first (for package usage)
    from .rag_pipeline import (
        create_documents_from_api,
        create_vector_store,
        get_rag_answer,
    )
    from .cache_utils import VectorStoreCache
except ImportError:
    # Fall back to direct imports (for standalone usage)
    from rag_pipeline import (
        create_documents_from_api,
        create_vector_store,
        get_rag_answer,
    )
    from cache_utils import VectorStoreCache

# Streamlit UI 설정
st.set_page_config(page_title="My Rights Keeper", layout="wide")

st.title("⚖️ My Rights Keeper: Korean Labor Law AI Assistant")
st.write(
    "Ask any questions about Korean labor law. Get accurate answers based on official Ministry of Government Legislation data."
)

# 세션 상태 초기화 (대화 기록 저장)
if "messages" not in st.session_state:
    # 초기 대화 기록 설정
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Feel free to ask any questions about Korean labor law.",
        }
    ]

# 벡터 스토어 캐시 초기화
if "vector_cache" not in st.session_state:
    st.session_state.vector_cache = VectorStoreCache(max_size=5)

# 캐시 통계 초기화
if "cache_stats" not in st.session_state:
    st.session_state.cache_stats = {"hits": 0, "misses": 0}

# 사이드바: 시스템 정보 및 캐시 통계
with st.sidebar:
    st.header("� API Key Settings")
    
    # 사용자로부터 API 키 입력 받기
    user_api_key = st.text_input(
        "Enter your Google API Key",
        type="password",
        help="Get your API key from https://aistudio.google.com/app/apikey",
        placeholder="AIzaSy..."
    )
    
    if user_api_key:
        # 입력받은 키를 환경 변수에 임시 설정
        os.environ["GOOGLE_API_KEY"] = user_api_key
        st.success("API Key applied for this session!")
    else:
        st.warning("Please enter your Google API Key to use the AI features.")
        st.markdown("[Get an API key here](https://aistudio.google.com/app/apikey)")

    st.divider()

    st.header("�📊 System Info")

    # Chat statistics
    user_message_count = len(
        [m for m in st.session_state.messages if m["role"] == "user"]
    )
    st.metric("Total Questions", user_message_count)

    # Cache statistics
    st.divider()
    st.subheader("⚡ Cache Performance")

    cache_stats = st.session_state.cache_stats
    total_queries = cache_stats["hits"] + cache_stats["misses"]
    hit_rate = (cache_stats["hits"] / total_queries * 100) if total_queries > 0 else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cache Hits", cache_stats["hits"])
    with col2:
        st.metric("Cache Misses", cache_stats["misses"])

    if total_queries > 0:
        st.progress(hit_rate / 100)
        st.caption(f"Hit Rate: {hit_rate:.1f}%")

    # Cache status
    cache_info = st.session_state.vector_cache.get_stats()
    st.metric("Cache Size", f"{cache_info['size']}/{cache_info['max_size']}")

    if cache_info["queries"]:
        with st.expander("View Cached Questions"):
            for i, query in enumerate(cache_info["queries"], 1):
                st.caption(f"{i}. {query[:30]}...")

    st.divider()

    # Usage guide
    st.header("💡 Usage Tips")
    st.markdown(
        """
    **💬 Natural Conversation Supported!**
    - Tell your story naturally: *"퇴사한지 3개월인데 대표가 퇴직금을 안줘"*
    - Use everyday language: *"My boss won't pay overtime"*
    - Keywords also work: *"severance pay calculation"*
    
    **🧠 Smart Keyword Detection**: The AI extracts legal terms automatically!
    
    **⚡ Cache Feature**: Similar questions get faster responses!
    """
    )

    st.divider()

    # Reset conversation button
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! Feel free to ask any questions about Korean labor law.",
            }
        ]
        st.rerun()

    # Clear cache button
    if st.button("🗑️ Clear Cache"):
        st.session_state.vector_cache.clear()
        st.session_state.cache_stats = {"hits": 0, "misses": 0}
        st.success("Cache has been cleared!")
        st.rerun()

# 기존 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input handling  
if prompt := st.chat_input("Tell me your situation: '퇴사한지 3개월인데 퇴직금을 안줘', 'My boss won't pay overtime', etc..."):
    # 1. 사용자 메시지 기록 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI 응답 처리 (RAG 파이프라인 실행)
    start_time = time.time()

    with st.spinner("Generating response... Please wait."):
        if not os.getenv("GOOGLE_API_KEY"):
            response_text = "⚠️ Error: Please enter your Google API Key in the sidebar to use this feature."
        else:
            # 캐시 확인
            cached_vector_store, cache_key = st.session_state.vector_cache.get(
                prompt, threshold=0.5
            )

            if cached_vector_store is not None:
                # 캐시 적중!
                st.session_state.cache_stats["hits"] += 1
                vector_store = cached_vector_store

                # User notification
                if cache_key != prompt:
                    st.info(
                        f"💡 Similar to previous question '{cache_key[:40]}...' - responding quickly!"
                    )
                else:
                    st.info("💡 Using cached data for fast response!")

                legal_documents = None  # 캐시 사용 시 문서 재생성 불필요
            else:
                # 캐시 미스 - 새로 생성
                st.session_state.cache_stats["misses"] += 1

                # Step 1: Document 생성 (API에서 법률 문서 가져오기)
                legal_documents = create_documents_from_api(prompt)

            # Check for practical knowledge first
            from practical_knowledge import get_practical_answer
            practical_answer = get_practical_answer(prompt)
            
            if practical_answer:
                # Use practical knowledge and try to add legal context if available
                response_text = practical_answer
                
                # Try to add legal context if we found relevant documents
                if cached_vector_store is not None or legal_documents:
                    try:
                        # Generate additional legal context
                        if cached_vector_store is None:
                            vector_store = create_vector_store(legal_documents)
                            st.session_state.vector_cache.put(prompt, vector_store)
                        
                        # Add brief legal context
                        legal_context = get_rag_answer(prompt, vector_store)
                        if legal_context and "참고할 수 있는 정확한 법률 문서를 찾지 못하여" not in legal_context:
                            response_text += f"\n\n**🏛️ 관련 법령해석:**\n{legal_context.split('---')[0].strip()}"
                    except:
                        pass  # If legal context fails, just use practical knowledge
                
                elapsed_time = time.time() - start_time
                response_text += f"\n\n---\n⏱️ *Response time: {elapsed_time:.2f}s*"
                response_text += "\n💡 *실무 가이드와 법령해석을 종합한 답변입니다.*"
            elif cached_vector_store is not None or legal_documents:
                try:
                    # Step 2: Vector Store 생성 (캐시 미스인 경우만)
                    if cached_vector_store is None:
                        vector_store = create_vector_store(legal_documents)
                        # 캐시에 저장
                        st.session_state.vector_cache.put(prompt, vector_store)

                    # Step 3: RAG 답변 생성
                    response_text = get_rag_answer(prompt, vector_store)

                    # Response time display
                    elapsed_time = time.time() - start_time
                    response_text += f"\n\n---\n⏱️ *Response time: {elapsed_time:.2f}s*"

                except Exception as e:
                    error_message = str(e)
                    if (
                        "API_KEY" in error_message
                        or "authentication" in error_message.lower()
                    ):
                        response_text = f"🚫 **AI Response Generation Error (Authentication):** Google API key is invalid or lacks permissions."
                    elif "404" in error_message or "NotFound" in error_message:
                        response_text = f"🚫 **AI Response Generation Error (Model Issue):** Gemini model not found. (Check model name)"
                    else:
                        response_text = f"🚫 **Unknown Error During AI Response Generation:** {error_message[:70]}..."
            else:
                response_text = """
                ❌ Could not find related legal documents after trying multiple search terms.
                
                **Please try these Korean labor law topics:**
                - **Severance pay**: "퇴직금", "퇴직급여", "퇴직금 계산"
                - **Wages**: "임금", "급여", "임금체불", "최저임금"
                - **Overtime**: "연장근로", "초과근무", "야근수당"
                - **Holiday pay**: "주휴수당", "주휴일", "유급휴일"
                - **Vacation**: "연차", "연차휴가", "휴가사용"
                - **Workplace harassment**: "직장내 괴롭힘", "괴롭힘"
                - **Dismissal**: "해고", "부당해고", "정리해고"
                - **Working hours**: "근로시간", "법정근로시간"
                - **Labor contract**: "근로계약", "근로계약서"
                
                *Try using specific Korean terms for better results!*
                """

        # --- Streamlit의 Chat Message 형식에 맞게 출력 및 기록 ---
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )
