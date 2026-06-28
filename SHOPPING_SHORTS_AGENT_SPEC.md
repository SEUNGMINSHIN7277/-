# 쇼핑 쇼츠 자동화 AI 에이전트 — 개발 명세서 (v3, 웹 검증판)

> 작성일 기준: 2026-06. 원본 명세서를 참고하되, **2025~2026년 유튜브 정책·쿠팡파트너스 구조·공정위 법규·API 현실을 웹 리서치로 검증·갱신**해 재설계한 문서입니다.
> 목표: 쇼핑 쇼츠를 **하루 약 5개, 지속적으로** 발행하면서 **채널이 죽지 않고(수익화 유지)**, **실제 구매 전환으로 돈을 버는** 시스템.

---

## 0. 가장 먼저 — 현실 점검 (이걸 모르고 만들면 100% 망함)

원본 명세서의 컨셉(완전 자동 + 동일 템플릿 + 하루 5개)은 2025~2026년 기준으로 **가장 빠르게 채널이 정지·비수익화되는 조합**입니다.

### 0-1. 유튜브 '비진정성 콘텐츠' 정책 (2025.7.15 시행) — 최대 리스크
- '반복 콘텐츠(repetitious)' → **'비진정성 콘텐츠(inauthentic)'**로 정책명 변경 및 단속 강화. (이전부터 비수익 대상이었으나 정의를 명확화)
- 금지 대상으로 명시된 예시:
  - **템플릿으로 제작되어 영상 간 변화가 거의 없는** 콘텐츠
  - **대규모로 쉽게 복제 가능한(easily replicable at scale)** 콘텐츠
  - 나레이션·해설 없는 이미지 슬라이드쇼·낮은 교육적 가치의 반복물
  - **일반 템플릿으로 만든 AI 생성물 중 창작자의 고유한 통찰·관점이 없는 것**
- **핵심 함정: 채널 단위 적용.** 위반 영상이 일부만 있어도 **채널 전체 수익화가 박탈**될 수 있음.
- **AI 자체는 금지 아님.** 판정 기준은 **"평균 시청자가 영상끼리 사실상 복제본임을 알아챌 수 있는가."** 각 영상의 *실질(substance)이 유의미하게 달라야 함(materially varied).*
- 참고: commentary/clips/compilation 등 '재사용(reused) 콘텐츠' 정책은 이번 변경에 영향 없음.

> **결론:** "JSON 템플릿에 변수만 갈아끼우는 양산"은 정책 정의 그대로의 위반 패턴. 자동화의 목표는 *양산*이 아니라 *고품질 제작의 가속*이어야 함.

### 0-2. ⚠️ 중요 정정 — "하루 5개" 제약은 더 이상 API 때문이 아니다
- **`videos.insert` 할당량이 1,600유닛 → 약 100유닛으로 인하됨(2025.12.4).** 또한 프로젝트당 **하루 100건의 videos.insert 호출**이 별도 버킷으로 배정됨.
- 즉, **API상으로는 하루 ~100개 업로드도 가능**. 과거 명세서의 "API 때문에 하루 6개가 한계"라는 전제는 **현재 무효**.
- **그럼에도 하루 5개로 캡을 두는 이유는 정책·품질·전환 효율 때문**이다. 양산은 0-1 정책 위반으로 직결되므로, "5개"는 *기술 한계가 아니라 전략적 선택*으로 재정의한다.
- 단, `search.list`는 여전히 **1콜당 100유닛**(검색은 별도로 하루 100콜 버킷). 시장조사 검색 남발 금지 → **캐싱 필수**. 할당량 리셋은 **태평양시(PT) 자정** 기준.

### 0-3. 쇼핑 콘텐츠로 돈 버는 진짜 구조 = 조회수가 아니라 '전환'
- 쿠팡파트너스 수수료는 **클릭이 아닌 '구매' 기준.** 강력한 장점: 사용자가 **내 링크 클릭 후 쿠팡에서 산 (추천 안 한 것 포함) 모든 상품**이 일정 기간 수익 대상.
- KPI는 `조회수`가 아니라 **`링크 클릭률(CTR) × 구매 전환율 × 객단가`**.
- 실전 핵심: **제품을 직접 사거나 빌려 직접 촬영하지 않으면, 스톡·AI만으로 전환 내기 매우 어렵다.** → **에셋(제품 실증 영상) 확보가 시스템의 진짜 병목.**

