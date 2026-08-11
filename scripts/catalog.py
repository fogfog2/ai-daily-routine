#!/usr/bin/env python3
"""문서 카탈로그 — 공개 사이트(GitHub Pages)의 단일 출처.

분류는 '파이프라인 단계'다. 모델이 만들어져 서비스되기까지의 순서라
겹침이 거의 없고, 순서 자체가 읽는 순서가 된다.
"""

STAGES = [
    {
        "id": "basics",
        "no": "01",
        "name": "기초",
        "tagline": "모든 모델의 밑바닥 부품",
        "desc": "구조를 논하기 전에 이미 정해져 있는 것들. 눈에 잘 띄지 않지만 되돌리기는 가장 어렵다.",
    },
    {
        "id": "arch",
        "no": "02",
        "name": "아키텍처",
        "tagline": "무엇을 쌓을 것인가",
        "desc": "어텐션을 축으로 한 구조와 그 변형들. 언어에서 출발해 이미지로, 그리고 조건부 연산으로.",
    },
    {
        "id": "train",
        "no": "03",
        "name": "학습",
        "tagline": "어떤 과제로 가르칠 것인가",
        "desc": "사전학습 과제의 설계가 곧 얻어지는 능력을 정한다. 그리고 얼마나 키울지의 경제학.",
    },
    {
        "id": "align",
        "no": "04",
        "name": "적응·정렬",
        "tagline": "학습된 모델을 길들이기",
        "desc": "전부 다시 학습하지 않고 방향만 바꾸는 방법들.",
    },
    {
        "id": "infer",
        "no": "05",
        "name": "추론 최적화",
        "tagline": "같은 모델을 싸고 빠르게",
        "desc": "품질을 내주지 않고 비용과 지연을 줄이는 기법들. 대부분 병목이 연산이 아니라 메모리라는 관찰에서 출발한다.",
    },
    {
        "id": "infra",
        "no": "06",
        "name": "학습 인프라",
        "tagline": "어떻게 굴리는가",
        "desc": "한 장의 GPU에 담기지 않는 모델을 실제로 학습시키는 공학. 무엇을 쪼개고 무엇을 다시 계산할지의 선택.",
    },
    {
        "id": "apply",
        "no": "07",
        "name": "응용·시스템",
        "tagline": "실제로 쓰이는 형태",
        "desc": "모델을 바깥 세계에 연결하는 패턴. 지식을 밖에 두고, 도구를 쥐여 주고, 여러 요청을 한 장비에 태운다.",
    },
    {
        "id": "eval",
        "no": "08",
        "name": "평가·안전",
        "tagline": "잘 됐는지 어떻게 아는가",
        "desc": "만드는 이야기가 끝나면 남는 질문. 무엇을 재고 있는지, 왜 틀리는지, 어디가 뚫리는지, 안을 들여다볼 수 있는지.",
    },
    {
        "id": "detect",
        "no": "09",
        "name": "특집 — 객체 검출",
        "tagline": "손으로 정하던 것을 하나씩 학습으로",
        "desc": (
            "검출기 계보를 순서대로 읽는 특집. 영역 제안 → 앵커 → 라벨 할당 → NMS가 "
            "차례로 학습에 흡수되는 과정이고, 마지막이 현재 도달점인 RF-DETR이다. "
            "위에서부터 읽도록 배열했다."
        ),
    },
]

