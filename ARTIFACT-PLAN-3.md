# 확장 계획 — 미완 6편 + 신규 20편

> **상태: 완료 (2026-08-11).** 26편 전부 작성·검증·배포했다.
> 최종 49편 / 9단계이고, **49편 모두 사이트에 직접 수록**되어
> 외부 아티팩트 링크에 의존하는 문서가 하나도 남지 않았다.
> 생성기 소스는 `scripts/docs/gen_*.py` 에 있어 이후 수정이 가능하다.

## 1부. 미완 6편

카탈로그에는 등록됐지만 `site-pages/docs/` 에 본문이 없는 문서들이다.
전부 claude.ai 아티팩트로만 존재하고, 초기에 쓴 것이라 현재 포맷(번호 절 · `.eq` ·
손으로 짠 SVG · `.note` · arXiv 인용 · 편별 팔레트)에 미달한다.

**회수보다 재작성이 맞다.** 어차피 포맷을 맞추려면 전면 손질이 필요하고,
그 작업량이 새로 쓰는 것과 다르지 않다. 재작성하면 소스가 `scripts/` 안에 남아
이후 수정도 가능해진다.

| slug | 편 | 단계 | 다룰 핵심 |
|---|---|---|---|
| `lora` | LoRA | 04 적응·정렬 | 저랭크 분해, ΔW=BA, 왜 랭크가 작아도 되는가, QLoRA |
| `flash-attention` | FlashAttention | 05 추론 최적화 | IO 인식, 타일링, 온라인 softmax, v2/v3 |
| `diffusion-models` | Diffusion Models | 03 학습 | 순/역확산, 노이즈 예측, DDIM, Latent Diffusion |
| `rlhf` | RLHF | 04 적응·정렬 | 보상 모델, PPO, KL 페널티, DPO로의 이행 |
| `yolov5` | YOLOv5 심화 | 07 특집 | 앵커 자동화, mosaic, CSP, 사용자의 실제 기준선 |
| `yolox` | YOLOX 심화 | 07 특집 | 앵커프리, decoupled head, SimOTA |

---

## 2부. 신규 20편 — 무엇이 비어 있는가

현 26편을 단계별로 세면 결손이 드러난다.

```
01 기초        4편
02 아키텍처     4편
03 학습        4편
04 적응·정렬    2편   ← 얇다
05 추론 최적화   4편
06 응용·시스템   2편   ← 얇다
07 특집        6편
```

두 가지 문제가 보인다.

1. **04와 06이 얇다.** 정렬은 지금 LLM 실무의 큰 축인데 2편뿐이고,
   응용·시스템은 RAG와 MCP만 있어 에이전트·서빙이 통째로 빠졌다.
2. **단계 자체가 빠져 있다.** 현재 7단계는 *모델을 만드는 과정*만 다룬다.
   실제로는 그 앞뒤에 **학습 인프라**(어떻게 굴리는가)와
   **평가·안전**(잘 됐는지 어떻게 아는가)이 있는데 둘 다 없다.

그래서 신규 20편은 얇은 단계를 채우고, 빠진 두 단계를 신설한다.

### 단계 신설

| 번호 | 이름 | 자리 |
|---|---|---|
| 06 | **학습 인프라** — 어떻게 굴리는가 | 05 추론 최적화 뒤 |
| 08 | **평가·안전** — 잘 됐는지 어떻게 아는가 | 응용 뒤, 특집 앞 |

기존 06 응용·시스템은 07로, 07 특집은 09로 밀린다.

### 편성

**02 아키텍처 (+3 → 7편)**

| slug | 제목 | 왜 |
|---|---|---|
| `mamba-ssm` | Mamba & State Space Models | 트랜스포머 대안 계열의 대표. 선택적 SSM, 선형 스케일링 |
| `graph-neural-networks` | Graph Neural Networks | 격자도 수열도 아닌 데이터. 메시지 패싱 |
| `autoencoders-vae` | Autoencoders & VAE | 잠재공간의 기원. Latent Diffusion의 전제 |

