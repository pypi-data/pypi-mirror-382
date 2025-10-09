import re
from typing import Tuple, Dict, List, Optional, Set

from .And import And
from .Equal import Equal
from ..DCOperand import DCOperand
from ..LogicElement import LogicElement
from ..LogicOperand import LogicOperand
from ..LogicOperator import LogicOperator
from ..unary import Not
from ...ParserError import DCParserError
from ...tokenizer import Token
from ...util.RenamableColumnList import RenamableColumnList
from ....db import Table


class ConditionalSet:
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '|',

    def __init__(self, projection: LogicOperand, condition: LogicElement):
        self.projection: LogicOperand = projection
        self.condition: LogicElement = condition

    @staticmethod
    def split_tree(le: LogicElement, invert: bool = False) -> Tuple[Optional[LogicElement], List[DCOperand]]:
        # Logical not applies to all further DCOperands.
        if isinstance(le, Not):
            # Therefore we set invert to true while doing a recursive call.
            return ConditionalSet.split_tree(le.target, invert=not invert)

        # DCOperands are the relations. They contain either custom attribute names ("AS") or constants.
        if isinstance(le, DCOperand):
            # If the function was called with invert set to true, we store this
            # information in every upcoming DCOperand.
            le.invert = invert

            # First we look for constants to replace them with separate "AND" statements.
            for i in range(len(le.names)):
                if not le.names[i].is_constant:
                    continue

                # If a constant was found, we store the value and replace it with a random attribute name.
                constant = le.names[i]
                new_token = Token.random(constant)
                new_operand = DCOperand(le.relation,
                                        le.names[:i] + (new_token,) + le.names[i + 1:],
                                        skip_comma=True,
                                        depth=le.depth)

                # We now need an equality comparison to ensure the introduced attribute is equal to the constant.
                equality = Equal(
                    LogicOperand(new_token),
                    LogicOperand(constant)
                )

                # The new operand might contain more constants. We make a recursive call to eliminate them too.
                new_le, dc_operands = ConditionalSet.split_tree(new_operand, invert=invert)

                # If the recursive call returns None as the new element, the DCOperand does not contain any more
                # constants, so we just return the equality operation together with the DCOperands.
                if new_le is None:
                    return equality, dc_operands

                # Otherwise we "chain" the current and the subsequent equality check using an "AND".
                else:
                    return And(equality, new_le), dc_operands

            # If no constants were found, return None and le as DCOperand.
            return None, [le]

        # LogicOperators are the usual operators like logical and, logical or, but also mathematical terms.
        if isinstance(le, LogicOperator):
            # First we create an empty list for the DCOperands.
            dc_operands = []

            # We replace the left and right operands using recursive calls. The resulting DCOperands are
            # added to the list we prepared above.
            le.left, d = ConditionalSet.split_tree(le.left, invert=invert)
            dc_operands += d

            le.right, d = ConditionalSet.split_tree(le.right, invert=invert)
            dc_operands += d

            # If the left operand is None, we return the right operand.
            # As we check if the return value is None outside the function,
            # it is fine if the right operand is also None.
            if le.left is None:
                return le.right, dc_operands

            # If the right operand is None, we return the left operand.
            # The left operand can not be None because of the previous if-clause.
            # However, it would not hurt if the left operand was also None.
            elif le.right is None:
                return le.left, dc_operands

            # If none of them is None, we do not need to replace the current LogicElement
            # and therefore return it unchanged.
            else:
                return le, dc_operands

        # LogicOperands other than DCOperands stay as they are.
        # if isinstance(le, LogicOperand):
        #     print('LogicOperand:', le)

        # The default case is to return the LogicElement with not DCOperands.
        return le, []

    def to_sql_with_renamed_columns(self, tables: Dict[str, Table]) -> Tuple[str, Dict[str, str]]:
        # First we have to find and remove all DCOperands from the operator tree.
        condition, dc_operands = self.split_tree(self.condition)

        # We then create a RenamableColumnList with the user defined names and
        # remove all references that only consist of underscores. In the same
        # loop the select-statements for each table is constructed.
        rcls: List[RenamableColumnList] = []
        table_statements: Dict[str, str] = {}

        underscore_regex = re.compile(r'_{1,}')

        for operand_i, operand in enumerate(dc_operands):
            source_columns = tables[Table.normalize_name(operand.relation)].columns

            # Raise an exception if the given number of operands does not match
            # the number of attributes in the relation.
            if len(source_columns) != len(operand.names):
                raise DCParserError(f'invalid number of attributes for relation {operand.relation}',
                                    depth=operand.depth)

            # Create a column list for this operand.
            rcl: RenamableColumnList = RenamableColumnList.from_iter(source_columns)
            for source, target in zip(source_columns, operand.names):
                rcl.rename(source.name, target)

            # Remove all the underscore references.
            i = 0
            while i < len(rcl):
                if underscore_regex.fullmatch(rcl[i].name):
                    del rcl[i]
                else:
                    i += 1

            # Store the created data structures to find the joins in the next step.
            rcls.append(rcl)

            # Construct and store the select statement for this relation.
            columns = ', '.join(f'{r.current_name} AS {r.name}' for r in rcl)
            table_name = f't{operand_i}'

            table_statements[table_name] = f'(SELECT {columns} FROM {operand.relation}) {table_name}'

        # After that we need to find the "positive" joins using the provided custom
        # names for the attributes. We store the related operands and the join conditions.
        # Furthermore, `select_columns` contains a mapping from column names to a part of
        # a "select as" statement and joined_columns is a list of all columns that were
        # used for joins, so the resulting sql statements do not become ambiguous if they
        # are used for filtering.
        positive_joins: List[Tuple[str, str, Optional[List[str]]]] = []
        select_columns: Dict[str, str] = {}
        joined_columns: RenamableColumnList = RenamableColumnList()

        relevant_positive = [(f't{i}', rcl, op) for i, (rcl, op) in enumerate(zip(rcls, dc_operands)) if not op.invert]

        if len(relevant_positive) > 1:
            already_joined: Set[Tuple[str, str]] = set()

            # try to join every table with every other table
            for left_name, left_rcl, left_op in relevant_positive:
                discovered_joins = 0

                for right_name, right_rcl, right_op in relevant_positive:
                    # Skip if left and right table are the same.
                    if left_name == right_name:
                        continue

                    # Create a tuple representing the join and break the loop
                    # if both tables have been joined before.
                    join_tuple = min(left_name, right_name), max(left_name, right_name)
                    if join_tuple in already_joined:
                        discovered_joins += 1
                        continue

                    # Find intersecting attributes.
                    intersection, other = RenamableColumnList.intersect(left_rcl, right_rcl)

                    if len(intersection) > 0:
                        # Create the join condition for this combination of tables.
                        join_conditions = []

                        for l, r in intersection:
                            join_conditions.append(f'{left_name}.{l.name} = {right_name}.{r.name}')
                            l.current_name = f'{right_name}.{l.name}'

                            joined_columns.append(l)

                        # Store the names of the other columns if they are used in a
                        # select statement later.
                        for o in other:
                            if o.name in self.projection:
                                if o in left_rcl:
                                    select_columns[o.name] = f'{left_name}.{o.name} AS {o.name}'
                                else:
                                    select_columns[o.name] = f'{right_name}.{o.name} AS {o.name}'

                        # Finally store the join for constructing the sql statement
                        # and the tuple representing the join, so the same join
                        # does not happen again in reversed order.
                        positive_joins.append((left_name, right_name, join_conditions))

                        already_joined.add(join_tuple)
                        discovered_joins += 1

                # If no common attributes were discovered using this table,
                # a cross join is used instead.
                if discovered_joins == 0:
                    # Find any other table for the cross join, so the joins
                    # can later be constructed.
                    for right_name, _, _ in relevant_positive:
                        if left_name != right_name:
                            break
                    else:
                        raise DCParserError(f'could not build join for relation {left_name}',
                                            depth=left_op.depth)

                    join_tuple = min(left_name, right_name), max(left_name, right_name)

                    # Store the join with a join condition that is None.
                    positive_joins.append((left_name, right_name, None))
                    already_joined.add(join_tuple)

        # Last but not least we need to include the "negative" joins. They only
        # remove tuples and never add any attributes, so we only track the
        # required join statements with their respective conditions.
        negative_joins: List[Tuple[str, str, List[str], List[str]]] = []

        relevant_negative = [(f't{i}', rcl, op) for i, (rcl, op) in enumerate(zip(rcls, dc_operands)) if op.invert]
        for right_name, right_rcl, right_op in relevant_negative:
            discovered_joins = 0

            for left_name, left_rcl, left_op in relevant_positive:
                # Find intersecting attributes.
                intersection, _ = RenamableColumnList.intersect(left_rcl, right_rcl)

                if len(intersection) > 0:
                    # Create the join and the filter condition for this
                    # combination of tables.
                    join_conditions = []
                    filter_conditions = []

                    for l, r in intersection:
                        join_conditions.append(f'{left_name}.{l.name} = {right_name}.{r.name}')
                        filter_conditions.append(f'{right_name}.{r.name} IS NULL')
                        l.current_name = f'{left_name}.{l.name}'

                    # Store the join for constructing the sql statement.
                    negative_joins.append((left_name, right_name, join_conditions, filter_conditions))
                    discovered_joins += 1

            # If no joins were discovered using this table, an exception is raised.
            if discovered_joins == 0:
                raise DCParserError('no common attributes found for join', depth=right_op.depth)

        # The joins have to be sorted in a topologic order starting from t0.
        used_relations: Set[str] = {'t0'}

        all_positive_conditions: Dict[str, List[str]] = {}
        for _, target_name, join_condition in positive_joins:
            if target_name not in all_positive_conditions:
                all_positive_conditions[target_name] = []
            if join_condition is not None:
                all_positive_conditions[target_name].extend(join_condition)

        sorted_positive_joins: List[Tuple[str, str, Optional[str]]] = []
        while len(used_relations) < len(relevant_positive):
            for source_name, target_name, _ in positive_joins:
                apc = all_positive_conditions[target_name]
                if len(apc) == 0:
                    join_condition = None
                else:
                    join_condition = ' AND '.join(apc)

                if source_name in used_relations and target_name not in used_relations:
                    sorted_positive_joins.append((source_name, target_name, join_condition))
                    used_relations.add(source_name)
                    used_relations.add(target_name)
                    break

                if source_name not in used_relations and target_name in used_relations:
                    sorted_positive_joins.append((target_name, source_name, join_condition))
                    used_relations.add(source_name)
                    used_relations.add(target_name)
                    break

            else:
                raise DCParserError('no valid topologic order found for positive joins',
                                    depth=min(op.depth for _, _, op in relevant_positive))

        all_negative_conditions: Dict[str, List[str]] = {}
        all_negative_filters: Dict[str, List[str]] = {}
        for _, target_name, join_condition, filter_condition in negative_joins:
            if target_name not in all_negative_conditions:
                all_negative_conditions[target_name] = []
            all_negative_conditions[target_name].extend(join_condition)
            if target_name not in all_negative_filters:
                all_negative_filters[target_name] = []
            all_negative_filters[target_name].extend(filter_condition)

        sorted_negative_joins: List[Tuple[str, str, str, str]] = []
        while len(used_relations) < len(relevant_positive) + len(relevant_negative):
            for source_name, target_name, _, _ in negative_joins:
                join_condition = ' AND '.join(all_negative_conditions[target_name])
                filter_condition = ' AND '.join(all_negative_filters[target_name])

                if source_name in used_relations and target_name not in used_relations:
                    sorted_negative_joins.append((source_name, target_name, join_condition, filter_condition))
                    used_relations.add(source_name)
                    used_relations.add(target_name)
                    break

                if source_name not in used_relations and target_name in used_relations:
                    sorted_negative_joins.append((target_name, source_name, join_condition, filter_condition))
                    used_relations.add(source_name)
                    used_relations.add(target_name)
                    break
            else:
                raise DCParserError('no valid topologic order found for negative joins',
                                    depth=min(op.depth for _, _, op in relevant_negative))

        # Build the SQL statement.
        sql_select = ', '.join(select_columns[col] if col in select_columns else col
                               for col in self.projection)

        sql_tables = table_statements[relevant_positive[0][0]]
        for _, target_name, join_condition in sorted_positive_joins:
            target_table_stmt = table_statements[target_name]
            if join_condition is None:
                sql_tables += f' CROSS JOIN {target_table_stmt}'
            else:
                sql_tables += f' JOIN {target_table_stmt} ON {join_condition}'
        for _, target_name, join_condition, _ in sorted_negative_joins:
            target_table_stmt = table_statements[target_name]
            sql_tables += f' LEFT JOIN {target_table_stmt} ON {join_condition}'

        sql_join_filters = '1=1'
        for _, _, _, join_filter in sorted_negative_joins:
            sql_join_filters += f' AND {join_filter}'

        sql_condition = condition.to_sql(joined_columns) if condition is not None else '1=1'
        sql_query = f'SELECT DISTINCT {sql_select} FROM {sql_tables} WHERE ({sql_join_filters}) AND ({sql_condition})'

        # Create a mapping from intermediate column names to constant values.
        column_name_mapping = {
            p: p.constant
            for o in dc_operands
            for p in o.names
            if p.constant is not None
        }

        return sql_query, column_name_mapping

    def to_sql(self, tables: Dict[str, Table]) -> str:
        sql, _ = self.to_sql_with_renamed_columns(tables)
        return sql
