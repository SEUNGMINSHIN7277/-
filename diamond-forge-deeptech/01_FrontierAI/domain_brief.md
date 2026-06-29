# Phase 0 — Domain Brief: Frontier AI Systems (딥테크 트랙)

> 작성일 2026-06-29 · 오케스트레이터: Frontier AI Systems 트랙
> 모든 수치는 출처 URL 동반. 추정/가설은 [가설] 표기.

---

## A. 최근 12~24개월 Frontier AI 기술 돌파 (논문/오픈소스/특허)

### A1. Test-time compute / 추론시점 연산 (가장 뜨거운 패러다임 전환)
- **DeepSeek-R1 (2025.01):** 순수 RL(outcome reward)로 o1급 추론 획득 증명. 쿼리당 토큰 10~100배 생성해 정확도 상승. 소형 모델도 test-time scaling으로 capacity 한계 보상 가능.
  - 출처: https://arxiv.org/pdf/2504.09037 (Survey of Frontiers in LLM Reasoning)
- **핵심 인사이트:** "파라미터 스케일링보다 test-time compute 스케일링이 더 효율적일 수 있다" — 작은 모델 + 더 오래 생각 = 큰 모델 대체 가능. 단, **토큰 10~100배 = 비용·지연 10~100배**가 곧 새로운 하드 난제.
  - 출처: https://introl.com/blog/inference-time-scaling-research-reasoning-models-december-2025
- **P1 Physics Model (2025.11):** 오픈소스로 IPhO 금메달급. 추론 모델의 도메인 침투 가속.

### A2. Test-time training / 메모리를 가진 새 아키텍처 (트랜스포머 그 이후)
- **Titans (Google, 2501.00663):** Neural Long-Term Memory Module — forward pass 중 자기 가중치를 경사하강으로 갱신("surprise" metric + momentum + adaptive forgetting). 2M+ 컨텍스트에서 GPT-4/Llama-3-RAG 능가.
  - 출처: https://arxiv.org/pdf/2501.00663
- **ATLAS (2505.23735), Nested Learning (2512.24695), Test-Time Training is Secretly Linear Attention (2602.21204):** test-time weight update 계열 폭발. 트랜스포머의 2차 attention 비용/장기메모리 부재를 정면 공격.
- **시사:** "추론 중 학습"은 신규 메커니즘 — 단순 LLM 래퍼로 복제 불가. 단 풀스케일 사전학습은 자본집약 → **레이어/모듈/적용 도메인**에서 모트 찾아야.

### A3. 온디바이스/엣지 추론 압축 (배포 경제학의 핵심 병목)
- **KV-cache 압축 폭발:** XQuant(K/V 대신 입력 액티베이션 캐시 후 재계산, 메모리 1/2), xKV(cross-layer SVD), LogQuant(2-bit), WindowKV, Cocktail(chunk-adaptive mixed precision).
  - 출처: https://blog.openvino.ai/blog-posts/q325-technology-update---low-precision-and-model-optimization
  - 출처: https://github.com/HuangOwen/Awesome-LLM-Compression
- **온디바이스 파인튜닝 돌파(2025~2026):** 모바일 GPU 최초 성공. Llama-3.2 3B + LoRA + 2048 ctx를 26.20GB → **1.02GB**까지. 12GB RAM 스마트폰에 온디바이스 personalization.
  - 출처: https://arxiv.org/html/2606.19528v1 (Peak Memory Reduction for LoRA on Edge)
  - 출처: https://arxiv.org/html/2512.08211v1 (MobileFineTuner)
- **EdgeLoRA (2507.01438):** 엣지에서 멀티테넌트 LLM 서빙(다수 user-adapter 동시).

### A4. 추론 가속 (speculative decoding의 생산표준화)
- **2025 = speculative decoding이 연구→생산표준.** vLLM/TensorRT-LLM/SGLang 모두 탑재. EAGLE-3(타깃 내부 레이어에 경량 헤드, 별도 draft 모델 불필요, 수락률 ~80%).
  - 출처: https://introl.com/blog/speculative-decoding-llm-inference-speedup-guide-2025
  - 출처: https://developer.nvidia.com/blog/an-introduction-to-speculative-decoding-for-reducing-latency-in-ai-inference/
- **핵심 발견:** draft 모델의 LM 정확도보다 **지연(latency)**이 throughput을 더 결정. → 도메인특화 초경량 draft에 기회.
  - 출처: https://arxiv.org/pdf/2510.20064 (Not-a-Bandit)

### A5. 에이전트 지속학습·장기메모리 (catastrophic forgetting)
- **SDFT (MIT/ETH 2025):** Self-Distillation Fine-Tuning — 단일 모델이 이전 능력 회귀 없이 다중 스킬 축적.
- **컨텍스트/외부메모리 큐레이션 계열:** weight-update 회피, 외부 메모리에 무엇을 남길지 학습. ProcMEM(non-parametric PPO 절차메모리), Hindsight 20/20(retain/recall/reflect 메모리).
  - 출처: https://github.com/Wang-ML-Lab/llm-continual-learning-survey
  - 출처: https://arxiv.org/pdf/2512.12818
