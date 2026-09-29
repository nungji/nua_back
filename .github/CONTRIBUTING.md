# 브랜치 네이밍

브랜치 이름 규칙만 이 문서에 둔다. 이슈·PR·커밋 규칙은 `AGENT.md` 를 본다.

브랜치 이름은 `<prefix>/<작업내용>` 형식이다.

| prefix | 용도 |
|---|---|
| `feature/...` | 기능 추가 |
| `fix/...` | 문제·버그 수정 |
| `refactor/...` | 구조를 크게 바꾸는 작업 (기술 스택 변경, 전반적인 구조 변경) |
| `rm/...` | 기능이나 요소 제거 |

- 작업내용은 그 브랜치가 무엇을 하는지 알 수 있게 영문 kebab-case 로 쓴다. 예: `feature/level-editor-snap`, `fix/marble-tunnel-through-track`
- **브랜치 이름에 번호를 넣지 않는다.** 이슈 번호는 브랜치가 아니라 PR 본문의 `Closes #이슈번호` 로 연결한다. `feature/#12`, `feature/12-level-editor` 같은 이름은 쓰지 않는다.
- 브랜치는 `main` 에서 따고, 작업이 끝나면 `main` 방향으로 PR 을 연다.
