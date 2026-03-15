import os
import requests
import threading
import time

class TelegramNotifier:
    def __init__(self, callback=None):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.callback = callback
        
        if not self.bot_token or not self.chat_id:
            print("Warning: Telegram credentials not fully configured in .env. Unknown questions will print to console only.")
        elif self.callback:
            # Start background thread to listen for new learned facts
            self.polling_thread = threading.Thread(target=self._poll_updates, daemon=True)
            self.polling_thread.start()
            
    def send_message(self, text):
        if not self.bot_token or not self.chat_id:
            print(f"\n--- [SIMULATED TELEGRAM ALERT] ---\n{text}\n----------------------------------\n")
            return False
            
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"Failed to send Telegram message: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Exception while sending Telegram message: {e}")
            return False

    def _poll_updates(self):
        last_update_id = 0
        
        # Burn outstanding messages so it doesn't try to learn history on start
        try:
            init_url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            res = requests.get(init_url, timeout=5).json()
            if res.get("result"):
                last_update_id = res["result"][-1]["update_id"]
        except Exception:
            pass
            
        while True:
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates?offset={last_update_id + 1}&timeout=30"
                response = requests.get(url, timeout=40)
                if response.status_code == 200:
                    data = response.json()
                    for update in data.get("result", []):
                        last_update_id = update["update_id"]
                        msg = update.get("message", {})
                        
                        # Only accept messages from your personal authorized chat_id!
                        if str(msg.get("chat", {}).get("id")) == str(self.chat_id):
                            text = msg.get("text")
                            if text and self.callback:
                                self.callback(text)
            except Exception:
                pass
            time.sleep(2)