- **반직관 발견:** decoder-only LLM은 **모델이 클수록 forgetting 악화**(1B~7B). Phi-3.5-mini는 최소 forgetting → **소형 엣지 모델이 지속학습에 오히려 유리**.
  - 출처: https://arxiv.org/abs/2504.01241

### A6. 기계적 해석가능성 (interpretability → production safety)
- **SAE 기반 steering 생산화:** code correctness 방향 추출→에러알람/선택적 개입, CB-SAE(해석성 +32.1%·조종성 +14.5%), 탈독성(Breaking Bad Tokens).
  - 출처: https://arxiv.org/pdf/2506.05451 (Interpretation Meets Safety Survey)
  - 출처: https://arxiv.org/abs/2512.10805 (Concept Bottleneck SAE)

---

## B. 아직 풀리지 않은 하드 기술 난제 (= 딥테크 모트 후보)

1. **추론모델 비용·지연 폭발:** test-time compute는 토큰 10~100배 → 온프레미스/엣지/실시간에서 경제성 붕괴. "정확도는 추론모델, 비용은 1B 모델" 동시 달성이 미해결.
2. **장기메모리 vs 망각의 트레이드오프:** 에이전트가 수주간 사용자/프로젝트 맥락 유지하려면 weight update는 forgetting, context는 비용폭발. test-time memory의 **안정성·검증가능성**이 미해결.
3. **온디바이스 개인화의 프라이버시-성능-메모리 3중 제약:** 로컬 적응은 가능해졌으나 (a)연속 학습 안정성 (b)다수 user-adapter 효율 서빙 (c)검증된 프라이버시(DP)의 동시충족이 미해결.
4. **추론모델의 검증가능성/신뢰성:** 더 오래 생각해도 hallucination·오류 누적. 추론 trace의 **선택적 개입·자기검증**(interpretability×reasoning)이 미해결.
5. **규제·주권 AI 시대의 온프레미스 추론 효율:** 한국 AI기본법·데이터주권으로 클라우드 못 쓰는 기관 급증 → "내 서버/내 디바이스에서 도는 추론급 지능"의 단위경제가 미해결.

---

## C. 시장·플레이어

- **추론/엣지 추론 인프라:** vLLM·SGLang·TensorRT-LLM(서버), llama.cpp·MLC·ONNX Runtime(엣지). 압축은 대부분 오픈소스 → **순수 압축 라이브러리는 모트 약함(래퍼 위험)**. 모트는 *도메인특화 데이터+학습된 정책*에 있어야.
- **온디바이스:** Apple Intelligence, Qualcomm AI Hub, 삼성 Gauss/온디바이스. → **칩벤더 종속 위험**, but 펌웨어/컴파일러/적응 레이어에 빈틈.
- **에이전트 메모리:** Mem0, Letta(MemGPT), Zep 등 스타트업 난립 — 대부분 벡터DB+휴리스틱(=래퍼 위험 높음). **학습된(파라메트릭) 메모리**는 미개척.
- **주권/온프레미스 추론:** 규제 산업(금융·의료·공공·국방)이 폭발 수요. 한국은 정책 드라이브 강함.

## D. 한국·경기도 레버리지 (Why Korea, Why Gyeonggi)

- **AI기본법 2026.1.22 시행:** EU 다음 세계 2번째 종합 AI법. 스타트업 지원·데이터센터·학습데이터 제공·표준화 명시. **데이터주권/온프레미스 수요 정책적 촉진**.
  - 출처: https://www.cooley.com/news/insight/2026/2026-01-27-south-koreas-ai-basic-act-overview-and-key-takeaways
- **주권 AI 대규모 투자:** MSIT가 Naver·SKT·LG·NCSoft·Upstage 5개 컨소시엄 선정($381M). 2027까지 GPU 50만장 계획, 2030까지 데이터센터 50곳·2GW.
  - 출처: https://introl.com/blog/south-korea-735b-sovereign-ai-initiative-infrastructure-requirements-opportunities
  - 출처: https://www.msit.go.kr/eng/bbs/view.do (Korea AI Basic Act)
- **경기도 자산:** 판교 테크노밸리(AI·ICT 본진, 가천대 인접), 용인·평택 반도체 클러스터(엣지 추론 칩 파트너), 차세대융합기술연구원(공동연구·자문), 경기도 제조 중소기업 밀집(온프레미스 추론 실증 고객풀).

---

## E. 트랙 전략 결론 (Phase 1 발산 방향 설정)

이 팀(AI/ML·데이터·풀스택 강함, 하드웨어 양산 불가, 4인 학생+자문)에게 **빌더블 + 방어가능**한 교집합은:

> **"test-time compute / test-time memory" 패러다임 × "온프레미스·엣지 효율" 병목 × "규제·주권 데이터" 수요**

순수 압축 라이브러리(오픈소스 즉복제=래퍼), 풀스케일 신아키텍처 사전학습(자본집약), 칩 양산(불가)은 회피.
**학습된 정책/적응 레이어/도메인 데이터 플라이휠**에 모트를 둔 소프트웨어 딥테크로 좁힌다.
