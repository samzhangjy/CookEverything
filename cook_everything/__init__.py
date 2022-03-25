from get_repo import Downloader
from analyzer import Analyzer
import json
import os

class CookEverything(object):
    def __init__(self) -> None:
        """Cook Everything, 文字菜谱转 JSON 转换器一枚"""
        super().__init__()
        self.analyzer = Analyzer()
    
    def generate_json(self, filepath: str, export_path: str = "./data/export") -> dict:
        """根据给定参数生成 JSON 文件。

        Args:
            filepath (str): 要转换的 Markdown 菜谱
            export_path (str, optional): 转换出的 JSON 菜谱存储文件夹路径. Defaults to "./data/export".

        Returns:
            dict: 转换出的菜谱的 Python 字典对象
        """
        if not os.path.isdir(export_path): os.mkdir(export_path)
        result = self.analyzer.analyze(filepath)
        with open(f"{export_path}/{result['name']}.json", "w") as f:
            f.write(json.dumps(result, ensure_ascii=False, indent=2))
        return result

if __name__ == "__main__":
    cook = CookEverything()
    cook.generate_json("data/dishes/aquatic/鳊鱼炖豆腐.md")
