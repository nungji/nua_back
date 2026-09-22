# AGENT.md — nua 백엔드

## 프로젝트

**nua** — 5세 유아의 컴퓨팅 사고능력 향상을 위한 게이미피케이션 앱.

- 유아가 기초적인 골드버그 장치를 직접 만드는 놀이가 중심이다. 구슬이 굴러갈 트랙을 배치해 목표 지점까지 도달시키는 것이 기본 목표다.
- 운반 대상은 구슬로 고정되지 않는다. 물류 상자, 고양이 등으로 바뀔 수 있고, 그에 맞춰 에스컬레이터·컨베이어 벨트 같은 장치가 주어진다.
- 배경(집, 물류창고, 어린이집 등)이 있고, 배경마다 등장하는 상황과 사물이 달라진다.
- 최종 목표는 게임 자체가 아니라 컴퓨팅 사고능력이다. 복잡한 문제를 작게 나누고 논리적인 순서로 해결하는 경험을 놀이로 전달한다.

### 타깃 사용자

사용자는 5세다. 다음이 전제다.

- 7 * 7 같은 계산은 하지 못한다.
- 보이는 것을 그대로 믿는다. 화면에 보이지 않는 상태 변화를 추론하지 않는다.
- 덧셈은 알아도 역연산을 모른다. 3+1=4는 알지만 4-3=1은 모른다.

따라서 계산이나 독해를 요구하는 인터페이스는 성립하지 않고, 응답 지연은 곧 "게임이 멈췄다"로 읽힌다. 백엔드는 응답을 짧게 유지하고, 실패를 조용히 삼키지 않는다.

### 팀

| 이름 | 역할 |
|---|---|
| 김주연 | 디자인, 캐릭터 디자인 |
| 곽영빈 | 프론트엔드 개발, 세부 UX 개발, 백엔드 리뷰 |
| 전지원 | 백엔드 주 개발 |

### 백엔드가 맡는 것 (문서 기준, 확정 전)

- 스테이지 데이터 제공 — 배경, 목표 지점, 지급되는 장치 구성
- 플레이 진행도와 결과 저장
- 유아 대상이므로 계정과 로그인을 전제하지 않는다. 기기 단위 식별자를 기본으로 본다.

## 기술 스택

| 영역 | 선택 |
|---|---|
| 언어 | Python 3.14 |
| 패키지·가상환경 | uv (PEP 517, src 레이아웃) |
| 웹 프레임워크 | FastAPI (엔드포인트는 전부 async) |
| DB | PostgreSQL |
| ORM | SQLAlchemy 2.0 (async) |
| 스키마·검증 | Pydantic v2 |

이 외의 스택은 아직 확정되지 않았다. 새 라이브러리를 추가하기 전에 먼저 확인받는다. 마이그레이션은 SQLAlchemy 생태계에 맞춰 Alembic을 쓴다.

```bash
uv sync
uv run nua                     # 개발 실행
uv run alembic upgrade head    # 마이그레이션 적용
```

## 디렉터리 구조

```text
nua-backend/
├── pyproject.toml
├── uv.lock
├── .env.example
├── migrations/          # Alembic
└── src/nua/
    ├── __init__.py      # main() 진입점
    ├── __main__.py      # main() 호출
    ├── config.py        # 설정 dataclass + .env 로딩
    ├── app.py           # FastAPI 인스턴스 생성, lifespan, 라우터 등록
    ├── api/
    │   ├── schemas.py   # Pydantic 요청·응답 모델
    │   └── routes/      # 도메인별 라우터
    ├── domain/          # 도메인 모델, enum, 도메인 예외 (DB·HTTP 무관)
    ├── db/
    │   ├── models.py    # SQLAlchemy ORM 매핑
    │   └── session.py   # async engine, sessionmaker
    └── services/        # 유스케이스 (라우터와 DB 사이)
```

규칙:

- 패키지명은 `nua`, 소스 루트는 `src/nua`.
- **도메인 단위로 파일을 나눈다.** 도메인이 늘면 `domain/<도메인>.py`, `api/routes/<도메인>.py`, `services/<도메인>.py`, `db/models/<도메인>.py`가 함께 늘어난다. 계층별로 한 파일에 몰아넣지 않는다.
- **enum을 중앙 `enums.py`에 모으지 않는다.** 해당 도메인 파일 안에 정의한다. 조회용 매핑 표가 필요하면 모듈 최상단 dict를 만들지 말고 enum 속성으로 붙인다.
- 라우터는 HTTP만 담당한다. 검증·계산·DB 접근은 service로 내린다.
- `domain/`은 FastAPI와 SQLAlchemy를 import하지 않는다.

## Git 컨벤션

### 커밋 메시지

`접두사: 영어 서술문` 형식. 서술은 무엇을 했는지가 아니라 왜 했는지가 드러나는 문장으로 쓴다.

| 접두사 | 용도 |
|---|---|
| add: | 새 기능·파일 추가 |
| edit: | 기존 동작 수정 |
| fix: | 버그 수정 |
| refactor: | 구조·설계 재작업. 동작 변경(큰 변경 포함)을 수반할 수 있다 |
| rm: | 삭제 |
| format: | 포맷팅만 변경 |

예:

- add: Stage placement validation before save
- fix: Problem fixed that progress was lost when the app was killed mid-stage
- refactor: Split stage loading out of the router into a service

### 커밋 분리

한 번에 여러 논리 단위를 지시받으면 논리 단위별로 커밋을 나눈다. API 추가, 기능 구현, 리팩토링은 서로 다른 커밋이다.

### 브랜치

