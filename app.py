import os
import json
import time
import threading
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv
from sheets.sheets_reader import read_deals
from sheets.sheets_writer import write_results
from agents.qualifier import qualify_deal

load_dotenv()

app = Flask(__name__)

# Global state
state = {
    "status": "idle",   # idle | running | done | error
    "results": [],
    "log": [],
    "progress": 0,
    "total": 0,
}
state_lock = threading.Lock()


def log(msg):
    with state_lock:
        state["log"].append({"ts": time.strftime("%H:%M:%S"), "msg": msg})


def run_pipeline():
    with state_lock:
        state.update({"status": "running", "results": [], "log": [], "progress": 0})

    try:
        log("Reading deal submissions from Google Sheets...")
        deals = read_deals()

        with state_lock:
            state["total"] = len(deals)

        log(f"Found {len(deals)} deal(s) to evaluate.")

        all_results = []
        for i, deal in enumerate(deals):
            log(f"[{i+1}/{len(deals)}] Qualifying: {deal['company']}...")
            result = qualify_deal(deal, log)
            all_results.append(result)
            with state_lock:
                state["results"] = list(all_results)
                state["progress"] = i + 1

        log("Writing scored cards to Deal-Flow-Tracker sheet...")
        write_results(all_results)
        log("Done. Sheet updated.")

        with state_lock:
            state["status"] = "done"

    except Exception as e:
        log(f"ERROR: {e}")
        with state_lock:
            state["status"] = "error"


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/run", methods=["POST"])
def run():
    with state_lock:
        if state["status"] == "running":
            return jsonify({"error": "Already running"}), 409
    t = threading.Thread(target=run_pipeline, daemon=True)
    t.start()
    return jsonify({"ok": True})


@app.route("/status")
def status():
    with state_lock:
        return jsonify(dict(state))


@app.route("/stream")
def stream():
    def event_gen():
        last_log_idx = 0
        while True:
            with state_lock:
                current = dict(state)
                new_logs = current["log"][last_log_idx:]
                last_log_idx = len(current["log"])

            for entry in new_logs:
                yield f"data: {json.dumps({'type': 'log', 'ts': entry['ts'], 'msg': entry['msg']})}\n\n"

            yield f"data: {json.dumps({'type': 'state', 'status': current['status'], 'progress': current['progress'], 'total': current['total'], 'results': current['results']})}\n\n"

            if current["status"] in ("done", "error"):
                break

            time.sleep(0.5)

    return Response(stream_with_context(event_gen()), mimetype="text/event-stream")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    app.run(debug=True, port=port)
