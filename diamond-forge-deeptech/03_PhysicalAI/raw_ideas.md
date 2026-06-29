# Phase 1 — 원석 (Raw Ideas) · Physical AI 트랙

> 규칙: 래퍼·앱·텔레오퍼레이션·하드웨어 양산 금지. 모트가 알고리즘/모델/데이터/물리에 있는 딥테크 원석만. 26개.

## A. 촉각/힘 sim2real & 데이터 엔진
1. **TactileBridge** — 커머디티 촉각센서($15 DIGIT급) 위 sim2real gap을 좁히는 잔차+도메인적응 모델. 시뮬로 정책 생성 후 실세계 소량(수십회) 보정으로 부품별 삽입 정책을 수십분 내 완성.
2. **ContactForge** — 접촉리치 조립(삽입·커넥터·나사·스냅핏) 전용 데이터 엔진: 저비용 텔레오 시연 + TacSL류 시뮬 대량생성 + 자동 잔차 라벨링 → data flywheel.
3. **Sensor-Invariant Tactile FM** — 센서 종류·개체 편차를 흡수하는 촉각 표현 파운데이션. 한 번 모은 데이터를 모든 센서/그리퍼에 재사용.
4. **ForceTwin** — 힘/토크 신호의 실→시(real-to-sim) 보정으로 시뮬 동역학을 부품별 자동 캘리브레이션, sim2real gap 자동 폐쇄.
5. **TactileGen** — 확산모델로 시뮬 촉각이미지를 실 도메인으로 변환·자동라벨링(Sim2Surf 일반화). 라벨 비용 0.
6. **GraspForce** — 촉각+관절토크(모터전류 근사) 관측공간으로 제로샷 force-based grasping. 토크센서 없이 기존 로봇에 적용.

## B. 접촉리치 조작 정책/알고리즘
7. **ResidualAssembly** — 시뮬 베이스 정책 + 실세계 비대칭 admittance 잔차 온라인학습(SPARR 계열) 제품화. HMLV 부품별 빠른 적응.
8. **ForceDirection Policy** — "힘의 방향" 명시 학습으로 접촉리치 sim2real 강건화(CVPR'25 Direction Matters 기반) 산업화.
9. **SkillReuse Engine** — 조립 스킬 라이브러리에서 기하/동역학/액션 유사도로 최적 사전정책 선택·파인튜닝(SRSA 제품화). 샘플 2.4배↓.
10. **CompliantDAgger Cloud** — 인간 보정 기반 접촉리치 정책 개선을 클라우드 data flywheel로. 현장 작업자 개입이 학습 데이터로.
11. **SafeExplore RL** — 힘 임계+동역학 랜덤화로 부품 손상 없이 self-improve하는 안전 탐색 정책(FORGE 산업화).
12. **PhaForce** — 위상 스케줄 비주얼-포스 정책(느린 계획+빠른 보정) 제품화.

## C. VLA/파운데이션 모델 (수직 특화)
13. **IndustrialVLA** — HMLV 정밀조립 특화 VLA: 비전+촉각+힘 멀티모달, "이 커넥터 꽂아" 같은 자연어 작업지시→접촉정책.
14. **TactileVLA** — 기존 VLA(π0/OpenVLA)에 촉각·힘 토큰을 추가한 접촉 인지 확장 + 어댑터 파인튜닝 레시피.
15. **WorldModelControl** — 접촉 동역학 월드모델로 test-time에 시뮬레이트하며 행동 선택(접촉 MPC).
16. **EmbodimentAdapter** — 임베디먼트(로봇팔·그리퍼)별 빠른 적응 어댑터 — 새 셀에 정책 이식 시간 단축.

## D. 배포·데이터 효율 시스템
17. **DeployMinutes** — 셀당 프로그래밍 150~400h를 수십분으로: 시뮬 자동생성+잔차보정+촉각 파이프라인을 통합한 "부품 등록→정책" 시스템. (모트=내부 sim2real/데이터 엔진)
18. **AutoDomainRand** — 부품 CAD→자동 도메인 랜덤화·시뮬 시나리오 생성으로 시연 0~소량으로 정책 학습.
19. **FewShotInsert** — 데이터 효율 일반화 삽입 정책(EasyInsert 산업화), 신규 부품 수회 시연으로 90% 성공.
20. **DataFlywheel-as-a-Service** — 고객 현장의 실패/보정 데이터를 익명화·통합해 모든 고객 정책을 동반 개선(네트워크 효과 모트).

## E. 인접/와일드카드
21. **DeformableTouch** — 변형물(케이블·커넥터 하네스·천) 촉각 기반 조작 — 비전으로 안 보이는 접촉 상태 추정.
22. **InHandRepose** — 손안 재파지(in-hand manipulation) 촉각 정책, 미세부품 자세 교정.
23. **WireHarness AI** — 와이어 하네스 자동 라우팅·삽입(자동차·전자 거대 수작업 시장) 촉각+힘 정책.
24. **MicroAssembly** — 0.1mm급 마이크로 광학·반도체 후공정 부품 정밀 삽입(경기 반도체 클러스터 레버리지).
25. **QualityFromTouch** — 조립 중 촉각·힘 시그니처로 불량(미삽입·과체결) 실시간 검출 — 데이터는 조작 정책과 공유.
26. **TactileTransfer Marketplace** — 검증된 접촉 정책·촉각 표현을 부품 카테고리별로 배포(독점 데이터 자산화).
