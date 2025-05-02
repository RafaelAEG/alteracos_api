from __future__ import annotations

import hashlib
from typing import ClassVar, Any

from django.db import models
from django.db.models import QuerySet
from django.utils.crypto import get_random_string
from mptt.models import MPTTModel, TreeForeignKey

from content.exceptions import TreeNodeDoesNotExistsError
from content.utils.normalize_value import normalize_value


class NodeMatrix(MPTTModel):
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=False)
    description = models.TextField(blank=True, null=False)
    skippable = models.BooleanField(default=False)
    key = models.CharField(max_length=255, unique=True, blank=True)
    local = models.IntegerField(default=0)

    class MPTTMeta:
        order_insertion_by: ClassVar[list[str]] = ["name"]

    def save(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        if self.name:
            normalized = normalize_value(self.name)
            max_len = self._meta.get_field("key").max_length
            random_suffix = get_random_string(6)
            suffix_len = len(random_suffix) + 1
            base = normalized[: max_len - suffix_len]
            self.key = f"{base}-{random_suffix}"
        super().save(*args, **kwargs)

    def get_children(self) -> QuerySet[NodeMatrix]:
        return super().get_children()

    def get_descendants(self, include_self: bool = False) -> QuerySet[NodeMatrix]:
        return super().get_descendants(include_self)

    @classmethod
    def get_path_dict_by_name(cls, name: str) -> dict[int, str]:
        try:
            node = NodeMatrix.objects.get(name=name)
            ancestors = node.get_ancestors(include_self=True)
            return {level: node.name for level, node in enumerate(ancestors, start=1)}
        except NodeMatrix.DoesNotExist:
            raise TreeNodeDoesNotExistsError(name)

    @classmethod
    def get_path_dict_by_id(cls, _id: str) -> dict[int, dict[str, int]]:
        try:
            node = NodeMatrix.objects.get(id=_id)
            ancestors = node.get_ancestors(include_self=True)
            return {
                level: {"name": n.name, "id": n.id}
                for level, n in enumerate(ancestors, start=1)
            }
        except NodeMatrix.DoesNotExist:
            raise TreeNodeDoesNotExistsError(_id)