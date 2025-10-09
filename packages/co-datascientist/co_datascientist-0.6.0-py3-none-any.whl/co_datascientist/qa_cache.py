import json
import hashlib
from pathlib import Path
from typing import List, Optional

class QACache:
    def __init__(self, cache_dir: str = ".qa_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, script_path: str) -> str:
        # Use script path as cache key - more stable than questions
        return hashlib.md5(script_path.encode()).hexdigest()[:8]

    def load(self, script_path: str) -> Optional[List[str]]:
        cache_key = self._get_cache_key(script_path)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                return data.get('answers')
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def save(self, script_path: str, answers: List[str]):
        cache_key = self._get_cache_key(script_path)
        cache_file = self.cache_dir / f"{cache_key}.json"

        data = {'script_path': script_path, 'answers': answers}
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass

    def clear(self, script_path: str):
        """Clear cache for a specific script path."""
        cache_key = self._get_cache_key(script_path)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                cache_file.unlink()
            except IOError:
                pass

def collect_answers(questions: List[str], script_path: str, observation: str = "") -> List[str]:
    # Clear any existing cache for this script before collecting new answers
    cache = QACache()
    cache.clear(script_path)

    if observation:
        print(observation)
        print()

    # Print all questions first
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
        print()  # Add blank line between questions

    print("Please answer each question:")

    # Then collect answers one by one
    answers = []
    for i, q in enumerate(questions, 1):
        ans = input(f"Answer {i}: ").strip()
        answers.append(ans)

    cache.save(script_path, answers)
    return answers

def get_answers(questions: List[str], script_path: str, observation: str = "", use_cache: bool = False) -> List[str]:
    if use_cache:
        cached = QACache().load(script_path)
        if cached:
            print("Using cached Q&A answers")
            return cached

    return collect_answers(questions, script_path, observation)
