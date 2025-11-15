# modules/psd_bottom_preview.py

from psd_tools import PSDImage
from PIL import Image
import uuid
import os
import tempfile

# ------------------------------------------------------------
# 🔍 Знаходимо найнижчий піксельний шар
# ------------------------------------------------------------
def _iter_layers(container):
    # convert to list so we can traverse from the bottom
    return reversed(list(container))

def _find_bottom_pixel_layer(container):
    for layer in _iter_layers(container):
        if layer.is_group():
            found = _find_bottom_pixel_layer(layer)  # group objects are iterable too
            if found:
                return found
        elif getattr(layer, "has_pixels", lambda: False)():
            return layer
    return None

def get_bottom_pixel_layer(psd):
    return _find_bottom_pixel_layer(psd)  # pass the PSDImage itself, not psd.layers


# ------------------------------------------------------------
# 🖼 Рендеримо лише 1 шар (включаємо тільки його)
# ------------------------------------------------------------
def render_single_layer(psd, layer):
    """
    Рендерить PNG повного розміру, де видимий лише 1 шар.
    Всі інші шари тимчасово вимикаються.
    """
    # Зберігаємо видимість
    original_visibility = [(l, l.visible) for l in psd.descendants()]

    # Все вимикаємо
    for l, _ in original_visibility:
        l.visible = False

    # Вмикаємо потрібний
    layer.visible = True

    # Рендер у full-size PNG
    img = psd.composite()

    # Відновлюємо видимість
    for l, v in original_visibility:
        l.visible = v

    return img


# ------------------------------------------------------------
# 📤 Експортуємо нижній шар → PNG для OpenCV
# ------------------------------------------------------------
def export_bottom_layer_png(psd_path, temp_dir=None):
    """
    Повертає шлях до PNG, де є тільки нижній піксельний шар.
    """
    if temp_dir is None:
        temp_dir = tempfile.gettempdir()
    os.makedirs(temp_dir, exist_ok=True)
    psd = PSDImage.open(psd_path)

    bottom = get_bottom_pixel_layer(psd)
    if bottom is None:
        raise RuntimeError("PSD не містить жодного піксельного шару.")

    img = render_single_layer(psd, bottom)

    # Створюємо унікальне ім'я PNG
    out_path = os.path.join(temp_dir, f"bottom_{uuid.uuid4().hex}.png")
    img.save(out_path, "PNG")

    return out_path