- `main` — 안정 브랜치. 직접 push하지 않는다. 병합은 별도 지시가 있을 때만 한다.
- `develop` — 작업 브랜치. 일상 작업은 여기서 한다.

### 스테이징 위생

- `git add -A`를 습관적으로 쓰지 않는다. `git status --short`로 확인하고 커밋 단위에 해당하는 경로만 올린다.
- `.gitignore`에 `__pycache__/`, `*.py[cod]`, `.venv/`, `dist/`, `build/`, `*.egg-info/`, `.env`가 있는지 먼저 확인한다. 없으면 커밋 전에 만든다.
- `uv sync`가 `uv.lock`을 바꾸면 같은 커밋에 포함한다.

## Python 코드 컨벤션

### 타입 힌트

- 클래스 생성자 인자와 필드, 함수 인자와 반환에는 힌트를 붙인다. 반환값이 없으면 `-> None`은 생략한다.
- 지역 변수는 필요할 때만 붙인다.
  - 리스트 컴프리헨션 결과: 힌트 없음
  - `map`, `filter` 등 stdlib 반복자 호출 결과: 힌트 있음
  - 빈 컬렉션·제네릭·하위 타입 초기화: 힌트 있음
  - `a = get_value()`처럼 피호출 함수에 이미 타입이 있는 경우: 힌트 없음
- `@property`, `@override`에는 명시적으로 붙인다.
- 판단이 애매하면 "PyCharm에서 하이라이팅과 자동완성이 동작하는가"를 기준으로 한다.
- 유니언은 PEP 604. `X | None`을 쓰고 `Optional[X]`를 쓰지 않는다.
- `Any`를 최소화한다. JSON 파싱용 `dict[str, Any]`, `**kwargs: Any` 같은 자리는 허용한다.
- 자주 쓰는 구조 타입은 `Protocol` 클래스 대신 공용 타입 유니언으로 선언한다. Python 3.14이므로 PEP 695 `type` 문을 쓰고, `from __future__ import annotations`는 쓰지 않는다.

### 데이터 모델

- 데이터 묶음은 `@dataclass`로 만들고, 컬렉션 필드는 `field(default_factory=list)`로 초기화한다.
- **목록 역할 필드에 `tuple`을 쓰지 않는다.** `tuple`은 고정 구조의 속성 묶음에만 쓴다.
- 불변 dataclass는 값을 고치지 않고 새 인스턴스를 반환한다.
- ORM 모델, 도메인 모델, API 스키마는 서로 다른 타입이다. 한 클래스로 겸용하지 않는다.

### 예외

- 예외 클래스는 한 줄로 정의한다.

```python
class StageNotFoundException(Exception): ...
```

- 도메인 예외는 `domain/`에 두고, FastAPI 예외 핸들러에서 HTTP 상태로 매핑한다. 라우터에서 `HTTPException`을 직접 던지지 않는다.
- 감싸서 다시 던질 때는 원인 예외를 유지한다.

### 비동기

- 엔드포인트, 서비스, DB 접근은 전부 `async def`로 쓴다.
- 블로킹 호출은 `asyncio.to_thread`로 넘긴다. 이벤트 루프에서 직접 호출하지 않는다.
- 외부 HTTP 호출은 `httpx.AsyncClient`를 쓴다. `requests`를 쓰지 않는다.
- DB 세션은 요청 단위로 열고 닫는다. 전역 세션을 재사용하지 않는다.
- 주기 작업은 lifespan에서 띄우고 종료 시 정리한다.

### 로깅

- 모듈 로거는 `_logger = logging.getLogger(__name__)`로 만든다.
- `print`를 남기지 않는다.

### import

- 패키지 바깥에서 import할 때는 그 패키지 `__init__.py`의 `__all__`에 있는 이름만 가져온다. 예외 없다.
- 같은 패키지·도메인 안에서는 상대 import를 쓴다. `..`가 3번 이상 반복되면 절대 import로 바꾼다.
- 도메인을 넘어갈 때는 최상위 패키지부터 시작하는 절대 import를 쓴다.

### 포맷

- 4칸 들여쓰기.
- 한 줄에 들어가면 한 줄로 쓴다.
- 여러 줄로 나눌 때는 여는 괄호 뒤에서 줄바꿈하고, 항목마다 자기 줄을 쓰고, **닫는 괄호는 반드시 자기 줄에 둔다.** 마지막 항목 뒤 콤마(trailing comma)는 쓰지 않는다.

```text
download(
    one,
    two,
    three
)
```

다음 형태는 쓰지 않는다.

```text
download(
         one, two, three)
```

### 주석과 문서

- 주석과 README를 채워 넣지 않는다. 비직관적인 계약만 짧은 영어 주석 한 줄로 남긴다.
- README는 비워 둔다.
- 지시받지 않은 리팩토링, 부가 기능, 문서를 함께 넣지 않는다.

### FastAPI·DB 관례

- 응답 스키마는 `api/schemas.py`에 두고 ORM 모델을 그대로 반환하지 않는다. ORM 객체에서 직렬화할 때는 `model_config = ConfigDict(from_attributes=True)`를 쓴다.
- DB 세션은 dependency로 주입한다. `async_sessionmaker`를 기반으로 한다.
- SQLAlchemy는 2.0 스타일(`Mapped[...]`, `mapped_column`)로 쓴다.
- 스키마 변경은 반드시 Alembic 마이그레이션으로 남긴다. 수동 DDL을 쓰지 않는다.

## 미정 사항

- 프론트엔드와의 통신 규약(경로 규칙, 에러 응답 형식)
- 인증과 기기 식별 방식
- 배포 방식
- lint 설정에서 여러 줄 import 블록의 마지막 콤마를 허용할지
