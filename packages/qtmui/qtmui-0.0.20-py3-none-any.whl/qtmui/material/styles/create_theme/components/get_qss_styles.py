import inspect
from typing import Callable, Dict, Union, Optional
from .qss_properties import QssProperties
from qtmui.material.styles import useTheme
from functools import lru_cache


def camel_to_kebab_case(s: str) -> str:
    """
    Chuyển đổi chuỗi từ camelCase sang kebab-case.
    """
    return ''.join(['-' + c.lower() if c.isupper() else c for c in s]).lstrip('-')


def resolve_theme_value(theme, value: Union[str, Callable], key: str=None) -> Optional[str]:
    """
    Giải quyết giá trị theme từ chuỗi dạng 'palette.primary.main', 'text.secondary', v.v.
    """

    if isinstance(value, str) and (
        value.startswith("text.") 
        or value.startswith("background.")
        or value.startswith("primary.")
        or value.startswith("secondary.")
        or value.startswith("info.")
        or value.startswith("warning.")
        or value.startswith("error.")
        or value.startswith("grey.")
        ):
        value = f"palette.{value}"
        # print(value)

    if isinstance(value, str) and value.startswith("palette."):
        parts = value.split(".")
        theme_value = theme
        _value = None
        for part in parts:
            theme_value = getattr(theme_value, part, None)
            if theme_value is None:
                return None
        if value == "palette.background.navigation":
            print('palette.background.navigation__________', _value)
        if value == "palette.grey.200":
            print('palette.grey.200__________', theme_value)
        return theme_value
    elif isinstance(value, Callable):
        # return value(theme) # cũ 
        
        sig = inspect.signature(value)
        # Tạo đối số mặc định nếu không có
        default_args = {
            k: (v.default if v.default is not inspect.Parameter.empty else None)
            for k, v in sig.parameters.items()
        }

        try:
            return value(**default_args)
        except Exception as e:
            return None
    elif "font" not in key and ((isinstance(value, int) or isinstance(value, float)) and 0 <= value <= 3):
        # value = 8 * value
        value = value * theme.spacing.default_spacing

    return value


def get_qss_style(sx: Dict, class_name: Optional[str] = None) -> str:
    """
    Hàm tạo chuỗi QSS từ dictionary sx, hỗ trợ nested selectors và pseudo-classes.
    Nếu class_name=None, chỉ trả về chuỗi thuộc tính mà không bao bọc trong block.
    """
    # print("get_qss_style_____________________", sx)
    if isinstance(sx, str):
        return sx

    theme = useTheme()
    base_styles = []  # Styles cấp cao
    nested_styles = []  # Styles cho các selector lồng nhau

    for key, value in sx.items():
        # Chỉ áp dụng camel_to_kebab_case cho các key không bắt đầu bằng "&"
        if not key.startswith("&"):
            css_key = camel_to_kebab_case(key)
        else:
            css_key = key

        # Xử lý các selector lồng nhau (bắt đầu bằng "&")
        if css_key.startswith("&"):
            selector = css_key[1:].strip()  # Bỏ "&" và khoảng trắng
            if class_name is None:
                continue  # Bỏ qua nested selectors nếu không có class_name
            if selector.startswith(":"):  # Pseudo-class như &:hover
                pseudo_part, *child_part = selector.split(" ", 1)
                pseudo = pseudo_part[1:]  # Bỏ ":"
                if child_part:  # Có selector con, ví dụ &:hover .Typography
                    nested_selector = f"{class_name}[slot={pseudo}] {child_part[0].lstrip('.')}"
                else:
                    nested_selector = f"{class_name}[slot={pseudo}]"
            else:  # Không có pseudo-class, ví dụ & Typography hoặc & #container
                if " " in selector:  # Có khoảng trắng, ví dụ & Typography
                    nested_selector = selector.split(" ", 1)[1]  # Lấy phần sau khoảng trắng
                else:
                    nested_selector = f"{class_name} {selector}"

            if isinstance(value, dict):
                nested_qss = get_qss_style(value, nested_selector)
                nested_styles.append(nested_qss)
            continue

        # Xử lý thuộc tính CSS cấp cao
        
        resolved_value = resolve_theme_value(theme, value, key)
        if resolved_value is None:
            continue

        if css_key in QssProperties.__dict__.values():

            if css_key in ["marginX", "mx"]:
                base_styles.append(f"margin-left: {resolved_value};")
                base_styles.append(f"margin-right: {resolved_value};")
            elif css_key in ["marginY", "my"]:
                base_styles.append(f"margin-top: {resolved_value};")
                base_styles.append(f"margin-bottom: {resolved_value};")
            elif css_key in ["paddingX", "px"]:
                base_styles.append(f"padding-left: {resolved_value};")
                base_styles.append(f"padding-right: {resolved_value};")
            elif css_key in ["paddingY", "py"]:
                base_styles.append(f"padding-top: {resolved_value};")
                base_styles.append(f"padding-bottom: {resolved_value};")
            elif css_key == "width" and str(resolved_value).find("%") == -1:
                base_styles.append(f"min-width: {resolved_value};")
                base_styles.append(f"max-width: {resolved_value};")
            elif css_key == "height" and str(resolved_value).find("%") == -1:
                base_styles.append(f"min-height: {resolved_value};")
                base_styles.append(f"max-height: {resolved_value};")
            elif css_key not in ["mb", "display", "flex-shrink", "flex-grow", "align-items", 
                                "flex-direction", "align-self", "z-index", "justify-content"]:
                base_styles.append(f"{css_key}: {resolved_value};")

    # Tạo QSS
    qss = ""
    if base_styles:
        if class_name:
            qss = f"{class_name} {{\n    " + "\n    ".join(base_styles) + "\n}}"
        else:
            qss = "\n    ".join(base_styles)  # Chỉ trả về chuỗi thuộc tính nếu không có class_name
    if nested_styles:
        if qss:
            qss += "\n\n"
        qss += "\n\n".join(nested_styles)

    return qss.strip().replace("}}", "}")