### 0-4. 그래서 설계 원칙
1. **완전 자동(X) → 반자동 + Human-in-the-loop 게이트(O).** 발행 직전 사람이 30초 검수.
2. **양산형 동일 템플릿(X) → 템플릿 풀 로테이션 + 영상별 실질 차별화(O).**
3. **조회수 최적화(X) → 전환 최적화(O).** 후킹·실증·CTA·번들에 집중.
4. **먼저 손으로 검증(Phase 0) → 그 다음 자동화.** 사람이 만들어도 안 팔리는 포맷은 자동화해도 안 팔림.

---

## 1. 수익 구조 — 어디서, 어떻게 돈이 나오는가

### 1-1. 수익 채널 두 가지
| 경로 | 설명 | 자격 조건 (2026 기준) |
|---|---|---|
| **설명란/고정 댓글 링크** | 쿠팡파트너스 딥링크를 영상 설명·고정 댓글에 삽입 | 자격 제한 없음 (초기엔 이것부터 시작) |
| **유튜브 쇼핑 제휴(인-비디오 제품 태그)** | 영상에 쿠팡 제품을 직접 태그, 앱 이탈 없이 바로 구매 | **YPP 가입 + 채널 구독자 요건.** 한국 쿠팡 연동 요건은 **2026.3월 기준 구독자 약 500명 이상으로 완화**(과거 1만명에서 하향). 단 음악/아동 채널 등 제외 조건 있음 |

- **단계 전략:** 초기에는 *설명란/고정 댓글 딥링크*로 시작 → 구독자/수익화 요건 충족 시 *인-비디오 제품 태그*로 확장.
- 쿠팡 수수료율은 카테고리·정책에 따라 변동(통상 한 자릿수 %, 소스마다 차이). **정확한 현재 요율·정산 조건은 발행 시점 쿠팡파트너스 공식 정책으로 재확인**할 것.

### 1-2. 전환을 만드는 핵심 레버 (= 시스템이 최적화할 대상)
1. **초반 3초 후킹** — 스와이프 이탈 방지. 정보 격차 / 패턴 인터럽트 / 두괄식.
2. **제품 실증** — Before/After, 사용 장면, 실측. *스톡으로는 거의 불가 → 1-3 참고.*
3. **명확한 CTA** — "댓글 링크 / 제품 태그 눌러서 확인" 행동 유도.
4. **다상품 번들** — 메인 1개 + 함께 쓰는 보조 상품. 클릭 후 모든 구매 집계 → 객단가↑.
5. **카테고리 선정** — 저관여·소액·반복구매 품목이 전환 쉬움. 수수료율·구매빈도·계절성 고려.

### 1-3. 에셋(제품 영상) 확보 전략 — 시스템의 진짜 병목
스톡(Pexels/Pixabay)에는 **특정 제품 영상이 없다.** 소스 전략을 계층화:
1. **(권장) 제조사/판매자 제공 소재** — 상세페이지 이미지·공식 영상의 사용 허락 확보. 가장 안전.
2. **직접 촬영** — 소액 제품을 실제 구매해 10~20초만 촬영. 차별화·신뢰도·정책 안전성 최고.
3. **AI 생성 보조 컷** — 배경·전환·분위기 컷만. 제품 자체는 1·2번으로.
4. **(주의) 타인 영상 재사용** — 저작권/재사용 정책 위반 위험. 단독 사용 금지.

> 시스템은 "**제품 컷(고유)** + **보조 컷(스톡/AI)** + **나레이션(고유 대본)**"을 조합해 *영상별 실질 차별화*를 자동 확보한다.

---

## 2. 반드시 지켜야 할 컴플라이언스 (위반 시 채널·법적 리스크)

