import os.path
import re
from typing import cast
from typing import Optional

import boto3
import pydelfini
from pydelfini.collections import FolderMixin
from pydelfini.exceptions import NotFoundError
from tqdm import tqdm

s3 = boto3.resource("s3")


class S3URL:
    """Parses an S3 URL.

    >>> u = S3URL('s3://example/path')
    >>> u.bucket
    'example'
    >>> u.path
    'path'

    >>> v = S3URL('s3://example/')
    >>> v.bucket
    'example'
    >>> v.path
    ''

    Raises ValueError if not parsable.

    >>> S3URL('something else')
    Traceback (most recent call last):
      ...
    ValueError: expect S3 URL of format s3://bucket-name/optional-path

    """

    def __init__(self, url: str):
        result = re.match(r"s3://([^/]+)/(.*)", url)
        if not result:
            raise ValueError("expect S3 URL of format s3://bucket-name/optional-path")
        self.bucket = result.group(1)
        self.path = result.group(2)

    def __str__(self) -> str:
        return f"s3://{self.bucket}/{self.path}"


def mkdirs(base: FolderMixin, path: str) -> FolderMixin:
    try:
        return cast(FolderMixin, base[path])
    except NotFoundError:
        dirs, name = os.path.split(path)
        if dirs:
            folder = mkdirs(base, dirs)
            return folder.new_folder(name)
        else:
            return base.new_folder(name)


def do_link(
    srv_base: str, collection_name: str, s3_url: S3URL, in_folder: Optional[str]
) -> None:
    client = pydelfini.login(srv_base)
    collection = client.get_collection_by_name(collection_name)
    if in_folder:
        base_folder = mkdirs(collection, in_folder)
    else:
        base_folder = collection

    bucket = s3.Bucket(s3_url.bucket)
    for obj in tqdm(bucket.objects.filter(Prefix=s3_url.path)):
        obj_path = obj.key.removeprefix(s3_url.path)
        obj_dir, obj_name = os.path.split(obj_path)
        if not obj_name:
            continue

        if obj_dir:
            folder = mkdirs(base_folder, obj_dir)
        else:
            folder = base_folder

        link_target = f"s3://{obj.bucket_name}/{obj.key}"
        folder.new_link(link_target, obj_name)


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--delfini-base", "-H", required=True)
    argparser.add_argument("--path", "-f")
    argparser.add_argument("s3_url", type=S3URL)
    argparser.add_argument("collection_name")

    args = argparser.parse_args()

    do_link(args.delfini_base, args.collection_name, args.s3_url, args.path)
