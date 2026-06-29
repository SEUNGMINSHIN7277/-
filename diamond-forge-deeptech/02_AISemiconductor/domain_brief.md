# Domain Brief — AI × Semiconductor 딥테크 트랙 (Phase 0)

> 작성일 2026-06-29. 모든 주장에 출처 URL. "가설"은 명시. 최근 12~24개월 돌파 중심.

---

## A. 기술 돌파 지형 (최근 12~24개월, 논문/특허/제품)

### A1. ML 기반 아날로그·RF 설계자동화 (가장 뜨거운 전장)
- **데이터 희소성이 핵심 병목.** AMS(아날로그·믹스드시그널) ML은 IC 설계 데이터 부족·IP/보안 문제·라벨링 비용으로 발목. SPICE 시뮬은 DAC 1개에 ~30분, 복잡 회로는 수일 → 대규모 학습셋 생성 자체가 난제. (https://arxiv.org/pdf/2507.06538, https://arxiv.org/html/2601.19439v1)
- **Few-shot / GNN 사전학습이 돌파구.** CircuitGPS(few-shot 기생효과 예측), Pretraining GNN for few-shot analog modeling, DICE(device-level GNN contrastive pretraining), ParaGraph(기생-aware GNN). (https://arxiv.org/abs/2507.06538, https://arxiv.org/pdf/2203.15913, https://arxiv.org/pdf/2502.08949, https://ieeexplore.ieee.org/document/9474253/)
- **신규 신경 시뮬레이터.** INSIGHT(autoregressive transformer 아날로그 universal neural simulator, DAC 2025), Alpha-RF(neural simulator + RL, 수치솔버 대비 최대 5자리수 가속), MAPES(AI용 멀티포트 EM 시뮬레이터). (https://arxiv.org/pdf/2603.00104, https://arxiv.org/pdf/2511.21274)
- **LLM/에이전트 흐름(주의: 래퍼 위험).** AnalogMaster, AnalogAgent, AMSnet-KG, ACDC — LLM을 EDA에 붙이는 시도. 핵심 가치가 LLM API에만 있으면 래퍼 킬 대상. (https://arxiv.org/html/2604.20916v1, https://arxiv.org/pdf/2603.23910, https://arxiv.org/html/2512.09199)
- **레이아웃 합성/플로어플랜.** RGNN+RL 아날로그 플로어플래닝(DATE 2025), 파라사이트-aware sizing(GNN+Bayesian opt). (https://www.preprints.org/manuscript/202503.2119)

### A2. 아날로그 IP 마이그레이션 / 공정노드 리타게팅 (저평가된 하드 니치)
- **여전히 수작업.** 아날로그는 소자 물리·기생·글로벌 공정제약에 극도로 민감 → 노드 이전(리타게팅)이 느리고 자원집약적, 대부분 수동. 디지털은 자동화됐지만 아날로그는 "커스텀 수작업" 잔존. (https://semiengineering.com/accelerating-analog-design-migration/, https://thalia-da.com/resources/cdnlive-analog-ip-reuse-process-migration-challenges-an-innovative-methodology-to-address-them/)
- **팹 용량 위기가 수요 증폭.** 팹리스/ASIC社가 멀티 파운드리 평가 강제됨 → IP를 여러 PDK로 이식 필요성 폭증. (https://www.eenewseurope.com/en/process-agnostic-analog-ip-tackles-fab-capacity-challenges/)
- Synopsys도 transfer learning으로 PDK 간 재구성 추론 진입(거대 경쟁자 존재 = 시장 검증 + 차별화 필요). (https://www.synopsys.com/blogs/chip-design/ai-driven-analog-digital-node-migration.html)

### A3. 인메모리/엣지 AI 컴퓨팅 SW·컴파일러·런타임
- **비이상성(non-idealities) 보정이 모트.** AIMC(PCM/ReRAM crossbar)의 MVM은 부정확 — 가중치 프로그래밍 노이즈, 드리프트, IR drop, DAC/ADC 양자화. per-array calibration + chip-in-the-loop fine-tuning으로 정확도 유지. (https://arxiv.org/pdf/2505.02314, NeuroSim V1.5)
- IBM 아날로그 칩 >12 TOPS/W, 토큰단위 LLM 추론. 신경망→크로스바 컴파일 문제 존재. (https://arxiv.org/pdf/2003.04293)
- **양산 의존 위험:** 칩 자체 제작은 4인팀 불가 → SW/컴파일러/보정 레이어만이 빌더블.

### A4. 수율·결함·열·신뢰성 물리 ML
- 물리정보 ML로 반도체 결함레벨 예측(물리적으로 valid, Wiley 2026), SEM 결함→전기적 fail 예측(Gradient Boosting), 2-step ML 수율예측. (https://advanced.onlinelibrary.wiley.com/doi/10.1002/adts.202501721, https://pmc.ncbi.nlm.nih.gov/articles/PMC12252516/, https://www.tandfonline.com/doi/full/10.1080/00207543.2025.2601804)
- **데이터 접근성 문제:** 실제 fab 공정 데이터는 삼성/하이닉스 내부 → 학생팀 접근 난망(경기도 파트너 필요).

### A5. 칩렛/패키징·테스트 최적화
- 열저항 예측(BP NN, Nature Sci Rep 2026), RL 마이크로채널 최적화(열저항 31%↓), 멀티에이전트 RL 칩렛 배치(TDPNavigator), 멀티피델리티 열모델(MFIT), 3DI 디지털트윈. (https://www.nature.com/articles/s41598-026-40640-1, https://arxiv.org/pdf/2602.11187, https://arxiv.org/pdf/2410.09188, https://arxiv.org/pdf/2601.23226)
- 적응형 테스트: 테스트비용 34%↓, fail 인식 99%+, test escape 90%↓; 아날로그/RF underkill 감소 outlier detection. (https://www.sciencedirect.com/science/article/abs/pii/S0167926025000586, https://ieeexplore.ieee.org/document/10140005/)

---

## B. 중소 팹리스·소부장·OSAT 하드 기술 난제 (첫고객 페인)
1. **아날로그/RF 설계 인력 부족 + SPICE 시뮬 비용.** 베테랑 아날로그 설계자 1명 양성에 10년+. 시뮬 1회 수십분~수일 → 설계 반복(iteration) 횟수가 곧 비용·일정.
2. **노드/파운드리 이전 시 아날로그 IP 전면 재설계.** 멀티파운드리 전략 강제됨에도 마이그레이션은 수동·고위험.
3. **소량다품종 팹리스는 EDA 라이선스(Cadence/Synopsys) 고가.** 대형사 전용 AI EDA 혜택에서 배제됨.
4. **fab 데이터 사일로.** 수율/결함 ML은 데이터 없는 외부팀에 닫혀 있음.
5. **검증/테스트 비용.** 아날로그 test escape(underkill)로 고객 반품 리스크.

→ **빌더블 + 모트 동시충족 스윗스팟: A2(아날로그 IP 마이그레이션) ⊕ A1(데이터생성/대리모델).** 칩 양산 불필요(순수 SW+데이터+물리모델), 페인 명확, 데이터 모트 구축 가능, 거대사가 못 챙기는 소량다품종 팹리스 롱테일.

---

## C. 시장·플레이어
- **거대 EDA:** Synopsys(2025 Analog In-Memory Computing 혁신리더, AI 노드 마이그레이션), Cadence, Keysight(mmWave). → 대형 고객·풀스택 타겟. 소량다품종·신흥 PDK·롱테일은 사각지대(가설).
- **스타트업/학계:** Thalia(아날로그 IP reuse), 다수 arXiv 연구팀(아직 제품화 전). 신경 시뮬레이터/few-shot은 학술단계 → 제품화 공백.
- **TAM(가설):** EDA 전체 ~$15B+('25, 가설), 아날로그/AMS EDA는 그 중 상당 부분. 아날로그 마이그레이션·시뮬 가속 SAM은 수억$ 규모(가설, 정밀화 필요).

## D. 한국·경기도 반도체 정책 레버리지
- **경기 반도체 메가클러스터:** 성남~수원~화성~용인~안성~평택~이천. 생산+연구+인재+소부장 생태계. (https://v.daum.net/v/20251112084447945)
- **용인 클러스터:** SK하이닉스 팹4 + 소부장 협력단지. (https://news.skhynix.co.kr/2026-expert-column-series-ep5/)
- **판교 팹리스 클러스터 + 경기도 팹리스 아카데미(제1판교):** 팹리스 설계인력 양성, 가천대·명지대·경기대 연계. ← **팀(가천대)과 직결: 첫고객·자문·인력·데이터 파이프라인.** (검색결과 요약)
- **정부 3S+1F 전략:** 수요·상생·보안 + 전폭지원. 소부장·중소 생태계 명시 → 소량다품종 팹리스 지원 정책 바람.

## E. 래퍼 함정 경고 (이 트랙 특유)
- LLM-to-EDA(AnalogMaster/AnalogAgent류)는 "GPT로 netlist 짜기" 수준이면 **래퍼 킬 즉살.** 모트는 반드시 (1) 자체 생성/축적한 회로-기생-공정 데이터, (2) 물리정보 대리모델/보정 알고리즘, (3) 노드 간 디바이스 물리 매핑 알고리즘에 있어야 함.