### 2-1. 공정위 표시·광고 심사지침 (2024.12.1 개정 시행) — 한국 법규
- 쿠팡파트너스 등으로 수익 발생 시 **경제적 이해관계 표시 의무.**
- **개정 핵심 ① 위치 강제:** 표시문구를 **반드시 '제목 또는 첫 부분'**에 게재(기존 끝부분 허용 → 이제 불가).
- **개정 핵심 ② 모호·조건부 표현 금지:** **"소정의 수수료를 지급받을 수 있음"** 같은 조건부·불확정 표현을 '명확하지 않은 표시'의 예시로 명시 → 사용 불가.
- **개정 핵심 ③ 미래·조건부 이해관계도 공개 대상:** 매출 실적에 따라 추후 대가를 받는 형태, 구매 후 환급형 등도 공개 의무.
- 부적절(위반) 예시: 본문 중간 삽입으로 구분 안 됨 / 댓글로만 표시 / '더보기' 눌러야 보임 / 글씨가 너무 작거나 배경과 색이 유사 / 너무 빠르게·작게 말함.
- 영상 매체: 추천·보증 내용과 **근접 위치**에, **명확**하게, **같은 언어**로.
- 위반 시: 시정명령·과징금 등.

> **시스템 구현(생략 불가 게이트):**
> ① 영상 **인트로 0~2초에 온스크린 자막**으로 표시문구 고정(예: "쿠팡파트너스 활동으로 일정액의 수수료를 제공받습니다").
> ② **제목 앞 또는 설명 첫 줄**에 동일 문구 자동 삽입.
> ③ 모호·조건부 표현(예: "지급받을 수 있음")은 **금칙어 검사로 차단**.

### 2-2. 유튜브 합성/AI 콘텐츠 공개
- 사실적인 AI 생성·합성 요소 포함 시 **'변경된 콘텐츠(altered/synthetic)' 공개** 토글 ON. 업로드 메타데이터에 포함.

### 2-3. 저작권 / 스톡 라이선스
- **Pexels / Pixabay**: 상업적 사용 무료, 출처표기 불필요. **단,**
  - **면책(indemnification) 없음** — 영상 속 상표·로고·식별 가능한 인물·건물 등 별도 권리 가능, **사용 책임은 전적으로 사용자.**
  - Pexels 소재는 **유의미하게 변형하지 않으면 재판매 불가.**
  - → 제품 클로즈업·상표 노출 컷은 **스톡 의존 금지**(1-3 전략 사용).
- 음원: 유튜브 오디오 보관함 / 라이선스 안전 음원만.

### 2-4. 쿠팡파트너스 금지행위 (적발 시 계정 정지)
- **자가구매**, 가족·지인 구매 유도, 단톡방 등 인위적 구매 유도 후 보상 — 전부 금지.
- 시스템은 트래픽을 *콘텐츠 품질*로만 유도.

---

## 3. 시스템 아키텍처

### 3-1. 전체 파이프라인 (반자동)
```
[1] 시장조사·상품선정  →  [2] 기획·대본(차별화)  →  [HUMAN GATE A: 상품·후킹 승인]
        ↓
[3] 에셋 수집(제품컷+보조컷)  →  [4] TTS 보이스오버  →  [5] 편집·렌더링  →  [6] 자막 스타일링
        ↓
[HUMAN GATE B: 최종 영상 30초 검수 + 컴플라이언스 자동검증]
        ↓
[7] 업로드·메타데이터(공정위 표시 자동삽입)  →  [8] 성과 수집·피드백 루프
```
- **HUMAN GATE A/B**: "전체 통과 / 일부 통과 / 반려" 가능. 바쁘면 A만 운영하고 B는 샘플링 검수로 완화 가능(정책 리스크↑).
- 큐 기반(작업 단위 = 1 영상)으로 5개를 병렬 처리.

### 3-2. 모듈별 명세

#### 모듈 A — 시장조사 & 상품 선정
- **입력:** 벤치마킹 채널 리스트, 카테고리 시드, 쿠팡 베스트/카테고리.
- **출력:** `ProductCandidate`(상품명, 카테고리, 예상 수수료, 후킹 가능성 점수, 소스 영상 확보 가능성).
- **기술:** YouTube Data API(검색·통계), 쿠팡파트너스 API(딥링크 생성), LLM(댓글·리뷰 니즈 분석).
- **주의:**
  - **`search.list`는 1콜당 100유닛**(하루 100콜 버킷). 검색 남발 금지 → 결과 캐싱 필수.
  - 경쟁자 *과거 조회수 추이*는 공식 API로 불가(Analytics는 채널 소유자만). 포인트-인-타임 지표만.
- **로직:** 후킹·전환·소스 확보 가능성 3축 스코어링 → 상위 N개를 GATE A로.

