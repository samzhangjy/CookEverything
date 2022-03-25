from requests import get as get_response
from zipfile import ZipFile
import os


class Downloader(object):
    def __init__(self) -> None:
        """HowToCook 菜谱下载器"""
        super().__init__()
        self.REQUEST_URL = "https://api.github.com/repos/{owner}/{repo}/zipball/"
        self.OWNER = "Anduin2017"
        self.REPO = "HowToCook"
    
    def crawl(self):
        data = get_response(self.REQUEST_URL.format(owner=self.OWNER, repo=self.REPO)).content
        with open("./data/__tmp.zip", "wb") as f:
            f.write(data)
    
    def unzip(self, filepath: str = "./data/__tmp.zip", extract_to: str = "./data/dishes"):
        with ZipFile(filepath, "r") as repo:
            files = repo.namelist()
            if not os.path.isdir(extract_to): os.mkdir(extract_to)
            for target in files:
                if target.split("/", 1)[-1].startswith("dishes"):
                    dir_name = target.split("/", 2)[-1].rsplit("/")[0]
                    file_name = target.rsplit('/')[-1]
                    if not file_name: continue
                    if not os.path.isdir(f"{extract_to}/{dir_name}"): os.mkdir(f"{extract_to}/{dir_name}")
                    with open(f"{extract_to}/{dir_name}/{file_name}", "wb") as f:
                        f.write(repo.read(target))
        os.remove(filepath)
    
    def download(self, filepath: str = "./data/dishes"):
        """HowToCook 菜谱自动下载器

        Args:
            filepath (str, optional): 下载路径. Defaults to "./data/dishes".
        """
        self.crawl()
        self.unzip(extract_to=filepath)


if __name__ == "__main__":
    downloader = Downloader()
    downloader.download()
