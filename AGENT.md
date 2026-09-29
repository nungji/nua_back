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
| ASGI 서버 | uvicorn |
| DB | PostgreSQL |
| DB 드라이버 | asyncpg |
| ORM | SQLAlchemy 2.x (async) |
| 마이그레이션 | Alembic (async 템플릿) |
| 스키마·검증 | Pydantic v2 |
| 설정 로딩 | python-dotenv + 설정 dataclass |
| DI | dependency-injector |
| 로깅 | reger |

이 외의 스택은 아직 확정되지 않았다. 새 라이브러리를 추가하기 전에 먼저 확인받는다.

```bash
uv sync
cp .env.example .env           # DATABASE_URL 등 채운다
uv run nua                     # 개발 실행 (uvicorn, /health)
uv run alembic upgrade head    # 마이그레이션 적용
docker compose up --build      # api + postgres (테스트 DB)
```

## 디렉터리 구조

```text
nua_back/
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── migrations/          # Alembic (async)
├── tests/
└── src/nua/
    ├── __init__.py      # main() 진입점
    ├── __main__.py      # main() 호출
    ├── config.py        # 설정 dataclass + .env 로딩
    ├── root_container.py # dependency-injector 컨테이너
    ├── bootstrap.py     # 로깅 셋업, 컨테이너 wiring, uvicorn 구동
    ├── app.py           # create_app(): FastAPI 생성, lifespan, 미들웨어, 라우터·핸들러 등록
    ├── api/
    │   ├── dependencies.py # 요청 단위 DB 세션 의존성
    │   ├── errors.py    # 도메인 예외 → HTTP 상태 매핑
    │   ├── schemas.py   # Pydantic 요청·응답 모델
    │   └── routes/      # 도메인별 라우터
    ├── domain/          # 도메인 모델, enum, 도메인 예외 (DB·HTTP 무관)
    ├── db/
    │   ├── base.py      # DeclarativeBase
    │   ├── models/      # 도메인별 ORM 매핑
    │   └── session.py   # async engine, sessionmaker
    └── services/        # 유스케이스 (라우터와 DB 사이)
```

규칙:

- 패키지명은 `nua`, 소스 루트는 `src/nua`.
- **도메인 단위로 파일을 나눈다.** 도메인이 늘면 `domain/<도메인>.py`, `api/routes/<도메인>.py`, `services/<도메인>.py`, `db/models/<도메인>.py`가 함께 늘어난다. 계층별로 한 파일에 몰아넣지 않는다.
- **enum을 중앙 `enums.py`에 모으지 않는다.** 해당 도메인 파일 안에 정의한다. 조회용 매핑 표가 필요하면 모듈 최상단 dict를 만들지 말고 enum 속성으로 붙인다.
- 라우터는 HTTP만 담당한다. 검증·계산·DB 접근은 service로 내린다.
- `domain/`은 FastAPI와 SQLAlchemy를 import하지 않는다.

## 부팅과 DI

부팅 구조는 piepy와 같은 형태를 쓴다.

1. `main()`이 `RootContainer`를 만들고 `Bootstrapper`에 넘긴다.
2. `Bootstrapper.run()`이 `asyncio.run(arun())`으로 흐르고, `arun()`이 로깅 셋업 → 컨테이너 wiring → uvicorn 구동 순서로 진행한다.
3. `__main__.py`는 `main()`만 호출한다.

- 컨테이너에는 앱 수명 동안 하나면 되는 것(config, engine, session_maker)만 싱글턴으로 둔다. 라우터와 서비스는 컨테이너에 넣지 않는다.
- 앱 인스턴스는 `app.create_app()`이 만들고, lifespan에서 엔진을 정리한다.
- 라우터에서 DB 세션을 받을 때는 `api/dependencies.py`의 `get_session`을 쓴다.

```python
async def get_stage(session: Annotated[AsyncSession, Depends(get_session)]):
    ...
```

- `get_session`은 `@inject`와 `Depends(Provide[...])`로 컨테이너에서 sessionmaker를 받는다. 컨테이너 wiring은 부팅에서 한 번만 한다. 라우터에 `Provide[...]`를 직접 쓰지 않는다.

## 도구

- lint는 `uv run ruff check .`. `ruff format`은 아래 미정 사항 참고.
- 테스트는 `uv run pytest`. DB가 필요한 테스트는 compose의 Postgres를 쓴다.
- 로컬 실행은 `docker compose up --build`로 api와 db를 함께 띄운다. 백엔드만 볼 때는 `uv run nua`.
- compose의 환경변수는 `${VAR:-기본값}` 형식이다. `.env`나 셸 환경에 값이 있으면 그 값을 쓰고, 없으면 기본값으로 뜬다. `DATABASE_URL`만은 컨테이너 안에서 `db` 호스트로 붙어야 해서 compose가 조립한다(`POSTGRES_*`는 `.env` 값을 따른다).
- `/openapi.json`과 `/docs`가 기본으로 열린다. 프론트엔드 타입은 `/openapi.json`에서 생성한다.

