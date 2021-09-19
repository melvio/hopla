#!/usr/bin/env python3
from hopla.hoplalib.errors import PrintableException, YouFoundABugRewardError


class TestYouFoundABugRewardError:
    def test___init__(self):
        errmsg = "This request is too hot to handle"
        ex = YouFoundABugRewardError(errmsg)

        assert errmsg in str(ex)
        assert "report it over here:"
        assert "https://github.com/melvio/hopla/issues/new" in str(ex)


class TestPrintableException:

    def test___repr___and___str__(self):
        msg = "This request is too cold to handle!"

        ex = PrintableException(msg=msg)

        assert str(ex) == msg
        assert repr(ex) == f"PrintableException({msg})"

    def test___repr__and___str___child_class(self):
        class DNASequencingError(PrintableException):
            """Exception for our test"""

        err_msg = "Sequencing was above acceptable price of 2.50$"
        err = DNASequencingError(msg=err_msg)

        assert str(err) == err_msg
        assert repr(err) == f"DNASequencingError({err_msg})"
