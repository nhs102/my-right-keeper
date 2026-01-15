# Vector Store Caching Feature

## Overview

세션별 벡터 스토어 캐싱 기능을 통해 유사한 질문에 대한 응답 시간을 최대 50% 단축합니다.

## How It Works

### 1. Keyword-Based Similarity

사용자 질문에서 핵심 키워드를 추출하고, Jaccard 유사도를 계산하여 캐시된 질문과 비교합니다.

```python
# 예시
query1 = "퇴직금 계산 방법"
query2 = "퇴직금 계산 기준"

# 키워드 추출: {"퇴직금", "계산", "방법"} vs {"퇴직금", "계산", "기준"}
# 교집합: {"퇴직금", "계산"}
# 합집합: {"퇴직금", "계산", "방법", "기준"}
# 유사도: 2/4 = 0.5 (50%)
```

### 2. LRU Cache Management

최대 5개의 벡터 스토어를 메모리에 유지하며, 가장 오래된 항목부터 제거합니다.

```
Cache: [Query1, Query2, Query3, Query4, Query5]
New Query → Evict Query1 → [Query2, Query3, Query4, Query5, New Query]
```

### 3. Cache Hit/Miss Tracking

사이드바에서 캐시 성능을 실시간으로 모니터링할 수 있습니다.

## Performance Improvement

### Before Caching
```
User: "퇴직금 계산 방법" → 10초
User: "퇴직금 계산 기준" → 10초 (similar query, but no cache)
Total: 20초
```

### After Caching
```
User: "퇴직금 계산 방법" → 10초 (cache miss)
User: "퇴직금 계산 기준" → 5초 (cache hit, 50% faster!)
Total: 15초 (25% improvement)
```

## Usage

### Automatic Caching

캐싱은 자동으로 작동합니다. 사용자는 다음과 같은 알림을 받습니다:

- **캐시 적중 (정확)**: "💡 캐시된 데이터를 사용하여 빠르게 답변합니다!"
- **캐시 적중 (유사)**: "💡 이전 질문 '...'와 유사하여 빠르게 답변합니다!"

### Cache Statistics

사이드바에서 다음 정보를 확인할 수 있습니다:

- **캐시 적중/미스 횟수**
- **적중률 (%)**
- **현재 캐시 크기**
- **캐시된 질문 목록**

### Manual Cache Management

- **캐시 초기화**: 사이드바의 "🗑️ 캐시 초기화" 버튼 클릭
- **자동 초기화**: 브라우저 세션 종료 시 자동으로 초기화됨

## Configuration

### Similarity Threshold

`cache_utils.py`에서 유사도 임계값을 조정할 수 있습니다:

```python
# 기본값: 0.5 (50% 유사도)
cached_vector_store, cache_key = st.session_state.vector_cache.get(
    prompt, 
    threshold=0.5  # 이 값을 조정
)
```

- **0.3-0.4**: 더 많은 캐시 적중 (낮은 정확도)
- **0.5-0.6**: 균형잡힌 설정 (권장)
- **0.7-0.8**: 높은 정확도 (적은 캐시 적중)

### Cache Size

`web_app.py`에서 최대 캐시 크기를 조정할 수 있습니다:

```python
st.session_state.vector_cache = VectorStoreCache(
    max_size=5  # 기본값: 5개
)
```

## Memory Usage

각 캐시 항목은 약 80-100KB를 사용합니다:

- **5개 캐시**: ~500KB
- **10개 캐시**: ~1MB

메모리 사용량이 적으므로 대부분의 환경에서 안전하게 사용할 수 있습니다.

## Testing

캐싱 기능을 테스트하려면:

```bash
# 단위 테스트 실행
pytest tests/test_cache_utils.py -v

# 전체 테스트 실행
pytest tests/ -v
```

## Example Scenarios

### Scenario 1: Follow-up Questions

```
User: "퇴직금은 어떻게 계산하나요?"
→ Cache miss, 10초

User: "퇴직금 계산 시 포함되는 항목은?"
→ Cache hit (유사도 66%), 5초 ✅
```

### Scenario 2: Topic Exploration

```
User: "주휴수당이란?"
→ Cache miss, 10초

User: "아르바이트 주휴수당"
→ Cache hit (유사도 50%), 5초 ✅

User: "퇴직금 계산"
→ Cache miss (다른 주제), 10초
```

## Limitations

1. **세션 기반**: 브라우저를 닫으면 캐시가 초기화됩니다
2. **키워드 기반**: 의미는 같지만 다른 단어를 사용하면 캐시 미스 발생
3. **메모리 제한**: 최대 5개 질문만 캐시됨

## Future Enhancements

- **의미 기반 유사도**: 임베딩을 사용한 더 정확한 유사도 계산
- **영구 캐시**: 디스크에 캐시 저장하여 세션 간 유지
- **사용자별 캐시**: 다중 사용자 환경에서 개인화된 캐시
