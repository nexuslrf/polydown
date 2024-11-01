import os
import requests
import json
from rich import print

from .poly import Poly


def polycli(args):
    # print(args, "\n")
    asset_type = args.asset_type[0]
    folder = args.folder
    overwrite = args.overwrite
    sizes = args.sizes
    category = args.category
    noimgs = args.noimgs
    iters = args.iters
    tone = args.tone
    fileformat = args.fileformat
    modelformat = args.modelformat
    s = requests.Session()

    # ->🔒asset type->
    asset_type_list = list(json.loads(s.get("https://api.polyhaven.com/types").content))
    if asset_type not in asset_type_list:
        print(f"'{asset_type}' is not a valid asset type!")
        exit()

    # ->🔒category->
    if category == "":
        js = json.loads(
            s.get(f"https://api.polyhaven.com/categories/{asset_type}").content
        )
        print(f"[green]There are {len(js)} available categories for {asset_type}:")
        print(js)
        exit()
    elif category != None:
        asset_category_list = list(
            json.loads(
                s.get(f"https://api.polyhaven.com/categories/{asset_type}").content
            )
        )
        if category not in asset_category_list:
            print(
                f"[red]{category} is not a valid category.[/red]\nEnter empty '-c' argument to get the category list of the {asset_type}."
            )
            exit()

    # ->🔒file_format->
    if asset_type == "hdris" and fileformat not in ["exr", "hdr"]:
        print(f"[red]{fileformat} is not a valid file format for {asset_type}.[/red]")
        exit()
    # elif asset_type in ["models", "textures"] and fileformat not in [
    #     "jpg",
    #     "png",
    #     "exr",
    # ]:
    #     print(f"[red]{fileformat} is not a valid file format for {asset_type}.[/red]")
    #     exit()

    # ->🔒folder->
    down_folder = os.path.abspath(folder) + ("/" if folder[-1:] != "/" else "")
    if not os.path.exists(down_folder):
        try:
            os.mkdir(folder)
            print(f'"{folder}" folder not found, creating...')
        except Exception as e:
            print("[red]Error: " + str(e))
            exit()

    print(
        f"\n[cyan]🔗(polyhaven.com/{asset_type}"
        + (f"/{category}" if category != None else "")
        + ("['all sizes']" if sizes == [] else str(sizes))
        + f")=>🏠"
        + (f"({folder})" if not folder == "" else "")
        + "\n"
    )

    Poly(
        asset_type,
        s,
        category,
        down_folder,
        sizes,
        overwrite,
        noimgs,
        iters,
        tone,
        fileformat,
        modelformat
    )
