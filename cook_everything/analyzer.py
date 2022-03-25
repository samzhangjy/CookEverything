import re
from pprint import pprint

from demoji import replace as replace_emoji


class Converter(object):
    def __init__(self) -> None:
        """Markdown 格式菜谱转换 Python Dict Object"""
        super().__init__()

    def _format_text(self, text: str) -> str:
        TO_REMOVE = ["\n", " "]
        for word in TO_REMOVE:
            text = text.strip(word)
        return text

    def _get_header_text(self, markdown: str) -> str:
        return self._format_text(markdown.lstrip("##").strip())

    def _get_main_content_text(self, markdown: str) -> str:
        return self._format_text(markdown.lstrip("-").lstrip("*"))

    def convert(self, filepath: str) -> dict:
        """转换 Markdown 菜谱文档为 Python Dict Object

        Args:
            filepath (str): Markdown 文档路径

        Returns:
            dict: 转换完成的 Python Dict 对象
        """
        with open(filepath, "r") as f:
            contents = f.readlines()
        result = {"desc": "", "name": filepath.rsplit("/")[-1].rsplit(".", 1)[0]}
        current_processing = None
        for line in contents[1:]:
            line = self._format_text(line)
            if not line:
                continue
            if line.startswith("##"):
                current_processing = self._get_header_text(line)
                result[current_processing] = {"desc": "", "steps": []}
            elif line.startswith("-") or line.startswith("*"):
                result[current_processing]["steps"].append(
                    self._get_main_content_text(line))
            elif current_processing is None:
                result["desc"] += line
            else:
                result[current_processing]["desc"] += line
        return result


class Analyzer(Converter):
    def __init__(self) -> None:
        """通过已转换的 Python Dict 对象分析生成 JSON 菜谱"""
        super().__init__()
        self.TO_SPLIT = [" ", "（", "(", "“", "\"", "'"]
        self.UNITS = {
            "克": "g",
            "千克": "kg",
            "公斤": "kg",
            "毫升": "ml",
            "升": "l"
        }
        self.IGNORE_SEP = ["/", "-", "~", "～"]

    def _format_unit(self, text: str) -> str:
        TO_REMOVE = ["\n", " ", "）", ")"]
        for word in TO_REMOVE:
            text = text.strip(word)
        return text

    def _format_tips(self, tips: list[str]) -> list[str]:
        for i in range(len(tips)):
            tips[i] = tips[i].strip("（").strip("）")
        return tips

    def _normalize_unit(self, unit: str) -> str:
        return self.UNITS[unit] if unit in self.UNITS else unit

    def _analyze_calculation(self, data: dict) -> dict:
        """分析“计算”栏目

        Args:
            data (dict): 该栏目的 Python Dict 对象

        Returns:
            dict: 分析完成后的 Python Dict 对象
        """
        result = {}
        for line in data["steps"]:
            item = replace_emoji(line, "")
            num = re.findall("[0-9]+", item)
            unit = None
            if len(num):
                num = num[0]
                unit_start = item.find(num) + len(num)
                if item[unit_start] == " ":
                    unit_start += 1
                for i in range(unit_start, len(item)):
                    if item[i] in self.TO_SPLIT:
                        unit = item[unit_start: i].strip()
                if unit is None:
                    unit = item[unit_start:].strip()
                if unit[0] in self.IGNORE_SEP:
                    num += unit[0]
                    unit = unit.strip(unit[0])
                    to_strip = ""
                    for i in unit:
                        if not i.isdigit():
                            break
                        num += i
                        to_strip += i
                    unit = unit.strip(to_strip)
                unit = self._format_unit(unit)
                name = self._format_text(
                    item[:unit_start - len(num) + 1].strip().split("：")[0].strip(num))
            else:
                num = None
                name = item.split("（")[0]
            tips = re.findall("（.*）", item)
            is_optional = any("可选" in tip for tip in tips)
            result[name] = {
                "quantity": num,
                "unit": self._normalize_unit(unit),
                "is_optional": is_optional,
                "tips": self._format_tips(tips),
                "original": line
            }
        return result

    def _analyze_materials(self, data: dict) -> dict:
        """分析“必备原料和工具”栏目

        Args:
            data (dict): 该栏目的 Python Dict 对象

        Returns:
            dict: 分析完成后的 Python Dict 对象
        """
        result = {}
        for line in data["steps"]:
            item = line.strip("-").strip()
            name = item.split("（")[0]
            tips = re.findall("（.*）", item)
            is_optional = any("可选" in tip for tip in tips)
            result[name] = {
                "is_optional": is_optional,
                "tips": self._format_tips(tips),
                "original": line
            }
        return result
    
    def _analyze_steps(self, data: list) -> dict:
        """分析“操作”栏目

        Args:
            data (dict): 该栏目的 Python Dict 对象

        Returns:
            dict: 分析完成后的 Python Dict 对象
        """
        return [line.strip("-").strip("*") for line in data["steps"]]
    
    def _analyze_additional(self, data: list) -> dict:
        """分析“附加内容”栏目

        Args:
            data (dict): 该栏目的 Python Dict 对象

        Returns:
            dict: 分析完成后的 Python Dict 对象
        """
        return [line.strip("-").strip("*") for line in data["steps"]]

    def analyze(self, filepath: str) -> dict:
        """从转换完成的 Dict 对象分析相关内容并生成 Dict 对象

        Args:
            filepath (str): 要分析的 Markdown 菜谱文档路径

        Returns:
            dict: 分析后的 Python Dict 对象
        """
        _converted = self.convert(filepath)
        materials = self._analyze_calculation(_converted["计算"])
        _materails = self._analyze_materials(_converted["必备原料和工具"])
        for name, material in _materails.items():
            if name in materials:
                materials[name]["is_optional"] = material["is_optional"]
                for tip in material["tips"]:
                    if tip not in materials[name]["tips"]:
                        materials[name]["tips"].append(tip)
                continue
            materials[name] = {
                "quantity": None,
                "unit": None,
                "is_optional": material["is_optional"],
                "tips": material["tips"],
                "original": material["original"]
            }
        steps = self._analyze_steps(_converted["操作"])
        additional = self._analyze_additional(_converted["附加内容"])
        return {
            "materials": materials,
            "steps": steps,
            "additional": additional,
            "desc": _converted["desc"],
            "name": _converted["name"]
        }


if __name__ == "__main__":
    analyzer = Analyzer()
    pprint(analyzer.analyze("data/dishes/aquatic/鳊鱼炖豆腐.md"))
