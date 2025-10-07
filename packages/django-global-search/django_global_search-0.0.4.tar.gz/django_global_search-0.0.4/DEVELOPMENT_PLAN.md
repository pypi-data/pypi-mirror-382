# Django Global Search - 개발 계획서

## 프로젝트 개요

### 배경
- Django Admin의 각 모델은 개별 `search_fields`를 통해 검색 가능
- 특정 키워드로 여러 모델을 검색하려면 각 Model Admin을 일일이 방문해야 함
- 시간 소모적이고 비효율적인 워크플로우

### 목표
**한 페이지에서 여러 모델을 선택하여 검색하고, 결과를 통합 조회할 수 있는 Django Admin 확장 기능 개발**

### 핵심 가치
- 최소한의 코드 변경으로 사용 가능
- Django Admin 위에서 자연스럽게 동작
- 기존 ModelAdmin 설정 활용

## 핵심 기능

### 1. 통합 검색 페이지
- 한 페이지에서 검색할 모델 선택 (체크박스 또는 드롭다운)
- 검색어 입력
- Ajax 기반 비동기 검색

### 2. 권한 기반 모델 필터링
- 사용자가 접근 가능한 모델만 검색 대상으로 표시
- `has_view_permission` 또는 `has_change_permission` 활용

### 3. 검색 결과 통합 표시
- 모델별로 그룹화된 결과
- 각 결과는 해당 ModelAdmin의 changelist로 링크
- 결과 미리보기 (제목, 주요 필드 등)

### 4. 성능 제어
- **모델별 타임아웃**: 느린 모델이 전체 검색을 지연시키지 않도록
- **결과 수 제한**: 각 모델당 최대 N개 결과만 표시
- **병렬 검색**: 여러 모델을 동시에 검색하여 속도 향상

### 5. 상세 검색 결과 링크
- 각 모델의 검색 결과는 해당 Admin의 필터링된 changelist URL 제공
- 예: `/admin/app/model/?q=searchterm`

## 기술 설계

### 아키텍처

```
User Request (검색어 입력)
    ↓
Ajax Request → SearchView
    ↓
Registry (사용자 권한 확인)
    ↓
Searcher (병렬 검색 실행)
    ↓
각 ModelAdmin.get_search_results() 호출
    ↓
결과 수집 및 정규화
    ↓
JSON Response → Frontend
    ↓
결과 렌더링
```

### 주요 컴포넌트

#### 1. Registry (`registry.py`)
**역할**: 검색 가능한 모델 관리

- 자동 등록: `AdminSite`에 등록된 모든 ModelAdmin 감지
- AdminSite class를 상속받는 방식
- custom admin site class가 없을경우 기본 AdminSite에 주입


```python
class SearchRegistry:
    def register(self, model_admin, **options)
    def get_searchable_models(self, user)
    def get_search_config(self, model)
```

#### 2. Searcher (`searcher.py`)
**역할**: 실제 검색 실행

- 타임아웃 처리: 각 모델 검색에 제한 시간 적용
- 결과 정규화: 다양한 모델의 결과를 통일된 형식으로 변환

```python
class GlobalSearcher:
    def search(self, query, models, user, timeout=10, max_results=20)
    def _search_model(self, model, query, timeout, max_results)
    def _normalize_results(self, results)
```

#### 3. Permissions (`permissions.py`)
**역할**: 권한 검증

- ModelAdmin의 권한 메서드 활용
- 사용자별 검색 가능 모델 필터링

```python
def get_searchable_models_for_user(user, admin_site):
    # has_view_permission 또는 has_change_permission 체크
```

#### 4. Views (`views.py`)
**역할**: HTTP 요청 처리

- `SearchPageView`: 검색 페이지 렌더링
- `SearchAPIView`: Ajax 검색 요청 처리 (JSON 응답)

```python
class SearchPageView(TemplateView):
    template_name = 'django_global_search/search.html'

class SearchAPIView(View):
    def get(self, request):
        # 검색 실행 및 JSON 반환
```

#### 5. Admin Integration (`admin.py`)
**역할**: Django Admin에 통합

- 커스텀 AdminSite 또는 기존 AdminSite 확장
- 네비게이션 메뉴에 검색 링크 추가

### 프론트엔드

#### JavaScript (`static/js/search.js`)
- Fetch API를 사용한 Ajax 검색
- 실시간 결과 업데이트
- 로딩 상태 표시
- 에러 핸들링

#### Template (`templates/search.html`)
- Django Admin 스타일과 일관된 UI
- 모델 선택 인터페이스
- 검색 결과 표시 영역
- 로딩 스피너

#### CSS (`static/css/search.css`)
- Django Admin 기본 스타일 상속
- 결과 그룹화 스타일링
- 반응형 디자인

## 사용자 API

### 기본 사용 (자동 설정)

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django_global_search',  # admin 앱 다음에 추가
    # ... 다른 앱들
]