#### 모듈 B — 기획 & 대본 (차별화의 핵심)
- **입력:** 승인된 상품 + 리뷰/니즈 데이터.
- **출력:** `Script`(기승전결 구어체 대본, 3초 후킹 후보 5개, 컷별 비주얼 지시, CTA, 공정위 표시문구, 포맷 유형).
- **기술:** LLM(스크립트 생성).
- **차별화 강제 장치 (정책 회피 핵심):**
  - **포맷 로테이션:** 후킹 유형/구성/톤을 매 영상 다르게(질문형·실측형·비교형·실패담형…). 동일 골격 반복 금지.
  - **고유 관점 주입:** 상품의 *구체적 사용 맥락·단점·대안 비교* 등 "창작자 통찰" 문장 필수.
  - **유사도 검사:** 직전 N개 영상과 인트로·구성 임베딩 코사인 유사도 임계치 초과 시 재생성.

#### 모듈 C — 에셋 수집
- **입력:** 컷별 비주얼 지시 + 상품. **출력:** `AssetBundle`(제품 컷[고유] + 보조 컷[스톡/AI] + 음원).
- **기술:** Pexels/Pixabay API(보조 컷), 제조사 소재 저장소, (선택)AI 영상 생성.
- **주의:** 제품 클로즈업/상표 컷은 1-3 전략으로만. 스톡 컷에 식별 가능한 제3자 IP 없는지 자동 필터.

#### 모듈 D — 보이스오버(TTS)
- **입력:** 대본. **출력:** 나레이션 오디오 + 단어 타임스탬프(자막 싱크).
- **기술 선택지(한국어 자연스러움 우선):**
  - **ElevenLabs** — 다국어·감정 표현 강점.
  - **한국어 특화 대안** — Supertone Play, Typecast, Naver CLOVA Voice 등. 한국어 억양은 국내 엔진이 더 자연스러운 경우 많음. **A/B 후 채택.**
- **주의:** 페르소나(목소리) 고정 = 채널 정체성·진정성↑. 영상마다 목소리 난사 금지.

#### 모듈 E — 편집 & 렌더링
- **입력:** AssetBundle + 나레이션 + 타임스탬프 + 컷 시퀀스. **출력:** 9:16 영상(자막 전 단계).
- **기술 두 갈래(섹션 4 비교):**
  - **(A) FFmpeg / MoviePy** — 무료·완전 제어·셀프호스팅. 자유도 최고(차별화 로직 직접 구현).
  - **(B) JSON API (JSON2Video / Creatomate / Shotstack)** — 빠름·유지보수 적음. **단, 변수만 바꾸는 단일 템플릿은 '비진정성' 리스크** → 템플릿 다수 + 동적 구성으로 완화.
- **주의:** "초반 3초 강한 전환 5개" 구조를 *모든 영상에 동일 적용 시 양산 신호*. 구성 자체를 로테이션.

#### 모듈 F — 자막 스타일링 (모바일 가독성 = 전환 직결)
- **로직:**
  - **안전 영역:** 상단 UI·하단 추천/링크 영역을 피해 배치(쇼츠 하단 인터랙션 UI 겹침 주의).
  - **가독성:** 굵은 산세리프 + 외곽선/그림자 + 키워드 강조. 한 화면 2줄 이내.
  - **공정위 표시 자막**은 인트로에 별도 레이어로 항상 삽입(F가 보장).
  - 라인 길이 초과 시 자동 줄바꿈·페이싱 조정.

#### 모듈 G — 업로드 & 메타데이터
- **입력:** 최종 영상 + 상품 + 대본. **출력:** 영상 ID, 제품 태그(자격 시)/링크.
- **기술:** YouTube Data API v3 (OAuth 2.0, `videos.insert`).
- **할당량 현황(정정됨):**
  - **`videos.insert` ≈ 100유닛(2025.12.4 인하), 하루 100콜 버킷 → API상 하루 ~100개 가능.**
  - **그래도 하루 5개로 캡**: 정책(양산 방지)·품질·전환 효율 때문. (기술 한계 아님)
  - `search.list`(모듈 A) 100유닛/콜은 별도 관리 → 검색 캐싱.
  - 할당량 리셋은 **PT 자정**. 한국 시간 기준으로 스케줄.
- **자동 삽입:** 제목 앞 공정위 표시문구, 설명 첫 줄 표시문구 + 딥링크, 합성콘텐츠 공개 토글, 해시태그/메타.

