from typing import Callable, Iterable
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
import sqlparse
from sqlparse.sql import Statement, Token
from sqlparse import tokens as T

from adam.sql.term_completer import TermCompleter

columns = TermCompleter(['id', 'x.', 'y.', 'z.'])

def fr(*args):
    for arg in args:
        pass

class SqlCompleter(Completer):
    # <select_statement> ::= SELECT <select_list>
    #                      FROM <table_expression>
    #                      [WHERE <search_condition>]
    #                      [<group_by_clause>]
    #                      [<having_clause>]
    #                      [<order_by_clause>]
    #                      [<limit_clause>]

    # <search_condition> ::= <boolean_term>
    #                      | <search_condition> OR <boolean_term>

    # <boolean_term> ::= <boolean_factor>
    #                  | <boolean_term> AND <boolean_factor>

    # <boolean_factor> ::= [NOT] <predicate>
    #                    | ([NOT] <search_condition>)

    # <predicate> ::= <comparison_predicate>
    #               | <between_predicate>
    #               | <in_predicate>
    #               | <like_predicate>
    #               | <null_predicate>
    #               | <exists_predicate>
    #               | <quantified_predicate>
    #               | <unique_predicate>
    #               | <match_predicate>
    #               | <overlaps_predicate>
    #               | <distinct_predicate>
    #               | <member_predicate>
    #               | <submultiset_predicate>
    #               | <set_predicate>

    # <comparison_predicate> ::= <row_value_expression> <comparison_operator> <row_value_expression>
    # <comparison_operator> ::= '=' | '<>' | '<' | '<=' | '>' | '>='

    # <row_value_expression> ::= <value_expression>
    #                          | (<value_expression> [ { <comma> <value_expression> }... ])

    # <value_expression> ::= <numeric_value_expression>
    #                      | <string_value_expression>
    #                      | <datetime_value_expression>
    #                      | <interval_value_expression>
    #                      | <boolean_value_expression>
    #                      | <user_defined_type_value_expression>
    #                      | <reference_value_expression>
    #                      | <collection_value_expression>
    #                      | <row_value_constructor>
    #                      | <case_expression>
    #                      | <cast_expression>
    #                      | <subquery>
    #                      | NULL
    #                      | DEFAULT
    #                      | <identifier>
    #                      | <literal>

    # <insert_statement> ::= INSERT INTO <table_name> [ ( <column_list> ) ]
    #                        VALUES ( <value_list> )
    #                      | INSERT INTO <table_name> [ ( <column_list> ) ]
    #                        <query_expression>

    # <table_name> ::= <identifier>

    # <column_list> ::= <column_name> [ , <column_list> ]

    # <column_name> ::= <identifier>

    # <value_list> ::= <expression> [ , <value_list> ]

    # <query_expression> ::= SELECT <select_list> FROM <table_reference_list> [ WHERE <search_condition> ] [ GROUP BY <grouping_column_list> ] [ HAVING <search_condition> ] [ ORDER BY <sort_specification_list> ]

    # <update_statement> ::= UPDATE <table_name>
    #                        SET <set_clause_list>
    #                        [WHERE <search_condition>]

    # <set_clause_list> ::= <set_clause> { , <set_clause> }

    # <set_clause> ::= <column_name> = <update_value>

    # <update_value> ::= <expression> | NULL | DEFAULT

    # <search_condition> ::= <boolean_expression>

    # <delete_statement> ::= DELETE FROM <table_name> [ WHERE <search_condition> ]

    # <table_name> ::= <identifier>

    # <search_condition> ::= <boolean_expression>

    # <boolean_expression> ::= <predicate>
    #                      | <boolean_expression> AND <predicate>
    #                      | <boolean_expression> OR <predicate>
    #                      | NOT <predicate>
    #                      | ( <boolean_expression> )

    # <predicate> ::= <expression> <comparison_operator> <expression>
    #              | <expression> IS NULL
    #              | <expression> IS NOT NULL
    #              | <expression> LIKE <pattern> [ ESCAPE <escape_character> ]
    #              | <expression> IN ( <expression_list> )
    #              | EXISTS ( <select_statement> )
    #              | ... (other predicates)

    # <comparison_operator> ::= = | <> | != | > | < | >= | <=

    # <expression> ::= <literal>
    #               | <column_name>
    #               | <function_call>
    #               | ( <expression> )
    #               | <expression> <arithmetic_operator> <expression>
    #               | ... (other expressions)

    # <literal> ::= <numeric_literal> | <string_literal> | <boolean_literal> | <date_literal> | ...

    # <column_name> ::= <identifier>

    # <identifier> ::= <letter> { <letter> | <digit> | _ }...

    # <pattern> ::= <string_literal>

    # <escape_character> ::= <string_literal> (single character)

    # <expression_list> ::= <expression> { , <expression> }...
    def __init__(self, tables: Callable[[], list[str]], dml: str = None, debug = False):
        super().__init__()
        self.dml = dml
        self.tables = tables
        self.debug = debug
        self.machine = self.automata()

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text = document.text_before_cursor.lstrip()
        if self.dml:
            state = f'{self.dml}_'
            text = f'{self.dml} {text}'

        completer = None
        stmts = sqlparse.parse(text)
        if not stmts:
            completer = TermCompleter(['select', 'insert', 'delete', 'update'])
        else:
            statement: Statement = stmts[0]
            state = self.traverse_tokens(text, statement.tokens)
            if self.debug:
                print('\n  =>', state)
            if state == '':
                completer = TermCompleter(['select', 'insert', 'delete', 'update'])

            elif state == 'select_':
                completer = TermCompleter(['*'])
            elif state == 'select_a':
                completer = TermCompleter(['from'])
            elif state == 'select_a_comma_':
                completer = TermCompleter(['*'])
            elif state == 'select_a_':
                completer = TermCompleter(['from'])
            elif state == "select_from_":
                completer = TermCompleter(self.tables())
            elif state == "select_from_x_":
                completer = TermCompleter(['as', 'where', 'inner', 'left', 'right', 'full', 'group', 'limit'])
            elif state == "select_from_x_as_x_":
                completer = TermCompleter(['where', 'inner', 'left', 'right', 'full', 'group', 'limit'])
            elif state == "select_from_x_comma_":
                completer = TermCompleter(self.tables())
            elif state == "select_from_x_as_":
                completer = TermCompleter(['x', 'y', 'z'])
            elif state == "select_from_x_as_x_comma_":
                completer = TermCompleter(self.tables())
            elif state == "select_where_":
                completer = columns
            elif state in ["select_where_a", "select_where_a_"]:
                completer = TermCompleter(['=', '<', '<=', '>', '>=', '<>', 'like', 'not', 'in'])
            elif state == "select_where_a_not_":
                completer = TermCompleter(['like', 'in'])
            elif state == "select_where_a_in":
                completer = TermCompleter(['('])
            elif state == "select_where_a_in_lp_":
                completer = TermCompleter(["'", ')'])
            elif state == "select_where_a_in_lp_a_comma_":
                completer = TermCompleter(["'"])
            elif state == "select_where_a_op":
                completer = TermCompleter(["'"])
            elif state == "select_where_sc_":
                completer = TermCompleter(['and', 'or', 'group', 'limit'])
            elif state == "select_where_sc_limit_":
                completer = TermCompleter(['1'])
            elif state == "select_group_":
                completer = TermCompleter(['by'])
            elif state == "select_group_by_":
                completer = columns
            elif state == "select_group_by_a_comma_":
                completer = columns
            elif state == "select_group_by_a_":
                completer = TermCompleter(['limit'])
            elif state == "select_group_by_a_limit_":
                completer = TermCompleter(['1'])
            elif state == "select_from_x_inner_":
                completer = TermCompleter(['join'])
            elif state in ["select_join_", "select_from_x_left_join_"]:
                completer = TermCompleter(self.tables())
            elif state == "select_x_join_y,":
                completer = TermCompleter(self.tables())
            elif state == "select_x_join_y_":
                completer = TermCompleter(['on'])
            elif state == "select_x_join_y_on_":
                completer = columns
            elif state == "select_x_join_y_on_a":
                completer = TermCompleter(['='])
            elif state == "select_x_join_y_on_a_op":
                completer = columns
            elif state == "select_x_join_y_on_a_op_b_":
                completer = TermCompleter(['where', 'group', 'limit'])
            elif state == "select_from_x_left_":
                completer = TermCompleter(['outer', 'join'])
            elif state == "select_from_x_left_outer_":
                completer = TermCompleter(['join'])
            elif state == "select_from_x_right_":
                completer = TermCompleter(['outer', 'join'])
            elif state == "select_from_x_right_outer_":
                completer = TermCompleter(['join'])
            elif state == "select_from_x_full_":
                completer = TermCompleter(['outer'])
            elif state == "select_from_x_full_outer_":
                completer = TermCompleter(['join'])

            elif state == "insert_":
                completer = TermCompleter(['into'])
            elif state == "insert_into_":
                completer = TermCompleter(self.tables())
            elif state == "insert_into_x_":
                completer = TermCompleter(['values(', 'select'])
            elif state == "insert_into_x_lp_":
                completer = columns
            elif state == "insert_into_x_lp_a_comma_":
                completer = columns
            elif state == "insert_into_x_lp_a_rp__":
                completer = TermCompleter(['values(', 'select'])
            elif state == "insert_values":
                completer = TermCompleter(['('])
            elif state == "insert_values_lp_":
                completer = TermCompleter(["'"])

            elif state == "update_":
                completer = TermCompleter(self.tables())
            elif state == "update_x_":
                completer = TermCompleter(['set'])
            elif state in ["update_set_", "update_set_sc_comma_"]:
                completer = columns
            elif state == "update_set_a":
                completer = TermCompleter(['='])
            elif state == "update_set_a_op":
                completer = TermCompleter(["'"])
            elif state == "update_set_sc_":
                completer = TermCompleter(['where'])
            elif state == "update_where_":
                completer = columns
            elif state == "update_where_a":
                completer = TermCompleter(['='])
            elif state == "update_where_sc_":
                completer = TermCompleter(['and', 'or'])

            elif state == "delete_":
                completer = TermCompleter(['from'])
            elif state == "delete_from_":
                completer = TermCompleter(self.tables())
            elif state == "delete_from_x_":
                completer = TermCompleter(['where'])
            elif state == "delete_where_":
                completer = columns
            elif state == "delete_where_a":
                completer = TermCompleter(['='])
            elif state == "delete_where_a_op":
                completer = TermCompleter(["'"])
            elif state == "delete_where_sc_":
                completer = TermCompleter(['and', 'or'])

        if completer:
            for c in completer.get_completions(document, complete_event):
                yield c

    def automata(self):
        y = [
            '                                > select           > select',
            'select_                         > name|*           > select_a',
            'select_a                        > ,                > select_a_comma_',
            'select_a_comma_                 > name|*           > select_a',
            'select_a_                       > from             > select_from',
            'select_from_                    > name             > select_from_x',
            'select_from_x                   > ,                > select_from_x_comma_',
            'select_from_x_comma_            > name             > select_from_x',
            'select_from_x_',
            'select_from_x_as_x_             > ,                > select_from_x_comma_',
            '-                               > as               > select_from_x_as',
            '-                               > where            > select_where',
            '-                               > limit            > select_where_sc_limit',
            '-                               > group            > select_group',
            '-                               > group by         > select_group_by',
            '-                               > inner            > select_from_x_inner',
            '-                               > inner join       > select_join',
            '-                               > left             > select_from_x_left',
            '-                               > left join        > select_join',
            '-                               > left outer join  > select_join',
            '-                               > right            > select_from_x_right',
            '-                               > right join       > select_join',
            '-                               > right outer join > select_join',
            '-                               > full             > select_from_x_full',
            '-                               > full outer join  > select_join',
            'select_from_x_as_               > name             > select_from_x_as_x',
            'select_from_x_as_x              > ,                > select_from_x_as_x_comma_',
            'select_from_x_as_x_comma_       > name             > select_from_x_as_x',
            'select_where_                   > name             > select_where_a',
            'select_where_a                  > comparison       > select_where_a_op',
            'select_where_a_                 > comparison       > select_where_a_op',
            '-                               > not              > select_where_a_not',
            '-                               > in               > select_where_a_in',
            'select_where_a_not_             > comparison       > select_where_a_not_op',
            '-                               > in               > select_where_a_in',
            'select_where_a_in               > (                > select_where_a_in_lp_',
            'select_where_a_in_lp_           > name|single      > select_where_a_in_lp_a',
            'select_where_a_in_lp_a          > ,                > select_where_a_in_lp_a_comma_',
            '-                               > )                > select_where_sc',
            'select_where_a_in_lp_a_comma_   > name|single      > select_where_a_in_lp_a',
            'select_where_a_not_op           > name|single      > select_where_sc',
            'select_where_a_op               > name|single      > select_where_sc',
            'select_where_sc_                > and|or           > select_where',
            '-                               > group            > select_group',
            '-                               > group by         > select_group_by',
            '-                               > limit            > select_where_sc_limit',
            'select_group_                   > by               > select_group_by',
            'select_group_by_                > name             > select_group_by_a',
            'select_group_by_a               > ,                > select_group_by_a_comma_',
            'select_group_by_a_comma_        > name             > select_group_by_a',
            'select_group_by_a_              > limit            > select_where_sc_limit',
            'select_where_sc_limit           > _                > select_where_sc_limit_',
            'select_where_x_inner_           > join             > select_join',
            'select_join_                    > name             > select_x_join_y',
            'select_from_x_left_             > join             > select_join',
            '-                               > outer            > select_from_x_left_outer',
            'select_from_x_left_outer_       > join             > select_join',
            'select_from_x_                  > left outer join  > select_join',
            'select_from_x_right_            > join             > select_join',
            '-                               > outer            > select_from_x_right_outer',
            'select_from_x_right_outer_      > join             > select_join',
            'select_from_x_full_             > join             > select_join',
            '-                               > outer            > select_from_x_full_outer',
            'select_from_x_full_outer_       > join             > select_join',
            'select_x_join_y                 > ,                > select_x_join_y_comma_',
            'select_x_join_y_comma_          > name             > select_x_join_y',
            'select_x_join_y_                > on               > select_x_join_y_on',
            'select_x_join_y_on_             > name             > select_x_join_y_on_a',
            'select_x_join_y_on_a            > comparison       > select_x_join_y_on_a_op',
            'select_x_join_y_on_a_op         > name|single      > select_x_join_y_on_a_op_b',
            'select_x_join_y_on_a_op_b       > ,                > select_x_join_y_on_',
            'select_x_join_y_on_a_op_b_      > and|or           > select_join',
            '-                               > where            > select_where',
            '-                               > group            > select_group',
            '-                               > group by         > select_group_by',
            '-                               > limit            > select_where_sc_limit',


            '                                > insert           > insert',
            'insert_                         > into             > insert_into',
            'insert_into_                    > name             > insert_into_x',
            'insert_into_x                   > (                > insert_into_x_lp_',
            'insert_into_x_                  > (                > insert_into_x_lp_',
            '-                               > values           > insert_values',
            'insert_into_x_lp_               > name             > insert_into_x_lp_a',
            'insert_into_x_lp_a              > ,                > insert_into_x_lp_a_comma_',
            '-                               > )                > insert_into_x_lp_a_rp_',
            'insert_into_x_lp_a_comma_       > name             > insert_into_x_lp_a',
            'insert_into_x_lp_a_rp__         > values           > insert_values',
            '-                               > select           > select',
            'insert_values                   > (                > insert_values_lp_',
            'insert_values_lp_               > name|single      > insert_values_lp_v',
            'insert_values_lp_v              > ,                > insert_values_lp_v_comma_',
            'insert_values_lp_v_comma_       > name|single      > insert_values_lp_v',


            '                                > update           > update',
            'update_                         > name             > update_x',
            'update_x_                       > set              > update_set',
            'update_set_                     > name             > update_set_a',
            'update_set_a                    > comparison       > update_set_a_op',
            'update_set_a_op                 > name|single      > update_set_sc',
            'update_set_sc                   > ,                > update_set_sc_comma_',
            'update_set_sc_comma_            > name             > update_set_a',
            'update_set_sc_                  > ,                > update_set_sc_comma_',
            '-                               > where            > update_where',
            'update_where_                   > name             > update_where_a',
            'update_where_a                  > comparison       > update_where_a_op',
            'update_where_a_op               > name|single      > update_where_sc',
            'update_where_sc_                > and|or           > update_where',


            '                                > delete           > delete',
            'delete_                         > from             > delete_from',
            'delete_from_                    > name             > delete_from_x',
            'delete_from_x_                  > where            > delete_where',
            'delete_where_                   > name             > delete_where_a',
            'delete_where_a                  > comparison       > delete_where_a_op',
            'delete_where_a_op               > name|single      > delete_where_sc',
            'delete_where_sc_                > and|or           > delete_where',
        ]

        def add_space_transition(from_s: str):
            # add whitespace transition if a state with trailing whitespace is found from from states, for example, select > _ > select_
            if from_s.endswith('_') and not from_s.endswith('_comma_') and not from_s.endswith('_lp_') and not from_s.endswith('_rp_'):
                if self.debug:
                    print(f'{from_s[:-1]} > _ = {to_s}')
                machine[f'{from_s[:-1]} > _'] = from_s

        machine: dict[str, str] = {}

        from_ss_to_add = []
        from_ss = ['']
        token = None
        tokens = []
        to_s = None
        for l in y:
            tks = l.split('>')
            if l.startswith('-'):
                token = tks[1].strip(' ')
                if len(tks) > 2:
                    to_s = tks[2].strip(' ')
                    for from_s in from_ss:
                        tokens = [token]
                        if '|' in token:
                            tokens = token.strip(' ').split('|')

                        for t in tokens:
                            if self.debug:
                                print(f'{from_s} > {t} = {to_s}')
                            machine[f'{from_s} > {t}'] = to_s
            else:
                if len(tks) == 1:
                    from_s = tks[0].strip(' ')
                    add_space_transition(from_s)
                    from_ss_to_add.append(f'{from_s}')
                    continue

                from_ss = []
                from_ss.extend(from_ss_to_add)
                from_ss_to_add = []
                from_ss.append(f'{tks[0].strip(" ")}')
                for from_s in from_ss:
                    add_space_transition(from_s)
                    token = tks[1].strip(' ')
                    tokens = [token]
                    if len(tks) > 2:
                        to_s = tks[2].strip(' ')

                        if '|' in token:
                            tokens = token.split('|')

                        for t in tokens:
                            if self.debug:
                                print(f'{from_s} > {t} = {to_s}')
                            machine[f'{from_s} > {t}'] = to_s

        return machine

    def traverse_tokens(self, text: str, tokens: list[Token], state: str = '', indent=0):
        keywords = [
            'select', 'from', 'as', 'not', 'in', 'where',
            'and', 'or', 'group', 'by', 'group by', 'limit',
            'inner join', 'on', 'left', 'right', 'full', 'outer', 'left outer join',
            'left join', 'right outer join', 'right join', 'full join', 'full outer join',

            'insert', 'into', 'values',

            'update', 'where', 'set',

            'delete'
        ]

        for token in tokens:
            if self.debug:
                if token.ttype == T.Whitespace:
                    print('_ ', end='')
                elif token.ttype in [T.DML, T.Wildcard, T.Punctuation]:
                    print(f'{token.value} ', end='')
                elif token.ttype:
                    tks = str(token.ttype).split('.')
                    typ = tks[len(tks) - 1]
                    if ' ' in token.value:
                        print(f'"{token.value}:{typ}" ', end='')
                    else:
                        print(f'{token.value}:{typ} ', end='')
                # print("  " * indent + f"Token: {token.value}, Type: {token.ttype}@{token.ttype.__class__}")

            if token.is_group:
                state = self.traverse_tokens(text, token.tokens, state, indent + 1)
            else:
                it = ''
                if (t := token.value.lower()) in keywords:
                    it = t
                elif token.ttype == T.Text.Whitespace:
                    it = '_'
                elif token.ttype in [T.Name, T.Literal.String.Single]:
                    it = 'name'
                elif token.ttype == T.Wildcard:
                    it = '*'
                elif token.ttype == T.Punctuation:
                    if token.value == ',':
                        it = ','
                    elif token.value == '(':
                        it = '('
                    elif token.value == ')':
                        it = ')'
                elif token.ttype == T.Operator.Comparison:
                    it = 'comparison'

                try:
                    state = self.machine[f'{state} > {it}']
                except:
                    pass

        return state

    def completions(table_names: Callable[[], list[str]]):
        return {
            'delete': SqlCompleter(table_names, 'delete'),
            'insert': SqlCompleter(table_names, 'insert'),
            'select': SqlCompleter(table_names, 'select'),
            'update': SqlCompleter(table_names, 'update'),
        }