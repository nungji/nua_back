# AGENT.md — nua 백엔드

## 프로젝트

**nua** — 5세 유아의 지능 향상을 위한 게이미피케이션 앱. 팀 이름은 능지떡상이다.

하나의 앱 안에 **4개 범주의 미니게임**을 품는다. 게임마다 트랙이 다르지만 캐릭터와 아이덴티티는 공통으로 쓴다.

1. **도형·기하·배치 지능 — 수리공.** 마을이나 여러 장소에서 부서지거나 망가진 물건을 고쳐주는 Drag&Drop 조합 게임이다. 부서진 조각이 와르르 쏟아지면 설계도(실루엣)를 펼쳐 주고, 조각을 제자리에 놓을 때마다 딸깍 소리와 함께 조립되고 색이 입혀진다. 다 고치면 물건이 작동하는 모습을 보여주며 끝난다.
2. **분류·속성 파악 — 만물상.** 손님이 원하는 것을 말하면 거기에 맞는 물건을 골라준다. 예를 들어 꽃이 시든 다람쥐에게 물을 담아 갈 물건이 필요하다면 양동이를 줘야 꽃이 살아나고, 양말을 주면 물이 새서 손님이 시무룩해 하며 다시 돌아온다. 틀린 선택은 실패로 끝나지 않고 다시 고르게 한다.
3. **언어·글자 — 글자가 사라진 마을.** 마녀가 마을의 글자를 없앴다. 주인공은 유일한 타지인이고, 마을 사람의 요청을 받아 스테이지마다 자음·모음 하나를 되찾는다. 학습 플로우는 자모 하나를 가이드 따라 그리기 → 그 음절의 발음 듣기 → 발음 맞추기·읽기 → 가이드 없이 그리기 순서다. 모든 스테이지를 끝내면 마녀의 사연이 네컷 만화로 나온다.
4. **수리 능력 — 주문서.** 주문서에 시각적으로 적힌 항목(체리 5개, 사과 3개, 빵 4개…)에 맞게 바구니를 채운다. 나중에는 같은 물건이 2개·3개씩 묶여 나오고, 더 어려운 단계에서는 주문서가 숫자로 나온다.

- **메인 화면에서 4개 게임 중 하나를 골라 들어간다.** 게임을 고르는 화면과 개별 트랙 화면이 나뉜다.
- **초기 개발 범위는 주문서 게임이다.** 나머지 세 범주는 후순위다.
- **`reports`(부모용 리포트)는 메인 스트림 게임과 완전히 다른 트랙이고 후순위다.** 아이의 진행도와 오답을 스테이지 단위로 정리해 부모 모드에서 보여준다. 부모 모드는 계정을 분리하지 않고 같은 계정에서 버튼으로 전환한다.

### 디자인·UX 컨셉

- Kurzgesagt처럼 컬러풀하고 벡터 느낌의 귀여운 디자인. 기존 유아용 앱에서 많이 차용된 스타일이다.
- **글자 대신 그림 위주**로 표현한다.
- 컬러풀하되 사용자의 초점이 흔들리지 않도록 무게감을 조정한다.
- 아기자기하고 디테일한 효과음을 많이 넣는다. 효과음 작업은 후순위다.

### 타깃 사용자

사용자는 5세다. 다음이 전제다.

- 7 * 7 같은 계산은 하지 못한다.
- 보이는 것을 그대로 믿는다. 화면에 보이지 않는 상태 변화를 추론하지 않는다.
- 덧셈은 알아도 역연산을 모른다. 3+1=4는 알지만 4-3=1은 모른다.

따라서 **의사나 정보를 전달할 때는 그림·아이콘 기반**으로 하고 글자는 약간의 보조 텍스트만 쓴다. 다만 **문제의 난이도와 직접 관계된 부분에서는 소량의 글자·숫자를 쓸 수 있다**(주문서에 적힌 숫자나 학습 대상인 자모처럼 그 자체가 문제인 경우). 응답 지연은 곧 "게임이 멈췄다"로 읽힌다. 백엔드는 응답을 짧게 유지하고, 실패를 조용히 삼키지 않는다.

### 팀

| 이름 | 역할 |
|---|---|
| 김주연 | 디자인, 캐릭터 디자인 |
| 곽영빈 | 프론트엔드 개발, 세부 UX 개발, 백엔드 리뷰 |
| 전지원 | 백엔드 주 개발 |

### 백엔드가 맡는 것 (문서 기준, 확정 전)

