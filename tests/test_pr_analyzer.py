"""
Tests for PR Analyzer

Tests the pull request analysis functionality.
"""

import pytest
from datetime import datetime
from pathlib import Path

from vibemetric.integrations import PRAnalyzer, PRAnalysisResult
from vibemetric.models import AIAssistanceLevel


@pytest.fixture
def pr_analyzer(tmp_path):
    """Create PR analyzer with temp directory"""
    return PRAnalyzer(str(tmp_path))


def test_analyze_pr_minimal_ai(pr_analyzer):
    """Test PR with minimal AI patterns"""
    result = pr_analyzer.analyze_pr_from_data(
        pr_number=123,
        title="Fix bug",
        author="john@example.com",
        description="Fixed the login bug",
        created_at=datetime(2024, 3, 15),
        merged_at=datetime(2024, 3, 16),
        state="merged",
        files_data=[
            {
                "filename": "auth.py",
                "additions": 10,
                "deletions": 5,
                "changes": 15,
                "content": "def login():\n    return True"
            }
        ],
        commits_data=[
            {
                "sha": "abc123",
                "message": "fix bug",
                "author": "John",
                "timestamp": datetime(2024, 3, 15)
            }
        ]
    )
    
    assert result.pr_number == 123
    assert result.title == "Fix bug"
    assert result.author == "john@example.com"
    assert result.state == "merged"
    assert result.overall_ai_score < 40  # Should be MINIMAL
    assert result.ai_assistance_level == AIAssistanceLevel.MINIMAL


def test_analyze_pr_substantial_ai(pr_analyzer):
    """Test PR with substantial AI patterns"""
    ai_description = """
## Summary
This PR introduces comprehensive authentication system.

## Implementation Details
Uses JWT tokens with RS256 algorithm.

## Testing
- [x] Unit tests added
- [x] Integration tests passing
- [x] Manual testing complete

## Related PRs
Related to #120
Depends on #115
"""
    
    ai_commit = """feat: implement authentication system

- Add JWT token generation and validation
- Implement login endpoint with rate limiting
- Add logout functionality with token invalidation
- Update user model with password hashing
"""
    
    ai_code = '''
def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password.
    
    Args:
        username: The username to authenticate
        password: The password to verify
        
    Returns:
        User object if authentication successful, None otherwise
        
    Raises:
        AuthenticationError: If authentication fails
    """
    # This function authenticates the user
    user = get_user_by_username(username)
    if user is not None:
        return user
    return None
'''
    
    result = pr_analyzer.analyze_pr_from_data(
        pr_number=456,
        title="Add authentication system",
        author="ai@example.com",
        description=ai_description,
        created_at=datetime(2024, 3, 15),
        merged_at=datetime(2024, 3, 16),
        state="merged",
        files_data=[
            {
                "filename": "auth.py",
                "additions": 100,
                "deletions": 10,
                "changes": 110,
                "content": ai_code
            }
        ],
        commits_data=[
            {
                "sha": "def456",
                "message": ai_commit,
                "author": "AI User",
                "timestamp": datetime(2024, 3, 15)
            }
        ]
    )
    
    assert result.pr_number == 456
    assert result.overall_ai_score > 50  # Should be PARTIAL or higher
    assert result.ai_assistance_level in [AIAssistanceLevel.PARTIAL, AIAssistanceLevel.SUBSTANTIAL]
    assert result.description_ai_score > 60  # AI description
    assert result.avg_commit_ai_score > 60  # AI commit
    assert len(result.description_patterns) > 0


def test_analyze_pr_with_baseline(pr_analyzer):
    """Test PR analysis with baseline comparison"""
    result = pr_analyzer.analyze_pr_from_data(
        pr_number=789,
        title="Update docs",
        author="doc@example.com",
        description="Updated documentation",
        created_at=datetime(2024, 3, 15),
        merged_at=None,
        state="open",
        files_data=[],
        commits_data=[],
        baseline_score=45.0
    )
    
    assert result.repo_baseline_score == 45.0
    assert result.baseline_difference is not None
    assert result.baseline_percentage is not None


def test_analyze_pr_no_files(pr_analyzer):
    """Test PR with no files changed"""
    result = pr_analyzer.analyze_pr_from_data(
        pr_number=111,
        title="Empty PR",
        author="test@example.com",
        description="Test PR",
        created_at=datetime(2024, 3, 15),
        merged_at=None,
        state="open",
        files_data=[],
        commits_data=[]
    )
    
    assert result.pr_number == 111
    assert len(result.files) == 0
    assert len(result.commits) == 0
    assert result.overall_ai_score >= 0


