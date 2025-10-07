# Admin Integration Guide

## 방법 1: 자동 주입 (간편하지만 충돌 가능성 있음)

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django_global_search',  # 자동으로 admin.site에 주입
    # ...
]
```

**장점**: 코드 변경 없음
**단점**: 다른 라이브러리와 충돌 가능

## 방법 2: 명시적 상속 (권장)

```python
# myproject/admin.py
from django.contrib.admin import AdminSite
from django_global_search.admin import GlobalSearchAdminSiteMixin

class MyAdminSite(GlobalSearchAdminSiteMixin, AdminSite):
    site_header = "My Admin"

# 기본 admin site 교체
admin_site = MyAdminSite(name='myadmin')
```

```python
# urls.py
from myproject.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
]
```

**장점**: 명확한 제어, 충돌 없음
**단점**: 약간의 boilerplate 코드

## 방법 3: 하이브리드 (설정으로 제어)

```python
# settings.py
DJANGO_GLOBAL_SEARCH = {
    'AUTO_INJECT': False,  # 자동 주입 비활성화
}
```

명시적으로 필요할 때만 사용.

