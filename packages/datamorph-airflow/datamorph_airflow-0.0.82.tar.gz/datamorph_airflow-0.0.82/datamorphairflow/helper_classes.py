from dataclasses import dataclass
from typing import Any, Dict

from airflow import DAG


"""
To achieve similar to Scala case class, in Python use dataclass
"""

@dataclass
class WorkflowDAG:
    dagid: str
    dag: DAG

@dataclass
class WorkflowDAGNode:
    name: str
    description: str
    type: str
    nodetype: str
    dependson: str
    taskparams: Dict[str,Any]

@dataclass
class S3url:
    bucket: str
    key: str