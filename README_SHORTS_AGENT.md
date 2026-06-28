# 쇼핑 쇼츠 자동화 AI 에이전트 (`shorts_agent`)

상품을 골라 → 후킹 대본을 쓰고 → 보이스오버·자막을 입혀 → 9:16 쇼츠를 만들고 → 유튜브에 올리는
**반자동(+옵션상 무인) 파이프라인.** 설계 근거와 정책/법규 배경은 [`SHOPPING_SHORTS_AGENT_SPEC.md`](./SHOPPING_SHORTS_AGENT_SPEC.md) 참고.

> 핵심 철학(명세 0): **"양산"이 아니라 "전환되는 고품질 쇼츠를 정책 안에서 지속 발행".**
> 그래서 ① 포맷 로테이션 + 유사도 검사로 *양산 신호*를 막고, ② 발행 전 *컴플라이언스 게이트*(공정위 표시·합성공개)를 강제하며, ③ 기본은 *사람 검수 게이트*를 둔다.

---

## 빠른 시작 (키 없이 바로 시연 — DRY-RUN)

키가 하나도 없어도 **실제 FFmpeg 로 .mp4 를 끝까지 생성**합니다(외부 API는 mock, 음성은 무음+타이밍).

```bash
pip install imageio-ffmpeg                 # dry-run 은 이거 하나면 충분
python -m shorts_agent --dry-run run --seeds "주방,청소,뷰티,수납정리,생활가전" --count 5 --auto
ls output/                                 # <job_id>.mp4 + <job_id>.meta.json 생성
```

- 폰트: `assets/fonts/NanumGothic.ttf` (한국어 자막용, 저장소에 포함).
- 산출물: `output/<job_id>.mp4` (9:16, 자막+공정위 표시 인트로 포함), `output/<job_id>.meta.json` (업로드될 제목/설명/딥링크/해시태그).

---

## 명령어

| 명령 | 설명 |
|---|---|
| `run --seeds "a,b" --count N [--auto]` | 일일 배치. `--auto` 면 게이트 없이 무인 발행 |
| `list` | 잡 목록/현재 단계 |
| `show <job_id>` | 대본·경로 등 상세 |
| `gate-a <job_id> [--reject]` | 🚦 상품·후킹 승인 → 통과 시 제작(에셋·보이스·렌더·자막) 후 GATE_B |
| `gate-b <job_id> [--reject]` | 🚦 최종 검수 승인 → 컴플라이언스 통과 시 업로드 |

상태는 `output/state.json` 에 저장되어 게이트 승인이 여러 번의 호출에 걸쳐 동작합니다.

### 반자동(권장) 흐름
```bash
python -m shorts_agent run --seeds "주방,청소,뷰티" --count 5   # GATE_A 에서 정지
python -m shorts_agent gate-a <job_id>                          # 상품·후킹 OK → 영상 제작
python -m shorts_agent gate-b <job_id>                          # 최종 30초 검수 → 발행
```

---

## 💸 무자본(무료) 구성 — 0원으로 실제 발행까지

| 부품 | 무료 선택 | 비용 |
|---|---|---|
| 두뇌(대본) | **Google Gemini** 무료 키 (aistudio.google.com) | 0원(무료 티어) |
| 목소리 | **edge-tts** (`TTS_PROVIDER=edge`, 키 불필요) | 0원 |
| 상품/딥링크 | 쿠팡파트너스 **수동** 딥링크(사이트에서 생성) 또는 API(승인 시) | 0원 |
| 영상 소재 | **본인 촬영**(`assets/products/`) 또는 Pexels 무료 키 | 0원 |
| 배경음악 | 유튜브 스튜디오 **오디오 보관함**(무료) → `assets/music/` | 0원 |
| 렌더링 | FFmpeg(내장) | 0원 |
| 업로드/트렌드 | YouTube Data API(무료 할당량) | 0원 |

**무자본 빠른 시작:**
```bash
pip install -r requirements.txt
cp .env.example .env
#  .env 에 GEMINI_API_KEY 만 넣으면 끝(나머지는 무료 기본값/수동).
#  TTS_PROVIDER=edge (기본), 상품은 수동 딥링크로 시작.
python -m shorts_agent run --seeds "주방,뷰티" --count 3      # 반자동(게이트 검수)
```
> Gemini 키 하나만 있어도 실모드로 동작합니다(쿠팡 API·음성 키 불필요).
> 쿠팡 API 가 아직 승인 안 났으면: 파트너스 사이트에서 상품별 딥링크를 직접 만들어
> 영상 설명/고정댓글에 붙이세요(시스템은 영상·자막·썸네일·업로드를 담당).

