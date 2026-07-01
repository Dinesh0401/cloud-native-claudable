import urllib.request
import json
import sys

def main():
    url = 'http://localhost:8000/sessions/session-26266d20b716/exec'
    
    prompt = (
        'bash: '
        'echo "[Orchestrator] Starting build process..."; '
        'sleep 1; '
        'echo "[Orchestrator] Writing index.js..."; '
        'echo "console.log(\\"hello world\\");" > index.js; '
        'sleep 1; '
        'echo "[Orchestrator] Writing README.md..."; '
        'echo "# My App" > README.md; '
        'sleep 1; '
        'echo "[Orchestrator] Writing package.json..."; '
        'echo "{\\"name\\\": \\\"test\\\"}" > package.json; '
        'echo "[Orchestrator] All files successfully created!"'
    )
    
    req = urllib.request.Request(
        url,
        data=json.dumps({"prompt": prompt}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        res = urllib.request.urlopen(req)
        print("--- Stream Started ---")
        while True:
            chunk = res.read(64)
            if not chunk:
                break
            sys.stdout.write(chunk.decode("utf-8", errors="replace"))
            sys.stdout.flush()
        print("\n--- Stream Finished ---")
    except Exception as e:
        print("Error executing request:", e)

if __name__ == "__main__":
    main()
