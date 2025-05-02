from __future__ import annotations
from temporalio import activity
from content.models.node_matrix import NodeMatrix
from content.services.matrix_svc.get_node_by_id import get_node_by_id
from content.utils.normalize_value import normalize_value
from content.types.indexing import (
    InsertTreeResultSchema,
    InsertTreeWorkflowInSubTree,
    NodeMatrixSerialized,
)


def to_subtree_model(data: dict) -> dict[str, InsertTreeWorkflowInSubTree]:
    result = {}
    for k, v in data.items():
        children = v.get("children", {})
        result[k] = InsertTreeWorkflowInSubTree(
            skippable=v.get("skippable", False),
            local=v.get("local", 0),
            children=to_subtree_model(children) if children else {}
        )
    return result



@activity.defn
def insert_on_tree_from_dict(
    data: dict[str, InsertTreeWorkflowInSubTree],
    _parent: NodeMatrixSerialized
) -> InsertTreeResultSchema:
    result = InsertTreeResultSchema(
        nodes_inserted=0,
        nodes_updated=0,
        total_nodes_processed=0
    )

    data = to_subtree_model(data)
    parent = get_node_by_id(_parent.id)

    for node_name, subtree_model in data.items():
        children = subtree_model.children if subtree_model.children is not None else {}
        normalized = normalize_value(node_name)
        key = normalized
        node, created = NodeMatrix.objects.update_or_create(
            key=key,
            defaults={
                'name': node_name,
                'parent': parent,
                'skippable': subtree_model.skippable,
                'local': getattr(subtree_model, 'local', 0),
            }
        )
        result.total_nodes_processed += 1
        if created:
            result.nodes_inserted += 1
        else:
            if node.parent is None and parent is not None:
                node.parent = parent
                node.save()
                result.nodes_updated += 1

        if children:
            child_result = insert_on_tree_from_dict(children, NodeMatrixSerialized.from_model(node))
            result.nodes_inserted += child_result.nodes_inserted
            result.nodes_updated += child_result.nodes_updated
            result.total_nodes_processed += child_result.total_nodes_processed

    return result