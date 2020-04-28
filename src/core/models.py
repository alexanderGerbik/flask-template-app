import enum
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import orm as so
from sqlalchemy.dialects import postgresql as ps
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_method

from .database import Base, TrackModificationTimeMixin, session


class _TaskType(enum.Enum):
    NORMAL = "NORMAL"
    CC = "CC"  # consistency check
    QC = "QC"  # quality check
    QA = "QA"  # quality assurance


class TaskQuery(so.Query):
    def assignable(self, task_set_id=None, has_skippable=False):
        assign = so.aliased(Assignment)
        uid = sa.bindparam("user_id")

        stmt = (
            session.query(
                assign.task_id,
                sa.func.count(assign.task_id).label("assignments_count"),
                sa.func.bool_or(assign.user_id != uid).label("started_by_anyone"),
                sa.func.bool_or(assign.user_id == uid).label("previously_assigned"),
            )
            .filter(assign.is_relevant())
            .group_by(assign.task_id)
            .subquery()
        )

        query = (
            self.join(TaskSet, Task.task_set)
            .join(Group, TaskSet.groups)
            .join(UserGroup, Group.id == UserGroup.group_id)
            .outerjoin(
                Exclusion, (Exclusion.task_id == Task.id) & (Exclusion.user_id == uid),
            )
            .outerjoin(stmt)
            .filter(UserGroup.user_id == uid)
            .filter(Task.status == Task.Status.PROC)
            .filter(Exclusion.user_id.is_(None))
            .filter(
                Task.assigned_group_id.is_(None) | (Task.assigned_group_id == Group.id)
            )
            .filter(~sa.func.coalesce(stmt.c.previously_assigned, False))
            .filter(
                sa.func.coalesce(stmt.c.assignments_count, 0)
                < Task.assignments_required
            )
            .order_by(sa.desc(Task.priority))
        )
        if task_set_id:
            query = query.filter(Task.task_set_id == task_set_id)

        if has_skippable:
            is_skippable_expr = (
                TaskSet.allow_skip
                & (Task.type != Task.Type.CC)
                & (~Task.is_pushback)
                & (
                    Task.assigned_group_id.is_(None)
                    | (Task.assigned_group_id == TaskSet.default_group_id)
                    | ~sa.func.coalesce(stmt.c.started_by_anyone, False)
                )
            )
            query = query.options(
                so.with_expression(Task.is_skippable, is_skippable_expr)
            )
        return query


class Task(TrackModificationTimeMixin, Base):
    Type = _TaskType
    query = session.query_property(TaskQuery)

    id = sa.Column(ps.UUID(as_uuid=True), default=uuid4, primary_key=True)
    type = sa.Column(sa.Enum(_TaskType), nullable=False)

    raw_forbidden_for = so.relationship(lambda: Exclusion)
    forbidden_for = association_proxy("raw_forbidden_for", "user_id")

    is_skippable = so.query_expression()

    @staticmethod
    def get_skippable_expression(user_id, on_date=None):
        # when changes are made here, they should also be made in TaskQuery.assignable() function
        # this logic is duplicated there for performance reasons
        assign = so.aliased(Assignment)
        stmt = (
            session.query(
                assign.task_id,
                sa.func.bool_or(assign.user_id != user_id).label("started_by_anyone"),
            )
            .filter(assign.is_relevant(on_date))
            .group_by(assign.task_id)
            .subquery()
        )
        tsk = so.aliased(Task)
        is_skippable = (
            session.query(
                TaskSet.allow_skip
                & (tsk.type != Task.Type.CC)
                & (~tsk.is_pushback)
                & (
                    tsk.assigned_group_id.is_(None)
                    | (tsk.assigned_group_id == TaskSet.default_group_id)
                    | ~sa.func.coalesce(stmt.c.started_by_anyone, False)
                )
            )
            .select_from(tsk)
            .join(TaskSet, tsk.task_set)
            .outerjoin(stmt)
            .filter(tsk.id == Task.id)
            .as_scalar()
        )
        return is_skippable

    @hybrid_method
    def is_relevant(self, on_date=None):
        if on_date is None:
            on_date = datetime.utcnow()
        return self.deadline is None or (on_date <= self.deadline)

    @is_relevant.expression
    def is_relevant(self, on_date=None):
        if on_date is None:
            on_date = datetime.utcnow()
        return on_date <= sa.func.coalesce(
            self.deadline, sa.cast("infinity", self.deadline.type)
        )


class Exclusion(Base):
    user_id = sa.Column(ps.UUID(as_uuid=True), primary_key=True)
    task_id = sa.Column(
        "task_id",
        ps.UUID(as_uuid=True),
        sa.ForeignKey("task.id", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (sa.Index("ix_exclusion__tid_uid", "task_id", "user_id"),)

    def __init__(self, user_id):
        self.user_id = user_id
