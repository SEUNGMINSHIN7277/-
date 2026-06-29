# Phase 0 — Domain Brief (Deep-Tech Wildcard / Frontier)

> 작성일 2026-06-29. 트랙: 예상 밖 딥테크(뉴로모픽/포토닉 SW, 양자 SW, 신규 센싱+AI, 보안·암호 딥테크, 센서퓨전). 모든 수치는 출처 URL 표기. "가설"은 명시.

---

## A. 스캔한 5개 프론티어 전장 + 각 결론

### 1. 보안·암호 딥테크 — 동형암호(FHE) 기반 프라이버시 ML  ★최종 채택 영역
- **돌파(12~24개월, 실재):**
  - GPU 가속 라이브러리 FIDESlib — CKKS bootstrapping **70배+** 가속(2025). [arXiv/관련]
  - FAST FPGA 가속기 — bootstrapping GPU 대비 8.84배, ResNet-20 추론 SOTA FPGA 대비 1.43배(ACM FPGA 2025). https://dl.acm.org/doi/10.1145/3706628.3708879
  - GPU FHEW/TFHE — MNIST 암호화 추론 **0.04초/이미지**(SOTA). https://tches.iacr.org/index.php/TCHES/article/view/11931
  - PowerSoftmax(IBM, FHE.org 2025) — 32층·10억+ 파라미터 다항 LLM 최초. https://research.ibm.com/publications/powersoftmax-towards-secure-llm-inference-over-fhe
  - HEIR(Google, NDSS 2024) — cross-scheme FHE 통합 IR/컴파일러 표현. https://www.ndss-symposium.org/wp-content/uploads/2024-67-paper.pdf
  - Orion — bootstrapping 배치를 DAG 최단경로로 자동화(2025). (arXiv 2604.03425)
- **풀리지 않은 하드 난제(핵심):**
  - FHE는 곱셈 깊이(multiplicative depth)가 비용을 지배. 비선형 함수(ReLU/GELU/Softmax/LayerNorm)는 다항 근사 필요 → **고차 다항=깊이 폭발=bootstrapping 폭증**, **저차 다항=정확도 붕괴**, 입력 범위 벗어나면 발산. 이 트레이드오프가 **현재 미해결 핵심 병목**. https://arxiv.org/pdf/2404.03216 , https://arxiv.org/html/2508.11575
  - 결과: FHE ML 추론은 평문 대비 **약 5자리수(10^5배)** 느림. https://arxiv.org/html/2606.17421v1
  - 즉, **"모델→FHE-friendly 모델"로의 자동 변환(컴파일·재훈련)** 레이어가 비어 있음. 학계 단편 논문은 많으나(QAT+다항 근사, depth-aware bootstrap 배치) **엔드투엔드 자동 툴체인 + 깊이/정확도 공동최적화 알고리즘**은 표준 부재.
- **시장·플레이어:** Privacy-Preserving ML 시장 2025 USD 3.82B → 2030 USD 15.91B (CAGR 32.9%). https://www.360iresearch.com/library/intelligence/privacy-preserving-machine-learning
  - Zama(Concrete ML, FHE 컴파일러·Series B), Duality(Series C USD 175M, 2026.1; Google Cloud Confidential Computing+H100 통합 2025.11), IBM Research, DESILO(韓, PETs). https://www.cbinsights.com/company/zama/alternatives-competitors
  - 빈틈: 기존 플레이어는 (a) 블록체인 온체인 프라이버시(Zama 최근 피벗), (b) MPC/대기업 SI(Duality), (c) 저수준 라이브러리. **"일반 ML팀이 자기 모델을 넣으면 FHE 배포 가능 모델로 자동 변환"하는 깊이최적화 컴파일러+서빙**은 약함.

### 2. 양자 SW — 오류완화(QEM)
- 돌파: ZNE/PEC/classical shadows 일반화, QESEM 등 런타임 수십배 단축(2025). 그러나 **여전히 heuristic·문제특화, 이론적 보장 약함**(WERQSHOP 2025). https://unitary.foundation/assets/WERQSHOP_report.pdf
- **기각 사유:** 24개월 빌더블 약함(실하드웨어 접근·물리 전문성 의존, 수익화 경로 불투명, 4인 학생팀 모트 약함). Gate C-4(빌더블 쐐기) 리스크 큼 → 보류.

