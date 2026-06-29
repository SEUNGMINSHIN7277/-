# Phase 1 — 딥테크 원석 (Raw Ideas) · Frontier AI Systems

> 규칙: 각 원석은 (a) 한 줄 (b) 어떤 최근 기술 돌파에 기반 (c) 모트 가설 (d) 빌더블 여부. 앱/래퍼 금지.
> 28개. Phase 2에서 Gate C 래퍼 킬 + 과학 킬로 컬링.

---

### 그룹 I — Test-time compute 효율 (추론모델 비용·지연 붕괴 해결)

1. **Adaptive Compute Router (ACR)** — 쿼리 난이도를 예측해 토큰예산/추론깊이를 동적 할당하는 *학습된 라우터*. 기반: test-time scaling(R1). 모트: 난이도→최적예산 매핑 학습 데이터. 빌더블: O.
2. **Reasoning Distillation Engine** — 큰 추론모델의 trace를 1~3B에 distill하되 도메인별 자동 커리큘럼. 기반: R1 distill. 모트: 자동 커리큘럼 알고리즘. 빌더블: O.
3. **Verifier-guided early-exit** — 추론 trace 중간을 SAE/verifier로 점검해 충분하면 조기종료(토큰 절감). 기반: interp×reasoning. 모트: verifier 학습. 빌더블: O.
4. **Speculative reasoning** — draft 모델이 추론 trace를 미리 깔고 타깃이 검증(speculative decoding의 추론 trace 확장). 기반: EAGLE-3. 모트: trace-level draft 정책. 빌더블: O(난이도↑).
5. **Self-consistency budget optimizer** — N-샘플 self-consistency에서 언제 멈출지 학습. 기반: TTS. 모트: 정지정책. 빌더블: O.
6. **On-prem reasoning compiler** — 추론모델을 특정 GPU/NPU에 KV압축+spec-decoding+예산라우팅 통합 컴파일. 기반: A3+A4. 모트: 통합 컴파일러+정책. 빌더블: △(엔지니어링 무거움).

### 그룹 II — Test-time memory / 지속학습 (forgetting 해결)

7. **Parametric Agent Memory (PAM)** — 에이전트의 장기메모리를 벡터DB가 아니라 *test-time weight update*(Titans식 surprise gating)로 구현, 검증가능한 롤백. 기반: Titans/ATLAS. 모트: 안정적 surprise-gating+롤백 알고리즘. 빌더블: O.
8. **Continual edge personalizer** — 온디바이스에서 user-adapter(LoRA)를 forgetting 없이 연속갱신. 기반: 온디바이스 파인튜닝+SDFT. 모트: 안정화 학습레시피+데이터. 빌더블: O.
9. **Memory consolidation scheduler** — "수면 중 통합"처럼 유휴시 메모리를 파라미터로 증류. 기반: SDFT+nested learning. 모트: 증류 스케줄러. 빌더블: O.
10. **Forgetting-as-a-feature (GDPR/AI기본법 삭제권)** — 학습된 메모리에서 특정 사용자/사실만 검증가능하게 제거(machine unlearning). 기반: unlearning+SAE. 모트: 검증가능 unlearning. 빌더블: O.
11. **Multi-tenant adapter server** — 한 베이스+수천 user-adapter를 엣지/온프렘에서 효율 서빙. 기반: EdgeLoRA. 모트: 서빙 스케줄러. 빌더블: O(but Mem0류 경쟁).

### 그룹 III — 온디바이스/엣지 효율 (배포 경제학)

12. **Domain-specific draft model factory** — 산업/언어별 초경량 draft 모델 자동 생성(한국어·금융·의료). 기반: spec-decoding latency 발견. 모트: 도메인 draft 학습 파이프라인+수락률 데이터. 빌더블: O.
13. **KV-cache policy learner** — eviction/quantization 정책을 워크로드별로 학습(휴리스틱 대신). 기반: KV압축 폭발. 모트: 학습된 정책. 빌더블: O.
14. **Edge reasoning runtime (Korea-sovereign)** — 추론모델을 온프렘 단일 GPU/NPU에서 도는 통합 런타임(압축+spec+라우팅). 기반: A3+A4+규제. 모트: 통합+한국어 도메인데이터. 빌더블: △.
15. **NPU-aware compiler for SLM** — 국산/엣지 NPU(리벨리온·퓨리오사 등)에 추론모델 컴파일. 기반: 압축+컴파일러. 모트: NPU별 커널. 빌더블: △(파트너 필수).
16. **Activation-cache reasoning (XQuant for CoT)** — 긴 CoT에서 K/V 대신 액티베이션 캐시·재계산으로 메모리 1/2. 기반: XQuant. 모트: CoT 특화 재계산 스케줄. 빌더블: O.

### 그룹 IV — Interpretability × 신뢰성 (검증가능 추론)

17. **Reasoning watchdog (SAE 기반)** — 추론 trace 내부 표현을 실시간 모니터해 hallucination/규정위반 방향 탐지·개입. 기반: SAE steering. 모트: 도메인 feature 사전+개입정책. 빌더블: O.
18. **Compliance steering layer** — 금융/의료 규정 위반 출력을 활성화 단계에서 차단·교정(필터 아님). 기반: CB-SAE. 모트: 규정 concept 사전. 빌더블: O.
19. **Interpretability-based eval** — 모델 내부로 답변 신뢰도 정량화(불확실성). 기반: SAE. 모트: 신뢰도 보정 데이터. 빌더블: O.

### 그룹 V — 신규 메커니즘/와일드카드

20. **Latent context compiler** — 긴 컨텍스트를 휴대가능한 압축 메모리로 증류(프롬프트 재사용). 기반: Latent Context Compilation(2602.21221). 모트: 증류 알고리즘. 빌더블: O.
21. **Test-time RL for agents** — 배포 후 환경피드백으로 추론정책을 즉석 RL. 기반: R1 RL+TTT. 모트: 안정적 online RL 레시피. 빌더블: △(불안정 위험).
22. **World-model surrogate for ops** — 산업공정/물류의 경량 world model로 시뮬레이션. 기반: world model. 모트: 도메인 시뮬데이터. 빌더블: △.
23. **Diffusion-spec hybrid decoding** — DART식 확산영감 spec decoding. 기반: DART(2601.19278). 모트: 알고리즘. 빌더블: △(연구성 높음).
24. **Cacheback decoding** — 캐시만으로 spec decoding(draft 불필요). 기반: Cacheback(2511.21699). 모트: 약함(논문 즉복제). 빌더블: O but 모트X.
25. **Procedural memory store (ProcMEM)** — 에이전트가 재사용 절차를 non-param 메모리로 축적. 기반: ProcMEM. 모트: 약~중. 빌더블: O.

### 그룹 VI — 통합/제품화 (모트=데이터 플라이휠)

26. **온프레미스 추론 어플라이언스 SW** — 규제기관 자체 서버에 "추론급 SLM"을 효율 배포하는 SW 스택(압축+spec+메모리+컴플라이언스). 기반: A2~A6 통합. 모트: 통합+한국 규제도메인 데이터 플라이휠. 빌더블: O(SW-only).
27. **Privacy-preserving continual SLM for 규제산업** — 온프렘에서 forgetting 없이 기관 데이터로 계속 학습+삭제권. 기반: II+III+unlearning. 모트: 안정화레시피+unlearning+데이터. 빌더블: O.
28. **추론 비용 거버넌스 플랫폼** — 조직의 추론 토큰예산을 ACR로 자동 최적화+감사로그. 기반: I. 모트: 라우터 학습+감사. 빌더블: O but SaaS래퍼 위험.
