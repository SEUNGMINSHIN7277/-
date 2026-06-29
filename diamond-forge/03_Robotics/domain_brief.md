# 03_Robotics — Domain Brief (Phase 0 정찰)

> 작성 2026-06-29 · DIAMOND-FORGE 지능형 로봇 도메인 오케스트레이터
> 제약: 4인 AI/SW 학생팀 → **순수 하드웨어 양산 금지. 기성 로봇 위 AI/SW 쐐기만 허용.**

---

## 0. 핵심 결론 (TL;DR)
한국은 **세계 1위 로봇 밀도(1,220대/만명)**임에도, 중소·중견 제조 현장은 **로봇을 "도입은 했으나 활용 못 하는"** 거대한 공백이 있다. 병목은 하드웨어가 아니라 **로봇을 가르치고(teaching)·재배치(re-tasking)·인지(vision)시키는 소프트웨어 레이어**다. 이것이 바로 AI/SW 학생팀이 하드웨어 양산 없이 진입할 수 있는 쐐기다.

---

## 1. 기술 돌파 (최근 12~18개월)

- **VLA(Vision-Language-Action) 모델 부상이 2025~2026 패러다임 전환.** VLM 백본 + 액션 디코더로 자연어 지시 → 연속 모터 제어를 end-to-end 매핑. 대표: Physical Intelligence π0/π0.5(미지의 가정환경 일반화), NVIDIA GR00T N1, Figure Helix, Google DeepMind Gemini Robotics. BMW가 2025.1 VLA 영구 배치(상업성 검증). [출처: arxiv 2505.04769, neuralcoretech, medium/RAKTIM]
- **데이터가 진짜 병목.** 로봇 파운데이션 모델의 한계는 모델이 아니라 "다양·고품질 시연 데이터 수집". 텔레오퍼레이션은 운영자-시간당 5~50 에피소드로 병목. 백만 시연 스케일에서는 "데이터 운영(logistics)" 문제로 전환. [출처: labellerr.com, shaip.com, evsint.com 2026, claru.ai]
- **LLM 기반 No-Code/Low-Code 로봇 프로그래밍 활발.** LLM이 자연어 지시 → 로봇 태스크 코드 생성. 단, 함수·루프 등 고차 코드 생성은 아직 약함(검증·복구 루프 필요). 다중에이전트(의도인식·파라미터추출·휴먼검증) 프레임워크 연구 중. [출처: arxiv 2409.11041, ScienceDirect S0278612525002584, RoboCritics arxiv 2603.06842]

## 2. 시장 규모·성장률 (출처)

- **로봇 SW 시장:** 2025 약 USD 24.23B → 2030 USD 64.46B, **CAGR 21.6%** (Mordor/GII). 다른 추정: 2025 14.17B → 2033 97.8B, CAGR 27.3%. [출처: giiresearch, alliedmarketresearch, nextmsc]
- **AI 로보틱스 전체:** 2024 USD 16.1B → 2030 USD 124.77B. [출처: neuralcoretech]
- **APAC가 최고 성장 지역**, 중·일·싱·**한국**·인도가 견인. [출처: nextmsc]
- 가설(출처 불충분): SME 대상 "로봇 활용 SW/teaching" 세그먼트는 전체 로봇SW의 일부이나 미충족이 가장 큼 → SOM 산정 시 보수적 적용.

## 3. 안 풀린 painful unmet need (가장 중요)

- **시스템 통합자(SI) 병목:** SI 캐파 부족, **백로그 6~12개월** → 도입 지연·비용. 사내 통합 역량 없는 SME가 최대 피해. [출처: globalgrowthinsights, smartindustry]
- **고혼합·소량(High-mix Low-volume) 재배치 지옥:** 제품 바뀔 때마다 로봇 재프로그래밍 필요 → 전문 엔지니어 없으면 멈춤. 비전문가 재배치 SW가 SME 세그먼트 공략 핵심. [출처: eliterobots, futuremarketinsights]
- **한국 SME 자동화 격차(★국내 진입 레버리지):** 대기업 신기술 수용 24.5% vs **중소기업 12.1%**. 초기투자 **USD 500k+** 부담. **제조 인력 40%가 로봇 운용 훈련 부족.** 로봇 밀도 1위(1,220/만명)인데 SME는 못 쓴다. [출처: IFR World Robotics 2025, xpert.digital, kenresearch]
- 노동력 부족: 미 제조 일자리 2030년까지 210만 미충원 전망(글로벌 구조적 수요). [출처: mwes, tomarobots]

