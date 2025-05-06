from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union, List

from ninja import Schema
from typing import Dict

from pydantic import RootModel

from content.models.node_matrix import NodeMatrix
from ninja import Schema
from typing import List

class BulkUpdateLocalIn(Schema):
    node_ids: List[int]
    new_local_value: str

class BulkUpdateLocalResult(Schema):
    updated_count: int
    errors: List[str] 

class NodeMatrixSerialized(Schema):
    id: int
    name: str
    key: str
    parent: Optional[str] = None
    local: str

    @classmethod
    def from_model(cls, node: NodeMatrix) -> "NodeMatrixSerialized":
        return cls(
            id=node.id,
            name=node.name,
            key=node.key,
            parent=node.parent.key if node.parent else None,
            local=node.local,

        )


class InsertTreeWorkflowInSubTree(Schema):
    skippable: Optional[bool] = False
    children: Optional[Dict[str, InsertTreeWorkflowInSubTree]] = None
    local: str

    class Config:
        extra = "allow"


class InsertTreeWorkflowIn(Schema):
    parent: NodeMatrixSerialized
    tree: Dict[str, InsertTreeWorkflowInSubTree]

    class Config:
        arbitrary_types_allowed = True


class InsertTreePayload(Schema):
    parent: str
    tree: Dict[str, InsertTreeWorkflowInSubTree]


class InsertTreeResultSchema(Schema):
  nodes_inserted: int
  nodes_updated: int
  total_nodes_processed: int

class NodeEntry(Schema):
    name: str
    id: int

class NodePathOrdered(RootModel[Dict[int, NodeEntry]]):
    pass

class InsertFragmentIn(Schema):
    fragment_value: str
    fragment_type: str

class BulkInsertFragmentIn(Schema):
    fragments: List[InsertFragmentIn]


class BulkInsertFragmentResult(Schema):
    workflow_id: str
    inserted_count: int
    fragment_ids: List[int]

class InsertFragmentResult(Schema):
    fragment_id: int

class InsertDataVecDBResult(Schema):
    id: str

@dataclass
class InsertFragmentWorkflowIn:
    fragment_value: str
    fragment_type: str
    vector_db_id: Optional[str] = None

class QuestionIndexerIn(Schema):
    fragments_amount_to_index: int
    root_node_id: Optional[int] = None
    fragments_ids: Optional[List[int]] = None

class FragmentsNodesToDeleteIn(Schema):
    fragments_ids: List[int]

class FragmentsDuplicatedStatsOut(Schema):
    total_fragments: int
    fragments_duplicated_count: int
    fragments_duplicated_not_indexed: int

class FragmentsDeletedStatsOut(Schema):
    total_duplicated_fragments: int
    deleted_fragments_without_nodes: int
    remaining_duplicated_fragments_with_nodes: int

class QuestionIndexerResultIn(Schema):
    indexed_fragments: int

@dataclass
class QuestionIndexerWorkflowIn:
  fragments_amount_to_index: int
  root_node_id: Optional[int] = None
  fragments_ids: Optional[List[int]] = None


@dataclass
class GetSuitableOptionsAgentsActivityIn:
    descendants: NodeDescendantsResponse
    fragment: FragmentSerialized


@dataclass
class SaveNodesOnFragmentActivityIn:
    nodes_ids: List[int]
    fragment_id: int


@dataclass
class CheckNextOptionsActivityIn:
    node_options_ids: List[int]
    fragment_id: int

@dataclass
class GetNonIndexedFragmentsActivityIn:
    amount: int
    root_node_id: int
    fragments_ids: Optional[List[int]] = None


@dataclass
class GetDescendantsForNodesActivityIn:
    root_node_id: int
    nodes_ids: List[int]

class NodeOptionResult(Schema):
    node_id: int
    children_count: int
    name: str

class RootNodeOut(Schema):
    root: NodeMatrixSerialized

    @classmethod
    def from_model(cls, node: NodeMatrix) -> "RootNodeOut":
        return cls(root=NodeMatrixSerialized.from_model(node))

class DescendantsResponse(Schema):
    descendants: List[NodeMatrixSerialized]

    @classmethod
    def from_model_list(cls, nodes: List[NodeMatrix]) -> "DescendantsResponse":
        return cls(descendants=[NodeMatrixSerialized.from_model(node) for node in nodes])


class FragmentResponse(Schema):
    id: int
    value: str


class UpdateFragmentNodesIn(Schema):
    fragment_id: int
    new_node_ids: List[int]


class UpdateFragmentNodesResponse(Schema):
    success: bool


class NodeBasicInfo(Schema):
    id: int
    name: str

    @classmethod
    def from_model(cls, node: NodeMatrix) -> "NodeBasicInfo":
        return cls(id=node.id, name=node.name)


class NodeDescendantsResponse(Schema):
    root_id: int
    root_name: str
    descendants: List[NodeBasicInfo]

    @classmethod
    def from_model(cls, root: NodeMatrix, descendants: List[NodeMatrix]) -> "NodeDescendantsResponse":
        return cls(
            root_id=root.id,
            root_name=root.name,
            descendants=[NodeBasicInfo.from_model(node) for node in descendants],
        )

class FragmentSerialized(Schema):
    id: int
    value: str
    fragment_type: str

class FragmentsIdsListOut(Schema):
    fragments_ids: List[int]


class IndexingSummary(Schema):
    total_fragments: int
    indexed_fragments: int
    reviewed_fragments: int
    duplicated_fragments: int
    invalid_fragments: int