#### 모듈 H — 성과 수집 & 피드백 루프
- **지표:** 시청 지속률/평균 시청시간, 스와이프 이탈, **링크 CTR**, **쿠팡 전환·수수료**, 후킹 유형별 성과.
- **데이터 소스:** YouTube Analytics API(자기 채널, OAuth), 쿠팡파트너스 실적 리포트.
- **루프 로직:** 후킹 유형·CTA·자막 스타일·카테고리별 성과 적재 → 다음 배치 프롬프트에 **'승자 패턴' 가중**. A/B는 "변수 1개만" 바꿔 인과 추적.

---

## 4. 기술 스택 의사결정 (현실적 권장)

### 4-1. 렌더링 엔진 비교
| 항목 | FFmpeg / MoviePy | Shotstack | Creatomate | JSON2Video | Remotion |
|---|---|---|---|---|---|
| 비용 | 무료(서버비) | 유료(분 단위) | 유료(크레딧) | 유료(분 단위) | 무료(렌더 인프라 비용) |
| 방식 | 코드 완전 제어 | JSON 타임라인 | 비주얼 템플릿+JSON | JSON(길이 자동) | React/TS 컴포넌트 |
| AI(TTS/이미지) | 직접 통합 | 외부 별도 | 외부 별도 | **TTS·이미지 내장** | 직접 통합 |
| 9:16/자막 | 직접 구현 | 가능 | 우수(반응형 텍스트) | 가능 | 우수 |
| 단점 | 구현·유지보수 부담 | 길이 사전계산·초과요금 | 크레딧 기반 | 복잡한 JSON | 인프라 직접 |
| 자동화 적합 | 높음 | 중 | 중상 | 상(Make/n8n 연동) | 중 |

**권장:**
- **MVP·풀커스텀·비용 0 우선 → FFmpeg/MoviePy.** 자막 안전영역·동적 구성 등 차별화 로직을 직접 짤 수 있어 *정책 회피*에 유리.
- **속도·운영 편의 우선 → JSON2Video(내장 TTS·이미지) 또는 Creatomate(반응형 자막).** 단, **템플릿 1개 고정 금지**(양산 신호).

### 4-2. 나머지 스택
- **상품/대본 LLM:** Claude 또는 GPT 등(구어체·후킹·차별화 프롬프트 엔지니어링이 품질의 8할).
- **TTS:** ElevenLabs vs 한국어 특화(Supertone/Typecast/CLOVA) — **A/B 후 채택.**
- **스톡:** Pexels / Pixabay (무료 API). Pixabay는 자체 캐싱 권장.
- **오케스트레이션:** 작업 큐(Celery/RQ + Redis) + 상태 DB. 5개 병렬 + 재시도.
- **스케줄링:** PT 자정 리셋 고려한 발행 타임테이블.

### 4-3. 월 비용 개념(추정)
- 렌더 API(택1, 사용 시) / TTS·LLM 사용량 기반 / 스톡 무료 / 서버는 셀프 FFmpeg면 소형 인스턴스.
- **FFmpeg 셀프호스팅이면 고정비를 LLM·TTS 사용량 위주로 최소화 가능.**

---

## 5. 개발 단계 (Milestones)

### Phase 0 — 수동 MVP 검증 (자동화 전 필수, 1~2주)
- **손으로** 10개 쇼핑 쇼츠 제작·발행. 후킹/구성/카테고리 3~4종 실험.
- 목표: "어떤 포맷이 CTR·전환을 만드는가" 데이터 확보. **여기서 안 팔리면 자동화해도 안 팔림.**
- 산출물: 승자 포맷 1~3개, 공정위 표시 워딩, 자막 스타일 가이드.

### Phase 1 — 데이터 수집·선정 자동화
- 모듈 A(YouTube/쿠팡 API + LLM 분석), 캐싱, 스코어링. GATE A UI(간단 승인 리스트).

### Phase 2 — 제작 파이프라인
- 모듈 B~F. **차별화 강제 장치(포맷 로테이션·유사도 검사)** 우선 구현. 렌더 엔진 확정.

### Phase 3 — 배포 자동화
- 모듈 G. 공정위 표시·합성 공개·메타데이터 자동삽입, 발행 스케줄, **일 5개 캡(전략적)**.

### Phase 4 — 실험·고도화 루프
- 모듈 H. KPI 적재 → 프롬프트 가중 → A/B(변수 1개). 후킹·CTA·카테고리 자동 개선.

