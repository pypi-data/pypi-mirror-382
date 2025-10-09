from dataclasses import dataclass, asdict
from typing import List
import json

@dataclass
class FileStats:
    nmb_repetitions: int #n
    time: float #s
    energy: float #J
    nmb_spots: int #n
    line_length: float #m

@dataclass
class LayerInfo:
    layer_index: int
    layer_height: float #mm
    recoate_time: float #s
    files: List[FileStats]

    def get_layer_time(self):
        return sum(file.time * file.nmb_repetitions for file in self.files) + self.recoate_time
    def get_layer_energy(self):
        return sum(file.energy * file.nmb_repetitions for file in self.files)
    
@dataclass
class BuildInfo:
    layers: List[LayerInfo]
    start_temp: float #degress C
    start_heat: List[FileStats]

    def get_total_duration(self):
        total = 0.0
        for layer in self.layers:
            total += layer.get_layer_time()
        return total

    def to_json(self, file_path: str):
        """Serialize the BuildInfo object to a JSON file."""
        with open(file_path, "w") as f:
            json.dump(asdict(self), f, indent=4)

    @staticmethod
    def from_json(file_path: str) -> 'BuildInfo':
        """Deserialize a JSON file into a BuildInfo object."""
        with open(file_path, "r") as f:
            data = json.load(f)
        
        layers = [
            LayerInfo(
                layer_index=l['layer_index'],
                layer_height=l['layer_height'],
                recoate_time=l['recoate_time'],
                files=[FileStats(**fs) for fs in l['files']]
            )
            for l in data['layers']
        ]
        start_heat = [FileStats(**fs) for fs in data['start_heat']]
        return BuildInfo(
            layers=layers,
            start_temp=data['start_temp'],
            start_heat=start_heat
        )

@dataclass
class GeometryLayerInfo:
    layer_index: int
    melt_area_mm2: float #mm2
    melt_portion: float #%

@dataclass
class GeometryInfo:
    layers: List[GeometryLayerInfo]

    def to_json_file(self, filepath: str, indent: int = 4) -> None:
        """Write the GeometryInfo object to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=indent)
    @classmethod
    def from_json_file(cls, filepath: str) -> "GeometryInfo":
        """Read a GeometryInfo object from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Accept either {"layers": [...]} or just a list [...]
        if isinstance(data, dict):
            layers_data = data.get("layers", [])
        elif isinstance(data, list):
            layers_data = data
        else:
            raise ValueError("Invalid JSON format: expected object with 'layers' or a list.")

        layers = [GeometryLayerInfo(**item) for item in layers_data]
        return cls(layers=layers)