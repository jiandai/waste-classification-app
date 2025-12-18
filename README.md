# waste-classification-app

## LAN / local Wi‑Fi testing (Issue #2)

If you open the web UI from another device (phone/laptop), **do not hardcode the API as `localhost`**—on that device, `localhost` points to itself. The web app now defaults to calling the API on the **same host** as the page (port `8000`).

### 1) Run the backend so other devices can reach it

From the repo root:

```bash
python3 -m pip install -r backend/requirements.txt
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify from the host machine:

- `http://127.0.0.1:8000/health`
- `http://<YOUR_LAN_IP>:8000/health`

### 2) Serve the web UI on your LAN IP

From the repo root:

```bash
python3 -m http.server 8080 --directory web --bind 0.0.0.0
```

Then open from another device on the same Wi‑Fi:

- `http://<YOUR_LAN_IP>:8080/`

Optional: you can force the API base via query param:

- `http://<YOUR_LAN_IP>:8080/?apiBase=http://<YOUR_LAN_IP>:8000`

### 3) If the page still isn’t reachable from other devices

- **Wi‑Fi “AP/client isolation”**: many routers block device-to-device traffic by default (guest network especially). Disable isolation or use a non-guest SSID.
- **Firewall**: allow inbound TCP on ports **8080** and **8000** on the host machine.
- **Wrong IP**: confirm the host’s LAN IP (e.g. `ip a`) and that the other device is on the same subnet.
