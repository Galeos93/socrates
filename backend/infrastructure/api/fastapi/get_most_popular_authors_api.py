from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

from fastapi import Depends

from application.use_cases.get_popular_authors import GetPopularAuthors
from domain.entities.author import AuthorPopularity
from domain.entities.user_id import UserId
from infrastructure.fastapi.common import get_anonymous_user


class GetPopularAuthorsAPIBase(ABC):
    """Abstract base class for getting popular authors endpoints."""

    @abstractmethod
    async def get_popular_authors(self, user_id: UserId) -> List[AuthorPopularity]:
        """Get a list of popular authors."""
        pass


@dataclass
class GetPopularAuthorsAPIImpl(GetPopularAuthorsAPIBase):
    """Implementation of the GetPopularAuthorsAPIBase."""
    get_popular_authors_use_case: GetPopularAuthors

    async def get_popular_authors(self, user_id: UserId = Depends(get_anonymous_user)) -> List[AuthorPopularity]:
        """Get a list of popular authors endpoint implementation."""
        return self.get_popular_authors_use_case.execute(user_id=user_id)
