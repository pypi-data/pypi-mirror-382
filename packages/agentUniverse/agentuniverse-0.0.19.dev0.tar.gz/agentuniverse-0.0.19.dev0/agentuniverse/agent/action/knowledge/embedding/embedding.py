# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 19:18
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: embedding.py
from abc import abstractmethod
from typing import List, Optional

from langchain_core.embeddings import Embeddings as LCEmbeddings

from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class Embedding(ComponentBase):
    """The basic class for embedding.

    Attributes:
        embedding_model_name (Optional[str]): The name of the embedding model.
    """

    component_type: ComponentEnum = ComponentEnum.EMBEDDING
    name: Optional[str] = None
    description: Optional[str] = None
    embedding_model_name: Optional[str] = None
    embedding_dims: Optional[int] = None

    @abstractmethod
    def get_embeddings(self, text: List[str], **kwargs) -> List[List[float]]:
        """Get embeddings."""

    @abstractmethod
    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[
        List[float]]:
        """Asynchronously get embeddings."""

    def as_langchain(self) -> LCEmbeddings:
        """Convert the agentUniverse(aU) embedding class to the langchain embedding class."""
        pass

    def _initialize_by_component_configer(self,
                                          embedding_configer: ComponentConfiger) \
            -> 'Embedding':
        """Initialize the embedding by the ComponentConfiger object.

        Args:
            embedding_configer(ComponentConfiger): A configer contains embedding
            basic info.
        Returns:
            Embedding: A embedding instance.
        """
        if embedding_configer.name:
            self.name = embedding_configer.name
        if embedding_configer.description:
            self.description = embedding_configer.description
        if hasattr(embedding_configer, "embedding_dims"):
            self.embedding_dims = embedding_configer.embedding_dims
        if hasattr(embedding_configer, "embedding_model_name"):
            self.embedding_model_name = embedding_configer.embedding_model_name
        return self
