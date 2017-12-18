# -*- coding: utf-8 -*-
import collections
import warnings
from functools import reduce


class Index(object):
    def __init__(self):
        self.inverted_index = dict()
        self.reserved = {'AND': 2, 'OR': 2, '(': None, ')': None, 'NOT': 1}
        self.document_counts = collections.Counter()
        self.token_counts = collections.Counter()
        self.documents = dict()
        self.operations = {
            "AND": reduce_by_intersection,
            "OR":
            lambda args: reduce(lambda s1, s2: s1.union(s2), args, set()),
            "NOT": lambda args: self.document_ids().difference(args[0])
        }

    def cardinality(self, operator):
        return self.reserved[operator]

    def document_ids(self):
        return set(self.document_counts.keys())

    def document(self, document_id):
        try:
            return (self.documents[document_id], None)
        except KeyError as e:
            return (None, e)

    def index_token(self, document_id, token):
        self.document_counts[document_id] += 1
        self.token_counts[token] += 1
        if token not in self.inverted_index:
            self.inverted_index[token] = collections.Counter()
        self.inverted_index[token][document_id] += 1

    def index_tokens(self, document_id, tokens):
        for token in tokens:
            self.index_token(document_id, token)

    def index(self, document_id, sentence, tokenizer=lambda s: s.split()):
        self.index_tokens(document_id, tokenizer(sentence.lower()))

    def index_document(self,
                       document_id,
                       document,
                       tokenizer=lambda s: s.split()):
        for key, value in document.items():
            self.index_field(document_id, key, to_list(value), tokenizer)
        self.documents[document_id] = document

    def index_field(self,
                    document_id,
                    field_name,
                    field_values,
                    tokenizer=lambda s: s.split()):
        for value in to_list(field_values):
            self.index(document_id, value, tokenizer)
            tokens = ["{0}:{1}".format(field_name, token)
                      for token in tokenizer(value)]
            self.index_tokens(document_id, tokens)

    def unindex_field(self,
                      document_id,
                      field_name,
                      field_values=None,
                      tokenizer=lambda s: s.split()):
        if not field_values:
            document, err = self.document(document_id)
            if err:
                field_values = []
            else:
                field_values = to_list(document.get(field_name, []))
        for value in field_values:
            self.unindex_string(document_id, value, tokenizer)
            tokens = ["{0}:{1}".format(field_name, token)
                      for token in tokenizer(value)]
            self.unindex_tokens(document_id, tokens)

    def unindex_string(self,
                       document_id,
                       sentence,
                       tokenizer=lambda s: s.split()):
        self.unindex_tokens(document_id, tokenizer(sentence))

    def unindex_tokens(self, document_id, tokens):
        removes = []
        for token in tokens:
            if document_id in self.inverted_index[token]:
                # decrease inverted_index count
                token_count = self.inverted_index[token][document_id]
                del self.inverted_index[token][document_id]
                count = self.inverted_index[token][document_id]
                # decrease doc count
                self.document_counts[document_id] -= token_count
                count = self.document_counts[document_id]
                if count == 0:
                    del self.document_counts[document_id]
                self.token_counts[token] -= token_count
                count = self.token_counts[token]

                if count == 0:
                    del self.token_counts[token]
            if len(self.inverted_index[token]) == 0:
                removes.append(token)
        for token in removes:
            del self.inverted_index[token]

    def unindex_document(self, document_id, tokenizer=lambda s: s.split()):
        document, err = self.document(document_id)
        if document:
            for key, value in document.items():
                self.unindex_field(document_id, key, to_list(value), tokenizer)
            if document_id in self.documents:
                del self.documents[document_id]

    def unindex(self, document_id):
        self.unindex_tokens(document_id, self.inverted_index.keys())

    def query_token(self, token):
        return set(
            self.inverted_index.get(token, collections.Counter()).keys())

    def query(self, q):
        try:
            return (self.process_query(
                q.replace('(', ' ( ').replace(')', ' ) ').split()), None)
        except Exception as e:
            return (set(), e)

    def process_query(self, expr):
        def is_term(token):
            return token not in self.reserved

        def is_op(token):
            return token in self.operations

        def is_lp(token):
            return token == '('

        def is_rp(token):
            return token == ')'

        def apply_operator(op, args):
            fn = self.operations.get(op, None)
            if fn:
                return fn(args)
            else:
                warnings.warn("Unknown operator: {0}".format(op))
                return set()

        value_stack = list()
        operator_stack = list()

        def reduce_operators():
            # print("reducing inside")
            op = operator_stack.pop()
            args = [value_stack.pop() for i in range(self.cardinality(op))]
            v = apply_operator(op, args)
            # print("op", op, "s1", s1, "s2", s2, "value", v)
            value_stack.append(v)

        # print("processing tokens")
        for token in expr:
            # print("current token is", token)
            if is_term(token):
                # print("Found a term", token)
                value_stack.append(self.query_token(token))
            elif is_lp(token):
                # print("found a lp", token)
                operator_stack.append(token)
            elif is_rp(token):
                # print("found a rp", token)
                while len(operator_stack) > 0 and not is_lp(operator_stack[
                        -1]):
                    reduce_operators()
                operator_stack.pop()  # pop off '('
            elif is_op(token):
                # print("found AND or OR, indexing to operator_stack")
                operator_stack.append(token)
        # print("operating on operator stack")
        while len(operator_stack) > 0:
            reduce_operators()
        # print("reducing values")
        return reduce_by_intersection(value_stack)


def reduce_by_intersection(sets):
    if len(sets) == 0:
        return set()
    else:
        head = sets[0]
        tail = sets[1:]
        return reduce(lambda s1, s2: s1.intersection(s2), tail, head)


def to_list(item):
    if type(item) is str:
        return [item]
    if type(item) is list:
        return item
    if getattr(item, '__iter__', None):
        list(item)
    return [item]
