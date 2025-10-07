// Generated from PCREParser.g4 by ANTLR 4.13.2
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link PCREParser}.
 */
public interface PCREParserListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link PCREParser#pcre}.
	 * @param ctx the parse tree
	 */
	void enterPcre(PCREParser.PcreContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#pcre}.
	 * @param ctx the parse tree
	 */
	void exitPcre(PCREParser.PcreContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#alternation}.
	 * @param ctx the parse tree
	 */
	void enterAlternation(PCREParser.AlternationContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#alternation}.
	 * @param ctx the parse tree
	 */
	void exitAlternation(PCREParser.AlternationContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterExpr(PCREParser.ExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitExpr(PCREParser.ExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#element}.
	 * @param ctx the parse tree
	 */
	void enterElement(PCREParser.ElementContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#element}.
	 * @param ctx the parse tree
	 */
	void exitElement(PCREParser.ElementContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#atom}.
	 * @param ctx the parse tree
	 */
	void enterAtom(PCREParser.AtomContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#atom}.
	 * @param ctx the parse tree
	 */
	void exitAtom(PCREParser.AtomContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#capture}.
	 * @param ctx the parse tree
	 */
	void enterCapture(PCREParser.CaptureContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#capture}.
	 * @param ctx the parse tree
	 */
	void exitCapture(PCREParser.CaptureContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#atomic_group}.
	 * @param ctx the parse tree
	 */
	void enterAtomic_group(PCREParser.Atomic_groupContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#atomic_group}.
	 * @param ctx the parse tree
	 */
	void exitAtomic_group(PCREParser.Atomic_groupContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#lookaround}.
	 * @param ctx the parse tree
	 */
	void enterLookaround(PCREParser.LookaroundContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#lookaround}.
	 * @param ctx the parse tree
	 */
	void exitLookaround(PCREParser.LookaroundContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#backreference}.
	 * @param ctx the parse tree
	 */
	void enterBackreference(PCREParser.BackreferenceContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#backreference}.
	 * @param ctx the parse tree
	 */
	void exitBackreference(PCREParser.BackreferenceContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#subroutine_reference}.
	 * @param ctx the parse tree
	 */
	void enterSubroutine_reference(PCREParser.Subroutine_referenceContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#subroutine_reference}.
	 * @param ctx the parse tree
	 */
	void exitSubroutine_reference(PCREParser.Subroutine_referenceContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#conditional_pattern}.
	 * @param ctx the parse tree
	 */
	void enterConditional_pattern(PCREParser.Conditional_patternContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#conditional_pattern}.
	 * @param ctx the parse tree
	 */
	void exitConditional_pattern(PCREParser.Conditional_patternContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#comment}.
	 * @param ctx the parse tree
	 */
	void enterComment(PCREParser.CommentContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#comment}.
	 * @param ctx the parse tree
	 */
	void exitComment(PCREParser.CommentContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#quantifier}.
	 * @param ctx the parse tree
	 */
	void enterQuantifier(PCREParser.QuantifierContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#quantifier}.
	 * @param ctx the parse tree
	 */
	void exitQuantifier(PCREParser.QuantifierContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#option_setting}.
	 * @param ctx the parse tree
	 */
	void enterOption_setting(PCREParser.Option_settingContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#option_setting}.
	 * @param ctx the parse tree
	 */
	void exitOption_setting(PCREParser.Option_settingContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#option_setting_flag}.
	 * @param ctx the parse tree
	 */
	void enterOption_setting_flag(PCREParser.Option_setting_flagContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#option_setting_flag}.
	 * @param ctx the parse tree
	 */
	void exitOption_setting_flag(PCREParser.Option_setting_flagContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#backtracking_control}.
	 * @param ctx the parse tree
	 */
	void enterBacktracking_control(PCREParser.Backtracking_controlContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#backtracking_control}.
	 * @param ctx the parse tree
	 */
	void exitBacktracking_control(PCREParser.Backtracking_controlContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#callout}.
	 * @param ctx the parse tree
	 */
	void enterCallout(PCREParser.CalloutContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#callout}.
	 * @param ctx the parse tree
	 */
	void exitCallout(PCREParser.CalloutContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#newline_conventions}.
	 * @param ctx the parse tree
	 */
	void enterNewline_conventions(PCREParser.Newline_conventionsContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#newline_conventions}.
	 * @param ctx the parse tree
	 */
	void exitNewline_conventions(PCREParser.Newline_conventionsContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#character}.
	 * @param ctx the parse tree
	 */
	void enterCharacter(PCREParser.CharacterContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#character}.
	 * @param ctx the parse tree
	 */
	void exitCharacter(PCREParser.CharacterContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#character_type}.
	 * @param ctx the parse tree
	 */
	void enterCharacter_type(PCREParser.Character_typeContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#character_type}.
	 * @param ctx the parse tree
	 */
	void exitCharacter_type(PCREParser.Character_typeContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#character_class}.
	 * @param ctx the parse tree
	 */
	void enterCharacter_class(PCREParser.Character_classContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#character_class}.
	 * @param ctx the parse tree
	 */
	void exitCharacter_class(PCREParser.Character_classContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#character_class_atom}.
	 * @param ctx the parse tree
	 */
	void enterCharacter_class_atom(PCREParser.Character_class_atomContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#character_class_atom}.
	 * @param ctx the parse tree
	 */
	void exitCharacter_class_atom(PCREParser.Character_class_atomContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#character_class_range}.
	 * @param ctx the parse tree
	 */
	void enterCharacter_class_range(PCREParser.Character_class_rangeContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#character_class_range}.
	 * @param ctx the parse tree
	 */
	void exitCharacter_class_range(PCREParser.Character_class_rangeContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#character_class_range_atom}.
	 * @param ctx the parse tree
	 */
	void enterCharacter_class_range_atom(PCREParser.Character_class_range_atomContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#character_class_range_atom}.
	 * @param ctx the parse tree
	 */
	void exitCharacter_class_range_atom(PCREParser.Character_class_range_atomContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#posix_character_class}.
	 * @param ctx the parse tree
	 */
	void enterPosix_character_class(PCREParser.Posix_character_classContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#posix_character_class}.
	 * @param ctx the parse tree
	 */
	void exitPosix_character_class(PCREParser.Posix_character_classContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#anchor}.
	 * @param ctx the parse tree
	 */
	void enterAnchor(PCREParser.AnchorContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#anchor}.
	 * @param ctx the parse tree
	 */
	void exitAnchor(PCREParser.AnchorContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#match_point_reset}.
	 * @param ctx the parse tree
	 */
	void enterMatch_point_reset(PCREParser.Match_point_resetContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#match_point_reset}.
	 * @param ctx the parse tree
	 */
	void exitMatch_point_reset(PCREParser.Match_point_resetContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#quoting}.
	 * @param ctx the parse tree
	 */
	void enterQuoting(PCREParser.QuotingContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#quoting}.
	 * @param ctx the parse tree
	 */
	void exitQuoting(PCREParser.QuotingContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#digits}.
	 * @param ctx the parse tree
	 */
	void enterDigits(PCREParser.DigitsContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#digits}.
	 * @param ctx the parse tree
	 */
	void exitDigits(PCREParser.DigitsContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#digit}.
	 * @param ctx the parse tree
	 */
	void enterDigit(PCREParser.DigitContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#digit}.
	 * @param ctx the parse tree
	 */
	void exitDigit(PCREParser.DigitContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#hex}.
	 * @param ctx the parse tree
	 */
	void enterHex(PCREParser.HexContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#hex}.
	 * @param ctx the parse tree
	 */
	void exitHex(PCREParser.HexContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#letters}.
	 * @param ctx the parse tree
	 */
	void enterLetters(PCREParser.LettersContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#letters}.
	 * @param ctx the parse tree
	 */
	void exitLetters(PCREParser.LettersContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#letter}.
	 * @param ctx the parse tree
	 */
	void enterLetter(PCREParser.LetterContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#letter}.
	 * @param ctx the parse tree
	 */
	void exitLetter(PCREParser.LetterContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#name}.
	 * @param ctx the parse tree
	 */
	void enterName(PCREParser.NameContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#name}.
	 * @param ctx the parse tree
	 */
	void exitName(PCREParser.NameContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#other}.
	 * @param ctx the parse tree
	 */
	void enterOther(PCREParser.OtherContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#other}.
	 * @param ctx the parse tree
	 */
	void exitOther(PCREParser.OtherContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#utf}.
	 * @param ctx the parse tree
	 */
	void enterUtf(PCREParser.UtfContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#utf}.
	 * @param ctx the parse tree
	 */
	void exitUtf(PCREParser.UtfContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#ucp}.
	 * @param ctx the parse tree
	 */
	void enterUcp(PCREParser.UcpContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#ucp}.
	 * @param ctx the parse tree
	 */
	void exitUcp(PCREParser.UcpContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#no_auto_possess}.
	 * @param ctx the parse tree
	 */
	void enterNo_auto_possess(PCREParser.No_auto_possessContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#no_auto_possess}.
	 * @param ctx the parse tree
	 */
	void exitNo_auto_possess(PCREParser.No_auto_possessContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#no_start_opt}.
	 * @param ctx the parse tree
	 */
	void enterNo_start_opt(PCREParser.No_start_optContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#no_start_opt}.
	 * @param ctx the parse tree
	 */
	void exitNo_start_opt(PCREParser.No_start_optContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#cr}.
	 * @param ctx the parse tree
	 */
	void enterCr(PCREParser.CrContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#cr}.
	 * @param ctx the parse tree
	 */
	void exitCr(PCREParser.CrContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#lf}.
	 * @param ctx the parse tree
	 */
	void enterLf(PCREParser.LfContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#lf}.
	 * @param ctx the parse tree
	 */
	void exitLf(PCREParser.LfContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#crlf}.
	 * @param ctx the parse tree
	 */
	void enterCrlf(PCREParser.CrlfContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#crlf}.
	 * @param ctx the parse tree
	 */
	void exitCrlf(PCREParser.CrlfContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#anycrlf}.
	 * @param ctx the parse tree
	 */
	void enterAnycrlf(PCREParser.AnycrlfContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#anycrlf}.
	 * @param ctx the parse tree
	 */
	void exitAnycrlf(PCREParser.AnycrlfContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#any}.
	 * @param ctx the parse tree
	 */
	void enterAny(PCREParser.AnyContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#any}.
	 * @param ctx the parse tree
	 */
	void exitAny(PCREParser.AnyContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#limit_match}.
	 * @param ctx the parse tree
	 */
	void enterLimit_match(PCREParser.Limit_matchContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#limit_match}.
	 * @param ctx the parse tree
	 */
	void exitLimit_match(PCREParser.Limit_matchContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#limit_recursion}.
	 * @param ctx the parse tree
	 */
	void enterLimit_recursion(PCREParser.Limit_recursionContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#limit_recursion}.
	 * @param ctx the parse tree
	 */
	void exitLimit_recursion(PCREParser.Limit_recursionContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#bsr_anycrlf}.
	 * @param ctx the parse tree
	 */
	void enterBsr_anycrlf(PCREParser.Bsr_anycrlfContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#bsr_anycrlf}.
	 * @param ctx the parse tree
	 */
	void exitBsr_anycrlf(PCREParser.Bsr_anycrlfContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#bsr_unicode}.
	 * @param ctx the parse tree
	 */
	void enterBsr_unicode(PCREParser.Bsr_unicodeContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#bsr_unicode}.
	 * @param ctx the parse tree
	 */
	void exitBsr_unicode(PCREParser.Bsr_unicodeContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#accept}.
	 * @param ctx the parse tree
	 */
	void enterAccept(PCREParser.AcceptContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#accept}.
	 * @param ctx the parse tree
	 */
	void exitAccept(PCREParser.AcceptContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#fail}.
	 * @param ctx the parse tree
	 */
	void enterFail(PCREParser.FailContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#fail}.
	 * @param ctx the parse tree
	 */
	void exitFail(PCREParser.FailContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#mark}.
	 * @param ctx the parse tree
	 */
	void enterMark(PCREParser.MarkContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#mark}.
	 * @param ctx the parse tree
	 */
	void exitMark(PCREParser.MarkContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#commit}.
	 * @param ctx the parse tree
	 */
	void enterCommit(PCREParser.CommitContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#commit}.
	 * @param ctx the parse tree
	 */
	void exitCommit(PCREParser.CommitContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#prune}.
	 * @param ctx the parse tree
	 */
	void enterPrune(PCREParser.PruneContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#prune}.
	 * @param ctx the parse tree
	 */
	void exitPrune(PCREParser.PruneContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#skip}.
	 * @param ctx the parse tree
	 */
	void enterSkip(PCREParser.SkipContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#skip}.
	 * @param ctx the parse tree
	 */
	void exitSkip(PCREParser.SkipContext ctx);
	/**
	 * Enter a parse tree produced by {@link PCREParser#then}.
	 * @param ctx the parse tree
	 */
	void enterThen(PCREParser.ThenContext ctx);
	/**
	 * Exit a parse tree produced by {@link PCREParser#then}.
	 * @param ctx the parse tree
	 */
	void exitThen(PCREParser.ThenContext ctx);
}