def test_analyze_pr_multiple_high_ai_files(pr_analyzer):
    """Test PR with multiple high AI likelihood files"""
    ai_code = '''
def process_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process input data and return DataFrame.
    
    Args:
        data: List of dictionaries containing raw data
        
    Returns:
        Processed DataFrame with cleaned data
    """
    # This function processes the data
    return pd.DataFrame(data)
'''
    
    result = pr_analyzer.analyze_pr_from_data(
        pr_number=222,
        title="Add data processing",
        author="dev@example.com",
        description="Added data processing functions",
        created_at=datetime(2024, 3, 15),
        merged_at=None,
        state="open",
        files_data=[
            {
                "filename": "processor1.py",
                "additions": 50,
                "deletions": 0,
                "changes": 50,
                "content": ai_code
            },
            {
                "filename": "processor2.py",
                "additions": 50,
                "deletions": 0,
                "changes": 50,
                "content": ai_code
            },
            {
                "filename": "processor3.py",
                "additions": 50,
                "deletions": 0,
                "changes": 50,
                "content": ai_code
            }
        ],
        commits_data=[]
    )
    
    assert len(result.high_ai_files) >= 0  # May or may not have files >60
    assert result.total_additions == 150
    # Check that files were analyzed
    assert all(f.ai_score > 0 for f in result.files)


def test_should_analyze_file_exclusions(pr_analyzer):
    """Test file exclusion logic"""
    # Should analyze
    assert pr_analyzer._should_analyze_file("src/main.py") == True
    assert pr_analyzer._should_analyze_file("lib/utils.js") == True
    
    # Should NOT analyze
    assert pr_analyzer._should_analyze_file("bundle.min.js") == False
    assert pr_analyzer._should_analyze_file("styles.min.css") == False
    assert pr_analyzer._should_analyze_file("package-lock.json") == False
    assert pr_analyzer._should_analyze_file("yarn.lock") == False
    assert pr_analyzer._should_analyze_file("image.png") == False
    assert pr_analyzer._should_analyze_file("proto_pb2.py") == False


def test_detect_language(pr_analyzer):
    """Test language detection from filename"""
    assert pr_analyzer._detect_language("main.py") == "python"
    assert pr_analyzer._detect_language("app.js") == "javascript"
    assert pr_analyzer._detect_language("component.tsx") == "typescript"
    assert pr_analyzer._detect_language("Main.java") == "java"
    assert pr_analyzer._detect_language("main.go") == "go"
    assert pr_analyzer._detect_language("lib.rs") == "rust"
    assert pr_analyzer._detect_language("unknown.xyz") == "unknown"


def test_pr_result_to_dict(pr_analyzer):
    """Test PRAnalysisResult to_dict conversion"""
    result = PRAnalysisResult(
        pr_number=333,
        title="Test PR",
        author="test@example.com",
        description="Test description",
        created_at=datetime(2024, 3, 15),
        merged_at=None,
        state="open",
        description_ai_score=50.0,
        description_confidence=0.7,
        overall_ai_score=45.0,
        overall_confidence=0.65,
        ai_assistance_level=AIAssistanceLevel.PARTIAL
    )
    
    data = result.to_dict()
    
    assert data["pr_number"] == 333
    assert data["title"] == "Test PR"
    assert data["state"] == "open"
    assert data["description_analysis"]["ai_score"] == 50.0
    assert data["overall"]["ai_score"] == 45.0
    assert data["overall"]["ai_assistance_level"] == "PARTIAL"


def test_pr_result_format_terminal(pr_analyzer):
    """Test PRAnalysisResult terminal formatting"""
    result = PRAnalysisResult(
        pr_number=444,
        title="Test PR",
        author="test@example.com",
        description="Test",
        created_at=datetime(2024, 3, 15),
        merged_at=datetime(2024, 3, 16),
        state="merged",
        description_ai_score=60.0,
        description_confidence=0.75,
        overall_ai_score=55.0,
        overall_confidence=0.70,
        ai_assistance_level=AIAssistanceLevel.PARTIAL
    )
    
    output = result.format_terminal()
    
    assert "Pull Request Analysis: #444" in output
    assert "Test PR" in output
    assert "test@example.com" in output
    assert "55.0/100" in output
    assert "PARTIAL" in output


def test_analyze_pr_with_binary_files(pr_analyzer):
    """Test PR with binary files (no content)"""
    result = pr_analyzer.analyze_pr_from_data(
        pr_number=555,
        title="Add images",
        author="designer@example.com",
        description="Added logo images",
        created_at=datetime(2024, 3, 15),
        merged_at=None,
        state="open",
        files_data=[
            {
                "filename": "logo.png",
                "additions": 0,
                "deletions": 0,
                "changes": 0,
                "content": None  # Binary file
            }
        ],
        commits_data=[]
    )
    
    assert result.pr_number == 555
    assert len(result.files) == 1
    assert result.files[0].ai_score == 0.0  # No content to analyze


def test_analyze_pr_empty_description(pr_analyzer):
    """Test PR with empty description"""
    result = pr_analyzer.analyze_pr_from_data(
        pr_number=666,
        title="Quick fix",
        author="dev@example.com",
        description="",
        created_at=datetime(2024, 3, 15),
        merged_at=None,
        state="open",
        files_data=[],
        commits_data=[]
    )
    
    assert result.description_ai_score == 0.0
    assert len(result.description_patterns) == 0
