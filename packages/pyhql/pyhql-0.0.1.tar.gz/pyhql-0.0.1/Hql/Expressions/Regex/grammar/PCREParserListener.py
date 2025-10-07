# Generated from PCREParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PCREParser import PCREParser
else:
    from PCREParser import PCREParser

# This class defines a complete listener for a parse tree produced by PCREParser.
class PCREParserListener(ParseTreeListener):

    # Enter a parse tree produced by PCREParser#pcre.
    def enterPcre(self, ctx:PCREParser.PcreContext):
        pass

    # Exit a parse tree produced by PCREParser#pcre.
    def exitPcre(self, ctx:PCREParser.PcreContext):
        pass


    # Enter a parse tree produced by PCREParser#alternation.
    def enterAlternation(self, ctx:PCREParser.AlternationContext):
        pass

    # Exit a parse tree produced by PCREParser#alternation.
    def exitAlternation(self, ctx:PCREParser.AlternationContext):
        pass


    # Enter a parse tree produced by PCREParser#expr.
    def enterExpr(self, ctx:PCREParser.ExprContext):
        pass

    # Exit a parse tree produced by PCREParser#expr.
    def exitExpr(self, ctx:PCREParser.ExprContext):
        pass


    # Enter a parse tree produced by PCREParser#element.
    def enterElement(self, ctx:PCREParser.ElementContext):
        pass

    # Exit a parse tree produced by PCREParser#element.
    def exitElement(self, ctx:PCREParser.ElementContext):
        pass


    # Enter a parse tree produced by PCREParser#atom.
    def enterAtom(self, ctx:PCREParser.AtomContext):
        pass

    # Exit a parse tree produced by PCREParser#atom.
    def exitAtom(self, ctx:PCREParser.AtomContext):
        pass


    # Enter a parse tree produced by PCREParser#capture.
    def enterCapture(self, ctx:PCREParser.CaptureContext):
        pass

    # Exit a parse tree produced by PCREParser#capture.
    def exitCapture(self, ctx:PCREParser.CaptureContext):
        pass


    # Enter a parse tree produced by PCREParser#atomic_group.
    def enterAtomic_group(self, ctx:PCREParser.Atomic_groupContext):
        pass

    # Exit a parse tree produced by PCREParser#atomic_group.
    def exitAtomic_group(self, ctx:PCREParser.Atomic_groupContext):
        pass


    # Enter a parse tree produced by PCREParser#lookaround.
    def enterLookaround(self, ctx:PCREParser.LookaroundContext):
        pass

    # Exit a parse tree produced by PCREParser#lookaround.
    def exitLookaround(self, ctx:PCREParser.LookaroundContext):
        pass


    # Enter a parse tree produced by PCREParser#backreference.
    def enterBackreference(self, ctx:PCREParser.BackreferenceContext):
        pass

    # Exit a parse tree produced by PCREParser#backreference.
    def exitBackreference(self, ctx:PCREParser.BackreferenceContext):
        pass


    # Enter a parse tree produced by PCREParser#subroutine_reference.
    def enterSubroutine_reference(self, ctx:PCREParser.Subroutine_referenceContext):
        pass

    # Exit a parse tree produced by PCREParser#subroutine_reference.
    def exitSubroutine_reference(self, ctx:PCREParser.Subroutine_referenceContext):
        pass


    # Enter a parse tree produced by PCREParser#conditional_pattern.
    def enterConditional_pattern(self, ctx:PCREParser.Conditional_patternContext):
        pass

    # Exit a parse tree produced by PCREParser#conditional_pattern.
    def exitConditional_pattern(self, ctx:PCREParser.Conditional_patternContext):
        pass


    # Enter a parse tree produced by PCREParser#comment.
    def enterComment(self, ctx:PCREParser.CommentContext):
        pass

    # Exit a parse tree produced by PCREParser#comment.
    def exitComment(self, ctx:PCREParser.CommentContext):
        pass


    # Enter a parse tree produced by PCREParser#quantifier.
    def enterQuantifier(self, ctx:PCREParser.QuantifierContext):
        pass

    # Exit a parse tree produced by PCREParser#quantifier.
    def exitQuantifier(self, ctx:PCREParser.QuantifierContext):
        pass


    # Enter a parse tree produced by PCREParser#option_setting.
    def enterOption_setting(self, ctx:PCREParser.Option_settingContext):
        pass

    # Exit a parse tree produced by PCREParser#option_setting.
    def exitOption_setting(self, ctx:PCREParser.Option_settingContext):
        pass


    # Enter a parse tree produced by PCREParser#option_setting_flag.
    def enterOption_setting_flag(self, ctx:PCREParser.Option_setting_flagContext):
        pass

    # Exit a parse tree produced by PCREParser#option_setting_flag.
    def exitOption_setting_flag(self, ctx:PCREParser.Option_setting_flagContext):
        pass


    # Enter a parse tree produced by PCREParser#backtracking_control.
    def enterBacktracking_control(self, ctx:PCREParser.Backtracking_controlContext):
        pass

    # Exit a parse tree produced by PCREParser#backtracking_control.
    def exitBacktracking_control(self, ctx:PCREParser.Backtracking_controlContext):
        pass


    # Enter a parse tree produced by PCREParser#callout.
    def enterCallout(self, ctx:PCREParser.CalloutContext):
        pass

    # Exit a parse tree produced by PCREParser#callout.
    def exitCallout(self, ctx:PCREParser.CalloutContext):
        pass


    # Enter a parse tree produced by PCREParser#newline_conventions.
    def enterNewline_conventions(self, ctx:PCREParser.Newline_conventionsContext):
        pass

    # Exit a parse tree produced by PCREParser#newline_conventions.
    def exitNewline_conventions(self, ctx:PCREParser.Newline_conventionsContext):
        pass


    # Enter a parse tree produced by PCREParser#character.
    def enterCharacter(self, ctx:PCREParser.CharacterContext):
        pass

    # Exit a parse tree produced by PCREParser#character.
    def exitCharacter(self, ctx:PCREParser.CharacterContext):
        pass


    # Enter a parse tree produced by PCREParser#character_type.
    def enterCharacter_type(self, ctx:PCREParser.Character_typeContext):
        pass

    # Exit a parse tree produced by PCREParser#character_type.
    def exitCharacter_type(self, ctx:PCREParser.Character_typeContext):
        pass


    # Enter a parse tree produced by PCREParser#character_class.
    def enterCharacter_class(self, ctx:PCREParser.Character_classContext):
        pass

    # Exit a parse tree produced by PCREParser#character_class.
    def exitCharacter_class(self, ctx:PCREParser.Character_classContext):
        pass


    # Enter a parse tree produced by PCREParser#character_class_atom.
    def enterCharacter_class_atom(self, ctx:PCREParser.Character_class_atomContext):
        pass

    # Exit a parse tree produced by PCREParser#character_class_atom.
    def exitCharacter_class_atom(self, ctx:PCREParser.Character_class_atomContext):
        pass


    # Enter a parse tree produced by PCREParser#character_class_range.
    def enterCharacter_class_range(self, ctx:PCREParser.Character_class_rangeContext):
        pass

    # Exit a parse tree produced by PCREParser#character_class_range.
    def exitCharacter_class_range(self, ctx:PCREParser.Character_class_rangeContext):
        pass


    # Enter a parse tree produced by PCREParser#character_class_range_atom.
    def enterCharacter_class_range_atom(self, ctx:PCREParser.Character_class_range_atomContext):
        pass

    # Exit a parse tree produced by PCREParser#character_class_range_atom.
    def exitCharacter_class_range_atom(self, ctx:PCREParser.Character_class_range_atomContext):
        pass


    # Enter a parse tree produced by PCREParser#posix_character_class.
    def enterPosix_character_class(self, ctx:PCREParser.Posix_character_classContext):
        pass

    # Exit a parse tree produced by PCREParser#posix_character_class.
    def exitPosix_character_class(self, ctx:PCREParser.Posix_character_classContext):
        pass


    # Enter a parse tree produced by PCREParser#anchor.
    def enterAnchor(self, ctx:PCREParser.AnchorContext):
        pass

    # Exit a parse tree produced by PCREParser#anchor.
    def exitAnchor(self, ctx:PCREParser.AnchorContext):
        pass


    # Enter a parse tree produced by PCREParser#match_point_reset.
    def enterMatch_point_reset(self, ctx:PCREParser.Match_point_resetContext):
        pass

    # Exit a parse tree produced by PCREParser#match_point_reset.
    def exitMatch_point_reset(self, ctx:PCREParser.Match_point_resetContext):
        pass


    # Enter a parse tree produced by PCREParser#quoting.
    def enterQuoting(self, ctx:PCREParser.QuotingContext):
        pass

    # Exit a parse tree produced by PCREParser#quoting.
    def exitQuoting(self, ctx:PCREParser.QuotingContext):
        pass


    # Enter a parse tree produced by PCREParser#digits.
    def enterDigits(self, ctx:PCREParser.DigitsContext):
        pass

    # Exit a parse tree produced by PCREParser#digits.
    def exitDigits(self, ctx:PCREParser.DigitsContext):
        pass


    # Enter a parse tree produced by PCREParser#digit.
    def enterDigit(self, ctx:PCREParser.DigitContext):
        pass

    # Exit a parse tree produced by PCREParser#digit.
    def exitDigit(self, ctx:PCREParser.DigitContext):
        pass


    # Enter a parse tree produced by PCREParser#hex.
    def enterHex(self, ctx:PCREParser.HexContext):
        pass

    # Exit a parse tree produced by PCREParser#hex.
    def exitHex(self, ctx:PCREParser.HexContext):
        pass


    # Enter a parse tree produced by PCREParser#letters.
    def enterLetters(self, ctx:PCREParser.LettersContext):
        pass

    # Exit a parse tree produced by PCREParser#letters.
    def exitLetters(self, ctx:PCREParser.LettersContext):
        pass


    # Enter a parse tree produced by PCREParser#letter.
    def enterLetter(self, ctx:PCREParser.LetterContext):
        pass

    # Exit a parse tree produced by PCREParser#letter.
    def exitLetter(self, ctx:PCREParser.LetterContext):
        pass


    # Enter a parse tree produced by PCREParser#name.
    def enterName(self, ctx:PCREParser.NameContext):
        pass

    # Exit a parse tree produced by PCREParser#name.
    def exitName(self, ctx:PCREParser.NameContext):
        pass


    # Enter a parse tree produced by PCREParser#other.
    def enterOther(self, ctx:PCREParser.OtherContext):
        pass

    # Exit a parse tree produced by PCREParser#other.
    def exitOther(self, ctx:PCREParser.OtherContext):
        pass


    # Enter a parse tree produced by PCREParser#utf.
    def enterUtf(self, ctx:PCREParser.UtfContext):
        pass

    # Exit a parse tree produced by PCREParser#utf.
    def exitUtf(self, ctx:PCREParser.UtfContext):
        pass


    # Enter a parse tree produced by PCREParser#ucp.
    def enterUcp(self, ctx:PCREParser.UcpContext):
        pass

    # Exit a parse tree produced by PCREParser#ucp.
    def exitUcp(self, ctx:PCREParser.UcpContext):
        pass


    # Enter a parse tree produced by PCREParser#no_auto_possess.
    def enterNo_auto_possess(self, ctx:PCREParser.No_auto_possessContext):
        pass

    # Exit a parse tree produced by PCREParser#no_auto_possess.
    def exitNo_auto_possess(self, ctx:PCREParser.No_auto_possessContext):
        pass


    # Enter a parse tree produced by PCREParser#no_start_opt.
    def enterNo_start_opt(self, ctx:PCREParser.No_start_optContext):
        pass

    # Exit a parse tree produced by PCREParser#no_start_opt.
    def exitNo_start_opt(self, ctx:PCREParser.No_start_optContext):
        pass


    # Enter a parse tree produced by PCREParser#cr.
    def enterCr(self, ctx:PCREParser.CrContext):
        pass

    # Exit a parse tree produced by PCREParser#cr.
    def exitCr(self, ctx:PCREParser.CrContext):
        pass


    # Enter a parse tree produced by PCREParser#lf.
    def enterLf(self, ctx:PCREParser.LfContext):
        pass

    # Exit a parse tree produced by PCREParser#lf.
    def exitLf(self, ctx:PCREParser.LfContext):
        pass


    # Enter a parse tree produced by PCREParser#crlf.
    def enterCrlf(self, ctx:PCREParser.CrlfContext):
        pass

    # Exit a parse tree produced by PCREParser#crlf.
    def exitCrlf(self, ctx:PCREParser.CrlfContext):
        pass


    # Enter a parse tree produced by PCREParser#anycrlf.
    def enterAnycrlf(self, ctx:PCREParser.AnycrlfContext):
        pass

    # Exit a parse tree produced by PCREParser#anycrlf.
    def exitAnycrlf(self, ctx:PCREParser.AnycrlfContext):
        pass


    # Enter a parse tree produced by PCREParser#any.
    def enterAny(self, ctx:PCREParser.AnyContext):
        pass

    # Exit a parse tree produced by PCREParser#any.
    def exitAny(self, ctx:PCREParser.AnyContext):
        pass


    # Enter a parse tree produced by PCREParser#limit_match.
    def enterLimit_match(self, ctx:PCREParser.Limit_matchContext):
        pass

    # Exit a parse tree produced by PCREParser#limit_match.
    def exitLimit_match(self, ctx:PCREParser.Limit_matchContext):
        pass


    # Enter a parse tree produced by PCREParser#limit_recursion.
    def enterLimit_recursion(self, ctx:PCREParser.Limit_recursionContext):
        pass

    # Exit a parse tree produced by PCREParser#limit_recursion.
    def exitLimit_recursion(self, ctx:PCREParser.Limit_recursionContext):
        pass


    # Enter a parse tree produced by PCREParser#bsr_anycrlf.
    def enterBsr_anycrlf(self, ctx:PCREParser.Bsr_anycrlfContext):
        pass

    # Exit a parse tree produced by PCREParser#bsr_anycrlf.
    def exitBsr_anycrlf(self, ctx:PCREParser.Bsr_anycrlfContext):
        pass


    # Enter a parse tree produced by PCREParser#bsr_unicode.
    def enterBsr_unicode(self, ctx:PCREParser.Bsr_unicodeContext):
        pass

    # Exit a parse tree produced by PCREParser#bsr_unicode.
    def exitBsr_unicode(self, ctx:PCREParser.Bsr_unicodeContext):
        pass


    # Enter a parse tree produced by PCREParser#accept.
    def enterAccept(self, ctx:PCREParser.AcceptContext):
        pass

    # Exit a parse tree produced by PCREParser#accept.
    def exitAccept(self, ctx:PCREParser.AcceptContext):
        pass


    # Enter a parse tree produced by PCREParser#fail.
    def enterFail(self, ctx:PCREParser.FailContext):
        pass

    # Exit a parse tree produced by PCREParser#fail.
    def exitFail(self, ctx:PCREParser.FailContext):
        pass


    # Enter a parse tree produced by PCREParser#mark.
    def enterMark(self, ctx:PCREParser.MarkContext):
        pass

    # Exit a parse tree produced by PCREParser#mark.
    def exitMark(self, ctx:PCREParser.MarkContext):
        pass


    # Enter a parse tree produced by PCREParser#commit.
    def enterCommit(self, ctx:PCREParser.CommitContext):
        pass

    # Exit a parse tree produced by PCREParser#commit.
    def exitCommit(self, ctx:PCREParser.CommitContext):
        pass


    # Enter a parse tree produced by PCREParser#prune.
    def enterPrune(self, ctx:PCREParser.PruneContext):
        pass

    # Exit a parse tree produced by PCREParser#prune.
    def exitPrune(self, ctx:PCREParser.PruneContext):
        pass


    # Enter a parse tree produced by PCREParser#skip.
    def enterSkip(self, ctx:PCREParser.SkipContext):
        pass

    # Exit a parse tree produced by PCREParser#skip.
    def exitSkip(self, ctx:PCREParser.SkipContext):
        pass


    # Enter a parse tree produced by PCREParser#then.
    def enterThen(self, ctx:PCREParser.ThenContext):
        pass

    # Exit a parse tree produced by PCREParser#then.
    def exitThen(self, ctx:PCREParser.ThenContext):
        pass



del PCREParser