import os

from openai import OpenAI, OpenAIError
from sqlalchemy.orm import Session

from app import models

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "You are an operations assistant helping dispatchers manage delivery orders. "
    "Only answer using the operational data provided in the user message. "
    "If the answer cannot be determined from that data, say so explicitly instead of guessing. "
    "Keep answers concise, and where relevant, recommend a clear next action for the dispatcher. "
    "Respond with the final answer only, not your reasoning."
)


class AIAssistantError(Exception):
    pass


def _build_context(db: Session) -> str:
    orders = db.query(models.Order).order_by(models.Order.id).all()

    if not orders:
        return "There are currently no orders in the system."

    lines = []
    for order in orders:
        driver_name = order.driver.name if order.driver else "Unassigned"
        last_change = max(
            (h.changed_at for h in order.status_history),
            default=order.created_at,
        )
        lines.append(
            f'Order #{order.id}: "{order.description}" | '
            f"Status: {order.status.value} | Driver: {driver_name} | "
            f"Created: {order.created_at.isoformat()} | "
            f"Last status change: {last_change.isoformat()}"
        )

    return "\n".join(lines)


def ask_assistant(question: str, db: Session) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIAssistantError("AI assistant is not configured. Set OPENAI_API_KEY to enable it.")

    context = _build_context(db)
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Current operational data:\n{context}\n\nQuestion: {question}",
                },
            ],
            temperature=0.2,
            max_tokens=300,
        )
    except OpenAIError as exc:
        raise AIAssistantError("The AI assistant is currently unavailable. Please try again later.") from exc

    if not response.choices or not response.choices[0].message.content:
        raise AIAssistantError("The AI assistant did not return a response. Please try again.")

    return response.choices[0].message.content.strip()
