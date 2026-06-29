# 05_ResourceCircular — Domain Brief (Phase 0 정찰)

> 도메인: 자원순환 및 에너지 재활용 (Resource Circularity & Energy Recycling)
> 팀 제약: AI/ML·SW 학생 4인. 플랜트·중장비·화학공정 자체 구축 불가 → **SW/AI/데이터 레이어로만 진입.**
> 작성일: 2026-06-29. 모든 수치는 출처 명기, 미검증은 [가설] 표기.

---

## 0. 핵심 결론 (먼저)
자원순환 도메인에서 **4인 SW/AI 학생팀이 18개월 내 실현 가능하고 글로벌 TAM이 크며 R3(환경오염)와 시너지**가 나는 쐐기는 **하드웨어(플랜트/로봇/선별기)가 아니라 "데이터·정산·증명(measurement/verification/accounting) 레이어"**다. 그중 **Why-now가 가장 폭발적인 지점은 EU CBAM 정식 시행(2026.1.1)으로 발생한 한국 수출 제조 중소기업의 "공급망 탄소 데이터 격차"**다. 이는 (a) 규제로 강제된 수요, (b) 순수 SW/AI 문제, (c) 친환경 가점, (d) founder-market-fit(데이터·AI 강점)이 모두 일치한다.

---

## 1. 시장 규모 & 성장률 (출처)

### 1-1. 순환경제 / 디지털 순환경제
- 글로벌 순환경제 시장: 2025 $517.79B → 2030 $888.22B, **CAGR 11.3%** (The Business Research Company / 검색종합).
- **디지털 순환경제(SW/데이터 세그먼트): 2025 $4.52B → 2030 $14.35B, CAGR 26%** (Mordor Intelligence). 별도 추정 2030 $8.4B, AI·클라우드·블록체인 견인 (GlobeNewswire 2025.11).
  - → 우리가 노리는 레이어는 "디지털 순환경제"이며 26% 고성장.

### 1-2. AI 폐기물 선별 (참고: HW라 비-진입, 시장신호용)
- AI-Powered Recycling Robot: 2025 $1.7B → 2034 $6.7B, CAGR 14.8% (market.us). AI 광학선별 정확도 99%, 시간당 1,000개 vs 사람 50~80개 (Columbia Climate / Fortune 2025).
- → **HW 의존이라 본 팀 폐기. 단 "선별을 위한 비전 모델"은 SW 쐐기로 일부 차용 가능(파트너 HW에 얹는 SaaS).**

### 1-3. 폐배터리 재활용
- 글로벌 폐배터리 재활용: 2030 약 $57.4B(≈68조원), **CAGR 33%** (SNE Research).
- 국내: 2023 $26.9B → 2030 $54.3B, CAGR 10.5% (IITP). 국내 EV 폐배터리 발생량 2025 ~8,300개 → 2030 8만개+ (10배↑) (Deloitte Korea / KOTI).
- 정책: 2025 포항 "EV 사용후 배터리 자원순환 클러스터", 산업화센터 2→4곳.