---

## 6. 클래스 구조 설계 (구현 골격)

> 오케스트레이터 + 모듈 인터페이스 + 파이프라인 상태 + 에러 핸들링 패턴. 각 모듈은 추상 인터페이스로 두어 교체(ElevenLabs↔CLOVA, FFmpeg↔JSON2Video) 가능.

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import logging, time

logger = logging.getLogger("shorts_agent")

# ---------- 파이프라인 상태 (영상 1개 = 1 Job) ----------
class Stage(str, Enum):
    SELECTED = "selected"; SCRIPTED = "scripted"
    GATE_A = "gate_a"           # 사람: 상품·후킹 승인
    ASSETS = "assets"; VOICED = "voiced"
    RENDERED = "rendered"; CAPTIONED = "captioned"
    GATE_B = "gate_b"           # 사람: 최종 검수 + 컴플라이언스 자동검증
    UPLOADED = "uploaded"; FAILED = "failed"

@dataclass
class ProductCandidate:
    name: str; category: str; coupang_deeplink: str
    est_commission_rate: float; hook_score: float
    source_availability: str    # "manufacturer" | "self_shot" | "stock_only"

@dataclass
class Script:
    hook_variants: list[str]            # 3초 후킹 후보 5개
    body: str                           # 구어체 기승전결
    shot_directions: list[str]          # 컷별 비주얼 지시
    cta: str
    disclosure_text: str                # 공정위 표시문구 (필수)
    format_type: str                    # 로테이션용 (질문형/실측형/비교형...)

@dataclass
class AssetBundle:
    product_clips: list[str]            # 고유(제조사/직접촬영)
    b_roll_clips: list[str]             # 스톡/AI 보조
    music_path: str | None

@dataclass
class VideoJob:
    job_id: str; product: ProductCandidate
    script: Script | None = None
    assets: AssetBundle | None = None
    voice_path: str | None = None
    voice_timestamps: list[dict] = field(default_factory=list)
    raw_video_path: str | None = None
    final_video_path: str | None = None
    stage: Stage = Stage.SELECTED
    error: str | None = None

# ---------- 모듈 인터페이스 (교체 가능) ----------
class ResearchModule(ABC):
    @abstractmethod
    def find_products(self, seeds: list[str], n: int) -> list[ProductCandidate]: ...

class ScriptModule(ABC):
    @abstractmethod
    def write(self, product: ProductCandidate, recent_intros: list[str]) -> Script:
        """recent_intros: 직전 인트로들 — 유사도 검사로 양산 방지"""

class AssetModule(ABC):
    @abstractmethod
    def gather(self, script: Script, product: ProductCandidate) -> AssetBundle: ...