## Git 컨벤션

### 커밋 메시지

`접두사: 한글 서술문` 형식. 접두사는 아래 표의 영어를 그대로 쓰고, 서술은 한글로 쓴다. 서술은 무엇을 했는지가 아니라 왜 했는지가 드러나는 문장으로 쓴다.

| 접두사 | 용도 |
|---|---|
| add: | 새 기능·파일 추가 |
| edit: | 기존 동작 수정 |
| fix: | 버그 수정 |
| refactor: | 구조·설계 재작업. 동작 변경(큰 변경 포함)을 수반할 수 있다 |
| rm: | 삭제 |
| format: | 포맷팅만 변경 |

예:

- add: 스테이지 저장 전 배치 검증 추가
- fix: 스테이지를 하던 중 앱이 죽으면 진행도가 사라지던 문제 수정
- refactor: 라우터에 붙어 있던 스테이지 로딩을 서비스로 분리

### 커밋 분리

한 번에 여러 논리 단위를 지시받으면 논리 단위별로 커밋을 나눈다. API 추가, 기능 구현, 리팩토링은 서로 다른 커밋이다.

### 브랜치와 워크플로우

`main`이 주축이다. `develop`는 쓰지 않는다. 작업 단위마다 워킹 브랜치를 분리한다.

1. 시작할 작업 하나를 설명하는 GitHub 이슈를 만든다. `.github/ISSUE_TEMPLATE/`의 `feature request`, `problem` 템플릿을 쓴다.
2. `main`에서 그 이슈에 연결된 워킹 브랜치를 딴다. 이름은 `.github/CONTRIBUTING.md` 규칙(`<prefix>/<작업내용>`, 번호 없음)을 따른다.
3. 워킹 브랜치에서 작업을 마친 뒤 워킹 브랜치 → `main` 방향으로 PR을 연다. 본문에 `Closes #이슈번호`를 적는다.
4. **PR 머지는 사람이 직접 한다. 에이전트는 머지하지 않는다.**

`main`에 직접 push하지 않는다.

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
- 로깅 셋업은 부팅에서 한 번만 한다. `reger.setup_logging(level=logging.INFO)`로 루트 로거를 잡고, 파일 로그가 필요하면 루트 로거에 `reger.ColourFormatter()` 핸들러를 붙인다.
- **uvicorn은 `log_config=None`으로 띄운다.** uvicorn이 자체 로깅 설정을 하면 uvicorn·access 로그가 reger 핸들러와 따로 놀아 포맷이 두 벌이 된다. `None`이면 uvicorn 로그가 루트 로거로 올라와 포맷이 하나로 유지된다.
- `print`를 남기지 않는다. 부트스트랩에서 로깅 셋업 직전에 찍는 안내 한 줄만 예외다(그 시점에는 로거 설정이 없다).

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
- DB URL은 `.env`의 `DATABASE_URL` 하나로 관리하고 `postgresql+asyncpg://` 형식을 쓴다.
- 세션은 `async_sessionmaker(engine, expire_on_commit=False)`로 만들고 요청 단위로 연다.
- `alembic revision --autogenerate`가 도메인 매핑을 찾으려면 그 모듈이 import되어 있어야 한다. `migrations/env.py`가 `nua.db.models`를 import하므로, 새 매핑은 `db/models/__init__.py`에 올린다.
- 첫 리비전은 첫 도메인 매핑이 생길 때 만든다. 지금 `migrations/versions/`는 비어 있고 `alembic upgrade head`는 아무것도 하지 않는다.

## 미정 사항

- 프론트엔드와의 통신 규약(경로 규칙, 에러 응답 형식). 타입은 `/openapi.json`에서 생성하는 방향으로 확정.
- 인증과 기기 식별 방식
- 배포 방식
- `ruff format` 적용 여부. **설정으로는 해결되지 않는다(실측)** — 여러 줄로 쓴 호출·컬렉션을 한 줄로 합치고(`skip-magic-trailing-comma`를 켜도 `__all__` 섹션 구분 빈 줄이 사라진다), 여러 줄로 쪼갤 때 마지막 항목 뒤 콤마를 넣는다(끄는 옵션이 없다). `line-length`도 어느 쪽이 쪼개질지만 바꾼다. 그래서 (a) 포맷터를 받아들이고 포맷 절을 다시 쓰거나 (b) `ruff check`만 쓸지 정해야 한다. 지금은 (b)다.
- CORS 허용 origin. 지금은 `CORS_ORIGINS` 기본값이 `*`다.
