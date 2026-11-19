"""
title: Aviso de Ambiente Simulado
author: Workshop Agents & Skills
version: 1.0.0
description: Acrescenta ao final de cada resposta um aviso de que as verificações usam uma base de dados fictícia do workshop.
"""

from typing import Optional

from pydantic import BaseModel, Field


class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=0, description="Execution order among filters.")
        notice: str = Field(
            default=(
                "⚠️ **Ambiente de treinamento.** As verificações deste agent usam uma base de dados fictícia "
                "criada para o workshop. Este resultado não vale para mensagens reais."
            ),
            description="Text appended to every assistant response.",
        )

    def __init__(self):
        self.valves = self.Valves()

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        messages = body.get("messages") or []
        if not messages or messages[-1].get("role") != "assistant":
            return body
        last = messages[-1]
        content = last.get("content") or ""
        if self.valves.notice not in content:
            last["content"] = f"{content}\n\n---\n{self.valves.notice}"
        return body
