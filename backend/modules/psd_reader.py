from psd_tools import PSDImage
from typing import List, Dict, Any

def analyze_psd(file_path: str) -> Dict[str, Any]:
    psd = PSDImage.open(file_path)
    layers_info: List[Dict[str, Any]] = []

    def walk_layers(layers, parent=None):
        for layer in layers:
            try:
                layer_info = {
                    "name": layer.name,
                    "visible": layer.visible,
                    "bbox": tuple(layer.bbox),
                    "is_group": layer.is_group(),
                    "is_smart_object": getattr(layer, "is_smart_object", lambda: False)(),
                    "parent": parent,
                }
                layers_info.append(layer_info)

                # якщо це група — обходимо її дітей
                if layer.is_group():
                    walk_layers(layer.layers, parent=layer.name)
            except Exception as e:
                layers_info.append({
                    "name": f"<error: {str(e)}>",
                    "visible": False,
                    "bbox": None,
                    "is_group": False,
                    "parent": parent,
                })
            if layer.is_group():
                walk_layers(layer, parent=layer.name)

    walk_layers(psd)

    # 🔹 Акуратно дістаємо загальні метадані для будь-якої версії psd_tools
    width = getattr(psd, "width", None) or psd.size[0]
    height = getattr(psd, "height", None) or psd.size[1]
    mode = getattr(psd, "image_mode", "unknown")
    channels = getattr(psd, "number_of_channels", "unknown")

    return {
        "layers": layers_info,
        "width": width,
        "height": height,
        "mode": mode,
        "channels": channels,
    }
