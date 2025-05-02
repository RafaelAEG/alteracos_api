from typing import Dict, List

from ninja import Router
from ninja.errors import HttpError

from content.exceptions import TreeNodeDoesNotExistsError
from content.services.matrix_svc.delete_root_node_and_descendants import delete_root_node_and_descendants
from content.services.matrix_svc.get_path_to_node_by_id import get_path_to_node_by_id
from content.services.matrix_svc.get_root_node_by_id import get_root_node_by_id
from content.services.matrix_svc.insert_tree_data_workflow import create_tree_workflow
from content.types.indexing import InsertTreeResultSchema, InsertTreePayload, RootNodeOut, DescendantsResponse, \
    NodeMatrixSerialized, NodePathOrdered
from content.types.workflow import WrapWorkflowResponse
from content.services.matrix_svc import get_path_to_node_by_name, get_descendants_at_same_level, get_root_nodes

router = Router()


@router.post("tree", response=WrapWorkflowResponse[InsertTreeResultSchema])
def create_or_update_tree(request, payload: InsertTreePayload) -> WrapWorkflowResponse[InsertTreeResultSchema]:
    response = create_tree_workflow(payload.parent, payload.tree)
    return response


@router.get("/node/path/name/{node_name}", response=dict[int, str])
def get_path_to_node(
    request,
    node_name: str
) -> Dict[int, str]:
    try:
        return get_path_to_node_by_name(node_name)
    except TreeNodeDoesNotExistsError:
        raise HttpError(404, f"The Node {node_name} was not found")


@router.get("node/path/{node_id}", response=NodePathOrdered)
def get_path_to_node(request, node_id: str) -> NodePathOrdered:
    try:
        return get_path_to_node_by_id(node_id)
    except TreeNodeDoesNotExistsError:
        raise HttpError(404, f"The Node with id {node_id} was not found")


@router.get("node/{node_id}/root", response=RootNodeOut)
def get_root_node(request, node_id: int):
    try:
        return get_root_node_by_id(node_id)
    except TreeNodeDoesNotExistsError as exc:
        raise HttpError(404, str(exc))


@router.get("node/{node_id}/descendants", response=DescendantsResponse)
def get_closest_descendants(request, node_id: int):
    try:
        return get_descendants_at_same_level(node_id)
    except TreeNodeDoesNotExistsError as exc:
        raise HttpError(404, str(exc))


@router.get("nodes/roots", response=List[NodeMatrixSerialized])
def get_available_trees(request):
    all_roots = get_root_nodes()
    filtered = [node for node in all_roots if node.local == 3]
    return [NodeMatrixSerialized.from_model(node) for node in filtered]


@router.delete("root/{node_id}")
def delete_root_node(request, node_id: int) -> None:
    delete_root_node_and_descendants(node_id)