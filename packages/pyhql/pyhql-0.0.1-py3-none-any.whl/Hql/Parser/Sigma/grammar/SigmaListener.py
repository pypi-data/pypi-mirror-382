# Generated from Sigma.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .SigmaParser import SigmaParser
else:
    from SigmaParser import SigmaParser

# This class defines a complete listener for a parse tree produced by SigmaParser.
class SigmaListener(ParseTreeListener):

    # Enter a parse tree produced by SigmaParser#condition.
    def enterCondition(self, ctx:SigmaParser.ConditionContext):
        pass

    # Exit a parse tree produced by SigmaParser#condition.
    def exitCondition(self, ctx:SigmaParser.ConditionContext):
        pass


    # Enter a parse tree produced by SigmaParser#orStatement.
    def enterOrStatement(self, ctx:SigmaParser.OrStatementContext):
        pass

    # Exit a parse tree produced by SigmaParser#orStatement.
    def exitOrStatement(self, ctx:SigmaParser.OrStatementContext):
        pass


    # Enter a parse tree produced by SigmaParser#andStatement.
    def enterAndStatement(self, ctx:SigmaParser.AndStatementContext):
        pass

    # Exit a parse tree produced by SigmaParser#andStatement.
    def exitAndStatement(self, ctx:SigmaParser.AndStatementContext):
        pass


    # Enter a parse tree produced by SigmaParser#statement.
    def enterStatement(self, ctx:SigmaParser.StatementContext):
        pass

    # Exit a parse tree produced by SigmaParser#statement.
    def exitStatement(self, ctx:SigmaParser.StatementContext):
        pass


    # Enter a parse tree produced by SigmaParser#notStatement.
    def enterNotStatement(self, ctx:SigmaParser.NotStatementContext):
        pass

    # Exit a parse tree produced by SigmaParser#notStatement.
    def exitNotStatement(self, ctx:SigmaParser.NotStatementContext):
        pass


    # Enter a parse tree produced by SigmaParser#bracketStatement.
    def enterBracketStatement(self, ctx:SigmaParser.BracketStatementContext):
        pass

    # Exit a parse tree produced by SigmaParser#bracketStatement.
    def exitBracketStatement(self, ctx:SigmaParser.BracketStatementContext):
        pass


    # Enter a parse tree produced by SigmaParser#ofStatement.
    def enterOfStatement(self, ctx:SigmaParser.OfStatementContext):
        pass

    # Exit a parse tree produced by SigmaParser#ofStatement.
    def exitOfStatement(self, ctx:SigmaParser.OfStatementContext):
        pass


    # Enter a parse tree produced by SigmaParser#ofSpecifier.
    def enterOfSpecifier(self, ctx:SigmaParser.OfSpecifierContext):
        pass

    # Exit a parse tree produced by SigmaParser#ofSpecifier.
    def exitOfSpecifier(self, ctx:SigmaParser.OfSpecifierContext):
        pass


    # Enter a parse tree produced by SigmaParser#ofTarget.
    def enterOfTarget(self, ctx:SigmaParser.OfTargetContext):
        pass

    # Exit a parse tree produced by SigmaParser#ofTarget.
    def exitOfTarget(self, ctx:SigmaParser.OfTargetContext):
        pass


    # Enter a parse tree produced by SigmaParser#selectionIdentifier.
    def enterSelectionIdentifier(self, ctx:SigmaParser.SelectionIdentifierContext):
        pass

    # Exit a parse tree produced by SigmaParser#selectionIdentifier.
    def exitSelectionIdentifier(self, ctx:SigmaParser.SelectionIdentifierContext):
        pass


    # Enter a parse tree produced by SigmaParser#patternIdentifier.
    def enterPatternIdentifier(self, ctx:SigmaParser.PatternIdentifierContext):
        pass

    # Exit a parse tree produced by SigmaParser#patternIdentifier.
    def exitPatternIdentifier(self, ctx:SigmaParser.PatternIdentifierContext):
        pass


    # Enter a parse tree produced by SigmaParser#basicIdentifier.
    def enterBasicIdentifier(self, ctx:SigmaParser.BasicIdentifierContext):
        pass

    # Exit a parse tree produced by SigmaParser#basicIdentifier.
    def exitBasicIdentifier(self, ctx:SigmaParser.BasicIdentifierContext):
        pass


    # Enter a parse tree produced by SigmaParser#wildcardIdentifier.
    def enterWildcardIdentifier(self, ctx:SigmaParser.WildcardIdentifierContext):
        pass

    # Exit a parse tree produced by SigmaParser#wildcardIdentifier.
    def exitWildcardIdentifier(self, ctx:SigmaParser.WildcardIdentifierContext):
        pass


    # Enter a parse tree produced by SigmaParser#regexIdentifier.
    def enterRegexIdentifier(self, ctx:SigmaParser.RegexIdentifierContext):
        pass

    # Exit a parse tree produced by SigmaParser#regexIdentifier.
    def exitRegexIdentifier(self, ctx:SigmaParser.RegexIdentifierContext):
        pass



del SigmaParser