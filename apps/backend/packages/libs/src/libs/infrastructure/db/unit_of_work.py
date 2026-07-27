"""UnitOfWork(トランザクション境界)のSQLAlchemy実装。

`libs.domain.repositories` の Protocol を構造的に満たす。ドメイン層側の
Protocol を import しないことで、データソース層 → ドメイン層 の一方向依存を保つ
(ドメインモデルを返すためのimportのみ)。
"""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

import sqlalchemy

from libs.infrastructure.db.repositories.billing import DbBillingRepository
from libs.infrastructure.db.repositories.catalog import DbCatalogRepository
from libs.infrastructure.db.repositories.reservation import DbReservationRepository


@dataclass(frozen=True)
class DbRepositories:
    """1つの接続に紐づくリポジトリの組。"""

    reservations: DbReservationRepository
    billing: DbBillingRepository
    catalog: DbCatalogRepository

    @classmethod
    def bind(cls, conn: sqlalchemy.engine.Connection) -> "DbRepositories":
        return cls(
            reservations=DbReservationRepository(conn),
            billing=DbBillingRepository(conn),
            catalog=DbCatalogRepository(conn),
        )


class SqlAlchemyUnitOfWork:
    def __init__(self, engine: sqlalchemy.Engine) -> None:
        self._engine = engine

    @contextmanager
    def begin(self) -> Iterator[DbRepositories]:
        """engine.begin() は正常終了でコミット、例外でロールバックする。"""
        with self._engine.begin() as conn:
            yield DbRepositories.bind(conn)

    @contextmanager
    def read(self) -> Iterator[DbRepositories]:
        with self._engine.connect() as conn:
            yield DbRepositories.bind(conn)