# urls.py (자동 등록 방식)
# django_global_search가 자동으로 admin URLs에 통합
```

### 고급 사용 (커스터마이징)

```python
# admin.py
from django.contrib import admin
from django_global_search import SearchConfig

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    search_fields = ['title', 'content']  # 기존 방식대로
    
    # 선택적: 검색 설정 커스터마이징
    search_config = SearchConfig(
        timeout=5,  # 초
        max_results=15,
        priority=10,  # 높을수록 먼저 표시
        display_fields=['title', 'created_at'],  # 결과에 표시할 필드
    )
```

### 설정 옵션

```python
# settings.py
DJANGO_GLOBAL_SEARCH = {
    # 기본값
    'DEFAULT_TIMEOUT': 10,  # 초
    'DEFAULT_MAX_RESULTS': 20,
    'ENABLE_AUTO_REGISTER': True,  # 모든 ModelAdmin 자동 등록
    'EXCLUDE_MODELS': [  # 제외할 모델 (app_label.model_name)
        'auth.Permission',
        'contenttypes.ContentType',
    ],
    'SEARCH_URL_NAME': 'global_search',  # URL name
    'ADD_TO_ADMIN_INDEX': True,  # Admin 인덱스에 링크 추가
}
```

## 프로젝트 구조

```
src/django_global_search/
├── __init__.py              # 버전, 공개 API
├── apps.py                  # AppConfig
├── admin.py                 # Admin 통합
├── urls.py                  # URL 라우팅
├── views.py                 # SearchPageView, SearchAPIView
├── registry.py              # SearchRegistry
├── searcher.py              # GlobalSearcher
├── permissions.py           # 권한 헬퍼
├── config.py                # SearchConfig 클래스
├── templates/
│   └── django_global_search/
│       ├── search.html      # 메인 검색 페이지
│       └── _results.html    # 결과 partial
└── static/
    └── django_global_search/
        ├── css/
        │   └── search.css
        └── js/
            └── search.js
```

## 개발 단계

### Phase 1: 기본 인프라
- [ ] 프로젝트 구조 생성
- [ ] `SearchRegistry` 구현 (자동 모델 감지)
- [ ] 기본 View 및 URL 설정
- [ ] 간단한 템플릿 (UI 없이 동작 확인)

### Phase 2: 검색 엔진
- [ ] `GlobalSearcher` 구현
- [ ] 단일 모델 검색 기능
- [ ] 병렬 검색 구현 (ThreadPoolExecutor)
- [ ] 타임아웃 처리
- [ ] 결과 정규화

### Phase 3: 권한 및 보안
- [ ] Permission 체크 로직
- [ ] 사용자별 모델 필터링
- [ ] CSRF 보호
- [ ] XSS 방지

### Phase 4: UI/UX
- [ ] 검색 페이지 UI 구현
- [ ] Ajax 검색 JavaScript
- [ ] 결과 렌더링 (모델별 그룹화)
- [ ] 로딩 상태 및 에러 표시
- [ ] Admin 스타일 통합

### Phase 5: 고급 기능
- [ ] 모델별 설정 (SearchConfig)
- [ ] 우선순위 기반 정렬
- [ ] 결과 필드 커스터마이징
- [ ] Admin 인덱스 페이지 통합

### Phase 6: 테스트
- [ ] 단위 테스트 (Registry, Searcher, Permissions)
- [ ] 통합 테스트 (View, Ajax)
- [ ] 권한 테스트
- [ ] 성능 테스트 (타임아웃, 병렬 처리)

### Phase 7: 문서화
- [ ] README 작성
- [ ] 사용 가이드
- [ ] API 문서
- [ ] 예제 프로젝트

## 핵심 원칙

### 1. 최소 침투성
- 기존 Django Admin 코드 수정 불필요
- `search_fields` 그대로 활용
- 선택적 기능 활성화

### 2. Pythonic 코드
- Type hints 사용
- Context manager 활용
- Generator 사용 (메모리 효율)
- 명확한 네이밍

### 3. 성능 우선
- 병렬 처리
- 타임아웃 보장
- 불필요한 쿼리 방지 (select_related, prefetch_related)

### 4. 확장성
- 플러그인 구조
- 커스터마이징 포인트 제공
- 다양한 사용 사례 지원

## 예상 이슈 및 해결책

### 1. 검색 성능
**문제**: 대용량 데이터베이스에서 느린 검색  
**해결**: 
- 타임아웃 설정
- 결과 수 제한
- DB 인덱스 권장 사항 문서화

### 2. 권한 복잡성
**문제**: 복잡한 커스텀 권한 로직  
**해결**: 
- ModelAdmin의 기존 메서드 활용
- 커스텀 권한 체크 훅 제공

### 3. 결과 표시 일관성
**문제**: 모델마다 다른 중요 필드  
**해결**: 
- `__str__` 메서드 활용
- `display_fields` 커스터마이징 옵션

### 4. Admin 사이트 통합
**문제**: 커스텀 AdminSite 사용 시  
**해결**: 
- 자동 감지 로직
- 수동 등록 옵션 제공

## 성공 지표

- ✅ 3줄 이하 코드로 기본 기능 활성화 가능
- ✅ 10개 모델 동시 검색 시 3초 이내 응답
- ✅ Django 4.2+ 호환
- ✅ Python 3.9+ 지원 

