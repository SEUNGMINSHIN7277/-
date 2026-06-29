# Phase 1 — 원석 24개 (각 어떤 돌파 기반인지 명시)

> 래퍼/앱 금지. 딥테크 원석만. 영역: 보안·암호 / 양자 / 센싱 / 뉴로모픽·포토닉 / 센서퓨전.

## 보안·암호 딥테크 (FHE/MPC/프라이버시)
1. **HE-Cast(채택 후보)** — 일반 PyTorch/ONNX 모델을 입력하면 깊이/정확도 공동최적화로 **FHE-friendly 모델(저차 다항 활성화+bootstrap 스케줄)** 자동 생성하는 컴파일러+재훈련 엔진. (돌파: 다항근사 난제 arXiv 2404.03216, HEIR IR, FIDESlib GPU)
2. **DepthSolver** — 신경망을 곱셈깊이 예산(depth budget) 제약 최적화 문제로 풀어 bootstrap 횟수를 최소화하는 컴파일러 패스. (돌파: Orion DAG 최단경로 bootstrap 배치)
3. **PolyTune** — 입력 분포 인지 적응 다항 근사(구간별·QAT) 자동 생성 라이브러리. (돌파: arXiv 2508.11575, 2605.22237 decision-aware quadratic ReLU)
4. **CipherServe** — FHE 추론을 위한 멀티-GPU 서빙 런타임(배치·패킹·하이브리드 병렬). (돌파: AEGIS 하이브리드 병렬 arXiv 2604.03425)
5. **MyData-HE** — 韓 MyData 전송데이터를 평문 비저장으로 암호화 협업분석하는 금융/의료 PoC 플랫폼. (돌파: MyData 2.0 + CKKS GPU)
6. **HE-Risk** — 은행이 암호화된 고객 피처로 신용/이상거래 스코어링(모델은 서버, 데이터는 암호문). (돌파: 다항 LR/CNN 추론 SOTA)
7. **FHE-Bench** — FHE-friendly 모델 정확도/지연/깊이 벤치마크·리더보드(데이터 해자 시드). (돌파: Event-LAB식 표준화 발상 이식)
8. **TEE-FHE Hybrid Router** — 연산자별로 TEE/FHE/MPC 스킴을 자동 분할 배치하는 스케줄러. (돌파: Bifrost 하이브리드 arXiv 2606.17421)
9. **KV-Cipher** — 생성형 LLM의 KV 캐시를 FHE로 보호하는 추론 경로. (돌파: Cachemir arXiv 2602.11470)
10. **Confidential RAG** — 암호문 임베딩 위 유사도검색+민감문서 RAG. (돌파: FHE text search 특허 12362906)

## 양자 SW
11. **QEM-Compiler** — 회로별 최적 오류완화 조합(ZNE+shadows+SV)을 자동 선택·런타임 예산화. (돌파: QESEM, classical shadows 일반화)
12. **ShadowLearn** — classical shadows로 양자상태 학습 데이터셋 압축·ML 대체모델. (돌파: ShadowNet arXiv 2308.11290)
13. **NoiseTwin** — 실하드웨어 노이즈 디지털트윈으로 사전 보정 추천. (돌파: noise-aware folding 2401.12495)

## 신규 센싱+AI
14. **RadarVitals** — mmWave 비접촉 ECG/심박 재구성 엣지 모델. (돌파: radarODE 2408.01672)
15. **PrivySense** — 프라이버시 인지 RF 심박 센싱(영상 없음). (돌파: PrivyWave 2511.02993)
16. **RF-Foundation** — WiFi/레이더 CSI 자기지도 파운데이션 모델(행동·생체 다운스트림). (돌파: RF sensing self-supervised 추세)
17. **EventFlow** — 이벤트카메라 초저지연 광류 SNN(엣지 로봇). (돌파: SNN optical flow 2025)
18. **EventLAB-SLAM** — 이벤트 기반 로컬라이제이션 표준 평가+경량 SLAM. (돌파: Event-LAB 2509.14516)

## 뉴로모픽/포토닉 컴퓨팅 SW
19. **SpikeC** — 표준 신경망→스파이킹 신경망 변환+뉴로모픽 칩 컴파일러. (돌파: SNN 변환 연구) — *칩 의존 리스크*
20. **PhotonMap** — 포토닉 가속기용 매핑/양자화 컴파일러. (돌파: 포토닉 컴퓨팅) — *소자 양산 의존 리스크*

## 센서퓨전/공간·엣지 통신
21. **FusionPINN** — 다중센서 융합에 물리정보신경망으로 캘리브레이션. (돌파: PINN)
22. **EdgeSplit** — 엣지-클라우드 스플릿 추론에 프라이버시(부분 암호화) 결합. (돌파: split inference + FHE)

## 데이터·프라이버시 알고리즘
23. **DP-Synth-HE** — 차등프라이버시 합성데이터+FHE 검증 가능 연산. (돌파: DataSeal 검증가능 연산 2410.15215)
24. **FedHE** — 연합학습 그래디언트를 FHE로 보호(of-the-shelf 모델). (돌파: HE+FL CNN 학습 2204.07752)
