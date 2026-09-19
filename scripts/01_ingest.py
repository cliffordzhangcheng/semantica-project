"""Document ingestion - compatibility wrapper"""
import sys
from semantica_workbench.pipeline.orchestrator import PipelineOrchestrator

if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()
    sys.exit(orchestrator.run_ingest())