- 스테이지 데이터 제공 — 게임별 스테이지 구성(주문서 항목, 조각과 설계도, 고를 수 있는 물건 목록, 자모 스테이지)
- 플레이 진행도와 결과 저장
- 메인 스트림은 계정과 로그인을 전제하지 않는다. 기기 단위 식별자를 기본으로 본다.
- `reports`(부모용 리포트) 트랙은 스테이지 단위 진행도와 오답 분석을 부모 모드에 제공한다. **후순위**이고 계정을 전제하므로 붙이는 시점에 인증 방식을 정한다.

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
| 스키마 생성 | 기동 시 `Base.metadata.create_all` |
| 스키마·검증 | Pydantic v2 |
| 설정 로딩 | python-dotenv + 설정 dataclass |
| DI | dependency-injector |
| 로깅 | reger |

이 외의 스택은 아직 확정되지 않았다. 새 라이브러리를 추가하기 전에 먼저 확인받는다.

```bash
uv sync
cp .env.example .env           # DATABASE_URL 등 채운다
uv run nua                     # 개발 실행 (uvicorn, /health)
docker compose up --build      # api + postgres (테스트 DB)
```

## 디렉터리 구조

```text
nua_back/
├── pyproject.toml
├── uv.lock
├── .env.example
├── Dockerfile
├── docker-compose.yml
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

- 린터·포맷터 도구를 두지 않는다. 포맷은 아래 코드 컨벤션의 포맷 절 규칙을 손으로 맞춘다.
- 테스트는 `uv run pytest`. DB가 필요한 테스트는 compose의 Postgres를 쓴다.
- 로컬 실행은 `docker compose up --build`로 api와 db를 함께 띄운다. 백엔드만 볼 때는 `uv run nua`.
- compose의 환경변수는 `${VAR:-기본값}` 형식이다. `.env`나 셸 환경에 값이 있으면 그 값을 쓰고, 없으면 기본값으로 뜬다. `DATABASE_URL`만은 컨테이너 안에서 `db` 호스트로 붙어야 해서 compose가 조립한다(`POSTGRES_*`는 `.env` 값을 따른다).
- `/openapi.json`과 `/docs`가 기본으로 열린다. 프론트엔드 타입은 `/openapi.json`에서 생성한다.

## Git 컨벤션

브랜치·커밋·이슈·PR 규칙과 워크플로우는 `.github/CONTRIBUTING.md` 에 있다. 그 문서를 따른다. 여기에는 에이전트가 항상 지켜야 하는 것만 둔다.

- 커밋은 `접두사: 한글 서술문` 형식이고, 접두사는 `add:` `edit:` `fix:` `refactor:` `chore:` `rm:` `format:` 중 하나다.
- 한 번에 여러 논리 단위를 지시받으면 논리 단위별로 커밋을 나눈다.
- PR 의 base 는 가능한 `main` 으로 한다. `main` 이 아니면 본문이나 이슈에 밝힌다.
- **PR 의 최종 머지는 언제나 사람이 한다. 에이전트는 머지하지 않는다.**
- `main` 에 직접 push하지 않는다.
- 시크릿(API 키·토큰·비밀번호)을 커밋하지 않는다. 값은 `.env` 에만 둔다.

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
- 스키마는 `db/models/`의 매핑이 정본이다. 손으로 DDL을 치지 않는다.
- DB URL은 `.env`의 `DATABASE_URL` 하나로 관리하고 `postgresql+asyncpg://` 형식을 쓴다.
- 세션은 `async_sessionmaker(engine, expire_on_commit=False)`로 만들고 요청 단위로 연다.
- 테이블은 기동할 때 lifespan에서 `Base.metadata.create_all`로 만든다. 새 매핑은 `db/models/<도메인>.py`에 두고 `db/models/__init__.py`에서 import한다(`app.py`가 `nua.db.models`를 import해 metadata에 등록한다).
- `create_all`은 없는 테이블만 만든다. 이미 있는 테이블의 컬럼 변경·삭제는 반영되지 않는다. 지금은 그때 다시 만드는 것으로 둔다.
- DB에 붙지 못하면 기동이 실패한다. 조용히 넘어가지 않는다.

## 미정 사항

- 프론트엔드와의 통신 규약(경로 규칙, 에러 응답 형식). 타입은 `/openapi.json`에서 생성하는 방향으로 확정.
- 인증과 기기 식별 방식
- 배포 방식
- 린터·포맷터 도구 도입 여부. 지금은 없다(포매터가 포맷 절 규칙과 충돌해서 제거했다).
- CORS 허용 origin. 지금은 `CORS_ORIGINS` 기본값이 `*`다.
- 마이그레이션 도구 도입 시점. 지금은 기동 시 `create_all`로 만든다.
