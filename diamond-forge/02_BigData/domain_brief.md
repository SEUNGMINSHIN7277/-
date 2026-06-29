# 빅데이터 도메인 정찰 브리프 (Phase 0)

> 작성: DIAMOND-FORGE 빅데이터 오케스트레이터 / 2026-06-29
> 목적: 「G스타 오디션」도약리그 수상용 빅데이터 다이아몬드 발굴을 위한 사실 접지.
> 채점 기준은 `_SHARED_CONTEXT.md` R1~R6 따름.

---

## 0. 핵심 결론 (먼저)
이 팀(데이터 분석·풀스택 강점, 4인, 18개월)에 맞는 빅데이터 해자는
**"LLM이 복제 못 하는 현장 1차 데이터(proprietary primary data)를 수집·축적하는 쐐기"**다.
a16z(2025): *"진짜 복제 불가능한 독점 데이터는 LLM 시대에 더 귀해진다 — 모든 에이전트가 필요로 하는 희소 입력이 된다."*
→ "데이터 수집·축적 해자"가 곡괭이 전략의 정답. 단순 분석 SaaS(LLM이 잡아먹음)는 폐기 대상.

가장 날카로운 **Why Now**: **EU CBAM 본 시행 2026.1.1** → 한국 수출 중소·협력사의 **제품단위 탄소배출(embedded emissions) 1차 데이터 부재**가 즉각적 비용·계약 리스크로 전환됨.

---

## 1. 시장 규모·성장률 (출처 포함)

| 지표 | 수치 | 출처 |
|---|---|---|
| 글로벌 빅데이터 시장 | 2025년 약 USD 224.46B, CAGR 12.44% (~2033) | marketdataforecast.com |
| 빅데이터·비즈니스 애널리틱스 | 2025년 USD 309.68B, CAGR 12.1%, 2035년 970B 전망 | researchnester.com |
| 빅데이터 기술 시장 | 2025년 USD 312.07B, CAGR 13.34% (~2030) | mordorintelligence.com |
| Vertical SaaS 시장 | 2025년 약 USD 130B, 연 18~22% 성장(수평형의 2배) | saasmag.com / qubit.capital |
| 데이터 moat 효과 | proprietary data 보유사가 0→$100M 매출 최단 기록 | a16z 2025 분석 (인용: scaled.co.uk) |

> 시사점: 단순 "빅데이터"는 너무 넓고 레드오션. **Vertical(산업특화) + 독점데이터 moat**가 성장률·진입장벽 둘 다 잡는 구간. 글로벌 TAM 충분(공고의 "해외진출" 요건 충족).

---

## 2. 안 풀린 Painful Unmet Need (정량 + 출처)

### A. ★ 공급망 탄소데이터 단절 (CBAM) — 최우선 후보
- **EU CBAM 본 시행 2026.1.1**: 전환기간(보고만) 종료 → EU 수입자가 제품 embedded emissions에 **재정 책임**(인증서 구매·제출). (taxation-customs.ec.europa.eu, asuene.com, BSI)
- 데이터가 없으면 **default value(가장 높은 배출집약도) 강제 적용 → 비용 폭증**. (carbonchain, icapcarbonaction)
- **중소기업 10곳 중 8곳이 CBAM을 제대로 파악 못 함** (중기중앙회 300개사 조사). (한국경제, 이코노믹데일리)
- "대기업은 준비됐지만 협력사는 멈췄다 — 공급망 탄소데이터 격차" (이코노믹데일리 2025.11)
- 핵심 공백: **제품단위(product-level) 1차 배출 데이터를 측정·산정·검증·전달**할 수단이 중소 협력사에 없음. 정부도 "표준 산정툴·전 공급망 지원 필요"라고 인정. → **데이터 수집 해자가 곧 솔루션.**
- 대상 품목: 철강, 알루미늄, 시멘트, 비료, 전력, 수소 + 확대 예정. 경기도 제조 협력사 다수 포함.

### B. 스마트공장 제조데이터 활용 실패 — 강력 후보
- 국내 중소·중견 제조 **스마트공장 도입률 19.5%**, 그중 **99.8%가 "부분 도입"**에 머묾(시스템 연동·통합 실패). (KDI, 씨메스 블로그)
- 활성화 핵심요구: **"제조데이터 분석·활용 인프라 구축" 42.4%**, 전문인력 양성 31.6%. → 데이터는 쌓이는데 못 씀.
- 예지보전(PdM) 최대 장벽: **고장 이력 데이터 부족** — AI 학습할 수년치 라벨 데이터가 없음. (HelloT, SNU HAI)
- 정부: 2030까지 AI 스마트공장 1.2만개, 중소제조 AI 도입률 10% 목표(스마트제조혁신 3.0). → 정책 순풍.

### C. 중소기업 "데이터 있어도 못 씀"
- 다수 중소·소상공인이 "데이터가 있어도 활용법을 모른다." 정부가 DATA-Stars, AI·데이터 문제해결은행 등으로 지원 중. (kdata.or.kr)

---