## 실모드(실제 API 연동)

```bash
pip install -r requirements.txt
cp .env.example .env      # 값 채우기
python -m shorts_agent run --seeds "주방,청소,뷰티" --count 5
```

필요 키(`.env`): `COUPANG_ACCESS_KEY/SECRET_KEY`(상품·딥링크), `ANTHROPIC_API_KEY`(대본),
`ELEVENLABS_API_KEY/VOICE_ID`(음성), `PEXELS_API_KEY`(보조 컷), `YOUTUBE_TOKEN_FILE`(업로드).
**일부만 채워도** 해당 모듈만 실제로 동작하고 나머지는 자동으로 mock 으로 폴백합니다(점진적 도입).

> YouTube 업로드 OAuth 토큰(`YOUTUBE_TOKEN_FILE`)은 `google-auth-oauthlib` 로 최초 1회
> 동의 후 발급한 authorized-user json 을 사용합니다. 스코프: `youtube.upload`.

### 실제 제품 소재 연결 (전환의 핵심!)
스톡엔 특정 제품 영상이 없습니다. **직접 촬영/제조사 제공 소재**를 폴더에 넣으면 최우선 사용됩니다.
```
assets/products/<상품키>/clip1.mp4, photo1.jpg   # 상품키=상품명 일부 또는 product_id (없으면 _default)
assets/broll/                                     # 공용 보조 컷
```
우선순위: **로컬 제품 소재 → 로컬 b-roll → (있으면)Pexels → 움직이는 그라데이션**.

### YouTube 업로드 토큰 발급
```bash
# Google Cloud: 프로젝트 → YouTube Data API v3 사용 → OAuth 클라이언트(데스크톱) → client_secret.json
python -m shorts_agent.auth_youtube client_secret.json youtube_token.json
# → .env 에 YOUTUBE_TOKEN_FILE=youtube_token.json
```

---

## 아키텍처 (모듈 = 교체 가능)

```
research(쿠팡) → script(LLM, 포맷로테이션+유사도) → [GATE A]
  → asset(제품컷+Pexels보조) → voice(ElevenLabs) → render(FFmpeg) → caption(libass, 안전영역)
  → [컴플라이언스 자동검증] → [GATE B] → upload(YouTube, 표시문구/합성공개 자동) → feedback
```

- `shorts_agent/providers/base.py` — 추상 인터페이스(8개 모듈).
- `shorts_agent/providers/*.py` — 실제 구현(`coupang/llm/pexels/tts/render/caption/youtube/feedback`) + `mock.py`.
- `shorts_agent/pipeline.py` — 오케스트레이터(게이트·재시도·일일 캡·양산방지·컴플라이언스).
- `shorts_agent/factory.py` — 설정에 따라 실/mock 프로바이더 조립.

### 양산 방지(유튜브 비진정성 정책 대응)
- **포맷 로테이션**: `질문형/실측형/비교형/실패담형/정보형/리액션형` 을 매 영상 순환.
- **유사도 검사**: 직전 20개 후킹과 코사인 유사(토큰 Jaccard+시퀀스) 임계 초과 시 포맷 바꿔 재생성, 발행 전 재검사.

### 동적 영상 엔진(끌리는 퀄리티)
- **모션 배경**: 이미지는 켄번스(줌인), 제품 이미지는 *블러 배경 + 선명한 제품 카드* 쇼케이스,
  소스가 없으면 *움직이는 그라데이션*(정적 컬러 금지). 컷 사이 **xfade 트랜지션** + 비네팅/채도 보정.
- **CapCut 풍 동적 자막**: 나레이션 단어 타임스탬프에 맞춘 **카라오케 하이라이트**(현재 단어가
  노란색으로 채워짐) + 등장 팝(scale) 애니메이션. 후킹은 더 크게, CTA는 컬러 팝.
- **배경음악**: `assets/music/` 에 라이선스 안전 음원을 넣으면 영상별 자동 선택 + 나레이션 아래로 덕킹.
  ⚠️ 음원은 직접 확보해야 합니다(저작권). dry-run 에는 음악 없음.

### 바이럴 자기학습 루프 (`learn`)
같은 니치의 **잘 터진 경쟁 쇼츠**를 분석해 다음 영상에 반영합니다.
```bash
python -m shorts_agent learn --seeds "주방,청소,뷰티"   # → output/trends.json
python -m shorts_agent run   --seeds "주방,청소,뷰티" --count 5   # trends 자동 반영
```
- YouTube Data API(`YOUTUBE_API_KEY`, OAuth 불필요)로 최근 N일 쇼츠를 **조회속도/참여율**로 랭킹 →
  제목·태그·제품을 LLM 이 분석해 `winning_hooks / hot_products / hot_categories / angles` 추출.
