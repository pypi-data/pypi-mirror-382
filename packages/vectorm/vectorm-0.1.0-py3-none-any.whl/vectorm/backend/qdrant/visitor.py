from __future__ import annotations

from typing import Any

from qdrant_client.http.models import (
    FieldCondition,
    IsNullCondition,
    MatchAny,
    MatchExcept,
    MatchValue,
    Range,
)
from qdrant_client.http.models import (
    Filter as QdrantFilter,
)

from vectorm.filter import (
    BinaryExpression,
    ExpressionVisitor,
    FieldExpression,
    LiteralExpression,
    Operator,
    UnaryExpression,
    VariadicExpression,
)


class QdrantExpressionVisitor(ExpressionVisitor):
    def visit_literal(self, literal: LiteralExpression) -> Any:
        return literal.value

    def visit_field(self, field: FieldExpression) -> Any:
        return ".".join(field.fields)

    def visit_unary(self, unary: UnaryExpression) -> Any:
        operand = unary.operand.accept(self)

        match unary.operator:
            case Operator.not_:
                return QdrantFilter(
                    must_not=[operand],
                )
            case Operator.exists:
                return QdrantFilter(
                    must=FieldCondition(
                        key=operand,
                        is_null=IsNullCondition(is_null=False)
                    )
                )
            case _:
                raise ValueError(f"Unsupported unary operator: {unary.operator}")

    def visit_binary(self, binary: BinaryExpression) -> Any:
        left = binary.left.accept(self)
        right = binary.right.accept(self)

        match binary.operator:
            case Operator.eq:
                return QdrantFilter(
                    must=FieldCondition(
                        key=left,
                        match=MatchValue(value=right)
                    )
                )
            case Operator.ne:
                return QdrantFilter(
                    must_not=[
                        FieldCondition(
                            key=left,
                            match=MatchValue(value=right)
                        )
                    ]
                )
            case Operator.lt:
                return QdrantFilter(
                    must=FieldCondition(
                        key=left,
                        range=Range(lt=right)
                    )
                )
            case Operator.le:
                return QdrantFilter(
                    must=FieldCondition(
                        key=left,
                        range=Range(lte=right)
                    )
                )
            case Operator.gt:
                return QdrantFilter(
                    must=FieldCondition(
                        key=left,
                        range=Range(gt=right)
                    )
                )
            case Operator.ge:
                return QdrantFilter(
                    must=FieldCondition(
                        key=left,
                        range=Range(gte=right)
                    )
                )
            case Operator.in_:
                return QdrantFilter(
                    must=FieldCondition(
                        key=left,
                        match=MatchAny(any=right)
                    )
                )
            case Operator.not_in:
                return QdrantFilter(
                    must_not=[
                        FieldCondition(
                            key=left,
                            match=MatchExcept(**{"except": right})
                        )
                    ]
                )
            case Operator.and_:
                return QdrantFilter(
                    must=[left, right],
                )
            case Operator.or_:
                return QdrantFilter(
                    should=[left, right],
                )

    def visit_variadic(self, variadic: VariadicExpression) -> Any:
        operands = [operand.accept(self) for operand in variadic.operands]

        match variadic.operator:
            case Operator.and_:
                return QdrantFilter(
                    must=operands,
                )
            case Operator.or_:
                return QdrantFilter(
                    should=operands,
                )
            case Operator.not_:
                return QdrantFilter(
                    must_not=operands,
                )
            case Operator.any_:
                return QdrantFilter(
                    should=operands,
                    min_should=1,
                )
            case Operator.all_:
                return QdrantFilter(
                    must=operands,
                )

        raise ValueError(f"Unsupported variadic operator: {variadic.operator}")
