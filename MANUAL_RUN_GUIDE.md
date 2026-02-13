# How to Run Services Manually (with Logs)

To run the services yourself and see the logs in real-time, you will need **two separate terminal windows**.

## Local IP Address
For your Flutter app on your phone, use this IP address in your `api_constants.dart`:
**IP**: `172.23.5.229`

---

## Terminal 1: OCR Service
1. Open a terminal.
2. Run this command:
   ```bash
   /home/rayu/DasTern/run_ocr_foreground.sh
   ```
   *This will run the OCR service on port 8000. You will see every request log here.*

## Terminal 2: AI Service
1. Open a second terminal.
2. Run this command:
   ```bash
   /home/rayu/DasTern/run_ai_foreground.sh
   ```
   *This will run the AI service on port 8001. It may take a moment to start if it needs to download models.*

## Testing Connection
Once both are running, you can verify they are connected by running this in a third terminal:
```bash
curl http://localhost:8001/api/v1/health
```

## Stopping Services
To stop a service, simply click in the terminal window and press **Ctrl+C**.
