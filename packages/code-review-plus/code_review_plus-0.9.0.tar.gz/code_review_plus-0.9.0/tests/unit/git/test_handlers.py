from code_review.plugins.git.handlers import compare_branches


class TestCompareBranches:
    def test_compare_handler(self):
        result = compare_branches("master", "feature/bulk_git_sync")
        assert result is not None
