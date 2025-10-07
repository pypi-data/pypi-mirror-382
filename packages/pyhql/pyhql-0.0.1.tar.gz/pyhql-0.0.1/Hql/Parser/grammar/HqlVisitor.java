// Generated from Hql.g4 by ANTLR 4.13.2
import org.antlr.v4.runtime.tree.ParseTreeVisitor;

/**
 * This interface defines a complete generic visitor for a parse tree produced
 * by {@link HqlParser}.
 *
 * @param <T> The return type of the visit operation. Use {@link Void} for
 * operations with no return type.
 */
public interface HqlVisitor<T> extends ParseTreeVisitor<T> {
	/**
	 * Visit a parse tree produced by {@link HqlParser#top}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTop(HqlParser.TopContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#query}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitQuery(HqlParser.QueryContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#statement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStatement(HqlParser.StatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letStatement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetStatement(HqlParser.LetStatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letVariableDeclaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetVariableDeclaration(HqlParser.LetVariableDeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letFunctionDeclaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetFunctionDeclaration(HqlParser.LetFunctionDeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letViewDeclaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetViewDeclaration(HqlParser.LetViewDeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letViewParameterList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetViewParameterList(HqlParser.LetViewParameterListContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letMaterializeDeclaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetMaterializeDeclaration(HqlParser.LetMaterializeDeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letEntityGroupDeclaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetEntityGroupDeclaration(HqlParser.LetEntityGroupDeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letMacroDeclaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetMacroDeclaration(HqlParser.LetMacroDeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letFunctionParameterList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetFunctionParameterList(HqlParser.LetFunctionParameterListContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scalarParameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScalarParameter(HqlParser.ScalarParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scalarParameterDefault}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScalarParameterDefault(HqlParser.ScalarParameterDefaultContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#tabularParameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTabularParameter(HqlParser.TabularParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#tabularParameterOpenSchema}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTabularParameterOpenSchema(HqlParser.TabularParameterOpenSchemaContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#tabularParameterRowSchema}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTabularParameterRowSchema(HqlParser.TabularParameterRowSchemaContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#tabularParameterRowSchemaColumnDeclaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTabularParameterRowSchemaColumnDeclaration(HqlParser.TabularParameterRowSchemaColumnDeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letFunctionBody}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetFunctionBody(HqlParser.LetFunctionBodyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#letFunctionBodyStatement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLetFunctionBodyStatement(HqlParser.LetFunctionBodyStatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternStatement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternStatement(HqlParser.DeclarePatternStatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternDefinition}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternDefinition(HqlParser.DeclarePatternDefinitionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternParameterList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternParameterList(HqlParser.DeclarePatternParameterListContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternParameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternParameter(HqlParser.DeclarePatternParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternPathParameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternPathParameter(HqlParser.DeclarePatternPathParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternRule}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternRule(HqlParser.DeclarePatternRuleContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternRuleArgumentList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternRuleArgumentList(HqlParser.DeclarePatternRuleArgumentListContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternRulePathArgument}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternRulePathArgument(HqlParser.DeclarePatternRulePathArgumentContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternRuleArgument}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternRuleArgument(HqlParser.DeclarePatternRuleArgumentContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declarePatternBody}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclarePatternBody(HqlParser.DeclarePatternBodyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#restrictAccessStatement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRestrictAccessStatement(HqlParser.RestrictAccessStatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#restrictAccessStatementEntity}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRestrictAccessStatementEntity(HqlParser.RestrictAccessStatementEntityContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#setStatement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSetStatement(HqlParser.SetStatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#setStatementOptionValue}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSetStatementOptionValue(HqlParser.SetStatementOptionValueContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declareQueryParametersStatement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclareQueryParametersStatement(HqlParser.DeclareQueryParametersStatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#declareQueryParametersStatementParameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclareQueryParametersStatementParameter(HqlParser.DeclareQueryParametersStatementParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#queryStatement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitQueryStatement(HqlParser.QueryStatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#expression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExpression(HqlParser.ExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#pipeExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPipeExpression(HqlParser.PipeExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#emptyPipedExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEmptyPipedExpression(HqlParser.EmptyPipedExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#pipedOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPipedOperator(HqlParser.PipedOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#pipeSubExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPipeSubExpression(HqlParser.PipeSubExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#beforePipeExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBeforePipeExpression(HqlParser.BeforePipeExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#afterPipeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAfterPipeOperator(HqlParser.AfterPipeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#beforeOrAfterPipeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBeforeOrAfterPipeOperator(HqlParser.BeforeOrAfterPipeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#forkPipeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForkPipeOperator(HqlParser.ForkPipeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#asOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAsOperator(HqlParser.AsOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#assertSchemaOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAssertSchemaOperator(HqlParser.AssertSchemaOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#consumeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitConsumeOperator(HqlParser.ConsumeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#countOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitCountOperator(HqlParser.CountOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#distinctOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDistinctOperator(HqlParser.DistinctOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#distinctOperatorStarTarget}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDistinctOperatorStarTarget(HqlParser.DistinctOperatorStarTargetContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#distinctOperatorColumnListTarget}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDistinctOperatorColumnListTarget(HqlParser.DistinctOperatorColumnListTargetContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#evaluateOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEvaluateOperator(HqlParser.EvaluateOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#evaluateOperatorSchemaClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEvaluateOperatorSchemaClause(HqlParser.EvaluateOperatorSchemaClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#extendOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExtendOperator(HqlParser.ExtendOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#executeAndCacheOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExecuteAndCacheOperator(HqlParser.ExecuteAndCacheOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#facetByOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFacetByOperator(HqlParser.FacetByOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#facetByOperatorWithOperatorClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFacetByOperatorWithOperatorClause(HqlParser.FacetByOperatorWithOperatorClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#facetByOperatorWithExpressionClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFacetByOperatorWithExpressionClause(HqlParser.FacetByOperatorWithExpressionClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperator(HqlParser.FindOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorParametersWhereClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorParametersWhereClause(HqlParser.FindOperatorParametersWhereClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorInClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorInClause(HqlParser.FindOperatorInClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorProjectClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorProjectClause(HqlParser.FindOperatorProjectClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorProjectExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorProjectExpression(HqlParser.FindOperatorProjectExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorColumnExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorColumnExpression(HqlParser.FindOperatorColumnExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorOptionalColumnType}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorOptionalColumnType(HqlParser.FindOperatorOptionalColumnTypeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorPackExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorPackExpression(HqlParser.FindOperatorPackExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorProjectSmartClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorProjectSmartClause(HqlParser.FindOperatorProjectSmartClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorProjectAwayClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorProjectAwayClause(HqlParser.FindOperatorProjectAwayClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorProjectAwayStar}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorProjectAwayStar(HqlParser.FindOperatorProjectAwayStarContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorProjectAwayColumnList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorProjectAwayColumnList(HqlParser.FindOperatorProjectAwayColumnListContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorSource}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorSource(HqlParser.FindOperatorSourceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#findOperatorSourceEntityExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFindOperatorSourceEntityExpression(HqlParser.FindOperatorSourceEntityExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#forkOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForkOperator(HqlParser.ForkOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#forkOperatorFork}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForkOperatorFork(HqlParser.ForkOperatorForkContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#forkOperatorExpressionName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForkOperatorExpressionName(HqlParser.ForkOperatorExpressionNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#forkOperatorExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForkOperatorExpression(HqlParser.ForkOperatorExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#forkOperatorPipedOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForkOperatorPipedOperator(HqlParser.ForkOperatorPipedOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#getSchemaOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGetSchemaOperator(HqlParser.GetSchemaOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMarkComponentsOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMarkComponentsOperator(HqlParser.GraphMarkComponentsOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMatchOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMatchOperator(HqlParser.GraphMatchOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMatchPattern}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMatchPattern(HqlParser.GraphMatchPatternContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMatchPatternNode}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMatchPatternNode(HqlParser.GraphMatchPatternNodeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMatchPatternUnnamedEdge}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMatchPatternUnnamedEdge(HqlParser.GraphMatchPatternUnnamedEdgeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMatchPatternNamedEdge}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMatchPatternNamedEdge(HqlParser.GraphMatchPatternNamedEdgeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMatchPatternRange}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMatchPatternRange(HqlParser.GraphMatchPatternRangeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMatchWhereClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMatchWhereClause(HqlParser.GraphMatchWhereClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMatchProjectClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMatchProjectClause(HqlParser.GraphMatchProjectClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphMergeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphMergeOperator(HqlParser.GraphMergeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphToTableOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphToTableOperator(HqlParser.GraphToTableOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphToTableOutput}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphToTableOutput(HqlParser.GraphToTableOutputContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphToTableAsClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphToTableAsClause(HqlParser.GraphToTableAsClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#graphShortestPathsOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGraphShortestPathsOperator(HqlParser.GraphShortestPathsOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#invokeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitInvokeOperator(HqlParser.InvokeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#joinOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJoinOperator(HqlParser.JoinOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#joinOperatorOnClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJoinOperatorOnClause(HqlParser.JoinOperatorOnClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#joinOperatorWhereClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJoinOperatorWhereClause(HqlParser.JoinOperatorWhereClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#lookupOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLookupOperator(HqlParser.LookupOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#macroExpandOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMacroExpandOperator(HqlParser.MacroExpandOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#macroExpandEntityGroup}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMacroExpandEntityGroup(HqlParser.MacroExpandEntityGroupContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#entityGroupExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEntityGroupExpression(HqlParser.EntityGroupExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeGraphOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeGraphOperator(HqlParser.MakeGraphOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeGraphIdClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeGraphIdClause(HqlParser.MakeGraphIdClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeGraphTablesAndKeysClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeGraphTablesAndKeysClause(HqlParser.MakeGraphTablesAndKeysClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeGraphPartitionedByClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeGraphPartitionedByClause(HqlParser.MakeGraphPartitionedByClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeSeriesOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeSeriesOperator(HqlParser.MakeSeriesOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeSeriesOperatorOnClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeSeriesOperatorOnClause(HqlParser.MakeSeriesOperatorOnClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeSeriesOperatorAggregation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeSeriesOperatorAggregation(HqlParser.MakeSeriesOperatorAggregationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeSeriesOperatorExpressionDefaultClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeSeriesOperatorExpressionDefaultClause(HqlParser.MakeSeriesOperatorExpressionDefaultClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeSeriesOperatorInRangeClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeSeriesOperatorInRangeClause(HqlParser.MakeSeriesOperatorInRangeClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeSeriesOperatorFromToStepClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeSeriesOperatorFromToStepClause(HqlParser.MakeSeriesOperatorFromToStepClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#makeSeriesOperatorByClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMakeSeriesOperatorByClause(HqlParser.MakeSeriesOperatorByClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#mvapplyOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMvapplyOperator(HqlParser.MvapplyOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#mvapplyOperatorLimitClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMvapplyOperatorLimitClause(HqlParser.MvapplyOperatorLimitClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#mvapplyOperatorIdClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMvapplyOperatorIdClause(HqlParser.MvapplyOperatorIdClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#mvapplyOperatorExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMvapplyOperatorExpression(HqlParser.MvapplyOperatorExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#mvapplyOperatorExpressionToClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMvapplyOperatorExpressionToClause(HqlParser.MvapplyOperatorExpressionToClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#mvexpandOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMvexpandOperator(HqlParser.MvexpandOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#mvexpandOperatorExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMvexpandOperatorExpression(HqlParser.MvexpandOperatorExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseOperator(HqlParser.ParseOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseOperatorKindClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseOperatorKindClause(HqlParser.ParseOperatorKindClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseOperatorFlagsClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseOperatorFlagsClause(HqlParser.ParseOperatorFlagsClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseOperatorNameAndOptionalType}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseOperatorNameAndOptionalType(HqlParser.ParseOperatorNameAndOptionalTypeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseOperatorPattern}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseOperatorPattern(HqlParser.ParseOperatorPatternContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseOperatorPatternSegment}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseOperatorPatternSegment(HqlParser.ParseOperatorPatternSegmentContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseWhereOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseWhereOperator(HqlParser.ParseWhereOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseKvOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseKvOperator(HqlParser.ParseKvOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parseKvWithClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParseKvWithClause(HqlParser.ParseKvWithClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#partitionOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPartitionOperator(HqlParser.PartitionOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#partitionOperatorInClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPartitionOperatorInClause(HqlParser.PartitionOperatorInClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#partitionOperatorSubExpressionBody}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPartitionOperatorSubExpressionBody(HqlParser.PartitionOperatorSubExpressionBodyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#partitionOperatorFullExpressionBody}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPartitionOperatorFullExpressionBody(HqlParser.PartitionOperatorFullExpressionBodyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#partitionByOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPartitionByOperator(HqlParser.PartitionByOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#partitionByOperatorIdClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPartitionByOperatorIdClause(HqlParser.PartitionByOperatorIdClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#printOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPrintOperator(HqlParser.PrintOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#projectAwayOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitProjectAwayOperator(HqlParser.ProjectAwayOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#projectKeepOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitProjectKeepOperator(HqlParser.ProjectKeepOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#projectOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitProjectOperator(HqlParser.ProjectOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#projectRenameOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitProjectRenameOperator(HqlParser.ProjectRenameOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#projectReorderOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitProjectReorderOperator(HqlParser.ProjectReorderOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#projectReorderExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitProjectReorderExpression(HqlParser.ProjectReorderExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#reduceByOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitReduceByOperator(HqlParser.ReduceByOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#reduceByWithClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitReduceByWithClause(HqlParser.ReduceByWithClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#renameOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRenameOperator(HqlParser.RenameOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#renameToExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRenameToExpression(HqlParser.RenameToExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#renderOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRenderOperator(HqlParser.RenderOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#renderOperatorWithClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRenderOperatorWithClause(HqlParser.RenderOperatorWithClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#renderOperatorLegacyPropertyList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRenderOperatorLegacyPropertyList(HqlParser.RenderOperatorLegacyPropertyListContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#renderOperatorProperty}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRenderOperatorProperty(HqlParser.RenderOperatorPropertyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#renderPropertyNameList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRenderPropertyNameList(HqlParser.RenderPropertyNameListContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#renderOperatorLegacyProperty}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRenderOperatorLegacyProperty(HqlParser.RenderOperatorLegacyPropertyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#sampleDistinctOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSampleDistinctOperator(HqlParser.SampleDistinctOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#sampleOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSampleOperator(HqlParser.SampleOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scanOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScanOperator(HqlParser.ScanOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scanOperatorOrderByClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScanOperatorOrderByClause(HqlParser.ScanOperatorOrderByClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scanOperatorPartitionByClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScanOperatorPartitionByClause(HqlParser.ScanOperatorPartitionByClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scanOperatorDeclareClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScanOperatorDeclareClause(HqlParser.ScanOperatorDeclareClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scanOperatorStep}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScanOperatorStep(HqlParser.ScanOperatorStepContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scanOperatorStepOutputClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScanOperatorStepOutputClause(HqlParser.ScanOperatorStepOutputClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scanOperatorBody}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScanOperatorBody(HqlParser.ScanOperatorBodyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scanOperatorAssignment}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScanOperatorAssignment(HqlParser.ScanOperatorAssignmentContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#searchOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSearchOperator(HqlParser.SearchOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#searchOperatorStarAndExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSearchOperatorStarAndExpression(HqlParser.SearchOperatorStarAndExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#searchOperatorInClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSearchOperatorInClause(HqlParser.SearchOperatorInClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#serializeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSerializeOperator(HqlParser.SerializeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#sortOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSortOperator(HqlParser.SortOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#orderedExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitOrderedExpression(HqlParser.OrderedExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#sortOrdering}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSortOrdering(HqlParser.SortOrderingContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#summarizeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSummarizeOperator(HqlParser.SummarizeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#summarizeOperatorByClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSummarizeOperatorByClause(HqlParser.SummarizeOperatorByClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#summarizeOperatorLegacyBinClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSummarizeOperatorLegacyBinClause(HqlParser.SummarizeOperatorLegacyBinClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#takeOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTakeOperator(HqlParser.TakeOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#topOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTopOperator(HqlParser.TopOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#topHittersOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTopHittersOperator(HqlParser.TopHittersOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#topHittersOperatorByClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTopHittersOperatorByClause(HqlParser.TopHittersOperatorByClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#topNestedOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTopNestedOperator(HqlParser.TopNestedOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#topNestedOperatorPart}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTopNestedOperatorPart(HqlParser.TopNestedOperatorPartContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#topNestedOperatorWithOthersClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTopNestedOperatorWithOthersClause(HqlParser.TopNestedOperatorWithOthersClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#unionOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUnionOperator(HqlParser.UnionOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#unionOperatorExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUnionOperatorExpression(HqlParser.UnionOperatorExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#whereOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWhereOperator(HqlParser.WhereOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#unnestOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUnnestOperator(HqlParser.UnnestOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#unnestOperatorOnClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUnnestOperatorOnClause(HqlParser.UnnestOperatorOnClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#contextualSubExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitContextualSubExpression(HqlParser.ContextualSubExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#contextualPipeExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitContextualPipeExpression(HqlParser.ContextualPipeExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#contextualPipeExpressionPipedOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitContextualPipeExpressionPipedOperator(HqlParser.ContextualPipeExpressionPipedOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#strictQueryOperatorParameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStrictQueryOperatorParameter(HqlParser.StrictQueryOperatorParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#relaxedQueryOperatorParameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRelaxedQueryOperatorParameter(HqlParser.RelaxedQueryOperatorParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#queryOperatorProperty}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitQueryOperatorProperty(HqlParser.QueryOperatorPropertyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#namedExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNamedExpression(HqlParser.NamedExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#staticNamedExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStaticNamedExpression(HqlParser.StaticNamedExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#namedExpressionNameClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNamedExpressionNameClause(HqlParser.NamedExpressionNameClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#namedExpressionNameList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNamedExpressionNameList(HqlParser.NamedExpressionNameListContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scopedFunctionCallExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScopedFunctionCallExpression(HqlParser.ScopedFunctionCallExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#unnamedExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUnnamedExpression(HqlParser.UnnamedExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#logicalOrExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLogicalOrExpression(HqlParser.LogicalOrExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#logicalOrOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLogicalOrOperation(HqlParser.LogicalOrOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#logicalAndExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLogicalAndExpression(HqlParser.LogicalAndExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#logicalAndOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLogicalAndOperation(HqlParser.LogicalAndOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#equalityExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEqualityExpression(HqlParser.EqualityExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#equalsEqualityExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEqualsEqualityExpression(HqlParser.EqualsEqualityExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#listEqualityExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitListEqualityExpression(HqlParser.ListEqualityExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#betweenEqualityExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBetweenEqualityExpression(HqlParser.BetweenEqualityExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#starEqualityExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStarEqualityExpression(HqlParser.StarEqualityExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#relationalExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRelationalExpression(HqlParser.RelationalExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#additiveExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAdditiveExpression(HqlParser.AdditiveExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#additiveOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAdditiveOperation(HqlParser.AdditiveOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#multiplicativeExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMultiplicativeExpression(HqlParser.MultiplicativeExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#multiplicativeOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMultiplicativeOperation(HqlParser.MultiplicativeOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#stringOperatorExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStringOperatorExpression(HqlParser.StringOperatorExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#stringBinaryOperatorExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStringBinaryOperatorExpression(HqlParser.StringBinaryOperatorExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#stringBinaryOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStringBinaryOperator(HqlParser.StringBinaryOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#stringStarOperatorExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStringStarOperatorExpression(HqlParser.StringStarOperatorExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#invocationExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitInvocationExpression(HqlParser.InvocationExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#functionCallOrPathExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionCallOrPathExpression(HqlParser.FunctionCallOrPathExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#functionCallOrPathRoot}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionCallOrPathRoot(HqlParser.FunctionCallOrPathRootContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#functionCallOrPathPathExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionCallOrPathPathExpression(HqlParser.FunctionCallOrPathPathExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#functionCallOrPathOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionCallOrPathOperation(HqlParser.FunctionCallOrPathOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#functionalCallOrPathPathOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionalCallOrPathPathOperation(HqlParser.FunctionalCallOrPathPathOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#functionCallOrPathElementOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionCallOrPathElementOperation(HqlParser.FunctionCallOrPathElementOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#legacyFunctionCallOrPathElementOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLegacyFunctionCallOrPathElementOperation(HqlParser.LegacyFunctionCallOrPathElementOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#toScalarExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitToScalarExpression(HqlParser.ToScalarExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#toTableExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitToTableExpression(HqlParser.ToTableExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#noOptimizationParameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNoOptimizationParameter(HqlParser.NoOptimizationParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#dotCompositeFunctionCallExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDotCompositeFunctionCallExpression(HqlParser.DotCompositeFunctionCallExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#dotCompositeFunctionCallOperation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDotCompositeFunctionCallOperation(HqlParser.DotCompositeFunctionCallOperationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#functionCallExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionCallExpression(HqlParser.FunctionCallExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#namedFunctionCallExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNamedFunctionCallExpression(HqlParser.NamedFunctionCallExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#argumentExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitArgumentExpression(HqlParser.ArgumentExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#countExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitCountExpression(HqlParser.CountExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#starExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStarExpression(HqlParser.StarExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#primaryExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPrimaryExpression(HqlParser.PrimaryExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#nameReferenceWithDataScope}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNameReferenceWithDataScope(HqlParser.NameReferenceWithDataScopeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#dataScopeClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDataScopeClause(HqlParser.DataScopeClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parenthesizedExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParenthesizedExpression(HqlParser.ParenthesizedExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#rangeExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRangeExpression(HqlParser.RangeExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#entityExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEntityExpression(HqlParser.EntityExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#entityPathOrElementExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEntityPathOrElementExpression(HqlParser.EntityPathOrElementExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#entityPathOrElementOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEntityPathOrElementOperator(HqlParser.EntityPathOrElementOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#entityPathOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEntityPathOperator(HqlParser.EntityPathOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#entityElementOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEntityElementOperator(HqlParser.EntityElementOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#legacyEntityPathElementOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLegacyEntityPathElementOperator(HqlParser.LegacyEntityPathElementOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#entityName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEntityName(HqlParser.EntityNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#entityNameReference}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEntityNameReference(HqlParser.EntityNameReferenceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#atSignName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAtSignName(HqlParser.AtSignNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#extendedPathName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExtendedPathName(HqlParser.ExtendedPathNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#wildcardedEntityExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWildcardedEntityExpression(HqlParser.WildcardedEntityExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#wildcardedPathExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWildcardedPathExpression(HqlParser.WildcardedPathExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#wildcardedPathName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWildcardedPathName(HqlParser.WildcardedPathNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#contextualDataTableExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitContextualDataTableExpression(HqlParser.ContextualDataTableExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#dataTableExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDataTableExpression(HqlParser.DataTableExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#rowSchema}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRowSchema(HqlParser.RowSchemaContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#rowSchemaColumnDeclaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRowSchemaColumnDeclaration(HqlParser.RowSchemaColumnDeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#externalDataExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExternalDataExpression(HqlParser.ExternalDataExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#externalDataWithClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExternalDataWithClause(HqlParser.ExternalDataWithClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#externalDataWithClauseProperty}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExternalDataWithClauseProperty(HqlParser.ExternalDataWithClausePropertyContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#materializedViewCombineExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMaterializedViewCombineExpression(HqlParser.MaterializedViewCombineExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#materializeViewCombineBaseClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMaterializeViewCombineBaseClause(HqlParser.MaterializeViewCombineBaseClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#materializedViewCombineDeltaClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMaterializedViewCombineDeltaClause(HqlParser.MaterializedViewCombineDeltaClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#materializedViewCombineAggregationsClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitMaterializedViewCombineAggregationsClause(HqlParser.MaterializedViewCombineAggregationsClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#scalarType}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitScalarType(HqlParser.ScalarTypeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#extendedScalarType}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExtendedScalarType(HqlParser.ExtendedScalarTypeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#parameterName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParameterName(HqlParser.ParameterNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#simpleNameReference}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSimpleNameReference(HqlParser.SimpleNameReferenceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#extendedNameReference}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExtendedNameReference(HqlParser.ExtendedNameReferenceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#wildcardedNameReference}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWildcardedNameReference(HqlParser.WildcardedNameReferenceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#simpleOrWildcardedNameReference}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSimpleOrWildcardedNameReference(HqlParser.SimpleOrWildcardedNameReferenceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#pathReference}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPathReference(HqlParser.PathReferenceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#simpleOrPathNameReference}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSimpleOrPathNameReference(HqlParser.SimpleOrPathNameReferenceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#tableNameReference}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTableNameReference(HqlParser.TableNameReferenceContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#identifierName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIdentifierName(HqlParser.IdentifierNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#keywordName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitKeywordName(HqlParser.KeywordNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#extendedKeywordName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExtendedKeywordName(HqlParser.ExtendedKeywordNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#escapedName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEscapedName(HqlParser.EscapedNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#pathOrKeyword}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPathOrKeyword(HqlParser.PathOrKeywordContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#pathOrExtendedKeyword}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPathOrExtendedKeyword(HqlParser.PathOrExtendedKeywordContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#wildcardedName}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWildcardedName(HqlParser.WildcardedNameContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#wildcardedNamePrefix}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWildcardedNamePrefix(HqlParser.WildcardedNamePrefixContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#wildcardedNameSegment}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWildcardedNameSegment(HqlParser.WildcardedNameSegmentContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#literalExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLiteralExpression(HqlParser.LiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#unsignedLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUnsignedLiteralExpression(HqlParser.UnsignedLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#numberLikeLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNumberLikeLiteralExpression(HqlParser.NumberLikeLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#numericLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNumericLiteralExpression(HqlParser.NumericLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#signedLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSignedLiteralExpression(HqlParser.SignedLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#longLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLongLiteralExpression(HqlParser.LongLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#intLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIntLiteralExpression(HqlParser.IntLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#realLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRealLiteralExpression(HqlParser.RealLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#decimalLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDecimalLiteralExpression(HqlParser.DecimalLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#dateTimeLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDateTimeLiteralExpression(HqlParser.DateTimeLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#timeSpanLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTimeSpanLiteralExpression(HqlParser.TimeSpanLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#booleanLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBooleanLiteralExpression(HqlParser.BooleanLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#guidLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitGuidLiteralExpression(HqlParser.GuidLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#typeLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTypeLiteralExpression(HqlParser.TypeLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#signedLongLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSignedLongLiteralExpression(HqlParser.SignedLongLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#signedRealLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSignedRealLiteralExpression(HqlParser.SignedRealLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#stringLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStringLiteralExpression(HqlParser.StringLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#dynamicLiteralExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDynamicLiteralExpression(HqlParser.DynamicLiteralExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonValue}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonValue(HqlParser.JsonValueContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonObject}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonObject(HqlParser.JsonObjectContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonPair}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonPair(HqlParser.JsonPairContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonArray}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonArray(HqlParser.JsonArrayContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonBoolean}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonBoolean(HqlParser.JsonBooleanContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonDateTime}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonDateTime(HqlParser.JsonDateTimeContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonGuid}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonGuid(HqlParser.JsonGuidContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonNull}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonNull(HqlParser.JsonNullContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonString}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonString(HqlParser.JsonStringContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonTimeSpan}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonTimeSpan(HqlParser.JsonTimeSpanContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonLong}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonLong(HqlParser.JsonLongContext ctx);
	/**
	 * Visit a parse tree produced by {@link HqlParser#jsonReal}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitJsonReal(HqlParser.JsonRealContext ctx);
}