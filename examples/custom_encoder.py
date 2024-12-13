from flipcache import FlipCache
from dataclasses import dataclass, field


@dataclass
class Shape:
    name: str = "default"
    dimensions: list[float] = field(default_factory=list)
    edges: int = 0
    area: float = 0

    def __post_init__(self):
        if not self.area and self.dimensions:
            self.area = self.dimensions[0] * self.dimensions[1]


def encode_shape(shape: Shape) -> str:
    return f"{shape.name}||{shape.dimensions}||{shape.edges}||{shape.area}"


def decode_shape(shape: str) -> Shape:
    data = shape.split("||")
    return Shape(
        name=data[0],
        dimensions=[float(num) for num in data[1].strip("[]").split(",") if num],
        edges=int(data[2]),
        area=float(data[3]),
    )


my_shape = Shape(name="womp", dimensions=[4.1, 3.4], edges=6, area=16.38)
shape2 = Shape(name="wat", dimensions=[11, 22])

custom = FlipCache(
    "custom",
    local_max=0,
    key_type="int",
    value_type="custom",
    value_default=Shape(),
    value_encoder=encode_shape,
    value_decoder=decode_shape,
)

custom[123] = my_shape
custom[456] = shape2
print(custom[123])  # Shape(name='womp', dimensions=[4.1, 3.4], edges=6, area=16.38)
print(custom[321])  # Shape(name='default', dimensions=[], edges=0, area=0.0)
print(custom[456])  # Shape(name='wat', dimensions=[11.0, 22.0], edges=0, area=242.0)
