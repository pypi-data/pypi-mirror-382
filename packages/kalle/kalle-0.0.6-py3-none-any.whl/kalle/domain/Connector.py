# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from pydantic import BaseModel
from typing import Optional, Dict


class Connector(BaseModel):
  name: str | None = None
  url: Optional[str] = None
  key: Optional[str] = None


class VertexaiConnector(Connector):
  project_id: Optional[str] = None
  region: Optional[str] = None
  credentials_path: Optional[str] = None


def connector_factory(data: Dict) -> Connector:
  if "project_id" in data or "region" in data:
    return VertexaiConnector(**data)
  else:
    return Connector(**data)
