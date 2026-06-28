"""CLI 진입점.

예시:
  python -m shorts_agent run --seeds "주방,청소,뷰티" --count 5            # 게이트 운영(반자동)
  python -m shorts_agent run --seeds "주방,청소" --count 5 --auto           # 무인 자동
  python -m shorts_agent list                                              # 잡 상태
  python -m shorts_agent gate-a <job_id> [--reject]                        # GATE A 승인/반려
  python -m shorts_agent gate-b <job_id> [--reject]                        # GATE B 승인/반려
  python -m shorts_agent show <job_id>
"""
from __future__ import annotations

import argparse
import logging
import sys

from .config import Settings
from .factory import build_providers
from .models import Stage
from .pipeline import ShortsAgent
from .store import Store

logger = logging.getLogger("shorts_agent")

_STAGE_KO = {
    Stage.SELECTED: "선정", Stage.SCRIPTED: "대본", Stage.GATE_A: "🚦GATE_A(상품·후킹 승인 대기)",
    Stage.ASSETS: "에셋", Stage.VOICED: "보이스", Stage.RENDERED: "렌더",
    Stage.CAPTIONED: "자막", Stage.GATE_B: "🚦GATE_B(최종 검수 대기)",
    Stage.UPLOADED: "✅발행완료", Stage.FAILED: "❌실패",
}


def _agent(args) -> ShortsAgent:
    s = Settings.load(
        dry_run=(True if getattr(args, "dry_run", False) else None),
        auto=(True if getattr(args, "auto", False) else None),
    )
    store = Store(s.output_dir / "state.json")
    return ShortsAgent(s, build_providers(s), store)


def _print_job(job, verbose=False):
    st = _STAGE_KO.get(job.stage, job.stage.value)
    hook = job.script.chosen_hook if job.script else "-"
    print(f"  {job.job_id}  [{st}]  {job.product.name}  | 후킹: {hook}")
    if job.error:
        print(f"      ⚠ {job.error}")
    if verbose:
        if job.final_video_path:
            print(f"      🎬 {job.final_video_path}")
        for l in job.log:
            print(f"      · {l}")


def cmd_run(args):
    agent = _agent(args)
    mode = "무인 자동(--auto)" if agent.s.auto else "반자동(게이트 운영)"
    dry = "DRY-RUN" if agent.s.dry_run else "실모드"
    print(f"▶ 배치 시작 [{dry} / {mode}] seeds={args.seeds} count={args.count}")
    seeds = [x.strip() for x in args.seeds.split(",") if x.strip()]
    jobs = agent.run_batch(seeds, args.count)
    print(f"\n생성된 잡 {len(jobs)}개:")
    for j in jobs:
        _print_job(j, verbose=True)
    if not agent.s.auto:
        gate_a = [j for j in jobs if j.stage == Stage.GATE_A]
        if gate_a:
            print(f"\n👉 GATE_A 승인 대기 {len(gate_a)}개. 승인: "
                  f"python -m shorts_agent gate-a <job_id>")


def cmd_list(args):
    agent = _agent(args)
    jobs = agent.store.all_jobs()
    if not jobs:
        print("잡이 없습니다. `run` 으로 시작하세요.")
        return
    print(f"전체 잡 {len(jobs)}개:")
    for j in sorted(jobs, key=lambda x: x.stage.value):
        _print_job(j)


def cmd_show(args):
    agent = _agent(args)
    job = agent.store.get(args.job_id)
    if not job:
        print("해당 job_id 없음")
        return
    _print_job(job, verbose=True)
    if job.script:
        print("\n--- 대본 ---")
        print("제목:", job.script.title)
        print("후킹:", job.script.chosen_hook)
        print("본문:", job.script.body)
        print("CTA:", job.script.cta)
        print("표시문구:", job.script.disclosure_text)


def cmd_gate_a(args):
    agent = _agent(args)
    job = agent.approve_a(args.job_id, approved=not args.reject)
    if not job:
        print("해당 job_id 없음")
        return
    _print_job(job, verbose=True)


def cmd_gate_b(args):
    agent = _agent(args)
    job = agent.approve_b(args.job_id, approved=not args.reject)
    if not job:
        print("해당 job_id 없음")
        return
    _print_job(job, verbose=True)


def main(argv=None):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(prog="shorts_agent", description="쇼핑 쇼츠 자동화 AI 에이전트")
    p.add_argument("--dry-run", action="store_true", help="키 없이 mock 으로 전 과정 시연")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="일일 배치 실행")
    r.add_argument("--seeds", default="주방,청소,뷰티,수납정리,생활가전", help="카테고리 시드(쉼표)")
    r.add_argument("--count", type=int, default=5, help="제작 개수(daily_cap 이하)")
    r.add_argument("--auto", action="store_true", help="게이트 자동 통과(무인 운영)")
    r.set_defaults(func=cmd_run)

    l = sub.add_parser("list", help="잡 목록/상태"); l.set_defaults(func=cmd_list)
    sh = sub.add_parser("show", help="잡 상세"); sh.add_argument("job_id"); sh.set_defaults(func=cmd_show)

    ga = sub.add_parser("gate-a", help="GATE A 승인/반려")
    ga.add_argument("job_id"); ga.add_argument("--reject", action="store_true")
    ga.set_defaults(func=cmd_gate_a)

    gb = sub.add_parser("gate-b", help="GATE B 승인/반려")
    gb.add_argument("job_id"); gb.add_argument("--reject", action="store_true")
    gb.set_defaults(func=cmd_gate_b)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
