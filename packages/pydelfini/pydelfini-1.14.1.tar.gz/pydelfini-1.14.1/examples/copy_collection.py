import json
import re
from collections.abc import Iterator
from typing import Any
from typing import cast
from typing import Generic
from typing import Literal
from typing import TypedDict
from typing import TypeGuard
from typing import TypeVar

import pydelfini
from pydelfini import exceptions
from pydelfini.collections import DelfiniFolder
from pydelfini.collections import DelfiniItem


class CycleMarker(TypedDict):
    n: int


def is_cycle_marker(val: Any) -> TypeGuard[CycleMarker]:
    return isinstance(val, dict) and "n" in val


T = TypeVar("T")


class CycleDetectQueue(Generic[T]):
    """Auto detect cycles in a queue.

    >>> q = CycleDetectQueue()
    >>> q.append('one')
    >>> q.append('two')
    >>> q.append('three')
    >>> _q = iter(q)
    >>> next(_q)
    'one'
    >>> next(_q)
    'two'
    >>> q.repeat('two')
    >>> next(_q)
    'three'
    >>> q.repeat('three')
    >>> next(_q)
    'two'
    >>> next(_q)
    'three'
    >>> q.repeat('three')
    >>> next(_q)
    'three'
    >>> q.repeat('three')
    >>> next(_q)
    Traceback (most recent call last):
        ...
    Exception: cycle detected, aborting

    """

    def __init__(self) -> None:
        self.items: list[T | CycleMarker] = [CycleMarker(n=0)]

    def append(self, item: T) -> None:
        marker = self.items.pop()
        assert is_cycle_marker(marker)
        self.items.append(item)
        marker["n"] = len(self.items)
        self.items.append(marker)

    def repeat(self, item: T) -> None:
        self.items.append(item)

    def __iter__(self) -> Iterator[T]:
        while self.items:
            item = self.items.pop(0)
            if is_cycle_marker(item):
                if item["n"] == 0:
                    return
                elif len(self.items) == item["n"]:
                    raise Exception("cycle detected, aborting")

                self.items.append(CycleMarker(n=len(self.items)))

            else:
                yield cast(T, item)


def do_copy(source_base: str, dest_base: str, collection_name: str) -> None:
    print("=== Login to source ===")
    source = pydelfini.login(source_base)
    if dest_base == source_base:
        dest = source
    else:
        print("=== Login to destination ===")
        dest = pydelfini.login(dest_base)

    source_collection = source.get_collection_by_name(collection_name)

    print()
    print("---- CREATING ----")

    print("[collection]", source_collection.name)
    dest_collection = dest.new_collection(
        source_collection.name,
        source_collection.description,
        source_collection.metadata,
    )

    map_q = CycleDetectQueue[DelfiniItem]()

    for item in source_collection.walk():
        if item.type == "folder":
            print("[folder]", item.path)
            base = (
                cast(DelfiniFolder, dest_collection[item.in_folder.path])
                if item.in_folder.path
                else dest_collection
            )
            base.new_folder(item.name)

        elif item.type == "dataview":
            map_q.append(item)

        elif item.type in ("file", "dictionary"):
            print(f"[{item.type}]", item.path)

            with dest_collection.open(
                item.path,
                "wb",
                type=cast(Literal["file", "dictionary"], item.type),
                parser=item.parser,
                columns=item.columns,
                metadata=item.metadata,
            ) as fp:
                fp.write(item.open("rb").read())

        elif item.type == "link":
            # TBD - need to have method for creating links
            pass

    # handle remapping dataviews
    for item in map_q:
        dv = item.open("r").read()
        dv = dv.replace("pigeon", "delfini")

        source_ids = re.findall(r"from `([-0-9a-f]+)`", dv)
        source_dest_map: dict[str, str] = {}
        for iid in source_ids:
            source_item = source_collection.get_item_by_id(iid)
            try:
                dest_item = dest_collection[source_item.path]
                source_dest_map[iid] = dest_item.id
            except exceptions.NotFoundError:
                print("Skipping dataview", item.path, "- will retry")
                pass

        if set(source_ids) != source_dest_map.keys():
            map_q.repeat(item)

        else:
            mapped_dv = dv
            for source_id, dest_id in source_dest_map.items():
                mapped_dv = mapped_dv.replace(source_id, dest_id)

            print("[dataview]", item.path)

            with dest_collection.open(
                item.path,
                "w",
                type="dataview",
                parser=item.parser,
                columns=item.columns,
                metadata=item.metadata,
            ) as fp:
                fp.write(mapped_dv)

    # update links and documents
    if "x-links-documents" in source_collection.metadata:
        links_docs = json.loads(source_collection.metadata["x-links-documents"])
        for doc in links_docs:
            if hit := re.match(r"delfini:([-0-9a-f]+)", doc.get("url", "")):
                source_item = source_collection.get_item_by_id(hit.group(1))
                print("[x-links-documents]", source_item.path)
                dest_item = dest_collection[source_item.path]
                doc["url"] = "delfini:" + dest_item.id

        new_metadata = source_collection.metadata.copy()
        new_metadata["x-links-documents"] = json.dumps(links_docs)

        dest_collection.set_metadata(new_metadata)


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--source-base", required=True)
    argparser.add_argument("--dest-base", required=True)
    argparser.add_argument("collection_name")

    args = argparser.parse_args()

    do_copy(args.source_base, args.dest_base, args.collection_name)