# 태그 — 단계(STAGES)와 다른 축이다.
#
#   단계는 '만들어지는 순서'라 한 문서가 정확히 하나에 속한다.
#   태그는 '무엇에 관한 것인가'라 여러 개가 붙는다.
#   그래서 단계로는 못 하던 것 — "vision 것만", "on-device 만" — 을 태그가 한다.
#
#   group: domain  큰 갈래. 문서마다 정확히 하나.
#          topic   세부 주제. 여러 개 가능.
TAGS = [
    # ---- 도메인 ----
    {"id": "llm", "group": "domain", "name": "LLM",
     "desc": "언어 모델 쪽 이야기"},
    {"id": "vision", "group": "domain", "name": "Vision",
     "desc": "이미지·영상 쪽 이야기"},
    {"id": "common", "group": "domain", "name": "공통",
     "desc": "어느 도메인에서나 쓰이는 밑바탕"},

    # ---- 주제 ----
    {"id": "detection", "group": "topic", "name": "검출·분류",
     "desc": "물체를 찾고 무엇인지 가른다"},
    {"id": "on-device", "group": "topic", "name": "온디바이스",
     "desc": "작은 장비에 올리기 — 경량화·양자화·가지치기"},
    {"id": "enhance", "group": "topic", "name": "화질 개선",
     "desc": "복원·초해상·생성으로 화질을 올린다"},
    {"id": "feature", "group": "topic", "name": "특징·매칭",
     "desc": "표현을 뽑아 같고 다름을 재는 것"},
    {"id": "generative", "group": "topic", "name": "생성",
     "desc": "없던 것을 만들어내는 모델"},
    {"id": "arch", "group": "topic", "name": "구조",
     "desc": "무엇을 어떻게 쌓는가"},
    {"id": "training", "group": "topic", "name": "학습",
     "desc": "어떤 과제와 방법으로 가르치는가"},
    {"id": "alignment", "group": "topic", "name": "정렬",
     "desc": "학습된 모델을 원하는 방향으로"},
    {"id": "efficiency", "group": "topic", "name": "효율",
     "desc": "같은 결과를 싸고 빠르게"},
    {"id": "systems", "group": "topic", "name": "시스템",
     "desc": "실제로 굴리는 공학"},
    {"id": "safety", "group": "topic", "name": "평가·안전",
     "desc": "잘 됐는지, 어디가 뚫리는지"},
]