class VoiceModule(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> tuple[str, list[dict]]:
        """returns (audio_path, word_timestamps)"""

class RenderModule(ABC):
    @abstractmethod
    def render(self, job: VideoJob) -> str: ...      # raw video path

class CaptionModule(ABC):
    @abstractmethod
    def stylize(self, job: VideoJob) -> str: ...     # final (자막+표시문구, 안전영역)

class UploadModule(ABC):
    @abstractmethod
    def upload(self, job: VideoJob) -> str: ...      # video id

class FeedbackModule(ABC):
    @abstractmethod
    def collect(self, video_ids: list[str]) -> dict: ...   # KPI → 다음 배치 가중치

# ---------- 공통 유틸: 재시도 + 에러 핸들링 ----------
class StageError(Exception):
    def __init__(self, stage: Stage, msg: str, retryable: bool = True):
        self.stage, self.retryable = stage, retryable
        super().__init__(msg)

def with_retry(fn, *, attempts=3, base_delay=2.0, stage: Stage):
    """쿼터초과/일시오류 백오프, 치명오류 즉시 중단."""
    for i in range(1, attempts + 1):
        try:
            return fn()
        except StageError as e:
            if not e.retryable or i == attempts:
                raise
            delay = base_delay * (2 ** (i - 1))
            logger.warning("[%s] 재시도 %d/%d (%.1fs): %s", stage, i, attempts, delay, e)
            time.sleep(delay)

# ---------- 오케스트레이터 ----------
class ShortsAgent:
    def __init__(self, research, script, asset, voice, render, caption,
                 upload, feedback, *, daily_upload_cap: int = 5,
                 require_gate_a: bool = True, require_gate_b: bool = True):
        self.research, self.script, self.asset = research, script, asset
        self.voice, self.render, self.caption = voice, render, caption
        self.upload, self.feedback = upload, feedback
        # 주의: 5는 API 한계가 아니라 '정책·품질·전환'상의 전략적 캡
        self.daily_cap = daily_upload_cap
        self.require_gate_a, self.require_gate_b = require_gate_a, require_gate_b
        self._uploaded_today = 0
        self._recent_intros: list[str] = []        # 양산 방지용

    def approve_gate_a(self, job: VideoJob, approved: bool):
        job.stage = Stage.ASSETS if approved else Stage.FAILED

    def approve_gate_b(self, job: VideoJob, approved: bool):
        job.stage = Stage.UPLOADED if approved else Stage.FAILED

    def _compliance_check(self, job: VideoJob) -> None:
        """발행 전 자동 검증: 표시문구 존재/위치/금칙어, 합성공개, 자막 안전영역, 유사도."""
        if not job.script or not job.script.disclosure_text:
            raise StageError(Stage.GATE_B, "공정위 표시문구 누락", retryable=False)
        banned = ["수수료를 지급받을 수 있", "소정의 수수료"]  # 모호·조건부 표현 차단
        if any(b in job.script.disclosure_text for b in banned):
            raise StageError(Stage.GATE_B, "모호·조건부 표시문구 사용(공정위 위반)", retryable=False)
        # TODO: 인트로 임베딩 유사도 임계치, 자막 safe-area 검사 등

    def run_one(self, product: ProductCandidate) -> VideoJob:
        job = VideoJob(job_id=_new_id(), product=product, stage=Stage.SELECTED)
        try:
            job.script = with_retry(
                lambda: self.script.write(product, self._recent_intros), stage=Stage.SCRIPTED)
            job.stage = Stage.SCRIPTED
            if self.require_gate_a:
                job.stage = Stage.GATE_A
                return job  # 승인 후 _resume_after_gate_a()
            return self._resume_after_gate_a(job)
        except StageError as e:
            job.stage, job.error = Stage.FAILED, str(e)
            logger.error("Job %s 실패: %s", job.job_id, e)
            return job

    def _resume_after_gate_a(self, job: VideoJob) -> VideoJob:
        p, s = job.product, job.script
        job.assets = with_retry(lambda: self.asset.gather(s, p), stage=Stage.ASSETS)
        job.stage = Stage.ASSETS
        job.voice_path, job.voice_timestamps = with_retry(
            lambda: self.voice.synthesize(s.body), stage=Stage.VOICED)
        job.stage = Stage.VOICED
        job.raw_video_path = with_retry(lambda: self.render.render(job), stage=Stage.RENDERED)
        job.stage = Stage.RENDERED
        job.final_video_path = with_retry(lambda: self.caption.stylize(job), stage=Stage.CAPTIONED)
        job.stage = Stage.CAPTIONED
        self._compliance_check(job)
        if self.require_gate_b:
            job.stage = Stage.GATE_B
            return job  # 승인 후 _publish()
        return self._publish(job)

    def _publish(self, job: VideoJob) -> VideoJob:
        if self._uploaded_today >= self.daily_cap:
            raise StageError(Stage.UPLOADED, "일일 발행 캡 도달(전략적 품질 캡)", retryable=False)
        vid = with_retry(lambda: self.upload.upload(job), stage=Stage.UPLOADED)
        self._uploaded_today += 1
        self._recent_intros.append(job.script.hook_variants[0])
        self._recent_intros = self._recent_intros[-20:]
        job.stage = Stage.UPLOADED
        logger.info("발행 완료 %s -> %s (오늘 %d/%d)",
                    job.job_id, vid, self._uploaded_today, self.daily_cap)
        return job

    def run_daily_batch(self, seeds: list[str]) -> list[VideoJob]:
        weights = self.feedback.collect(self._recent_video_ids())  # 승자 패턴 가중
        candidates = self.research.find_products(seeds, n=self.daily_cap * 2)  # 여유분
        return [self.run_one(c) for c in candidates[: self.daily_cap]]

def _new_id() -> str: ...
```

**에러 핸들링 설계 요점**
- **API별 예외 분류:** `quotaExceeded`(YouTube)·rate limit·일시 5xx → `retryable=True` 백오프 / 인증·정책·표시문구 누락·금칙어 → `retryable=False` 즉시 중단.
- **할당량 가드:** API상 하루 ~100개 가능하나, **전략적 캡(5)**으로 양산·정책 리스크 차단. PT 자정 리셋에 맞춰 `_uploaded_today` 리셋.
- **부분 실패 격리:** 1개 Job 실패가 배치 전체를 막지 않게 Job 단위 try/except.
- **컴플라이언스 게이트:** 표시문구·위치·금칙어·합성공개·자막 안전영역·유사도 검사를 *발행 전 강제*.

---

## 7. 리스크 & 실패 포인트 체크리스트
| 리스크 | 영향 | 대응 |
|---|---|---|
| 비진정성 콘텐츠 판정 | **채널 전체 비수익화/정지** | 템플릿 로테이션, 영상별 실질 차별화, 고유 통찰, 유사도 검사 |
| 공정위 표시 누락/위치/모호표현 | 시정명령·과징금 | 제목/인트로 자동삽입, 금칙어 차단, 발행 전 게이트 |
| 제품 영상 미확보 | 전환 저조 = 수익 0 | 제조사 소재/직접 촬영 우선, 스톡은 보조만 |
| 검색 할당량(search.list 100유닛) | 시장조사 실패 | 검색 캐싱, 프로젝트 분리 |
| 스톡 IP(상표/인물) | 저작권 클레임 | 제품 컷 스톡 금지, 자동 필터 |
| 쿠팡 금지행위(자가/지인 구매) | 계정 정지 | 품질 기반 트래픽만 |
| 음원 저작권 | 수익화 제한 | 라이선스 안전 음원만 |
| "사람도 안 팔리는 포맷" 자동화 | 시간·비용 낭비 | Phase 0 수동 검증 선행 |

---

## 8. 성공 KPI
- **선행지표:** 평균 시청 지속률, 3초 이탈률, 스와이프 유지율.
- **전환지표(핵심):** 링크 **CTR**, 쿠팡 **구매 전환율**, **객단가**, 영상당 **수수료**.
- **운영지표:** 영상당 제작 비용(LLM+TTS+렌더), 영상당 순이익, 일 5개 달성률.
- **학습지표:** 후킹 유형별·카테고리별 ROI → 다음 배치 가중치.

> **북극성 지표: 영상 1개당 순수익(수수료 − 제작비) 과 그 추세.** 양산 개수가 아니라 *전환 효율*을 키우는 방향으로 진화.

---

## 9. 참고 출처 (정책·기술 근거, 2026-06 검증)
- YouTube 채널 수익화 정책(비진정성 콘텐츠, 2025.7.15): https://support.google.com/youtube/answer/1311392
- YouTube의 비진정성/반복 콘텐츠 변경 해설: https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/
- YouTube Data API 할당량 계산(videos.insert ≈100유닛, 2025.12.4 인하): https://developers.google.com/youtube/v3/determine_quota_cost
- YouTube API 할당량·감사: https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits
- 공정위 추천·보증 표시·광고 심사지침(2024.12.1 개정): https://www.law.go.kr/LSW//admRulInfoP.do?admRulSeq=2100000190311
- 공정위 경제적 이해관계 표시 안내서: https://www.ftc.go.kr/www/selectBbsNttView.do?bordCd=3&key=12&nttSn=46709
- 유튜브 쇼핑 제휴(쿠팡파트너스) 자격·연동(구독자 요건 완화): https://support.google.com/youtube/answer/13376398?hl=ko
- 유튜브 쇼핑 입점 가이드(조건·제휴사·수수료): https://colosseum.global/market-trend/youtube-shopping-affiliate-guide/
- Pexels 라이선스: https://www.pexels.com/license/
- Pixabay 라이선스: https://pixabay.com/service/license-summary/

---

### 한 줄 요약
**"하루 5개 양산"이 목표가 아니라 "전환되는 고품질 쇼츠 5개를, 정책·법규 안에서, 사람 검수 한 번 거쳐 지속 발행"이 목표.** 자동화는 양산 도구가 아니라 *고품질 제작의 가속·차별화 강제 장치*로 설계할 것.
> 참고: API 할당량은 더 이상 "5개" 제약의 근거가 아니다(현재 ~100개/일 가능). 5개는 **정책·품질·전환을 위한 전략적 선택**이다.
