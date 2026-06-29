# Phase 2 — 컬링 (Gate C 래퍼 킬 + 과학 킬 1순위)

> 두 킬 테스트:
> - **래퍼 킬:** 유능한 팀이 공개 API/오픈소스로 주말 안에 복제 가능? YES = 즉살.
> - **과학 킬(제1원리):** 물리·정보이론·수학으로 불가능? YES = 즉살.
> 추가: 빌더블(4인+자문 24개월) 불가 = 폐기.

---

## 폐기 목록 (사유)

| # | 아이디어 | 폐기 사유 |
|---|---|---|
| 4 | Speculative reasoning | 흥미롭지만 EAGLE-3 위 점진개선, 연구난이도 매우 높고 모트가 알고리즘 1편에 의존(논문화되면 즉복제). 24개월 내 10배 메트릭 입증 불확실. |
| 6 | On-prem reasoning compiler | #14/#26에 흡수(중복). 단독으론 엔지니어링만 무겁고 모트 약. |
| 11 | Multi-tenant adapter server | EdgeLoRA/Mem0/Letta가 이미 점유. 핵심이 서빙 스케줄(엔지니어링)=주말은 아니나 모트가 데이터/알고리즘 아님. 래퍼 인접. |
| 15 | NPU-aware compiler | 국산 NPU 파트너십·커널 엔지니어링 자본/인력 과대, 4인 학생팀 빌더블 경계 밖. |
| 21 | Test-time RL for agents | online RL 안정성 미해결(과학 리스크 Tier2~3), 24개월 데모 신뢰성 낮음. |
| 22 | World-model surrogate for ops | 도메인 시뮬데이터 확보가 본질, Frontier AI보다 AI4Science 트랙 적합. |
| 23 | Diffusion-spec hybrid | 순수 연구, 모트=논문(즉복제 위험), 빌더블 불확실. |
| 24 | Cacheback decoding | **래퍼 킬 FAIL** — 논문 그대로 주말 재현 가능. 모트 없음. |
| 25 | Procedural memory store | Mem0/ProcMEM 인접, 모트 약(휴리스틱+메모리). |
| 28 | 추론 비용 거버넌스 플랫폼 | **래퍼 킬 위험** — 감사로그+API 호출 비중 크면 SaaS 래퍼. 단 ACR 코어(#1)는 살림. |
| 1,2,3,5,9,10,12,13,16,17,18,19,20,27 | (개별 평가 아래) | 일부는 #14/#26로 통합 또는 생존 |

---

## 생존 후보 평가 (래퍼 킬·과학 킬·빌더블·모트 강도)

**핵심 통찰:** 개별 알고리즘 1편은 논문화되면 복제된다(약한 모트). **진짜 모트 = (a) 여러 메커니즘의 통합 시스템 + (b) 폐쇄 도메인 데이터 플라이휠 + (c) 규제·온프렘 진입장벽.** 그래서 강한 단일 알고리즘 코어를 *데이터 해자가 도는 제품*으로 묶은 것을 우선 생존시킨다.

### 생존 1 — Adaptive Compute Router (ACR) [#1, #28코어 흡수]
쿼리 난이도→최적 추론예산(토큰수·샘플수·추론깊이) 학습 라우터.
- 래퍼 킬: PASS — 난이도 예측·예산 매핑은 *학습된 정책+레이블 데이터*가 코어. 공개 API로 주말 복제 불가(레이블링 데이터·보정 필요).
- 과학 킬: PASS — TTS는 실증된 패러다임. 난이도-예산 단조관계 제1원리 성립.
- 모트: 학습 데이터 플라이휠(어떤 쿼리에 얼마 썼더니 정답?). 강도 中.
- 하드 메트릭: 동일 정확도에 추론 토큰 3~10배 절감 [가설].

### 생존 2 — Parametric Agent Memory (PAM) [#7, #9 흡수]
test-time weight update(surprise gating)+검증가능 롤백+유휴 증류로 forgetting 없는 장기메모리.
- 래퍼 킬: PASS — 벡터DB 래퍼(Mem0)와 근본 다름. *파라메트릭 메모리 안정화 알고리즘*이 코어, 주말 복제 불가.
- 과학 킬: PASS — Titans/ATLAS 실증. 안정성·롤백은 엔지니어링 난제(=모트).
- 모트: 알고리즘+안정화 레시피+롤백 보증. 강도 中~상. 단 학술 추격 빠름.
- 하드 메트릭: 동일 메모리예산에 장기 recall 정확도 ↑, 컨텍스트 토큰 비용 ↓.

### 생존 3 — Reasoning Watchdog / Compliance Steering [#17, #18, #19 통합]
추론 trace 내부표현을 SAE로 실시간 모니터→hallucination/규정위반 활성화 단계 탐지·개입.
- 래퍼 킬: PASS — 출력 필터(즉복제)와 다름. *모델 내부 feature 사전+개입정책*이 코어.
- 과학 킬: PASS — SAE steering 생산 실증.
- 모트: 도메인(금융·의료) concept feature 사전 = 폐쇄 데이터 해자. 강도 상.
- 하드 메트릭: 규정위반 출력 탐지율 ↑, 오탐 ↓, 외부 필터 대비 지연 ↓.

### 생존 4 — Domain-specific Draft Model Factory [#12]
한국어·금융·의료 등 도메인별 초경량 draft 모델 자동 생성으로 spec-decoding 가속.
- 래퍼 킬: PASS — draft 학습 파이프라인+도메인 수락률 데이터가 코어.
- 과학 킬: PASS — spec decoding 무손실, latency가 throughput 결정(실증).
- 모트: 도메인 draft 학습 노하우+수락률 데이터. 강도 中.
- 하드 메트릭: 추론 2~3배 가속(무손실), 도메인 특화로 수락률 ↑.

### 생존 5 — On-Prem Reasoning Appliance SW [#26, #14, #16 흡수] ★통합 시스템
규제기관 자체 서버에 "추론급 SLM"을 효율 배포하는 SW 스택: ACR(예산라우팅)+spec(가속)+PAM(기관메모리)+Watchdog(컴플라이언스)+KV/activation 압축.
- 래퍼 킬: PASS — 클라우드 API 못 쓰는 온프렘 + 여러 학습 코어 통합 + 한국 규제 도메인 데이터 플라이휠. 주말 복제 불가능(통합·데이터·온프렘 진입).
- 과학 킬: PASS — 구성요소 전부 실증.
- 모트: **통합 시스템 + 폐쇄 규제도메인 데이터 + 온프렘 진입장벽 = 최강.** 강도 상.
- 하드 메트릭: 온프렘 단일 GPU에서 추론모델 동급 정확도를 비용/지연 5~10배 개선 [가설].
- 단, 4인 24개월에 전부는 과함 → **쐐기(wedge)부터**: Watchdog/Compliance가 최소제품.

### 생존 6 — Privacy-preserving Continual SLM (forgetting-free + 삭제권) [#8, #10, #27]
온프렘에서 forgetting 없이 기관 데이터로 연속학습 + 검증가능 unlearning(AI기본법/GDPR 삭제권).
- 래퍼 킬: PASS — 연속학습 안정화+검증가능 unlearning 코어.
- 과학 킬: PASS — SDFT/unlearning 실증. unlearning 검증은 난제(=모트).
- 모트: 안정화 레시피+unlearning 보증+규제 적합. 강도 中~상.
- 하드 메트릭: forgetting 0에 수렴 + 삭제 검증 통과율.

---

## Phase 2 결론 (생존 6개)
1. On-Prem Reasoning Appliance SW (통합, 모트 최강) ★
2. Reasoning Watchdog / Compliance Steering (interp 모트, 쐐기 후보) ★
3. Parametric Agent Memory (PAM)
4. Adaptive Compute Router (ACR)
5. Domain-specific Draft Model Factory
6. Privacy-preserving Continual SLM (unlearning)

> 다음(Phase 3): 단위경제·TAM·첫고객·경기도레버리지로 2~3개로 압축. #1과 #2는 강하게 연결(쐐기→플랫폼) → 사업화 격투에서 한 묶음으로 검증.
