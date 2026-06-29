# Physical AI / Robotics Foundation — Domain Brief (Phase 0)

> 작성: 2026-06-29 · DIAMOND-FORGE 2회차 딥테크 트랙 03 · 모든 수치는 출처 URL 명시. 추정/가설은 [가설] 표기.

---

## 0. 핵심 결론 (TL;DR)

- 최근 18개월의 진짜 돌파는 **조작용 VLA 파운데이션 모델**(π0, OpenVLA, RT-X)이지만, **남은 최대 난제는 "접촉이 많은 정밀 조작(contact-rich manipulation)"의 sim2real gap과 데이터 효율**이다. 픽앤플레이스는 거의 풀렸으나, **삽입/조립/체결(peg-in-hole, 커넥터, 나사, 스냅핏)** 은 여전히 미해결.
- **돈이 새는 지점:** 산업 로봇 셀 1개당 **프로그래밍/통합 인건비 $18,750~$80,000, 150~400시간**. 로봇 본체는 전체 비용의 30~50%일 뿐, 나머지는 통합·프로그래밍·튜닝. 고혼합·소량(High-Mix Low-Volume, HMLV) 라인은 부품마다 재셋업 → **부품당 수일~수주**가 자동화 보급의 진짜 병목.
- **모트가 서는 자리:** 하드웨어가 아니라 **(a) 접촉/힘/촉각 sim2real을 좁히는 알고리즘 + (b) 저비용 촉각·힘 데이터로 부품별 정책을 며칠→수십분으로 줄이는 데이터 엔진**. 촉각 센서(DIGIT) 제조원가 ~$15 → 하드웨어는 커머디티, **지능 레이어가 해자.**
- **경기도 적합:** 제조 중소기업 밀집 + 구조적 노동력 부족(제조 고용 2020~2024 -8.2%, 출력 +12.4%) + 정부 스마트공장 보조금(최대 75%). HMLV 정밀조립(전자·커넥터·소형부품) 실증 파트너 풍부.

---

## 1. 최근 12~24개월 돌파 (Why Now)

