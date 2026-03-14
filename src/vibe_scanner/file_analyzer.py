"""
Code file analyzer orchestration.

This module orchestrates the analysis of individual code files by:
- Detecting programming language
- Integrating all detection modules
- Parsing code with tree-sitter (when available)
- Collecting and aggregating signals
- Calculating per-file vibe scores
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import FileAnalysisResult, DetectionSignal, VibeScore
from .detectors.pattern_detector import PatternDetector
from .detectors.statistical_analyzer import StatisticalAnalyzer
from .detectors.style_analyzer import StyleAnalyzer
from .detectors.git_analyzer import GitMetadataAnalyzer
from .scorer import VibeScoreCalculator


class CodeFileAnalyzer:
    """
    Analyzes individual code files using multiple detection methods.
    
    Coordinates pattern detection, statistical analysis, style analysis,
    and git metadata analysis to produce comprehensive file-level results.
    """
    
    def __init__(self, enable_git: bool = True):
        """
        Initialize the code file analyzer.
        
        Args:
            enable_git: Whether to enable git metadata analysis
        """
        self.pattern_detector = PatternDetector()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.style_analyzer = StyleAnalyzer()
        self.git_analyzer = GitMetadataAnalyzer() if enable_git else None
        self.scorer = VibeScoreCalculator()
    
    def analyze_file(self, file_path: str, repo_path: str = ".") -> FileAnalysisResult:
        """
        Analyze a single code file.
        
        Args:
            file_path: Relative path to the file
            repo_path: Path to repository root
            
        Returns:
            FileAnalysisResult with complete analysis
        """
        # Construct full path
        full_path = os.path.join(repo_path, file_path)
        
        # Read file content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return self._create_error_result(file_path, f"Failed to read file: {e}")
        
        # Detect language
        language = self._detect_language(file_path, code)
        
        # Count lines
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        
        # Parse AST (optional, for now we'll skip)
        ast = None  # TODO: Implement tree-sitter parsing in Task 19
        
        # Collect detection signals
        signals = []
        
        # Pattern detection
        try:
            pattern_signal = self.pattern_detector.detect(code, language, ast)
            signals.append(pattern_signal)
        except Exception as e:
            print(f"Pattern detection failed: {e}")
        
        # Statistical analysis
        try:
            statistical_signal = self.statistical_analyzer.analyze(code, language)
            signals.append(statistical_signal)
        except Exception as e:
            print(f"Statistical analysis failed: {e}")
        
        # Style analysis
        try:
            style_signal = self.style_analyzer.analyze(code, language, None)
            signals.append(style_signal)
        except Exception as e:
            print(f"Style analysis failed: {e}")
        
        # Git metadata analysis
        if self.git_analyzer:
            try:
                git_signal = self.git_analyzer.analyze(file_path, repo_path)
                signals.append(git_signal)
            except Exception as e:
                print(f"Git analysis failed: {e}")
        
        # Calculate vibe score
        vibe_score = self.scorer.calculate_file_score(signals)
        
        # Extract metrics from signals
        pattern_matches = []
        statistical_metrics = None
        style_metrics = None
        git_metrics = None
        
        for signal in signals:
            if signal.signal_name == "pattern_detection":
                # Extract pattern matches from evidence
                for evidence in signal.evidence:
                    pattern_matches.append({
                        "type": evidence.evidence_type,
                        "score": evidence.score,
                        "details": evidence.details
                    })
            elif signal.signal_name == "statistical_analysis":
                statistical_metrics = signal.metadata
            elif signal.signal_name == "style_analysis":
                style_metrics = signal.metadata.get("features", {})
            elif signal.signal_name == "git_metadata":
                git_metrics = signal.metadata
        
        # Create result
        return FileAnalysisResult(
            file_path=file_path,
            language=language,
            total_lines=total_lines,
            code_lines=code_lines,
            vibe_score=vibe_score,
            pattern_matches=pattern_matches,
            statistical_metrics=statistical_metrics,
            style_metrics=style_metrics,
            git_metrics=git_metrics,
            analysis_timestamp=datetime.now()
        )
    
    def _detect_language(self, file_path: str, code: str) -> str:
        """
        Detect programming language from file extension and content.
        
        Args:
            file_path: Path to the file
            code: File content
            
        Returns:
            Language identifier
        """
        # Extension-based detection
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.rb': 'ruby',
            '.php': 'php',
        }
        
        _, ext = os.path.splitext(file_path)
        language = ext_map.get(ext.lower(), 'unknown')
        
        # Content-based hints (if extension unknown)
        if language == 'unknown' and code:
            if 'def ' in code or 'import ' in code:
                language = 'python'
            elif 'function ' in code or 'const ' in code:
                language = 'javascript'
            elif 'public class ' in code or 'package ' in code:
                language = 'java'
        
        return language
    
    def _create_error_result(self, file_path: str, error_msg: str) -> FileAnalysisResult:
        """Create an error result for failed analysis."""
        from .models import RiskLevel
        
        return FileAnalysisResult(
            file_path=file_path,
            language='unknown',
            total_lines=0,
            code_lines=0,
            vibe_score=VibeScore(
                overall_score=0.0,
                confidence=0.0,
                contributing_signals={},
                risk_level=RiskLevel.LOW,
                explanation=f"Analysis failed: {error_msg}",
                line_scores=None
            ),
            pattern_matches=[],
            statistical_metrics=None,
            style_metrics=None,
            git_metrics=None,
            analysis_timestamp=datetime.now()
        )