# (제목, 부제, uuid, slug, 단계, 한 줄 요약, 날짜, [태그])
#
#   uuid — claude.ai 아티팩트 ID (원본 보관용)
#   slug — 공개 사이트의 파일명이자 URL. docs/<slug>.html
#   태그 — 도메인 1개 + 주제 1~3개. TAGS 의 id 를 쓴다.
DOCS = [
    ("Tokenization", "글자와 단어 사이에서 타협하다",
     "f8f8805b-7531-4174-b236-967c0df9bb60", "tokenization", "basics",
     "BPE가 빈도만 세어 형태소를 찾아내는 과정, 그리고 한국어가 비싼 구조적 원인.", "2026-08-09", ["common", "training"]),
    ("Normalization", "분포를 붙잡아 학습을 안정시키다",
     "ad1cb4e8-ad04-45ea-b015-a12a06428589", "normalization", "basics",
     "평균을 어느 축으로 내느냐가 배치 의존성과 추론 동작을 가른다. Pre-LN과 RMSNorm.", "2026-08-09", ["common", "training"]),
    ("Embeddings & Positional Encoding", "토큰이 벡터가 되고 순서를 얻기까지",
     "1129729a-3605-4549-a164-c6e7b5796444", "embeddings", "basics",
     "어텐션은 순서를 모른다. 위치를 더할 것인가 회전시킬 것인가 — 정현파에서 RoPE까지.", "2026-08-09", ["common", "arch"]),
    ("Backpropagation & Optimizers", "학습이 실제로 도는 방식",
     "bfa7b3c6-9bd9-4f3c-a708-731fc2bc8f7d", "backprop-optimizers", "basics",
     "연쇄 법칙의 계산 순서가 만든 역전파, 그리고 Adam에서 AdamW로 옮겨간 한 줄.", "2026-08-09", ["common", "training"]),

    ("Transformer", "모든 단어가 서로를 바라보다",
     "6011e936-624f-4f83-8ab1-1b0a4120d784", "transformer", "arch",
     "셀프 어텐션이 문장 속 모든 단어를 동시에 저울질하는 방식. 현대 LLM의 뼈대.", "2026-08-06", ["common", "arch"]),
    ("Vision Transformer", "이미지를 단어처럼 자르다",
     "52b3884c-6c7e-4495-9085-d45506dabfd4", "vision-transformer", "arch",
     "비전 전용 구조를 걷어낸 대가와 보상 — 편향은 시작점을 높이고 천장을 낮춘다.", "2026-08-09", ["vision", "arch"]),
    ("Mixture of Experts", "필요한 전문가만 깨우는 신경망",
     "5dfd51ef-514f-4c49-b849-4d131cbd2552", "mixture-of-experts", "arch",
     "top-k 라우팅으로 파라미터 수와 토큰당 연산량을 분리하는 구조.", "2026-08-06", ["common", "arch", "efficiency"]),
    ("RNN & LSTM", "순서대로 읽던 시절",
     "6ccc860e-8ce2-4bb8-b9b8-c104ced4bdea", "rnn-lstm", "arch",
     "셀 상태가 그래디언트를 살린 방식과, 어텐션이 이긴 진짜 이유인 순차성 병목.", "2026-08-09", ["common", "arch"]),
    ("Mamba & State Space Models", "다시 순서대로, 그러나 빠르게",
     "", "mamba-ssm", "arch",
     "입력에 따라 변하는 상태공간 모델. 선형 스케일링을 얻고 무엇을 내주었는가.", "2026-08-10", ["common", "arch", "efficiency"]),
    ("Autoencoders & VAE", "압축이 만들어낸 잠재공간",
     "", "autoencoders-vae", "arch",
     "재구성만 시켰더니 의미가 생긴 이유, 그리고 확산 모델이 올라탄 그 공간.", "2026-08-10", ["common", "arch", "generative"]),
    ("Graph Neural Networks", "격자도 수열도 아닌 데이터",
     "", "graph-neural-networks", "arch",
     "이웃에게 메시지를 받아 자신을 갱신하는 구조. 층을 쌓을수록 뭉개지는 문제까지.", "2026-08-10", ["common", "arch"]),

    ("BERT & Masked LM", "빈칸을 메우며 언어를 익히다",
     "c7cb6375-bd3c-4420-ba3e-ed124da6d17f", "bert-masked-lm", "train",
     "양방향 학습을 막던 제약을 구조가 아니라 과제 교체로 푼 방법.", "2026-08-09", ["llm", "training"]),
    ("Diffusion Models", "잡음 속에서 그림을 꺼내다",
     "f69ce0e7-cf74-4588-b066-1ce2e7b6be53", "diffusion-models", "train",
     "노이즈를 더하는 과정을 거꾸로 되돌리는 법을 배워 이미지를 꺼내는 원리.", "2026-08-06", ["vision", "generative", "training"]),
    ("CLIP", "그림과 말을 같은 공간에 놓다",
     "9fe5e678-28e3-4240-a0b1-d2dbcd7ade9d", "clip", "train",
     "이미지와 텍스트를 하나의 임베딩 공간에 놓아 제로샷 분류를 가능하게 한 학습.", "2026-07-30", ["vision", "feature", "training"]),
    ("Scaling Laws", "크기와 데이터의 최적 배분",
     "11b175e4-3ce3-4bc4-9e51-67fee0d6ce13", "scaling-laws", "train",
     "같은 관측에서 정반대 처방이 나온 이유. Chinchilla의 20:1과 그것을 어기는 근거.", "2026-08-09", ["common", "training"]),
    ("Self-Supervised Learning", "라벨 없이 배우는 법",
     "", "self-supervised-learning", "train",
     "데이터 자신이 정답이 되는 과제 설계. 대조학습과 붕괴를 피하는 장치들.", "2026-08-10", ["common", "training", "feature"]),
    ("GAN", "두 신경망을 맞붙이다",
     "", "gan", "train",
     "판별자를 손실 함수로 쓴 발상, 그리고 확산 모델에 자리를 내준 이유.", "2026-08-10", ["vision", "generative", "training"]),
    ("데이터 품질과 커리큘럼", "무엇을 먹이느냐가 정한다",
     "", "curriculum-data-quality", "train",
     "중복 제거와 필터링이 파라미터를 늘리는 것보다 싸게 먹히는 구간.", "2026-08-10", ["common", "training"]),

    ("LoRA", "얼린 가중치 옆에 샛길을 내다",
     "dfdb6442-a674-4514-8fd7-9347669eca80", "lora", "align",
     "ΔW를 저랭크로 쪼개 학습 파라미터를 0.06%로 줄이는 법.", "2026-08-07", ["common", "alignment", "efficiency"]),
    ("RLHF", "선호를 손실 함수로 번역하다",
     "8cbf3343-09a7-4c84-a2eb-cdb53ee864b2", "rlhf", "align",
     "선호 쌍을 보상으로 바꾸고, 끝내 보상 모델을 소거해 버린 DPO의 유도까지.", "2026-08-08", ["llm", "alignment"]),
    ("Instruction Tuning", "지시를 따르게 만들기",
     "", "instruction-tuning", "align",
     "다음 단어를 맞추던 모델이 부탁을 알아듣게 되는 단계. 정렬의 첫 관문.", "2026-08-10", ["llm", "alignment"]),
    ("DPO", "보상 모델을 지워버린 정렬",
     "", "dpo-alignment", "align",
     "RLHF의 최적해를 역산해 강화학습 없이 같은 목표에 도달하는 유도.", "2026-08-10", ["llm", "alignment"]),
    ("PEFT — Adapter·Prefix·IA³", "LoRA 말고도 있는 길",
     "", "peft-adapters", "align",
     "어디에 무엇을 끼워넣을지의 선택지 비교. 추론 지연이 갈리는 지점.", "2026-08-10", ["common", "alignment", "efficiency"]),
    ("Constitutional AI", "사람 라벨 대신 원칙",
     "", "constitutional-ai", "align",
     "모델이 자기 답을 원칙에 비춰 고치게 하는 방식. RLAIF의 실체.", "2026-08-10", ["llm", "alignment", "safety"]),

    ("FlashAttention", "어텐션을 메모리 계층에 맞춰 다시 쓰다",
     "bb1a09e1-70e1-43ec-b223-07bbec025750", "flash-attention", "infer",
     "병목이 FLOPs가 아니라 HBM 왕복이었다는 것. 타일링과 온라인 소프트맥스.", "2026-08-09", ["common", "efficiency", "systems"]),
    ("KV Cache & PagedAttention", "문맥을 페이지로 관리하다",
     "27bddc7c-8e2e-4698-86af-4312ac0351bd", "kv-cache-paged-attention", "infer",
     "GPU 메모리의 60~80%를 낭비하던 구조를, OS의 페이징을 빌려 4% 미만으로.", "2026-08-09", ["llm", "efficiency", "systems"]),
    ("Speculative Decoding", "초안을 쓰고 한 번에 검산하다",
     "c886662a-20a5-4845-a2ac-6b5a8ec67059", "speculative-decoding", "infer",
     "작은 모델의 초안을 채택해도 출력 분포가 수학적으로 보존되는 이유.", "2026-08-09", ["llm", "efficiency"]),
    ("Quantization", "정밀도를 깎아 모델을 옮기다",
     "590c43d7-94b7-40ca-8941-6838734b52b2", "quantization", "infer",
     "4비트에서도 버티는 이유는 목표를 바꿨기 때문. GPTQ와 AWQ.", "2026-08-09", ["common", "efficiency", "on-device"]),
    ("Knowledge Distillation", "큰 모델의 판단을 옮겨 담다",
     "", "knowledge-distillation", "infer",
     "정답 대신 큰 모델의 확률 분포를 배우게 하는 것이 왜 더 나은가.", "2026-08-10", ["common", "efficiency", "on-device"]),
    ("Pruning & Sparsity", "쓰지 않는 연결을 잘라내다",
     "", "pruning-sparsity", "infer",
     "비정형 희소성이 이론상 이득을 실제 속도로 바꾸지 못하는 이유. 2:4 구조적 희소성.", "2026-08-10", ["common", "efficiency", "on-device"]),

    # ---- 06 학습 인프라 ----
    ("분산 학습 — DP·TP·PP", "한 장에 담기지 않을 때",
     "", "distributed-training", "infra",
     "데이터·텐서·파이프라인 병렬의 분담과 통신량. ZeRO가 줄인 중복.", "2026-08-10", ["common", "systems", "training"]),
    ("Mixed Precision", "16비트로 학습하기",
     "", "mixed-precision", "infra",
     "fp16이 언더플로로 무너지는 지점과 loss scaling, 그리고 bf16이 이긴 이유.", "2026-08-10", ["common", "systems", "efficiency"]),
    ("Gradient Checkpointing", "메모리를 연산으로 사다",
     "", "gradient-checkpointing", "infra",
     "활성값을 버리고 필요할 때 다시 계산하는 거래. √n 지점의 유래.", "2026-08-10", ["common", "systems", "efficiency"]),

    ("RAG", "모델 밖에 기억을 두다",
     "3e03a99a-8acb-47b5-bdc9-9c269de55b78", "rag", "apply",
     "지식을 가중치에서 꺼내 외부로 옮기는 선택과 그 대가.", "2026-08-09", ["llm", "systems", "feature"]),
    ("Model Context Protocol", "도구를 모델에 꽂는 규약",
     "c941306d-b0b9-4e57-a3c7-f14082e3a5a4", "model-context-protocol", "apply",
     "호스트·클라이언트·서버 구조와 프리미티브. 상태를 버린 2026-07-28 개정.", "2026-08-09", ["llm", "systems"]),
    ("In-Context Learning", "가중치를 건드리지 않는 학습",
     "", "in-context-learning", "apply",
     "예시 몇 개로 새 과제를 하는 현상. 무엇을 배우는 게 아니라 무엇을 고르는가.", "2026-08-10", ["llm", "training"]),
    ("Chain-of-Thought", "생각할 시간을 주다",
     "", "chain-of-thought", "apply",
     "중간 과정을 쓰게 했더니 정답률이 오른 이유, 그리고 추론 시간 스케일링.", "2026-08-10", ["llm", "training"]),
    ("AI Agents & Tool Use", "모델에 손을 달아주다",
     "", "ai-agents-tool-use", "apply",
     "관측·결정·행동의 순환. 언제 에이전트가 필요하고 언제 과한가.", "2026-08-10", ["llm", "systems"]),
    ("LLM 서빙 — 배칭과 스케줄링", "한 장비에 여러 요청을 태우다",
     "", "llm-serving", "apply",
     "연속 배칭이 처리량을 끌어올리는 원리와 지연·처리량의 맞바꿈.", "2026-08-10", ["llm", "systems", "efficiency"]),

    # ---- 08 평가·안전 ----
    ("평가와 벤치마크", "무엇을 재고 있는가",
     "", "evaluation-benchmarks", "eval",
     "점수가 오르는 것과 능력이 오르는 것의 차이. 오염과 포화, 그리고 대안.", "2026-08-10", ["common", "safety"]),
    ("환각", "왜 그럴듯하게 틀리는가",
     "", "hallucination", "eval",
     "구조에서 비롯된 원인과, 완화가 제거를 뜻하지 않는 이유.", "2026-08-10", ["llm", "safety"]),
    ("Prompt Injection", "데이터가 명령이 되는 순간",
     "", "prompt-injection", "eval",
     "지시와 데이터를 구분하지 못하는 구조적 취약점. 에이전트에서 커지는 위험.", "2026-08-10", ["llm", "safety", "systems"]),
    ("해석가능성", "안을 들여다볼 수 있는가",
     "", "interpretability", "eval",
     "중첩 때문에 뉴런 하나가 여러 뜻을 갖는 문제와, 희소 오토인코더의 접근.", "2026-08-10", ["common", "safety"]),

    # ---- 09 특집: 객체 검출 (계보 순서대로 읽도록 배열) ----
    ("① Object Detection 계보", "2단계에서 1단계로",
     "71cf0a62-df49-43d2-9335-e5e68bb60e3f", "detection-lineage", "detect",
     "가변 개수 출력이라는 난점, 제안 단계를 없앤 과정, Focal Loss가 푼 클래스 불균형.", "2026-08-09", ["vision", "detection", "arch"]),
    ("② YOLO 계보", "v5에서 YOLO26까지",
     "444d6619-fee3-4b49-a9ec-9e32ec434d5b", "yolo-lineage", "detect",
     "버전 번호의 혼란을 정리하고, 앵커·NMS를 하나씩 없앤 과정과 라이선스 갈림.", "2026-08-09", ["vision", "detection", "on-device"]),
    ("③ DETR 계보", "검출을 집합 예측으로",
     "cd8d4e33-d873-4614-a690-584c59188b09", "detr-lineage", "detect",
     "헝가리안 매칭으로 중복을 원천 차단한 발상과, 실용화까지 걸린 5년.", "2026-08-09", ["vision", "detection", "arch"]),
    ("④ RF-DETR", "실시간 검출의 현재 도달점",
     "5cd17b82-bd3f-4228-b47c-19a02bfce923", "rf-detr", "detect",
     "실시간 최초 60 AP. DINOv2 백본의 이점과 CPU 경로 부재라는 대가, 이전 판단 기준.", "2026-08-09", ["vision", "detection"]),
    ("＋ YOLOv5 (심화)", "격자 위에 앵커를 놓다",
     "e3fde2cf-aa7d-4998-9403-e20e893e89bd", "yolov5", "detect",
     "앵커 디코딩 공식, 이웃 칸까지 쓰는 정적 라벨 할당, 그리고 모델 스케일링.", "2026-08-06", ["vision", "detection", "on-device"]),
    ("＋ YOLOX (심화)", "앵커를 걷어내고 머리를 나누다",
     "8cbd9ed8-0e68-4ee9-aa7f-83b014652264", "yolox", "detect",
     "성능을 끌어올린 것이 왜 백본이 아니라 라벨 할당이었는지.", "2026-08-06", ["vision", "detection", "on-device"]),
]

