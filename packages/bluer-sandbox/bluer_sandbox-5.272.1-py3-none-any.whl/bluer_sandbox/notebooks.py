import numpy as np
from typing import List, Union
import base64
from functools import reduce
from IPython.display import display, HTML
import matplotlib.pyplot as plt

from bluer_objects import storage, mlflow


def get_image_base64(filename):
    with open(filename, "rb") as f:
        data = f.read()
        return "data:image/gif;base64," + base64.b64encode(data).decode("utf-8")


def imshow(
    list_of_files: Union[
        np.ndarray,
        List[List[str]],
        List[str],
        str,
    ],
    dryrun: bool = False,
):
    if isinstance(list_of_files, np.ndarray):
        plt.figure(figsize=(10, 10))
        plt.imshow(
            list_of_files,
            cmap="viridis",
            aspect="equal",
        )
        plt.axis("off")
        plt.show()
        return

    if not isinstance(list_of_files, list):
        list_of_files = [list_of_files]
    list_of_files = [(row if isinstance(row, list) else [row]) for row in list_of_files]

    html = "".join(
        ["<table>"]
        + reduce(
            lambda x, y: x + y,
            [
                ["<tr>"]
                + [
                    '<td><img src="{}"></td>'.format(get_image_base64(filename))
                    for filename in row
                ]
                + ["</tr>"]
                for row in list_of_files
            ],
            [],
        )
        + ["</table>"]
    )

    if not dryrun:
        display(HTML(html))


def upload(
    object_name: str,
    public: bool = False,
    zip: bool = False,
) -> bool:
    if not storage.upload(
        object_name=object_name,
        public=public,
        zip=zip,
    ):
        return False

    if public or zip:
        return True

    return mlflow.log_run(object_name)