### 1.1 조작용 VLA / 파운데이션 모델
- **π0 (Physical Intelligence, 2024):** 사전학습 VLM 위에 flow-matching 액션 헤드. 단일팔·양팔·모바일 매니퓰레이터 등 다종 로봇 데이터로 학습한 범용 제어 모델. 일반화의 새 기준선. ([researchgate π0](https://www.researchgate.net/publication/395364425_p_A_Vision-Language-Action_Flow_Model_for_General_Robot_Control), [SVRC 분석](https://www.roboticscenter.ai/research/foundation-models-robot-manipulation-2025))
- **OpenVLA (Stanford+Berkeley, 2024):** 7B LLaMA-2 + DINOv2/SigLIP 비전 인코더, Open X-Embodiment로 파인튜닝한 대표 오픈웨이트 모델. ([SVRC](https://www.roboticscenter.ai/research/foundation-models-robot-manipulation-2025))
- **RT-X / Open X-Embodiment:** 다종 로봇 10만+ 시연을 묶은 데이터셋·정책 → 교차 임베디먼트 일반화 입증.
- **시사점:** 비전·언어 기반 "무엇을 할지(semantic)"는 빠르게 좋아짐. 그러나 **"접촉 순간 힘을 어떻게 줄지(physical contact dynamics)"** 는 카메라만으로 안 풀림 → 촉각·힘 모달리티 + 물리가 다음 전장. ([Forceful Robotic Foundation Models survey, 2025](https://arxiv.org/pdf/2504.11827))

### 1.2 접촉 시뮬레이션·sim2real 가속 (이게 핵심 인에이블러)
- **TacSL (NVIDIA):** GPU 기반 비주오택타일 이미지 + 접촉-힘장(contact-force field) 시뮬을 **이전 SOTA 대비 200배 가속**. → 촉각 데이터를 시뮬에서 대량 생성 가능해짐. ([NVIDIA R²D²](https://developer.nvidia.com/blog/r2d2-unlocking-robotic-assembly-and-contact-rich-manipulation-with-nvidia-research/))
- **Isaac Lab (2025):** GPU 가속 멀티모달 로봇러닝 프레임워크 — 대규모 도메인 랜덤화·병렬 RL 표준화. ([arxiv 2511.04831](https://arxiv.org/pdf/2511.04831))
- **TACTO / Taxim / Tacchi 2.0 / SimTac:** 비전기반 촉각센서(GelSight/DIGIT) 시뮬레이터 계열 발전. ([Tacchi 2.0](https://arxiv.org/pdf/2503.09100), [SimTac](https://arxiv.org/pdf/2511.11456))
- **R²D² (NVIDIA, 2025):** 조립·접촉리치 매니퓰레이션을 시뮬→실 전이로 풀기 위한 연구 스택 공개. ([Edge AI Vision](https://www.edge-ai-vision.com/2025/05/r%C2%B2d%C2%B2-unlocking-robotic-assembly-and-contact-rich-manipulation-with-nvidia-research/))

### 1.3 데이터 효율·잔차(residual)·힘 인지 정책 (난제를 정조준한 최신 논문 군집)
- **SRSA (ICLR 2025 Spotlight):** 조립 스킬 라이브러리에서 가장 적합한 사전정책을 골라 재사용·파인튜닝 → **신규 과제 성공률 +19%, 샘플 2.4배 감소, 실세계 평균 성공률 90%.** ([R²D² 블로그 내 인용](https://developer.nvidia.com/blog/r2d2-unlocking-robotic-assembly-and-contact-rich-manipulation-with-nvidia-research/))
- **EasyInsert (2025):** 데이터 효율·일반화 삽입 정책. ([arxiv 2505.16187](https://arxiv.org/pdf/2505.16187))
- **SPARR (2026):** 시뮬 정책 + 비대칭 실세계 잔차(admittance residual) 온라인 학습으로 조립 sim2real 효율화. ([arxiv 2602.23253](https://arxiv.org/pdf/2602.23253))
- **Compliant Residual DAgger (NeurIPS 2025):** 인간 보정으로 접촉리치 조작 개선.
- **FORGE (2024):** 힘 임계값 + 동역학 랜덤화로 위치 불확실성 하에서도 안전 탐색하는 sim2real 정책. ([arxiv 2408.04587](https://arxiv.org/pdf/2408.04587))
- **Direction Matters (CVPR 2025):** "힘의 방향"을 학습하면 sim2real 접촉리치 조작이 풀림 → 힘 모달리티의 중요성 입증. ([arxiv 2602.14174](https://arxiv.org/pdf/2602.14174))
- **Zero-Shot Sim2Real Dexterous Force-Based Grasping (2026):** 촉각 + 관절토크(모터전류 근사) 관측공간 설계로 제로샷 전이. ([arxiv 2601.02778](https://arxiv.org/html/2601.02778v1))

### 1.4 촉각 하드웨어의 커머디티화 (모트가 SW로 이동하는 이유)
- **DIGIT 제조원가 ~$15/개**(1000개 배치: PCB $1.5 + 전자부품 $8 + 플라스틱 $2 + 젤 $3), 공구리스·COTS 부품 설계로 양산 용이. **소비자가 $350.** ([DIGIT 논문](https://arxiv.org/pdf/2005.14679), [SVRC 비교](https://www.roboticscenter.ai/learn/tactile-sensor-comparison))
- **GelSight Mini $499**, GelSlim 3.0 재료비 ~$122. DIGIT·GelSlim·9DTact 등 **오픈소스 하드웨어 다수** → 하드웨어 자체는 진입장벽이 아님. ([SVRC](https://www.roboticscenter.ai/learn/tactile-sensor-comparison))
- **Sensor-Invariant Tactile Representation (2025), Large-scale Deployment on Multi-fingered Grippers (2024):** 센서 종류·개체 변동을 흡수하는 표현학습이 새 연구축. ([arxiv 2502.19638](https://arxiv.org/pdf/2502.19638), [arxiv 2408.02206](https://arxiv.org/pdf/2408.02206))

---

## 2. 풀리지 않은 난제 (여기서 10배가 나온다)

| 난제 | 현황 | 왜 어려운가 |
|---|---|---|
| **촉각 sim2real gap** | 비전기반 촉각센서의 큰 sim2real gap이 시뮬 학습 스킬의 실전 전이를 막음. 젤·제조 편차로 실 DIGIT 거동 불일치. | 광학·접착탄성체 물리+전자노이즈 풀 모델링 비현실적, 개체별 편차. ([researchgate Sim2Real Tactile RL](https://www.researchgate.net/publication/382987316), [ManiSkill-ViTac 2025](https://arxiv.org/pdf/2411.12503)) |
| **접촉리치 정밀 조작** | 삽입·기어물림·나사체결·스냅핏은 마찰·컴플라이언스·정렬을 불확실성 하에 정밀 제어해야 함 — 픽앤플레이스와 차원이 다름. | 위치 추정 오차 < 부품 공차 시 카메라만으로 불가, 힘/촉각 피드백 필수. ([Imitation Learning for Contact-Rich survey 2025](https://arxiv.org/pdf/2506.13498)) |
| **데이터 병목** | "데이터 딜레마": 비표준·저품질·양 부족. 효율적 data flywheel 구축 + sim2real이 최우선 과제. | 실 로봇 시연 수집 비용 큼, 소스간 통합 불가, 모델 요구량 대비 절대 부족. ([Manipulation Survey 2510.10903](https://arxiv.org/pdf/2510.10903)) |
| **일반화** | 학습 안 한 객체·장면으로의 전이가 모트. 사전학습 10만+ 시연이 주 메커니즘. | 접촉 동역학은 객체·표면마다 달라 비전 일반화보다 어려움. |
| **배포 시간(상업적 난제)** | 셀당 프로그래밍 150~400h / $18,750~80,000. HMLV는 부품마다 재셋업. | 통합 SW·튜닝이 진짜 병목, 하드웨어 아님. ([RoboDK/Automate 2025](https://www.automate.org/robotics/news/robodk-...), [Standard Bots](https://standardbots.com/blog/robots-for-manufacturers-a-guide), [IndustryX](https://industryx.ai/2025/12/04/industrial-robots-guide-2025/)) |
| **안전** | 힘 임계·컴플라이언스 없는 접촉은 부품·로봇 손상. | 탐색 중 과도한 힘 방지 학습 필요. ([FORGE](https://arxiv.org/pdf/2408.04587)) |

---

## 3. 시장·플레이어

### 3.1 투자·시장 규모
- **로봇 스타트업 2025년 총 펀딩 $13.8B** (2024 $7.8B에서 급증, 2021 피크 $13.1B 상회). 데이터가 주된 모트로 부상 — 독점 데이터로 학습한 정책이 공개데이터 대비 우월. ([Crunchbase/SVRC](https://www.roboticscenter.ai/research/robot-manipulation-market-landscape-2025))
- **한국 공장자동화·산업제어 시장:** 2025 $9.14B → 2031 $13.21B, CAGR 6.34%. ([Mordor](https://www.mordorintelligence.com/industry-reports/south-korea-factory-automation-and-industrial-controls-market))

### 3.2 주요 플레이어 (지능 레이어)
- **Physical Intelligence (π0):** Sergey Levine 등, 밸류 $2.4B→$5.6B→**$11B**(4개월 만에 2배). 범용 VLA. ([The Elec](https://www.thelec.net/news/articleView.html?idxno=6214), [Sacra](https://sacra.com/c/physical-intelligence/))
- **Skild AI:** "omni-bodied" 통합 파운데이션 모델, 매출 0→$30M(수개월), 밸류 **$14B**. 보안·물류·제조·데이터센터. ([Crunchbase](https://news.crunchbase.com/venture/robotics-startup-skild-ai-triples-valuation/), [Robot Report](https://www.therobotreport.com/skild-ai-raises-1-4b-building-omni-bodied-robot-skild-brain/))
- **Figure AI:** 휴머노이드 최대 펀딩, $39B 밸류. (하드웨어 중심 — 본 트랙 금지영역과 대비)

### 3.3 공백 (우리가 들어갈 틈)
거대 플레이어는 **범용·휴머노이드·픽앤플레이스 일반화**에 집중. **HMLV 산업 정밀조립의 접촉리치 sim2real + 부품별 빠른 배포**라는 좁고 깊은 수직은 상대적으로 비어 있음. 범용 모델은 0.1mm급 커넥터 삽입을 셀별로 며칠 내 세우지 못함. → **수직 특화 데이터 엔진 + 힘/촉각 sim2real 모트**로 진입 가능.

---

## 4. 한국·경기도 실증 레버리지

- **구조적 노동력 부족:** 제조 고용 2020~2024 **-8.2%**, 출력 **+12.4%**. 합계출산율 0.72(2025) → 최소 10년 지속될 구조적 부족 → 자동화 절박. ([Medium/robot density](https://medium.com/@creed_1732/...), [trade.gov](https://www.trade.gov/country-commercial-guides/south-korea-manufacturing-technology-smart-factory))
- **정부 보조:** 중기부 2026 스마트제조혁신 ~450개 프로젝트(자율공장 30 + AI특화 400). 스마트공장+ **최대 75% 보조·세액공제**, SME 페이백 18개월 미만으로 단축. ([MSS](https://www.mss.go.kr/site/eng/ex/bbs/View.do?cbIdx=244&bcIdx=1062921), [trade.gov](https://www.trade.gov/country-commercial-guides/south-korea-manufacturing-technology-smart-factory))
- **경기도 자산:** 제조 중소기업 밀집(스마트제조·로봇 실증), 수원·화성 삼성 반도체, 이천 SK하이닉스, 판교 AI·ICT, 차세대융합기술연구원. 전자·커넥터·소형 정밀부품 HMLV 라인이 실증 파트너로 풍부.
- **로봇 밀도 세계 1위** 한국 → 본체는 이미 깔림, **지능·재배포 레이어 수요**가 큼.

---

## 5. 딥테크 모트 가설 (Phase 1 발산의 씨앗)

1. **힘/촉각 sim2real을 좁히는 잔차·도메인적응 알고리즘** (커머디티 촉각센서 위) — 부품별 정책을 시뮬에서 만들고 실세계 소량 보정으로 며칠→수십분.
2. **접촉리치 조작 전용 데이터 엔진** — 저비용 촉각/힘 시연 + 시뮬 대량생성(TacSL류) + 자동 잔차 라벨링으로 data flywheel.
3. **센서-불변 촉각 표현** — 센서·개체 편차를 흡수해 전이 비용 절감, 데이터 재사용성↑.
4. **힘-인지 안전 탐색 정책** — 부품 손상 없이 self-improve.

→ 공통 본질: **"이미 깔린 로봇팔 + $15짜리 촉각센서 위에서, 0.1mm급 접촉 조작을 부품마다 수일이 아니라 수십분에 세우는 지능 레이어."** 하드웨어 양산 없음, 모트는 알고리즘·데이터·물리.

---

## 6. 출처 목록 (주요)
- π0: researchgate.net/publication/395364425 · SVRC foundation-models-robot-manipulation-2025
- OpenVLA/RT-X: roboticscenter.ai/research/foundation-models-robot-manipulation-2025
- Forceful Robotic Foundation Models survey: arxiv.org/pdf/2504.11827
- TacSL/R²D²: developer.nvidia.com/blog/r2d2-... · edge-ai-vision.com/2025/05/r²d²-...
- Isaac Lab: arxiv.org/pdf/2511.04831
- SRSA / EasyInsert / SPARR / FORGE / Direction Matters / Zero-Shot Force Grasping: arxiv 2505.16187, 2602.23253, 2408.04587, 2602.14174, 2601.02778
- 촉각 sim2real: arxiv 2411.12503, 2503.09100, 2511.11456, researchgate 382987316
- 촉각 하드웨어 원가: arxiv.org/pdf/2005.14679 (DIGIT) · roboticscenter.ai/learn/tactile-sensor-comparison
- 센서불변 표현/대규모배포: arxiv 2502.19638, 2408.02206
- 배포비용: standardbots.com/blog/robots-for-manufacturers-a-guide · industryx.ai/2025/12/04 · automate.org RoboDK
- 시장/펀딩: roboticscenter.ai/research/robot-manipulation-market-landscape-2025 · Crunchbase Skild · thelec.net 6214 · sacra.com
- 한국/경기 제조·보조: trade.gov SK smart factory · mss.go.kr 2026 program · mordorintelligence SK factory automation
- 데이터 딜레마/일반화: arxiv.org/pdf/2510.10903 · 2506.13498
