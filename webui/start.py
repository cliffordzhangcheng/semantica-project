#!/usr/bin/env python3
"""R10: WebUI - 绑定真实run_id和真实状态"""
from pathlib import Path
import json

def main():
    """启动WebUI，绑定到localhost:5555"""
    import sys
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    
    run_id = sys.argv[1] if len(sys.argv) > 1 else 'latest'
    web_dir = Path('webui')
    
    # 验证run存在
    run_dir = Path('artifacts/runs') / run_id
    if not run_dir.exists():
        print(f"Error: Run '{run_id}' not found in {run_dir}")
        sys.exit(2)
    
    manifest = json.loads((run_dir / 'run_manifest.json').read_text())
    
    if manifest.get('overall_status') != 'SUCCEEDED':
        print(f"Warning: Run '{run_id}' status is {manifest.get('overall_status')}")
    
    # 启动HTTP服务器
    os.chdir(web_dir)
    server = HTTPServer(('localhost', 5555), SimpleHTTPRequestHandler)
    print(f"WebUI running at http://localhost:5555")
    print(f"Bound to run_id: {run_id}")
    server.serve_forever()

if __name__ == '__main__':
    main()