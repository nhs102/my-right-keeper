import logging
from dotenv import load_dotenv
from typing import List
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
try:
    # Try relative imports first (for package usage)
    from .api_connector import (
        get_law_interpretations,
        get_full_interpretation_text,
        parse_interpretation_list,
        parse_full_text,
    )
    from .config import config
except ImportError:
    # Fall back to direct imports (for standalone usage)
    from api_connector import (
        get_law_interpretations,
        get_full_interpretation_text,
        parse_interpretation_list,
        parse_full_text,
    )
    from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Load the environment variables from the .env file
load_dotenv()


def extract_keywords_from_natural_language(text: str) -> List[str]:
    """
    Extracts labor law related keywords from natural language text.
    
    Args:
        text: Natural language input from user
        
    Returns:
        List of extracted keywords relevant to labor law
    """
    # Labor law keyword patterns
    keyword_patterns = {
        # Severance pay patterns
        "퇴직금": ["퇴직금", "퇴사", "그만두", "나가", "떠나", "퇴직", "퇴직급여", "퇴직수당"],
        
        # Wage patterns  
        "임금": ["월급", "급여", "돈", "임금", "페이", "salary", "pay", "wage", "money"],
        "임금체불": ["안줘", "못받", "안받", "밀려", "체불", "안주", "미지급", "지연", "연체"],
        
        # Overtime patterns
        "연장근로": ["야근", "초과근무", "잔업", "overtime", "연장근로", "추가근무", "오버타임"],
        "연장근로수당": ["야근수당", "잔업수당", "초과수당", "overtime pay"],
        
        # Holiday pay patterns
        "주휴수당": ["주휴", "일요일", "휴일", "쉬는날", "주휴수당", "휴일수당"],
        
        # Vacation patterns
        "연차": ["휴가", "연차", "vacation", "유급휴가", "연가", "쉬고싶", "쉬어", "허가", "승인"],
        "연차사용": ["휴가거부", "연차거부", "휴가못", "연차못", "허가안", "승인안", "거부", "안해줘"],
        
        # Working hours patterns
        "근로시간": ["근무시간", "일하는시간", "몇시간", "시간당", "working hours"],
        "장시간근로": ["오래일", "너무오래", "많이일", "과로"],
        
        # Harassment patterns
        "직장내괴롭힘": ["괴롭", "따돌", "무시", "욕설", "폭언", "harassment", "bullying", "괴롭힘"],
        "성희롱": ["성희롱", "sexual", "추행", "성적"],
        
        # Dismissal patterns
        "해고": ["짤리", "자르", "fired", "해고", "그만두라", "나가라", "dismiss"],
        "부당해고": ["부당", "억울", "unfair", "wrongful", "부당해고"],
        
        # Contract patterns
        "근로계약": ["계약서", "contract", "근로계약", "고용계약", "사인"],
        
        # General work issues
        "근로조건": ["조건", "처우", "environment", "condition", "대우"],
        "노동분쟁": ["문제", "분쟁", "싸움", "dispute", "갈등", "trouble"],
    }
    
    extracted_keywords = []
    text_lower = text.lower()
    
    # Check each pattern category
    for main_keyword, patterns in keyword_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                extracted_keywords.append(main_keyword)
                break  # Only add once per category
    
    # If no specific keywords found, try general labor terms
    if not extracted_keywords:
        general_patterns = ["직장", "회사", "상사", "대표", "사장", "근로", "일", "work", "job", "boss"]
        for pattern in general_patterns:
            if pattern in text_lower:
                extracted_keywords.append("근로기준법")
                break
    
    # Remove duplicates while preserving order
    unique_keywords = list(dict.fromkeys(extracted_keywords))
    
    logger.debug(f"Extracted keywords from '{text}': {unique_keywords}")
    return unique_keywords


