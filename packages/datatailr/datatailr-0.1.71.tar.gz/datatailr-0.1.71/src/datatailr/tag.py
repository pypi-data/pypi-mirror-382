# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

from typing import Any, ClassVar


class dt__Tag:
    """
    Tag management for local runs in the absence of the DataTailr platform.
    All instances share the same tag store.
    """

    # shared across all instances
    tags: ClassVar[dict[str, Any]] = {
        "blob_storage_prefix": "local-no-dt-",
    }

    def ls(self) -> dict[str, Any]:
        return self.__class__.tags

    def get(self, name: str) -> Any:
        return self.__class__.tags.get(name)

    def set(self, name: str, value: Any) -> None:
        self.__class__.tags[name] = value

    def rm(self, name: str) -> None:
        self.__class__.tags.pop(name, None)
