from rtamt.syntax.ast.visitor.stl.ast_visitor import StlAstVisitor
from rtamt.pastifier.ltl.horizon import LtlHorizon

from rtamt.exception.exception import RTAMTException


class StlHorizon(LtlHorizon, StlAstVisitor):

    def __init__(self):
        LtlHorizon.__init__(self)

    def visit(self, node, *args, **kwargs):
        return StlAstVisitor.visit(self, node, *args, **kwargs)

    def visitTimedEventually(self, node, *args, **kwargs):
        op_horizon = self.visit(node.children[0], *args, **kwargs)
        self.horizons[node] = op_horizon + node.end
        return op_horizon + node.end

    def visitTimedAlways(self, node, *args, **kwargs):
        op_horizon = self.visit(node.children[0], *args, **kwargs)
        self.horizons[node] = op_horizon + node.end
        return op_horizon + node.end

    def visitTimedUntil(self, node, *args, **kwargs):
        op1_horizon = self.visit(node.children[0], *args, **kwargs)
        op2_horizon = self.visit(node.children[1], *args, **kwargs)
        out = max(op1_horizon, op2_horizon) + node.end
        self.horizons[node] = out
        return out

    def visitTimedOnce(self, node, *args, **kwargs):
        op_horizon = self.visit(node.children[0], *args, **kwargs)
        self.horizons[node] = op_horizon
        return op_horizon

    def visitTimedHistorically(self, node, *args, **kwargs):
        op_horizon = self.visit(node.children[0], *args, **kwargs)
        self.horizons[node] = op_horizon
        return op_horizon

    def visitTimedSince(self, node, *args, **kwargs):
        op1_horizon = self.visit(node.children[0], *args, **kwargs)
        op2_horizon = self.visit(node.children[1], *args, **kwargs)
        out = max(op1_horizon, op2_horizon)
        self.horizons[node] = out
        return out

    def visitTimedPrecedes(self, node, *args, **kwargs):
        op1_horizon = self.visit(node.children[0], *args, **kwargs)
        op2_horizon = self.visit(node.children[1], *args, **kwargs)
        out = max(op1_horizon, op2_horizon)
        self.horizons[node] = out
        return out

    def visitDefault(self, node):
        raise RTAMTException('STL Pastifier: encountered unexpected type of node.')