- `run` 이 이를 **상품 시드 보강 + 대본 후킹/앵글 힌트**로 사용(복붙 아님, 구조만 흡수).
- ⚠️ 한계: 남의 영상의 **실제 수익·시청지속률은 비공개**라 조회수×참여도로 *추정*. 화면(편집) 자동분석은 미포함.

### 사람이 만든 티 — 자연스러움 루프 + 스타일 학습
- **자연스러움 자기검열**(`NATURALNESS_PASS=true`): 대본 생성 후 LLM 이 'AI 티(만연체·광고체·번역투)'를
  스스로 잡아 **사람 구어체로 재작성**.
- **스타일 학습**: `assets/style_profile.json`(예시: `style_profile.example.json`)에 채널 말투/레퍼런스
  톤을 적어두면 생성·재작성에 조건으로 주입 → 점점 당신 취향에 수렴.
- ❗ 진짜 '사람이 만든 티'의 결정적 요소는 **실제 촬영 화면**입니다(아래 한계 참고). 자연스러움 루프는
  대본·말투를, 실소재(`assets/products/`)는 화면을 담당합니다 — 둘 다 있어야 완성.

### 고도화 기능
- **특색 상품 LLM 큐레이션**: Anthropic 키가 있으면 후보 풀을 '신박/화제성/전환' 기준으로
  LLM 이 재선별(`curation.py`). 없으면 휴리스틱(신박 키워드·저관여 가산)으로 동작.
- **자동 썸네일**: 후킹 문구가 박힌 세로 커버(`<id>.thumb.jpg`) 생성, 업로드 시 자동 설정.
- **성과 피드백 루프**: `performance.json`(또는 YouTube Analytics 실연동)에서 포맷·카테고리별
  가중치를 계산해 **다음 배치의 상품 순위·후킹 포맷 선택에 반영**(승자 패턴 강화).
- **한국어 TTS 선택**: `TTS_PROVIDER=elevenlabs|clova|typecast`. 한국어 억양은 CLOVA/Typecast 권장.

### 컴플라이언스 게이트(발행 전 강제)
- 공정위 표시문구 **존재 + 위치(제목/설명 첫 줄/인트로 0~2.5초 자막)** 자동 삽입.
- **모호·조건부 표현 금칙어** 차단(예: "수수료를 지급받을 수 있음").
- YouTube **합성/변경 콘텐츠 공개** 플래그(`containsSyntheticMedia=True`).

---

## 매일 5개 지속 발행 (스케줄링)

`videos.insert` 할당량은 2025.12.4 이후 ≈100유닛(하루 ~100개 가능)이라 **API 가 5개를 제한하지 않습니다.**
"5개"는 품질·정책·전환을 위한 전략 캡(`DAILY_CAP`)입니다. 할당량 리셋은 **태평양시(PT) 자정** 기준이니 그에 맞춰 cron 을 거세요.

예) 매일 KST 09:00 에 배치 생성(반자동: GATE_A 까지) — crontab:
```cron
0 9 * * *  cd /path/to/repo && /usr/bin/python3 -m shorts_agent run --seeds "주방,청소,뷰티,수납정리,생활가전" --count 5 >> output/cron.log 2>&1
```
완전 무인으로 굴리려면 `--auto` 를 붙이되, **유튜브 비진정성/공정위 리스크를 본인이 감수**해야 합니다. 초기에는 반자동(사람 30초 검수)을 강력 권장합니다.

---

## 한계 / 다음 단계 (정직한 고지)
- **에셋이 진짜 병목**(명세 1-3): 스톡엔 *특정 제품* 영상이 없습니다. 전환을 내려면 제조사 제공 소재나
  직접 촬영 컷을 `AssetProvider` 에 연결해야 합니다. 현재 보조 컷만 Pexels, 제품 컷은 상품 이미지/플레이스홀더.
- **음성**: dry-run 은 무음(타이밍만). 실모드에서 ElevenLabs(또는 CLOVA/Typecast 로 교체) 연결 필요.
- **피드백 루프(모듈 H)**: 현재 로컬 집계 골격. YouTube Analytics + 쿠팡 실적 연동은 `feedback.py` 의 TODO.
- **드라마틱한 편집(전환/줌/효과)**: 현재는 컷 분할+자막 중심. 트랜지션/모션은 렌더러 확장 포인트.
