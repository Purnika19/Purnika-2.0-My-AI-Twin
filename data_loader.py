import json
import os
import requests

class DataLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def load_resume(self):
        resume_path = os.path.join(self.data_dir, "resume.json")
        chunks = []
        if os.path.exists(resume_path):
            try:
                with open(resume_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Intelligent chunking of JSON data
                for section, content in data.items():
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                chunk_text = f"[{section.upper()}] " + ", ".join([f"{k}: {v}" for k, v in item.items() if v])
                                chunks.append(chunk_text)
                            else:
                                chunks.append(f"[{section.upper()}] {item}")
                    elif isinstance(content, dict):
                        chunk_text = f"[{section.upper()}] " + ", ".join([f"{k}: {v}" for k, v in content.items() if v])
                        chunks.append(chunk_text)
                    else:
                        chunks.append(f"[{section.upper()}] {content}")
            except Exception as e:
                print(f"Error loading resume.json: {e}")
        else:
            print("Note: data/resume.json not found. You can add one.")
            # We don't auto-create here to avoid polluting with empty JSOn chunks,
            # but users can place it.
                
        return chunks

    def load_text_file(self, filename):
        path = os.path.join(self.data_dir, filename)
        chunks = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                # Simple markdown/text chunking separated by 2 newlines
                chunks = [p.strip() for p in content.split("\n\n") if p.strip()]
        else:
            print(f"Note: data/{filename} not found. Creating a blank file so you can fill it later.")
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
        return chunks

    def fetch_github_repos(self, username, token=None):
        if not username:
            return []
            
        print(f"Fetching GitHub repos for {username}...")
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if token:
            headers['Authorization'] = f'token {token}'
            
        url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=15"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                repos = response.json()
                chunks = []
                for repo in repos:
                    chunk = f"[GITHUB PROJECT] Repo Name: {repo.get('name')} | Description: {repo.get('description', 'No description')} | Primary Language: {repo.get('language', 'Unknown')} | Stars: {repo.get('stargazers_count', 0)}"
                    chunks.append(chunk)
                return chunks
            else:
                print(f"GitHub API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error fetching Github repos: {e}")
        return []

    def load_all_data(self):
        chunks = []
        
        # Load local JSON and text files
        chunks.extend(self.load_resume())
        chunks.extend(self.load_text_file("linkedin.txt"))
        chunks.extend(self.load_text_file("portfolio.txt"))
        
        # Load remote Github data
        github_username = os.getenv("GITHUB_USERNAME")
        github_token = os.getenv("GITHUB_TOKEN")
        
        if github_username:
            chunks.extend(self.fetch_github_repos(github_username, github_token))
            
        # Prevent crash if knowledge base is completely empty
        if not chunks:
            chunks.append("[SYSTEM] This is an AI Digital Twin. The creator hasn't loaded any data yet. Say you are working on it.")
            
        return chunks

    def add_learned_fact(self, text):
        path = os.path.join(self.data_dir, "linkedin.txt")
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n\n[USER DIRECT LEARNING] {text}")
        except Exception as e:
            print(f"Failed to save learned fact to disk: {e}")