### 3. 신규 센싱+AI — mmWave 레이더 생체신호
- 돌파: radarODE(ECG 재구성), 비접촉 낙상·심박, 프라이버시 우위(2024~25). https://arxiv.org/pdf/2408.01672
- **기각 사유:** 가치의 상당부는 센서 HW·신호처리 미들웨어. SW 모트는 있으나 **알고리즘 난이도가 FHE보다 낮고 차별화 좁음**, 데이터 해자 구축에 임상 파트너·시간 큼. 차순위.

### 4. 이벤트카메라/뉴로모픽 비전
- 돌파: SNN optical flow, event-LAB 표준화(2025). https://arxiv.org/pdf/2509.14516
- **기각:** 강한 가치가 뉴로모픽 칩(Loihi 등) 하드웨어와 결합될 때 극대화 → 양산 의존 리스크·시장 협소. 차순위.

### 5. PQC 마이그레이션/크립토-어질리티
- 돌파: NIST FIPS 203/204/205(2024.8), HQC 선정(2025.3), CNSA 2.0 2027 시작. https://csrc.nist.gov/projects/post-quantum-cryptography/post-quantum-cryptography-standardization
- **기각:** 상용 툴 다수(Venafi/Keyfactor/AppViewX) — **스캐닝·인벤토리 SaaS는 래퍼 킬 위험**, 딥테크 알고리즘 모트 약함. Gate C-2 위험.

---

## B. 최종 영역 선정: FHE-friendly 모델 컴파일·서빙 (깊이/정확도 공동최적화)
**왜 wildcard인가:** Frontier AI(아키텍처), 반도체(EDA/칩), Physical AI(로봇), AI4Science(소재) 어느 트랙도 **"암호화된 채로 추론하는 모델을 자동 생성하는 컴파일러·알고리즘"**을 다루지 않음. 보안×ML 교차의 미답 영역.

**왜 이 팀에 맞나:** 핵심 모트가 **알고리즘(다항 근사·QAT·깊이 스케줄링)+컴파일러+서빙 SW** → 칩 양산 0. 기성 GPU(클라우드)·오픈소스 라이브러리(OpenFHE/FIDESlib) 위에서 구동. 팀의 AI/ML(김범수)·풀스택(신승민·송채우) 강점에 정합.

## C. 한국·경기도 인프라·정책 레버리지
- **MyData 2.0(2025.3 시행, 의료·통신 시작 → 2026.6 에너지, 이후 7개 영역 확대):** 개인이 데이터 이동 요청 가능 → **수신측이 민감데이터를 평문 보관 없이 처리**할 강한 수요. https://www.mlex.com/mlex/articles/2309993/
- PIPC 2025 핵심 의제: 전송요구권 기술요건(암호화 다운로드/API). https://www.lexology.com/library/detail.aspx?g=60639d3c-75ad-4f42-b6c8-97304aaa0258
- 금융 혁신금융서비스 520건+(2025.5, MyData·대안신용 다수) → 암호화 협업분석 PoC 토양. https://iclg.com/practice-areas/fintech-laws-and-regulations/korea
- 경기도: 판교(핀테크·AI·보안 기업 밀집), 차세대융합기술연구원·대학 암호/보안 연구실(자문), 경과원 지원망. 韓 딥테크 R&D 그랜트 사업화 6억+R&D 6억 KRW 트랙. https://koreatechdesk.com/korea-ip-protection-infrastructure-13-4b-sme-startups

## D. 핵심 출처 URL
- 비선형 다항 근사 난제: https://arxiv.org/pdf/2404.03216 , https://arxiv.org/html/2508.11575 , https://arxiv.org/html/2605.22237
- FHE LLM/Transformer 추론 SOTA·5자리수 갭: https://arxiv.org/html/2606.17421v1 , https://arxiv.org/html/2602.11470v1
- bootstrapping 가속/배치: https://dl.acm.org/doi/10.1145/3706628.3708879 , https://tches.iacr.org/index.php/TCHES/article/view/11931 , https://arxiv.org/html/2604.03425
- 컴파일러 IR(HEIR): https://www.ndss-symposium.org/wp-content/uploads/2024-67-paper.pdf
- 시장: https://www.360iresearch.com/library/intelligence/privacy-preserving-machine-learning
- 플레이어: https://www.cbinsights.com/company/zama/alternatives-competitors , https://www.zama.ai/post/quantization-of-neural-networks-for-fully-homomorphic-encryption
- 한국 정책: MyData https://www.mlex.com/mlex/articles/2309993/ , PIPC https://www.lexology.com/library/detail.aspx?g=60639d3c-75ad-4f42-b6c8-97304aaa0258
