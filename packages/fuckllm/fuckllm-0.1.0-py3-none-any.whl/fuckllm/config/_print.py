from dataclasses import dataclass


@dataclass
class PrintConfig:
    show_reasoning: bool = True
    show_tools: bool = True
    show_content: bool = True

    def to_dict(self) -> dict:
        return self.__dict__
