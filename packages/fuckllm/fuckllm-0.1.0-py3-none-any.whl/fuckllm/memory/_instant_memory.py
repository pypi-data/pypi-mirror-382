from fuckllm.type import ChatResponse


class InstantMemory:
    def __init__(self):
        self.memory: list[ChatResponse] = []

    def add_memory(self, memory: ChatResponse):
        self.memory.append(memory)

    def extend_memory(self, memory: list[ChatResponse]):
        self.memory.extend(memory)

    def get_memory(self):
        return self.memory

    def clear_memory(self):
        self.memory = []

    def to_openai(self):
        return [memory.to_openai() for memory in self.memory]

    def to_dict(self):
        return [memory.to_dict() for memory in self.memory]

    @classmethod
    def from_dict(self, data: dict):
        self.memory = [ChatResponse.from_dict(memory) for memory in data]