def expand_search_keywords(query: str) -> List[str]:
    """
    Expands search keywords to improve API search success rate.
    
    Args:
        query: Original search query
        
    Returns:
        List of expanded/alternative search terms
    """
    # Keyword expansion mapping
    keyword_expansions = {
        # Severance pay related
        "퇴직금": ["퇴직급여", "퇴직", "근로기준법 퇴직", "퇴직금 계산"],
        "퇴직": ["퇴직금", "퇴직급여", "근로관계 종료"],
        "severance": ["퇴직금", "퇴직급여", "퇴직"],
        
        # Wages and overtime
        "주휴수당": ["주휴일", "유급휴일", "주휴", "휴일근로"],
        "임금": ["급여", "월급", "임금체불", "근로기준법 임금"],
        "연장근로": ["초과근무", "야근", "연장근로수당"],
        "overtime": ["연장근로", "초과근무", "연장근로수당"],
        
        # Workplace harassment
        "괴롭힘": ["직장내 괴롭힘", "괴롭힘 금지", "직장 내 괴롭힘"],
        "harassment": ["직장내 괴롭힘", "괴롭힘"],
        
        # Leave and vacation
        "연차": ["연차휴가", "휴가", "유급휴가"],
        "휴가": ["연차", "연차휴가", "휴가사용"],
        "vacation": ["연차", "휴가", "연차휴가"],
        
        # Dismissal and termination
        "해고": ["부당해고", "정리해고", "징계해고", "근로관계 종료"],
        "부당해고": ["해고", "정리해고", "징계"],
        "dismissal": ["해고", "부당해고"],
        
        # Working hours
        "근로시간": ["법정근로시간", "연장근로", "근로기준법 근로시간"],
        "hours": ["근로시간", "법정근로시간"],
        
        # Contracts
        "근로계약": ["계약서", "근로계약서", "고용계약"],
        "contract": ["근로계약", "계약서"],
        
        # General fallbacks
        "노동법": ["근로기준법", "노동", "근로"],
        "근로": ["노동", "근로기준법", "근로자"],
        "labor": ["노동", "근로", "근로기준법"]
    }
    
    expanded_queries = []
    
    # Extract key terms from the query
    query_lower = query.lower().strip()
    
    # Direct mapping lookup
    for keyword, expansions in keyword_expansions.items():
        if keyword in query_lower:
            expanded_queries.extend(expansions)
    
    # If no direct matches, try general labor law terms
    if not expanded_queries:
        expanded_queries = ["근로기준법", "노동", "근로자", "근로"]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in expanded_queries:
        if q not in seen and q != query:
            seen.add(q)
            unique_queries.append(q)
    
    return unique_queries[:3]  # Limit to top 3 alternatives


def create_documents_from_api(query: str) -> List[Document]:
    """
    Retrieves legal interpretations from the API and converts them into LangChain Document objects.
    Uses natural language keyword extraction and fallback searches to improve success rate.

    Args:
        query: Search query (can be natural language or keywords).

    Returns:
        List of LangChain Document objects.
    """
    logger.info(f"Creating documents from API for query: '{query}'")
    
    # Helper function to check if API response has results
    def has_results(api_response):
        if not api_response:
            return False
        # Check for CgmExpc structure
        if "CgmExpc" in api_response:
            total_count = api_response["CgmExpc"].get("totalCnt", "0")
            return int(total_count) > 0
        return False
    
    # Try original query first
    raw_list_data = get_law_interpretations(query)
    
    # If no results, try AI-enhanced query understanding
    if not has_results(raw_list_data):
        try:
            from query_enhancer import enhance_query_understanding
            ai_keywords = enhance_query_understanding(query)
            logger.info(f"Original query failed, trying AI-enhanced keywords: {ai_keywords}")
            
            for keyword in ai_keywords:
                logger.info(f"Trying AI-enhanced keyword: '{keyword}'")
                raw_list_data = get_law_interpretations(keyword)
                if has_results(raw_list_data):
                    logger.info(f"Success with AI-enhanced keyword: '{keyword}'")
                    break
        except Exception as e:
            logger.warning(f"AI query enhancement failed: {e}")
    
    # If still no results, try extracting keywords from natural language (fallback)
    if not has_results(raw_list_data):
        extracted_keywords = extract_keywords_from_natural_language(query)
        logger.info(f"AI enhancement failed, trying extracted keywords: {extracted_keywords}")
        
        for keyword in extracted_keywords:
            logger.info(f"Trying extracted keyword: '{keyword}'")
            raw_list_data = get_law_interpretations(keyword)
            if has_results(raw_list_data):
                logger.info(f"Success with extracted keyword: '{keyword}'")
                break
    
    # If still no results, try expanded keywords (final fallback)
    if not has_results(raw_list_data):
        expanded_queries = expand_search_keywords(query)
        logger.info(f"All methods failed, trying expanded keywords: {expanded_queries}")
        
        for expanded_query in expanded_queries:
            logger.info(f"Trying expanded query: '{expanded_query}'")
            raw_list_data = get_law_interpretations(expanded_query)
            if has_results(raw_list_data):
                logger.info(f"Success with expanded query: '{expanded_query}'")
                break
    
    if not has_results(raw_list_data):
        logger.warning("No results found from API after all attempts")
        return []

    logger.debug("Parsing list data...")
    parsed_list = parse_interpretation_list(raw_list_data)
    if not parsed_list:
        logger.warning("No parsed list data")
        return []

    documents = []
    for item in parsed_list:
        interpretation_id = item.get("interpretation_id")
        if not interpretation_id:
            continue

        raw_full_text = get_full_interpretation_text(interpretation_id)
        if not raw_full_text:
            continue

        parsed_full_text = parse_full_text(raw_full_text)

        # Create a LangChain Document object
        # The 'page_content' is the main text, and 'metadata' is additional info
        document = Document(
            page_content=parsed_full_text.get("text", ""),
            metadata={
                "title": parsed_full_text["metadata"].get("title"),
                "case_name": item.get("case_name"),
                "source": f"법제처 법령해석 일련번호 {parsed_full_text['metadata'].get('interpretation_id')}",
                "reply_date": parsed_full_text["metadata"].get("reply_date"),
                "link": item.get("link"),
                "interpretation_id": item.get("interpretation_id"),
            },
        )
        documents.append(document)

    logger.info(f"Created {len(documents)} documents from API")
    return documents


