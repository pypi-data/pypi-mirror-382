from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Union

PaddingType = Union[int, Dict[Literal["left", "top", "right", "bottom"], int]]
AxisType = Literal["x", "y"]
ChartType = Literal["area", "bar", "bubble", "doughnut", "pie", "line", "polarArea", "radar", "scatter"]
AlignmentType = Literal["center", "left", "right"]


@dataclass
class DataSet:
    label: Optional[str] = None
    data: list[Any] = field(default_factory=list)
    clip: Optional[Union[int, dict]] = None
    type: Optional[str] = None
    order: Optional[int] = None
    stack: Optional[str] = None
    parsing: Optional[Union[bool, dict]] = None
    hidden: bool = False
    options: dict = field(default_factory=dict)
    background_color: Optional[str] = None

    def add_row(self, value: Any) -> None:
        self.data.append(value)

    def as_dict(self) -> Dict[str, Any]:
        data: dict[str, Any] = {"data": self.data}
        if self.label:
            data["label"] = self.label
        if self.hidden:
            data["hidden"] = True
        if self.options:
            data["options"] = self.options
        if self.type:
            data["type"] = self.type
        if self.background_color:
            data["backgroundColor"] = self.background_color

        return data


@dataclass
class ChartData:
    datasets: list[DataSet] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)

    def add_labels(self, *labels: str) -> None:
        for label in labels:
            if not isinstance(label, str):
                raise TypeError("label/s must be str type")
            self.labels.append(str(label))

    def add_dataset(self, dataset: DataSet) -> None:
        self.datasets.append(dataset)

    def as_dict(self) -> Dict[str, Any]:
        return {"labels": self.labels, "datasets": [dataset.as_dict() for dataset in self.datasets]}


@dataclass
class Chart:
    id: str
    type: ChartType
    data: ChartData = field(default_factory=ChartData)
    plugins: list = field(default_factory=list)
    options: dict = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        data_dict = {"type": self.type, "data": self.data.as_dict(), "options": self.options, "plugins": self.plugins}

        return data_dict
