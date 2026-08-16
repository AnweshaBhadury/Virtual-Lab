"""
AI assistant service.

Right now AI_PROVIDER=anthropic in your .env, so this calls the Anthropic
API over the internet. Later, when you build the offline version, you
just implement `_ask_local()` (e.g. call a local Ollama server) and flip
AI_PROVIDER=local in .env - nothing else in the app needs to change,
because every router only ever calls `ai_service.ask(...)`.
"""
import json
import requests

from app.config import settings


SYSTEM_PROMPT = """You are an AI lab assistant embedded in a virtual engineering
lab platform called ENGiTwin. A student is working through a hands-on
experiment. Your job:

1. Ask the student short, focused questions about what they are doing and
   observing in the simulation (one question at a time).
2. React to their answers - correct misconceptions gently, ask a follow-up,
   or move to the next concept.
3. Keep responses short (2-4 sentences), conversational, and encouraging.
4. Base your questions on the experiment context given to you (title,
   description, and the live simulation data/measurements if provided).
5. Never just give away the final answer - guide the student to reason
   it out.
"""


class AIService:
    def ask(self, experiment_context: dict, conversation: list[dict]) -> str:
        """
        experiment_context: {"title": ..., "description": ..., "simulation_data": {...}}
        conversation: list of {"role": "assistant"|"student", "content": "..."}
        Returns the assistant's next message (string).
        """
        if settings.AI_PROVIDER == "local":
            return self._ask_local(experiment_context, conversation)
        return self._ask_anthropic(experiment_context, conversation)

    def feedback(self, experiment_context: dict, measurements: dict, score: float, max_score: float) -> str:
        """Generate end-of-attempt narrative feedback for the Analytics/AI Feedback stage."""
        prompt = (
            f"Experiment: {experiment_context.get('title')}\n"
            f"Description: {experiment_context.get('description')}\n"
            f"Final measurements: {json.dumps(measurements)}\n"
            f"Score: {score}/{max_score}\n\n"
            "Write short feedback (3-5 sentences) for the student: what they "
            "did well, one specific thing to improve, and one concept to "
            "review if the score is low."
        )
        if settings.AI_PROVIDER == "local":
            return self._call_local(prompt)
        return self._call_anthropic(prompt)

    # ---------------- Anthropic (online) ----------------

    def _ask_anthropic(self, experiment_context: dict, conversation: list[dict]) -> str:
        context_line = (
            f"Experiment: {experiment_context.get('title')}\n"
            f"Description: {experiment_context.get('description')}\n"
            f"Live simulation data: {json.dumps(experiment_context.get('simulation_data', {}))}\n"
        )
        messages = [{"role": "user", "content": context_line}]
        for turn in conversation:
            role = "assistant" if turn["role"] == "assistant" else "user"
            messages.append({"role": role, "content": turn["content"]})
        if not conversation:
            messages.append({"role": "user", "content": "Start the lab conversation with your first question."})

        return self._call_anthropic_messages(messages)

    def _call_anthropic(self, prompt: str) -> str:
        return self._call_anthropic_messages([{"role": "user", "content": prompt}])

    def _call_anthropic_messages(self, messages: list[dict]) -> str:
        if not settings.ANTHROPIC_API_KEY:
            return "[AI assistant not configured: set ANTHROPIC_API_KEY in your .env file]"

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.ANTHROPIC_MODEL,
                    "max_tokens": 400,
                    "system": SYSTEM_PROMPT,
                    "messages": messages,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
            return "\n".join(text_blocks).strip() or "Sorry, I didn't get a response - try again."
        except requests.RequestException as e:
            return f"[AI assistant error: {e}]"

    # ---------------- Local (offline, fill in later) ----------------

    def _ask_local(self, experiment_context: dict, conversation: list[dict]) -> str:
        context_line = (
            f"Experiment: {experiment_context.get('title')}\n"
            f"Description: {experiment_context.get('description')}\n"
        )
        history = "\n".join(f"{t['role']}: {t['content']}" for t in conversation)
        prompt = SYSTEM_PROMPT + "\n\n" + context_line + "\n" + history
        return self._call_local(prompt)

    def _call_local(self, prompt: str) -> str:
        """
        Placeholder for your future fully-offline model (e.g. Ollama).
        Once you install Ollama and pull a model, this will work as-is:
            ollama pull llama3
            ollama serve
        """
        try:
            response = requests.post(
                settings.LOCAL_AI_URL,
                json={"model": settings.LOCAL_AI_MODEL, "prompt": prompt, "stream": False},
                timeout=60,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.RequestException as e:
            return f"[Local AI not reachable yet: {e}. Set AI_PROVIDER=anthropic in .env until you set this up.]"


ai_service = AIService()