## 3. 최근 12~18개월 빅데이터/데이터인프라 돌파
- **독점데이터 moat의 재평가**: LLM이 분석·요약은 잡아먹지만, *현장에서만 나오는 1차 데이터*는 못 만든다 → 데이터 수집 자체가 해자(a16z, Menlo, scaled.co.uk).
- **Vertical AI SaaS**가 수평 플랫폼 대비 2배 성장 — 규제/컴플라이언스 lock-in + 워크플로우 임베딩이 가장 단단한 해자(Menlo Ventures, Vendep).
- **산업AI 소량데이터 학습**: 데이터 적어도 초기부터 결함진단 가능한 기법 등장 → PdM 데이터부족 장벽 일부 완화(SNU HAI).
- **탄소회계 SaaS 글로벌 부상**: CarbonChain, Coolset, Asuene, OneClickLCA, Climatiq 등 → 시장은 검증됨. 단, **한국 중소 협력사·제품단위 1차데이터 수집** 영역은 공백(국내 스타트업 두드러진 솔루션 부재 — koreatechdesk).

---

## 4. 한국·경기도 데이터 정책/클러스터 (레버리지 R5)
- **경기 데이터플랫폼 구축** 2024~2026 3개년 단계 사업 / **경기데이터드림**(민·관 1,700여종 원시데이터 제공). (gg.go.kr, data.gg.go.kr)
- **마이데이터 통합플랫폼 "경기똑D"** 운영 — 도민 데이터 활용. (gg.go.kr)
- **미래차 제조데이터(XAI) 센터** 구축 등 제조데이터 정책 추진. (boannews)
- **차세대융합기술연구원(광교)**, 판교 테크노밸리(AI·ICT), 경기도 제조 중소기업 밀집 → 제조데이터·탄소데이터 실증 파트너 풍부.
- 국가: **스마트제조혁신 3.0**(MSS), **데이터산업진흥 기본계획**, DATA-Stars, ESG통합플랫폼/CBAM 인프라(kosmes). → 공동사업·레퍼런스 확보 경로.

## 5. 규제 환경 (R6 / 컴플라이언스 = lock-in)
- **데이터3법**(개인정보보호법·정보통신망법·신용정보법): **가명정보** 동의없이 통계·과학연구·공익 목적 처리 가능 / **데이터 결합은 국가지정 전문기관 통해서만** 허용. (정책브리핑, 김·장)
- **마이데이터**: 본인정보 통합조회·전송요구권 — 금융 외 확대 중(경기똑D 사례).
- **개인정보보호위원회** 중앙행정기관화로 집행 강화 → 개인정보 다루는 모델은 컴플라이언스 비용↑(B2B 산업데이터·탄소데이터는 개인정보 회피로 리스크 낮음 = 유리).
- **EU CBAM/CSRD/ESPR(디지털제품여권)**: 제품단위 환경데이터 의무화 흐름 → 규제가 만든 강제 수요 = lock-in 해자.
- IP 전략: 공고상 공개 아이디어 법적보호 불가 → 핵심 산정 알고리즘·데이터 스키마는 **영업비밀 + 핵심 청구항 사전 출원(공지예외 12개월)**.

---

## 6. 발산 방향(Phase1 입력) — 데이터수집 해자 우선순위
1. CBAM/공급망 제품단위 탄소데이터 수집·산정·검증·전달 (규제강제 수요 + 데이터moat + 글로벌)
2. 중소제조 설비 운전·고장 1차데이터 수집(엣지) → PdM 데이터셋 해자
3. 제조 품질/불량 이미지·공정 데이터 라벨 자동축적
4. 중소 수출기업 ESG/공급망 실사(CSDDD) 데이터 수집
5. 디지털제품여권(DPP) 대비 제품 생애주기 데이터 축적
(상세는 raw_ideas.md)

## 출처 URL
- https://www.marketdataforecast.com/market-reports/big-data-market
- https://www.researchnester.com/reports/big-data-and-business-analytics-market/6469
- https://www.mordorintelligence.com/industry-reports/big-data-technology-market
- https://www.saasmag.com/vertical-saas-outperforming-horizontal-2026/
- https://qubit.capital/blog/rise-vertical-saas-sector-specific-opportunities
- https://scaled.co.uk/the-vertical-saas-reckoning-which-moats-llms-destroy-and-which-ones-get-stronger/
- https://menlovc.com/perspective/software-finally-gets-to-work-the-opportunity-in-vertical-ai/
- https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en
- https://asuene.com/us/blog/cbam-enters-its-definitive-phase-on-january-1-2026-what-companies-must-be-ready-for
- https://www.bsigroup.com/en-US/insights-and-media/insights/blogs/preparing-for-eu-cbam-the-20262027-transition-explained/
- https://www.carbonchain.com/cbam
- https://icapcarbonaction.com/en/news/eu-adopts-simplifications-cbam-rules-ahead-compliance-phase-starting-2026
- https://www.hankyung.com/article/202511206767i
- https://www.economidaily.com/view/20251124161039615
- https://koreatechdesk.com/eu-cbam-response-korea-policy-coordination-sme-carbon-readiness
- https://eiec.kdi.re.kr/publish/reviewView.do?idx=88&ridx=8&fcode=000020003600004
- https://blog.cmesrobotics.ai/smartfactory-cmes
- https://www.hellot.net/mobile/article.html?no=71647
- https://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=86&bcIdx=1062738
- https://m.korea.kr/special/policyCurationView.do?newsId=148867915
- https://www.gg.go.kr/bbs/boardView.do?bIdx=142365296&bsIdx=469&menuId=1547
- https://data.gg.go.kr/
- https://m.boannews.com/html/detail.html?idx=113455
