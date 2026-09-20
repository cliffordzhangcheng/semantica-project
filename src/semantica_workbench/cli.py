#!/usr/bin/env python3
"""
R08: 统一CLI入口 - 调用semantica_workbench实现
所有scripts/0*.py都是薄包装，最终都调用这个入口
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from semantica_workbench.pipeline.orchestrator import PipelineOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Semantica Pipeline")
    parser.add_argument("command", choices=["ingest", "normalize", "build", "export", "validate", "run"])
    parser.add_argument("--config", "-c", default="config.yaml", help="Config file")
    parser.add_argument("--run-id", "-r", help="Run ID (auto-generated if not provided)")
    
    args = parser.parse_args()
    
    orchestrator = PipelineOrchestrator(args.config)
    
    try:
        if args.command == "run":
            exit_code = orchestrator.run_all(run_id=args.run_id)
        elif args.command == "validate":
            exit_code = orchestrator.validate()
        else:
            # 其他命令映射到具体阶段
            stage_map = {
                "ingest": orchestrator.ingest,
                "normalize": orchestrator.normalize,
                "build": orchestrator.build_and_store,
                "export": orchestrator.export,
            }
            exit_code = stage_map[args.command]()
        
        return exit_code
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3  # EXIT_EXECUTION_ERROR


if __name__ == "__main__":
    sys.exit(main())
