# Phase 0 — Domain Brief: AI for Science & Materials (딥테크 트랙 04)

> 작성: 2026-06-29 | 오케스트레이터: AI for Science 트랙 | 웹 리서치 접지(출처 URL 포함)
> 목적: 최근 12~24개월 돌파·미해결 난제·시장·플레이어·경기도 인프라를 접지해, 래퍼가 아닌 **진짜 딥테크 모트**가 설 좌표를 찾는다.

---

## 1. 최근 12~24개월 핵심 돌파 (Why Now)

### 1.1 생성형 소재 설계의 도약 (그러나 결함 노출)
- **GNoME (DeepMind, Nature 2023.11):** 2.2M 신규 무기결정 구조 예측, 안정 후보 4.5만→38만. 안정성 예측 정밀도 80%(기존 ~50%). 1회 추론으로 카탈로그 확장. [출처](https://www.nature.com/articles/d41586-025-03147-9)
- **MatterGen (Microsoft Research, 2024.1, 2025 오픈소스):** 확산모델 기반 **역설계(inverse design)** — 목표 물성(화학·대칭·전자·자성)을 조건으로 신규 안정 구조를 직접 생성. 스크리닝 패러다임을 깨고 "원하는 물성 → 구조" 직접 생성. [출처](https://www.turingpost.com/p/mattergen) · [오픈소스](https://hyper.ai/en/news/37442)
- **Universal MLIP 파운데이션 모델:** MACE-MP-0, UMA(Open Catalyst) 등 단일 모델로 다원소·다조성 near-DFT 정확도 + 수천~수만배 속도. [출처](https://www.nature.com/articles/s41524-025-01727-x)
- **Open Catalyst 2025 (OC25, Meta):** 고체-액체 계면(용매·이온 명시) 780만 DFT 단일점 계산 신규 공개. 촉매·전기화학 계면 ML의 데이터 지평 확대. [출처](https://www.emergentmind.com/topics/open-catalyst-2025-oc25-dataset)

### 1.2 검증 루프의 물리적 실증
- Berkeley Lab **A-Lab:** GNoME 후보 58종 중 41종을 17일 내 자율 합성 — 디지털→물리 전환 가능성 입증. [출처](https://www.nature.com/articles/d41586-025-03147-9)

---

## 2. 풀리지 않은 핵심 난제 (여기서 10배가 나온다)

### 2.1 ★ 합성가능성 격차 (Synthesizability Gap) — **최대 미해결 난제**
- Cheetham & Seshadri(2024)의 GNoME 반박: 예측 구조 다수가 **(a) 기존 물질의 사소한 변형(non-novel), (b) 방사성 등 비현실 원소, (c) 합성 불가**. "안정(thermodynamically stable) ≠ 합성가능(synthesizable) ≠ 유용(useful)". [출처](https://www.theregister.com/2024/04/11/google_deepmind_material_study/)
- Nature(2025): "AI가 수백만 신소재를 꿈꾸지만 — 쓸만한가?" — 생성 구조의 **합성가능성·신규성·유용성 필터 부재**가 산업 적용의 진짜 병목. [출처](https://www.nature.com/articles/d41586-025-03147-9)

### 2.2 ★ 무기소재 역합성(retrosynthesis) 부재 — **방법·데이터 모두 공백**
- 유기화학은 상용 반응 DB(Reaxys 등)로 역합성 DNN이 성숙. **무기소재는 상용 반응 DB가 존재하지 않음.** 합성은 "전구체→반응→목표상" 단일공정이나 **통일 이론 없이 시행착오 의존.** [출처](https://pmc.ncbi.nlm.nih.gov/articles/PMC10256153/)
- 텍스트마이닝 레시피(고체합성 ~29,900건) 기반 전구체 추천이 SOTA지만, **신규 반응 일반화 실패**(known precursor 의존), 다중라벨 분류 한계. Retro-Rank-In(2025) 등은 부분 개선. [출처](https://arxiv.org/html/2502.04289v1)
- RSC Faraday Discussions(2025): 텍스트마이닝 레시피로 합성 통찰을 학습하려는 시도에 대한 **비판적 성찰** — 레시피 데이터의 노이즈·결측·맥락소실. [출처](https://pubs.rsc.org/en/content/articlehtml/2025/fd/d4fd00112e)

### 2.3 DFT↔실험 격차 + UMLIP 일반화 한계
- 단일 통합 포텐셜로 전 화학공간 ab initio 정확도 = 장기 미해결. 반응장벽·상전이·표면에너지에서 파운데이션 모델 정확도 부족, OOD(분포 밖) 급격 저하. [출처](https://pubs.acs.org/doi/10.1021/acsami.4c03815)
- DFT 자체가 실험과 어긋남(PBE 범함수 등) → **DFT-네이티브 모델은 실험을 직접 못 맞춤.** 실험+시뮬 데이터 융합이 떠오르나 미성숙. [출처](https://www.nature.com/articles/s41524-024-01251-4)

### 2.4 데이터 부족 + 불확실성정량화(UQ)
- 전해질·SSE 등 응용: 고품질 실험 데이터 희소, 도메인 전이 실패(카보네이트→에테르). [출처](https://pubs.acs.org/doi/10.1021/acsomega.5c08467)
- 능동학습용 신뢰가능 UQ가 미성숙(앙상블 분산·BNN 비교 진행 중). [출처](https://www.nature.com/articles/s41524-025-01758-4)

> **결론(난제 좌표):** 생성·스크리닝(GNoME/MatterGen)은 빅테크가 선점. **빈 공간 = "이론적 후보 → 실제로 만들 수 있는가 + 어떻게 만드는가"의 합성가능성·역합성 레이어.** 여기에 능동학습 실험설계와 UQ가 결합되면 빅테크 미보유 + 산업 적용 직결.

---

## 3. 시장 · 플레이어

### 3.1 시장 규모 (출처 표기, 보고서별 정의 상이)
- AI in Materials Discovery: 2024 $536.4M → 2034 $5,584.2M, CAGR 26.4%. [출처](https://market.us/report/ai-in-materials-discovery-market/)
- Materials Informatics: 2025 $208.41M → 2035 $1,314.25M, CAGR ~20%. [출처](https://www.precedenceresearch.com/material-informatics-market)
- 상위 응용 TAM(소재가 깎는 비용): 배터리·촉매·반도체 소재·기후소재(CO2전환, 그린수소)는 수백조원급 산업의 핵심 변수.

### 3.2 플레이어 지형
- **빅테크 모델 레이어:** DeepMind(GNoME), Microsoft(MatterGen), Meta(Open Catalyst/UMA) — 생성·UMLIP 선점. (오픈소스화 → 모델 자체는 차별화 약함, 래퍼 리스크)
- **플랫폼/SaaS:** Citrine Informatics, Schrödinger, Dassault, Materials Zone, Exabyte — 데이터·워크플로우. [출처](https://finance.yahoo.com/news/material-informatics-company-evaluation-report-142500699.html)
- **자율실험실(SDL):** Kebotix, A-Lab(Berkeley) — AI+로봇 합성. (자본집약, 학생팀 직접 진입 불가 → **SW 레이어로 우회**)
- **공백:** 생성구조의 **합성가능성 평가 + 무기 역합성(전구체·조건 추천) + 능동학습 검증설계**를 산업 정확도로 묶은 SW-only 모트 플레이어는 미성숙(텍스트마이닝 학계 PoC 수준).

---

## 4. 한국 · 경기도 인프라 레버리지

- **차세대융합기술연구원(융기원, AICT):** 경기도+서울대 공동출연, 수원 광교 소재. 지역 R&D·AI 인프라·장비 보유, 관학협력 — **검증 합성·DFT 컴퓨팅·교수 자문 파트너 후보.** [출처](https://aict.snu.ac.kr/) · [장비현황](https://aict.snu.ac.kr/?p=210)
- **경기도 배터리·소재 산업:** 용인·평택 반도체 클러스터(소재·전구체 수요), 배터리·이차전지 소부장 기업 밀집. AI 기반 배터리 소재/셀/리사이클 개발이 국내 트렌드. [출처](https://www.sneresearch.com/kr/business/report_view/230/page/0)
- **가천대(성남):** 팀 소속, 창업지원단, 판교 인접 — DFT용 GPU·클라우드 크레딧, 화학·재료 교수 자문 접근.
- **KAIST 등 국내:** AI로 그린수소·배터리 신소재 탐색 활발 — 검증·공동연구 생태계 존재. [출처](https://news.kaist.ac.kr/news/html/news/?mode=V&mng_no=41710)

> **경기도 레버리지 포인트:** 융기원·경기도 소부장 기업을 **검증 합성·실험 데이터 조달 파트너**로, 핵심 모트(합성가능성·역합성·능동학습 모델)는 팀 주도 인실리코로 보유 → 웻랩 외주 구조가 본 트랙 제약(웻랩 자체구축 금지)과 정합.

---

## 5. 딥테크 좌표 결론 (Phase 1 발산 방향)

1. **합성가능성 게이트 모델** — 생성 후보를 "만들 수 있는가" 확률+신규성+유용성으로 필터(빅테크 생성기 뒤에 붙는 필수 레이어).
2. **무기 역합성 엔진** — 목표상 → 전구체·소성조건·경로 추천(상용 DB 부재 = 데이터 모트 기회).
3. **능동학습 실험설계 + UQ** — 희소 데이터에서 다음 실험을 최소비용 최대정보로 추천(검증 파트너와 폐루프).
4. **DFT-실험 격차 보정 surrogate** — 융합 데이터로 실험 물성 직접 예측.
5. **응용 수직(배터리 전해질/SSE, CO2 촉매)** — 도메인 데이터+물리 제약으로 일반 모델 능가.

→ 가장 방어가능 + 빅테크 미보유 + SW-only + 경기도 정합: **(1)+(2)+(3) 결합 = "생성 이후(post-generative) 합성가능성·역합성·능동검증 레이어."** Phase 1에서 이 좌표 중심으로 원석 발산.