def create_vector_store(documents: List[Document]) -> Chroma:
    """
    Creates a Chroma vector store from a list of documents.

    Args:
        documents: List of LangChain Document objects.

    Returns:
        Chroma vector store instance.
    """
    logger.info(f"Creating vector store with {len(documents)} documents")
    # Initialize the Gemini embedding model
    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)

    # Create the vector store from the documents and embeddings
    try:
        vector_store = Chroma.from_documents(documents=documents, embedding=embeddings)
        logger.info("Vector store created successfully")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")
        raise


def get_rag_answer(query: str, vector_store: Chroma) -> str:
    """
    Performs a RAG search and generates a final answer.
    Returns the final answer text.
    """
    # Create a retriever from the vector store
    retriever = vector_store.as_retriever()

    # Define the LLM with a stable model name
    logger.debug(f"Initializing LLM with model: {config.GEMINI_MODEL}")
    llm = ChatGoogleGenerativeAI(model=config.GEMINI_MODEL)

    # Create a prompt template for the LLM
    template = """
    당신은 **대한민국 노동법 전문가 AI 비서 'My Rights Keeper'**입니다. 다음 법률 문서들을 참고하여 사용자 질문에 대해 **전문적이고 상세하며 깔끔하게** 답변해주세요.
    
    **참고 문서 (Context):**
    {context}
    
    **지침:**
    1. **어투 및 톤앤매너:** 답변은 **매우 전문적인 어투와 공식적인 용어**를 사용하여 작성하십시오. (~합니다, ~에 해당됩니다. 단정적 표현을 지양하고, ~할 수 있습니다, ~로 판단됩니다와 같이 **조심스러운 어투**를 사용하십시오.)
    2. **답변 구성:** 답변은 최소 3문단 이상으로 구성하고, 다음 항목들을 반드시 포함하십시오.
        a. **문제 정의:** 사용자의 상황이 법률적으로 어떤 문제(예: 임금체불, 괴롭힘)에 해당하는지 명확히 언급.
        b. **법적 근거:** 관련 법률(예: 근로기준법) 및 법령해석의 세부 내용을 활용하여 문제에 대한 법적 판단 근거를 상세히 설명.
        c. **결론 및 조언:** 상황 해결을 위한 실질적인 다음 단계(예: 고용노동부 진정, 내용증명)를 제안.
    3. **출처는 별도 처리:** 답변 본문에는 출처를 포함하지 말고, 순수하게 내용만 작성하십시오.
    4. **무응답 지침:** 참고 문서에 관련 내용이 없다면, "참고할 수 있는 정확한 법률 문서를 찾지 못하여 상세한 답변을 드릴 수 없습니다."라고 답하세요.
    
    사용자의 질문: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # Create the RAG chain using LCEL
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    try:
        logger.info(f"Generating RAG answer for query: '{query}'")
        answer = rag_chain.invoke(query)
        
        # Get the source documents to extract links
        relevant_docs = retriever.invoke(query)
        
        # Add source links at the end
        if relevant_docs:
            answer += "\n\n---\n\n**📖 참고 법령해석:**\n"
            for i, doc in enumerate(relevant_docs[:3], 1):  # Show top 3 sources
                case_name = doc.metadata.get('case_name', '제목 없음')
                interpretation_id = doc.metadata.get('interpretation_id', '')
                link = doc.metadata.get('link')
                reply_date = doc.metadata.get('reply_date', '')
                
                # Truncate long case names
                if case_name and len(case_name) > 60:
                    case_name = case_name[:57] + "..."
                
                if link:
                    answer += f"\n{i}. [{case_name}]({link})"
                    if reply_date:
                        answer += f" ({reply_date})"
                else:
                    answer += f"\n{i}. {case_name}"
                    if reply_date:
                        answer += f" ({reply_date})"
                    if interpretation_id:
                        answer += f" [일련번호: {interpretation_id}]"
        
        logger.info("RAG answer generated successfully")
        return answer
    except Exception as e:
        logger.error(f"Failed to generate RAG answer: {e}")
        raise


if __name__ == "__main__":
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        exit(1)

    # Example execution when run directly (for console testing)
    query = "모의 데이터 테스트"
    legal_documents = create_documents_from_api(query)

    if legal_documents:
        vector_store = create_vector_store(legal_documents)
        user_question = "퇴직금을 못 받았을 때 어떻게 해야 하나요?"

        final_answer = get_rag_answer(user_question, vector_store)

        print("\n--- Final Answer ---")
        print(final_answer)
        print("--------------------")
    else:
        print("\nNo documents were created to populate the vector store.")
