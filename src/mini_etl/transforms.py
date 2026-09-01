from typing import Any, Callable, Generator, Iterable, Protocol

class TransformProtocol(Protocol):
    def transform(self, data: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
        ...

class BaseTransform:
    """Tüm dönüşümlerin atası ve >> operatörünün (rshift) tanmlandığı sınıf."""
    def transform(self, data: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
        raise NotImplementedError

    def __rshift__(self, other: Any) -> "PipelineChain":
        # Sağ tarafa başka bir transform veya sink geldiğinde zincir kurar
        return PipelineChain([self, other])

class MapTransform(BaseTransform):
    """Her satıra verilen bir fonksiyonu uygulayan (map) dönüşüm sınıfı."""
    def __init__(self, func: Callable[[dict[str, Any]], dict[str, Any]]):
        self.func = func

    def transform(self, data: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
        for row in data:
            yield self.func(row)

class PipelineChain:
    """Birden fazla transformasyonun veya sink'in >> ile birbirine bağlanmasını yönetir."""
    def __init__(self, steps: list[Any]):
        self.steps = steps

    def __rshift__(self, other: Any) -> "PipelineChain":
        self.steps.append(other)
        return self

    def execute(self, source_data: Iterable[dict[str, Any]]) -> None:
        current_data = source_data
        for step in self.steps:
            if hasattr(step, "transform"):
                current_data = step.transform(current_data)
            elif hasattr(step, "write"):
                step.write(current_data)
            else:
                raise TypeError(f"Geçersiz pipeline adımı: {step}")