**03 학습 (+3 → 7편)**

| slug | 제목 | 왜 |
|---|---|---|
| `self-supervised-learning` | Self-Supervised Learning | 라벨 없이 배우는 원리. 대조학습·BYOL |
| `gan` | GAN | 확산 이전의 생성 모델. 왜 밀려났는가 |
| `curriculum-data-quality` | 데이터 품질과 커리큘럼 | 중복제거·필터링. 스케일링 법칙의 실제 조건 |

**04 적응·정렬 (+4 → 8편, 재작성 2편 포함)**

| slug | 제목 | 왜 |
|---|---|---|
| `instruction-tuning` | Instruction Tuning | 사전학습과 정렬 사이의 빠진 고리 |
| `dpo-alignment` | DPO & 보상 없는 정렬 | RLHF의 현행 대체재 |
| `constitutional-ai` | Constitutional AI | 사람 라벨 대신 원칙. RLAIF |
| `peft-adapters` | PEFT — Adapter·Prefix·IA³ | LoRA 이외의 선택지 비교 |

**05 추론 최적화 (+2 → 6편)**

| slug | 제목 | 왜 |
|---|---|---|
| `knowledge-distillation` | Knowledge Distillation | 소형화의 정석. soft target |
| `pruning-sparsity` | Pruning & Sparsity | 양자화와 짝을 이루는 축 |

**06 학습 인프라 (신설, 3편)**

| slug | 제목 | 왜 |
|---|---|---|
| `distributed-training` | 분산 학습 — DP·TP·PP | 대형 모델 학습의 실체 |
| `mixed-precision` | Mixed Precision & 수치 안정성 | fp16/bf16/fp8, loss scaling |
| `gradient-checkpointing` | Gradient Checkpointing | 메모리와 연산의 교환 |

**07 응용·시스템 (+4 → 6편)**

| slug | 제목 | 왜 |
|---|---|---|
| `ai-agents-tool-use` | AI Agents & Tool Use | MCP 문서의 상위 맥락 |
| `chain-of-thought` | Chain-of-Thought & 추론 | 추론 시간 스케일링 |
| `in-context-learning` | In-Context Learning | 가중치 갱신 없는 학습 |
| `llm-serving` | LLM 서빙 — 배칭과 스케줄링 | KV Cache 문서의 시스템 짝 |

**08 평가·안전 (신설, 4편)**

| slug | 제목 | 왜 |
|---|---|---|
| `evaluation-benchmarks` | 평가와 벤치마크 | 오염·포화 문제 포함 |
| `hallucination` | 환각 — 원인과 완화 | 실무에서 가장 자주 묻는 주제 |
| `prompt-injection` | Prompt Injection & 보안 | 에이전트·MCP의 직접적 위험 |
| `interpretability` | 해석가능성 | 회로·SAE·활성 조향 |

### 합계

```
미완 재작성   6편
신규         20편
────────────────
발행 후 총계  46편 · 9단계
```

---

## 3부. 진행 방식

기존과 동일하다.

1. `scripts/docs/gen_<slug>.py` 에 편별 생성기 작성 (팔레트 + 본문)
2. `build.py` 로 렌더 → `check.py` 로 점검 (태그 균형·테마 3중 정의·SVG 접근성·미정의 변수)
3. `catalog.py` 에 등록 → `sync-catalog.sh` 로 3개 대상 동기화
4. `build-docs.py` 로 네비 주입 → 커밋 → 배포

사실 확인이 필요한 편(RF-DETR 때 수치가 틀렸던 전례)은 작성 전 웹 확인을 거친다.
특히 `evaluation-benchmarks`, `ai-agents-tool-use`, `prompt-injection`, `mamba-ssm` 은
최신 상황이 자주 바뀌므로 반드시 확인한다.