### 1-4. 산업공생(Industrial Symbiosis) 부산물 마켓
- 글로벌 산업공생 시장 2030 $75B+ (Sustainability Atlas). Rheaply 자산재사용 $100M+ 중개(Google/McDonald's 고객). Kalundborg 공생 연 €24M 절감.

### 1-5. SME 탄소회계 / PCF / LCA SW
- Scope 3가 기업 총배출의 70~90% 차지(공급망). 자동 LCA로 6개월→수주로 단축 (Carbonmaps).
- 유럽 CSRD 압박으로 mid-market SaaS(Coolset, Arbor, Sweep 등) 급성장 중. **그러나 대부분 EU/US 타깃, 한국 수출 제조 SME·CBAM 6대 품목 특화 + 공급망 1차협력사 데이터 자동수집은 공백.**

---

## 2. 가장 Painful한 Unmet Need (핵심)

### ★ CBAM 공급망 탄소 데이터 격차 (한국 수출 제조 중소기업)
- **규제 강제 수요:** EU CBAM 2026.1.1 정식 시행. 철강·알루미늄·시멘트·비료·전력·수소 6대 품목 + 전구물질. 인증서가 2026 default값에 +10%, 2027 +20%, 2028+ +30% 마크업 → **실측 데이터 없으면 관세폭탄.** 미신고 톤당 €100 과태료. 인증서가 €75.36/tCO2 (2026.4 첫 분기가).
- **고통의 실증(서베이):** 중기중앙회 조사 — 중소기업 **80%가 CBAM을 제대로 모름**(잘 안다 21.7%). **38%가 "탄소배출량 산정·검증 역량 부족"을 1순위 애로**로 지목. "탄소는 줄여야 하는데 산정을 못 하겠다"(산업종합저널).
- **공급망 격차:** 대기업은 자체 시스템으로 대응하나 **중간단계 중소 협력사는 데이터 확보·산정 역량 전무**(이코노믹데일리 2025.11 "대기업은 준비됐지만 협력사는 멈췄다"). default값보다 높게 잡히면 거래 경쟁력↓, 낮게 잡히면 신뢰도 문제로 추가검증 요구 → **실측·검증가능 데이터가 곧 돈.**
- **확장:** 2030 CBAM이 석유화학·플라스틱까지 확대 예상(CarbonLink) → SAM 급팽창.
- **순수 SW/AI 문제:** 배출량 산정 = 데이터 수집(ERP/전력/연료/구매)·매핑·배출계수 적용·LCA·EU양식 산출·검증 추적. **공장도 중장비도 필요 없음.** AI로 (a)인보이스/전력고지서 OCR·자동분류, (b)활동데이터→배출량 자동산정, (c)공급망 1차협력사 데이터 수집 자동화, (d)default 대비 실측 절감액 시뮬레이션.

### 차순위 unmet needs (생존 후보)
- 폐배터리 SOH(잔존수명)·이력 데이터 부재 → 재사용/재활용 분기 판단 불가 (단, 진단 HW 의존 리스크).
- 제조 SME 부산물의 거래상대·물류 매칭 부재 → 매립 (단, 양면시장 cold-start 리스크).
- 사업장 폐기물 배출자 신고·정산(올바로 시스템) 수작업 부담 (규제 SW).

---

## 3. 한국·경기도 정책 / 규제 (레버리지)
- **순환경제사회 전환 촉진법** 2024.1.1 시행(자원순환기본법 전면개정). 폐기물발생감량률 2025.1.1 시행. 국가 중장기 순환경제 목표(감량률·최종처분율·순환이용률·에너지회수율).
- **EPR(생산자책임재활용)**: 재활용 의무 미이행 시 부과금. iEPR 운영.
- **EU CBAM** 2026.1.1 정식 시행(상기). 환경부 "배출량 산정해설서" + CBAM 컨설팅 60개사 지원 → **정부가 수요·예산을 만들어줌 = GTM 파트너.**
- **경기도:** 「경기도 순환경제사회 전환 촉진 조례」, 제1차 자원순환시행계획(2023~2027, 31개 시군), 2025 경기도 중소기업 지원시책. 경기도 = **제조 중소기업·수출기업 최다 밀집 광역** → CBAM 피해기업 모수 최대. 경과원·가천대 창업지원단 연계.

## 4. R3(환경오염) 점검 — 시너지
자원순환·탄소 데이터는 **환경오염 유발의 정반대 = 친환경 가점 강함.** 게임/사행성 무관. IP: 데이터 파이프라인·배출계수 매핑·검증 알고리즘은 영업비밀 우선 + 핵심 산정 방법 일부 특허 검토.

## 출처 URL
- The Business Research Company / Mordor Intelligence(digital circular economy) / GlobeNewswire 2025-11-25 (digital circular economy $8.4B)
- market.us, fortune.com 2025-06-26, news.climate.columbia.edu 2025-06-18 (AI recycling)
- SNE Research(sneresearch.com), Deloitte Korea, KOTI (폐배터리)
- sustainableatlas.org, news.sustainability-directory.com (industrial symbiosis), researchgate Rheaply
- EU Taxation-customs (CBAM), onestopesg.com, icapcarbonaction.com, gmk.center (CBAM 2026 €75.36, +10/20/30% markup, €100/t)
- economidaily.com 2025-11-24, industryjournal.co.kr, gcnc.or.kr CBAM 중소중견 매뉴얼, hankyung 2025-11 (한국 SME CBAM 격차, 80% 인지부족, 38% 산정역량부족)
- carbonmaps.io, carbalyze.com, sweep.net (SME carbon/LCA SaaS)
- law.go.kr/moleg.go.kr (순환경제사회 전환 촉진법), iepr.or.kr (EPR), gg.go.kr (경기도 자원순환시행계획), ulex.co.kr (경기도 조례)
