from pytest import mark

from yaenv import utils


@mark.describe('Test utilities')
class TestUtils:

    @mark.it('it can detect truthy values')
    def test_is_truthy(self):
        for val in utils._truthy:
            assert utils.is_truthy(val)
        assert not utils.is_truthy('maybe')
        assert not utils.is_truthy(None)

    @mark.it('it can detect falsy values')
    def test_is_falsy(self):
        for val in utils._falsy:
            assert utils.is_falsy(val)
        assert not utils.is_falsy('maybe')
        assert not utils.is_falsy(None)