## 4. 한국·경기도 정책/실증/클러스터 레버리지

- **2026 로봇활용 제조혁신 지원사업:** 중소·중견 제조기업 로봇자동화 도입 + 엔지니어링/안전 컨설팅 패키지, **과제당 사업비 50%·최대 2.5억원 지원.** [출처: bizinfo PBLN_116712]
- **2025 경기도 로봇 실증 지원사업(경기도 로봇산업 육성지원):** 실증화 단계 로봇 중소기업 지원. 성남시혁신지원센터/경과원 G-PMS 운영. [출처: bizinfo 105828, sisc.or.kr, pms.gbsa.or.kr]
- **첨단제조로봇 실증사업(KIMM/KITECH):** 공공·민간 제조시설 로봇공정모델 실증. [출처: kimm.re.kr, kitech.re.kr]
- **2026 스마트 제조혁신 통합공고(제조로봇 도입 자동화지원).** [출처: bizinfo PBLN_116027]
- **경기도 자산:** 판교(AI/ICT), 차세대융합기술연구원, **경기도 제조 중소기업 밀집(스마트제조·로봇 실증 최적)**, 가천대 창업지원단(성남) → 실증 파트너·정부지원금 레버리지 강력.

## 5. 규제 (KC·안전인증)

- **실외이동로봇 운행안전인증(지능형로봇법 법정 의무):** 최대속도 15km/h·질량 500kg 이하, 16개 심사항목, 보험·공제 의무. 인증 시 보행자 자격(보도·횡단보도 통행). [출처: kiria.org/cert, AI타임스 155217, 국가법령정보센터]
- **2025 규제샌드박스로 실증·인증 절차 간소화 착수**, 첨단로봇 규제혁신 방안 진행. [출처: bizinfo 첨단로봇 규제혁신, ZDNet 2026.06.28]
- **시사점:** 실외 자율주행/배송 로봇 = 인증·보험 부담 큼(하드웨어 의존도↑). **공장·물류센터 内 cobot SW 레이어 = 운행안전인증 대상 아님 → 규제 부담 낮음 + 하드웨어 비의존.** → 진입 우선순위는 사내(in-facility) cobot SW.

## 6. 도메인 채굴 함의 (Phase 1 입력)
1. 하드웨어 양산 의존 아이디어 즉살(휴머노이드 제작·드론 제작·AMR 제작 등).
2. **우선 사냥터:** (a) SME 제조 cobot 자연어·노코드 teaching/재배치 SW, (b) 로봇 비전·픽앤플레이스 인지 레이어, (c) 로봇 시연 데이터/시뮬레이션 운영 SW, (d) 사내 물류 cobot/AMR 오케스트레이션 SW.
3. 규제 부담 낮은 **사내(in-facility)** 우선, 실외 인증 필요 영역은 후순위.
4. 글로벌 진출: 로봇SW는 SW이므로 SaaS/라이선스로 국경 무관 → 공고의 "해외 진출" 요건 충족 용이.

## 출처 URL
- https://arxiv.org/html/2505.04769v2 (VLA survey)
- https://neuralcoretech.com/physical-ai-architecture-vla-robotics/
- https://www.giiresearch.com/report/moi1642129-robot-software-market-share-analysis-industry.html
- https://www.nextmsc.com/report/robot-software-market
- https://www.alliedmarketresearch.com/press-release/robot-software-market.html
- https://www.labellerr.com/blog/robot-training-datasets-collection/
- https://www.shaip.com/blog/robot-training-data-strategy/
- https://www.evsint.com/embodied-ai-data-collection-teleoperation-sim-to-real-2026/
- https://www.globalgrowthinsights.com/blog/collaborative-robots-companies-1038
- https://www.smartindustry.com/.../55322754 (integrator backlog)
- https://arxiv.org/abs/2409.11041 (No-Code cobot LLM)
- https://www.sciencedirect.com/science/article/abs/pii/S0278612525002584 (LLM low-code industrial robot)
- https://www.industrial-production-worldwide.com/news/world-robotics-2025-report-reveals-south-korea-singapore-and-germany-have-highest-robot-density
- https://xpert.digital/en/robotics-in-south-korea/
- https://www.kenresearch.com/south-korea-robotics-and-automation-in-manufacturing-market
- https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000116712 (2026 로봇활용 제조혁신)
- https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000105828 (경기도 로봇 실증)
- https://www.kiria.org/portal/cert/portalCertEstiSafe.do (실외이동로봇 운행안전인증)
- https://www.aitimes.com/news/articleView.html?idxno=155217 (지능형로봇법 시행)
