# 04_Semiconductor — Domain Brief (Phase 0 정찰)

> 작성일 2026-06-29. 팀: AI/ML·SW 4인 학생팀(칩 양산·팹·설계 IP 역량 없음). 진입 레이어 = **반도체 산업의 SW/데이터 레이어**.
> 모든 수치는 출처 표기. 출처 없는 추정은 "[가설]" 표기.

---

## A. 시장 규모·성장률 (출처)

| 세부 시장 | 규모(연도) | 전망/CAGR | 출처 |
|---|---|---|---|
| Semiconductor Process Control AI | USD 1.42B (2024) → 6.74B (2033) | CAGR 18.6% (25–33) | dataintelo |
| AI Defect Detection (전산업) | USD 3.31B (2024) → 6.63B (2034) | CAGR 11.9% | navistrat/intelmarket |
| Semiconductor Yield Analytics Tools | USD 0.94B (2024) → 2.18B (2034) | CAGR 8.76% | Precedence Research |
| 시스템반도체 시장(글로벌) | 약 374조원 (2025) | — | KITA/한국무역협회 |
| 지역: APAC | 글로벌 점유 55%+ (2024) | 최고성장 19.8% | 시장보고서들 |

핵심: **수율·공정관리 AI는 두 자릿수 CAGR, APAC(=한국 포함) 최대 시장.** 글로벌 TAM 충족.

## B. 최근 12~18개월 돌파 (Why Now)

1. **Vision Foundation Model + GenAI로 결함분류 데이터 부족 문제 해결.**
   - NVIDIA Cosmos Reason(VLM): wafer 결함 few-shot 분류, 자연어 설명, 자동 라벨링, 파인튜닝 시 96%+ 정확도. (NVIDIA Tech Blog)
   - FCCIL: 15–20 shot으로 신규 결함 85%+ 정확, 학습 100 epoch로 단축. (ScienceDirect 2025)
   - Tiny ViT / G2LGAN: 소량·불균형 데이터에서도 wafer map 분류. (arXiv 2504.02494, Springer 2025)
   - → **소량 라벨·기밀 데이터 환경(=중소 팹/소부장의 현실)에서 비로소 실용화 가능해진 것이 결정적 Why Now.**
2. **Agentic EDA / GenAI EDA 본격화** (Siemens DAC 2025, Synopsys DSO.ai, Cadence Cerebrus, ChipAgents 10x RTL). → 대형 EDA 벤더가 이미 점령 중인 레드오션, 학생팀 진입 부적합.
3. **예지보전 GenAI**: 합성데이터로 희귀 고장 시나리오 생성, edge AI+5G 실시간. 다운타임 1건 $100K–500K, EUV 스캐너 시간당 $50K–100K. (mst-sg, appitsoftware)

## C. 안 풀린 painful unmet need (★쐐기 후보의 원천)

1. **데이터 단편화 지옥(fabless/소부장):** 여러 파운드리·OSAT에서 오는 STDF/비STDF 테스트 파일이 레이아웃·bin코드·메타데이터 제각각 → **엔지니어가 수작업 병합·클린징**, 인사이트 지연·휴먼에러. (Synopsys/yieldWerx/PDF.com)
2. **라벨 부족 + 기밀성:** wafer map은 영업기밀이라 외부 공개 불가, 라벨링 비용 매우 높음 → 기존 딥러닝 적용 불가. (ScienceDirect)
3. **인력난(구조적, 한국 특화):** 시스템반도체 전문인력 2031년 약 5.4만명 부족(한국반도체산업협회/경향). 인재가 대기업 쏠림 → **소부장 중소기업 인력 공동화**, 품질·수율 엔지니어 부재. (글로벌이코노믹, 시사저널e)
4. **국내 팹리스 4대 고통:** 인력·투자·융자·해외진출. 중국과 가격경쟁, 창업 감소. (디일렉)
5. 중소 소부장의 SPC/MES 디지털전환 미비 — 오프라인 SPC는 테스트 워크피스 多 → 비용·시간 낭비. (USPTO/논문)

## D. 한국·경기도 정책 (R5 레버리지)

- **용인 반도체 클러스터(SK하이닉스 처인구 원삼면 126만평):** 팹 4기 + **소부장 협력단지 약 14만평** 조성. R&D·설계·전공정·후공정·소부장 토탈 거점. (나무위키, SK뉴스룸)
- 경기 반도체 메가 클러스터: 이천·평택·화성·안성·성남·판교·수원 기존 시설 + 용인. → **첫 고객 후보가 경기도에 물리적으로 밀집.**
- 김동연 지사 2026 신속추진, 건설 3~4년 단축. 반도체특별법: 전력·용수·기반시설 50~100% 국비. (다음/파이낸셜뉴스)
- 경과원·가천대(성남) 창업지원망, 차세대융합기술연구원. → 실증·레퍼런스 고객 확보 용이.

## E. 규제·보안 (R6 / 진입장벽)

- wafer/테스트 데이터 = 영업기밀. **데이터 반출 불가 → on-prem / edge 추론 필수**가 오히려 진입장벽이자 해자 설계 포인트.
- 대형 벤더(Synopsys exensio, PDF.com, yieldWerx, yieldHUB)는 대형 IDM·OSAT 타깃·고가·SI 무거움 → **중소·소부장 long-tail은 미충족(언번들 기회).**
- 게임/사행성/환경오염 무관 → R3 클리어.

## F. 정직성 메모

- 칩 설계/양산/팹 운영 의존 아이디어는 전부 Phase 2에서 즉살.
- 학생팀 실현 가능 영역 = **데이터 파이프라인 + 소량학습 비전/이상탐지 + 워크플로 SW(on-prem 경량)**.
- EDA 코어(RTL/PPA 최적화)는 대형 벤더+딥인프라 필요 → 학생팀 부적합, 회피.

### 출처 URL
- precedenceresearch.com/semiconductor-yield-analytics-tools-market
- dataintelo.com/report/semiconductor-process-control-ai-market
- navistratanalytics.com/report_store/ai-defect-detection-market/
- developer.nvidia.com/blog/optimizing-semiconductor-defect-classification-with-generative-ai-and-vision-foundation-models/
- sciencedirect.com/science/article/abs/pii/S0166361525001976
- arxiv.org/pdf/2504.02494 ; link.springer.com/article/10.1186/s13640-025-00666-3
- synopsys.com/blogs/chip-design/improving-semiconductor-yield-with-test-data-analytics.html
- yieldwerx.com/blog/complete-guide-to-test-data-manipulation-in-semiconductor-manufacturing/ ; pdf.com/products/exensio-analytics-platform/overview/
- mst-sg.com/predictive-maintenance-for-semiconductor-equipment ; appitsoftware.com/blog/semiconductor-equipment-predictive-maintenance-ai
- khan.co.kr/article/202511071408001 ; sisajournal-e.com/news/articleView.html?idxno=419730 ; g-enews.com/article/Global-Biz/2026/01/...
- thelec.kr/news/articleView.html?idxno=19630 ; kita.net (시스템반도체 374조)
- namu.wiki/w/용인_반도체_클러스터 ; news.skhynix.co.kr/2026-expert-column-series-ep5/ ; v.daum.net/v/20260609200226736 ; fnnews.com/news/202606251858555891
