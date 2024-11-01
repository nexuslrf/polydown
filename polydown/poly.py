import os, json
from rich import print

from .report import Report
from .downloader import Downloader
from . import theme


class Poly:
    def __init__(
        self,
        type,
        session,
        category,
        down_folder,
        sizes,
        overwrite,
        noimgs,
        iters,
        tone,
        file_format,
        model_format='blend',
    ):
        self.s = session
        self.type = type
        self.asset_url = f"https://api.polyhaven.com/assets?t={type}"
        if category != None:
            self.asset_url = f"https://api.polyhaven.com/assets?t={type}&c={category}"
        self.asset_list = [i for i in json.loads(self.s.get(self.asset_url).content)]

        self.down_folder = down_folder
        self.down_sizes = sizes
        self.overwrite = overwrite
        self.noimgs = noimgs
        self.iters = iters
        self.tone = tone
        self.file_format = file_format
        self.model_format = model_format

        self.corrupted_files = []
        self.exist_files = 0
        self.downloaded_files = 0

        self.report = Report()
        if type == "textures" or type == "models":
            self.main()
        else:
            self.hdris()
        self.report.show_report(self.overwrite, self.corrupted_files)

    def main(self):
        count = 0
        for asset in self.asset_list:
            files_url = "https://api.polyhaven.com/files/" + asset
            file_js = json.loads(self.s.get(files_url).content)
            if self.model_format not in file_js:
                print(f'{asset} does not have {self.model_format}, skip')
                continue
            k_list = [i for i in file_js[self.model_format]]
            k_list.sort(key=lambda fname: int(fname.split("k")[0]))

            def create_subfolder(k):
                # downfolder>ArmChair_01>ArmChair_01_1k>textures
                self.subfolder = self.down_folder + asset
                if not os.path.exists(self.subfolder):
                    os.mkdir(self.subfolder)
                if not os.path.exists(self.subfolder + f"/{asset}_{k}"):
                    os.mkdir(self.subfolder + f"/{asset}_{k}")
                    os.mkdir(self.subfolder + f"/{asset}_{k}/textures")

            print(
                theme.t_atitle
                + " ".join([i.capitalize() for i in asset.split("_")])
                + ":"
            )
            print(theme.t_file)

            for k in k_list if self.down_sizes == [] else self.down_sizes:
                if k in k_list:
                    include = file_js[self.model_format][k][self.model_format]["include"]
                    # download blend file
                    create_subfolder(k)
                    bl_url = file_js[self.model_format][k][self.model_format]["url"]
                    bl_md5 = file_js[self.model_format][k][self.model_format]["md5"]
                    filename = bl_url.split("/")[-1]
                    args = (
                        self.type,
                        asset,
                        self.s,
                        self.down_folder,
                        self.subfolder,
                        filename,
                        self.overwrite,
                        self.tone,
                        self.file_format,
                        bl_url,
                        bl_md5,
                        k,
                        True,
                    )
                    dw = Downloader(*args)
                    d = dw.file()
                    print(d[0])
                    self.report.add(d[1])
                    if d[2] == False:
                        self.corrupted_files.append(filename)
                    # download texture files
                    for i in include:
                        url = include[i]["url"]
                        md5 = include[i]["md5"]
                        filename = url.split("/")[-1]
                        args = (
                            self.type,
                            asset,
                            self.s,
                            self.down_folder,
                            self.subfolder,
                            filename,
                            self.overwrite,
                            self.tone,
                            self.file_format,
                            url,
                            md5,
                            k,
                            False,
                        )
                        dw = Downloader(*args)
                        d = dw.file()
                        print(d[0])
                        self.report.add(d[1])
                        if d[2] == False:
                            self.corrupted_files.append(filename)

            if self.noimgs != True:
                dw.img()
            count += 1
            if count == self.iters:
                break

    def hdris(self):
        count = 0

        for asset in self.asset_list:
            files_url = "https://api.polyhaven.com/files/" + asset
            file_js = json.loads(self.s.get(files_url).content)
            file_sizes_list = [i for i in file_js["hdri"]]
            file_sizes_list.sort(key=lambda fname: int(fname.split("k")[0]))

            print(
                theme.t_atitle
                + " ".join([i.capitalize() for i in asset.split("_")])
                + ":"
            )
            print(theme.t_file)

            for k in file_sizes_list if self.down_sizes == [] else self.down_sizes:
                url = file_js["hdri"][k][self.file_format]["url"]
                md5 = file_js["hdri"][k][self.file_format]["md5"]
                filename = url.split("/")[-1]
                args = (
                    self.type,
                    asset,
                    self.s,
                    self.down_folder,
                    None,
                    filename,
                    self.overwrite,
                    self.tone,
                    self.file_format,
                    url,
                    md5,
                )
                dw = Downloader(*args)
                d = dw.file()
                print(d[0])
                self.report.add(d[1])
                if d[2] == False:
                    self.corrupted_files.append(filename)

            if self.noimgs != True:
                dw.img()

            count += 1
            if count == self.iters:
                break