ARCHIVE_URL = "https://claude.ai/code/artifact/1d524519-2d1c-4a35-83b1-a64eddcae541"


PAGES_URL = "https://fogfog2.github.io/ai-concepts/"


def url(uid, slug=None):
    """바깥에서 여는 절대주소.

    아티팩트에서 출발한 문서는 원본을 가리키고,
    직접 쓴 문서(uuid 없음)는 공개 사이트의 해당 문서를 가리킨다.
    """
    if uid:
        return "https://claude.ai/code/artifact/" + uid
    return PAGES_URL + href(slug)


def href(slug):
    """공개 사이트의 내부 문서 경로."""
    return "docs/" + slug + ".html"


def by_stage():
    out = []
    for st in STAGES:
        items = [d for d in DOCS if d[4] == st["id"]]
        out.append((st, items))
    return out


def validate():
    # uuid 는 아티팩트에서 출발한 문서만 갖는다.
    # 직접 쓴 문서는 원본 아티팩트가 없으므로 빈 문자열이고, 검사에서 제외한다.
    ids = [d[2] for d in DOCS if d[2]]
    assert len(ids) == len(set(ids)), "중복 UUID"
    assert all(len(i) == 36 for i in ids), "UUID 형식 오류"

    slugs = [d[3] for d in DOCS]
    assert len(slugs) == len(set(slugs)), "중복 slug"
    import re as _re
    bad = [s for s in slugs if not _re.fullmatch(r"[a-z0-9-]+", s)]
    assert not bad, f"slug 형식 오류(영문 소문자·숫자·하이픈만): {bad}"

    # 제목·부제·요약은 평문이어야 한다.
    # HTML 엔티티를 담아 두면 ai.js 가 렌더할 때 한 번 더 이스케이프해
    # 화면에 '&amp;' 라는 글자가 그대로 보인다. 이스케이프는 HTML 에 넣는 쪽 책임이다.
    import re as _re2
    ent = [(d[3], f) for d in DOCS for f in (d[0], d[1], d[5])
           if _re2.search(r"&(amp|lt|gt|quot|#\d+);", f)]
    assert not ent, f"제목·부제·요약에 HTML 엔티티가 있습니다(평문으로 쓸 것): {ent}"

    # 태그 — 정의된 것만 쓰고, 도메인은 정확히 하나여야 한다.
    tag_ids = {t["id"] for t in TAGS}
    domains = {t["id"] for t in TAGS if t["group"] == "domain"}
    for d in DOCS:
        tags = d[7] if len(d) > 7 else []
        bad = [t for t in tags if t not in tag_ids]
        assert not bad, f"{d[3]}: 미정의 태그 {bad}"
        dom = [t for t in tags if t in domains]
        assert len(dom) == 1, f"{d[3]}: 도메인 태그가 {len(dom)}개 (정확히 1개여야 함)"

    stage_ids = {s["id"] for s in STAGES}
    assert all(d[4] in stage_ids for d in DOCS), "미정의 단계 참조"
    empty = [s["name"] for s, items in by_stage() if not items]
    assert not empty, f"빈 단계: {empty}"
    return len(DOCS), len(STAGES)


if __name__ == "__main__":
    n, s = validate()
    print(f"검증 통과: {n}편 / {s}단계")
    for st, items in by_stage():
        print(f"  {st['no']} {st['name']:8} {len(items)}편")
