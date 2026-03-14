"""
Report generation for scan results.

This module generates reports in multiple formats:
- Terminal output with colors and formatting (using rich)
- JSON output for CI/CD integration
- Markdown output for documentation
"""

import json
from typing import Dict, Any
from enum import Enum

from .models import ScanResult, RiskLevel, OutputFormat


class ReportGenerator:
    """
    Generates reports in multiple output formats.
    
    Formats scan results for terminal display, JSON export, or markdown documentation.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        pass
    
    def generate(self, result: ScanResult, format: OutputFormat = OutputFormat.TERMINAL) -> str:
        """
        Generate report in specified format.
        
        Args:
            result: Scan result to format
            format: Output format
            
        Returns:
            Formatted report as string
        """
        if format == OutputFormat.TERMINAL:
            return self.generate_terminal_report(result)
        elif format == OutputFormat.JSON:
            return self.generate_json_report(result)
        elif format == OutputFormat.MARKDOWN:
            return self.generate_markdown_report(result)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_terminal_report(self, result: ScanResult) -> str:
        """Generate terminal output with colors and formatting."""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("           VIBE SCANNER - AI Code Detection")
        lines.append("=" * 60)
        lines.append("")
        
        # Explanatory info
        lines.append("📊 Understanding Your Results:")
        lines.append("")
        lines.append("• Vibe Score: Likelihood that code was AI-generated (0-100%)")
        lines.append("  - 0-30%: LOW risk (mostly human-written)")
        lines.append("  - 30-70%: MEDIUM risk (mixed or uncertain)")
        lines.append("  - 70-100%: HIGH risk (likely AI-generated)")
        lines.append("")
        lines.append("• Confidence: How certain the analysis is (0.0-1.0)")
        lines.append("  - Higher confidence = more detection signals agree")
        lines.append("")
        lines.append("• Detection Signals: Different analysis methods used:")
        lines.append("  - Pattern Detection: AI-style comments, code patterns")
        lines.append("  - Statistical Analysis: Code predictability, token distribution")
        lines.append("  - Style Analysis: Coding style consistency")
        lines.append("  - Git Metadata: Authoring speed, commit patterns")
        lines.append("")
        lines.append("=" * 60)
        lines.append("")
        
        # Overall results
        score = result.overall_vibe_score.overall_score
        risk_emoji = self._get_risk_emoji(result.overall_vibe_score.risk_level)
        
        lines.append(f"Repository: {result.repo_path}")
        lines.append(f"Files Scanned: {result.total_files_scanned}")
        lines.append(f"Lines Analyzed: {result.total_lines_analyzed:,}")
        lines.append("")
        lines.append(f"Vibe Score: {score:.1f}% {risk_emoji}")
        lines.append(f"Risk Level: {result.overall_vibe_score.risk_level.value.upper()}")
        lines.append(f"Confidence: {result.overall_vibe_score.confidence:.2f}")
        lines.append("")
        
        # AI vs Human breakdown
        ai_pct = (result.ai_generated_lines / result.total_lines_analyzed * 100) if result.total_lines_analyzed > 0 else 0
        human_pct = 100 - ai_pct
        
        lines.append(f"AI-Generated: {result.ai_generated_lines:,} lines ({ai_pct:.1f}%)")
        lines.append(f"Human-Written: {result.human_written_lines:,} lines ({human_pct:.1f}%)")
        lines.append("")
        
        # Top AI-likely files
        if result.file_results:
            lines.append("-" * 60)
            lines.append("Top AI-Likely Files:")
            lines.append("-" * 60)
            
            sorted_files = sorted(result.file_results, key=lambda f: f.vibe_score.overall_score, reverse=True)[:10]
            
            for i, file_result in enumerate(sorted_files, 1):
                file_score = file_result.vibe_score.overall_score
                file_risk = self._get_risk_emoji(file_result.vibe_score.risk_level)
                lines.append(f"{i}. {file_result.file_path}")
                lines.append(f"   Score: {file_score:.1f}% {file_risk} | Lines: {file_result.code_lines}")
            
            lines.append("")
        
        # Detection signals
        if result.overall_vibe_score.contributing_signals:
            lines.append("-" * 60)
            lines.append("Detection Signals:")
            lines.append("-" * 60)
            
            for signal_name, score in result.overall_vibe_score.contributing_signals.items():
                signal_display = signal_name.replace('_', ' ').title()
                bar = self._create_progress_bar(score, 40)
                lines.append(f"{signal_display:25s} {score:5.1f}% {bar}")
            
            lines.append("")
        
        # Risk summary
        lines.append("-" * 60)
        lines.append("Risk Summary:")
        lines.append("-" * 60)
        lines.append(f"High Risk Files: {result.risk_summary.high_risk_files}")
        lines.append(f"Medium Risk Files: {result.risk_summary.medium_risk_files}")
        lines.append(f"Low Risk Files: {result.risk_summary.low_risk_files}")
        lines.append("")
        
        # Footer
        lines.append(f"Scan completed in {result.scan_duration:.2f} seconds")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def generate_json_report(self, result: ScanResult) -> str:
        """Generate JSON output for CI/CD integration."""
        data = {
            "version": "1.0.0",
            "scan_timestamp": result.scan_timestamp.isoformat(),
            "repo_path": result.repo_path,
            "scan_duration": result.scan_duration,
            "overall_results": {
                "vibe_score": result.overall_vibe_score.overall_score,
                "confidence": result.overall_vibe_score.confidence,
                "risk_level": result.overall_vibe_score.risk_level.value,
                "total_files": result.total_files_scanned,
                "total_lines": result.total_lines_analyzed,
                "ai_generated_lines": result.ai_generated_lines,
                "human_written_lines": result.human_written_lines
            },
            "detection_signals": result.overall_vibe_score.contributing_signals,
            "file_results": [
                {
                    "file_path": f.file_path,
                    "language": f.language,
                    "total_lines": f.total_lines,
                    "code_lines": f.code_lines,
                    "vibe_score": f.vibe_score.overall_score,
                    "confidence": f.vibe_score.confidence,
                    "risk_level": f.vibe_score.risk_level.value,
                    "explanation": f.vibe_score.explanation
                }
                for f in result.file_results
            ],
            "risk_summary": {
                "high_risk_files": result.risk_summary.high_risk_files,
                "medium_risk_files": result.risk_summary.medium_risk_files,
                "low_risk_files": result.risk_summary.low_risk_files,
                "critical_files_affected": result.risk_summary.critical_files_affected
            }
        }
        
        return json.dumps(data, indent=2)
    
    def generate_markdown_report(self, result: ScanResult) -> str:
        """Generate markdown output for documentation."""
        lines = []
        
        # Header
        lines.append("# Vibe Scanner Report")
        lines.append("")
        lines.append(f"**Repository:** {result.repo_path}")
        lines.append(f"**Scan Date:** {result.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Scan Duration:** {result.scan_duration:.2f} seconds")
        lines.append("")
        
        # Overall Results
        lines.append("## Overall Results")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Vibe Score | {result.overall_vibe_score.overall_score:.1f}% {self._get_risk_emoji(result.overall_vibe_score.risk_level)} |")
        lines.append(f"| Risk Level | {result.overall_vibe_score.risk_level.value.upper()} |")
        lines.append(f"| Confidence | {result.overall_vibe_score.confidence:.2f} |")
        lines.append(f"| Total Files | {result.total_files_scanned} |")
        lines.append(f"| Total Lines | {result.total_lines_analyzed:,} |")
        
        ai_pct = (result.ai_generated_lines / result.total_lines_analyzed * 100) if result.total_lines_analyzed > 0 else 0
        human_pct = 100 - ai_pct
        
        lines.append(f"| AI-Generated Lines | {result.ai_generated_lines:,} ({ai_pct:.1f}%) |")
        lines.append(f"| Human-Written Lines | {result.human_written_lines:,} ({human_pct:.1f}%) |")
        lines.append("")
        
        # Detection Signals
        if result.overall_vibe_score.contributing_signals:
            lines.append("## Detection Signals")
            lines.append("")
            lines.append("| Signal | Score |")
            lines.append("|--------|-------|")
            
            for signal_name, score in result.overall_vibe_score.contributing_signals.items():
                signal_display = signal_name.replace('_', ' ').title()
                lines.append(f"| {signal_display} | {score:.1f}% |")
            
            lines.append("")
        
        # High-Risk Files
        if result.file_results:
            high_risk_files = [f for f in result.file_results if f.vibe_score.risk_level == RiskLevel.HIGH]
            
            if high_risk_files:
                lines.append("## High-Risk Files")
                lines.append("")
                lines.append("| File | Vibe Score | Risk Level |")
                lines.append("|------|------------|------------|")
                
                for file_result in sorted(high_risk_files, key=lambda f: f.vibe_score.overall_score, reverse=True):
                    lines.append(f"| {file_result.file_path} | {file_result.vibe_score.overall_score:.1f}% | {self._get_risk_emoji(file_result.vibe_score.risk_level)} HIGH |")
                
                lines.append("")
        
        # Risk Summary
        lines.append("## Risk Summary")
        lines.append("")
        lines.append(f"- **High Risk Files:** {result.risk_summary.high_risk_files}")
        lines.append(f"- **Medium Risk Files:** {result.risk_summary.medium_risk_files}")
        lines.append(f"- **Low Risk Files:** {result.risk_summary.low_risk_files}")
        
        critical_files = result.risk_summary.critical_files_affected
        if critical_files:
            lines.append(f"- **Critical Files Affected:** {', '.join(critical_files[:5])}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _get_risk_emoji(self, risk_level: RiskLevel) -> str:
        """Get emoji for risk level."""
        if risk_level == RiskLevel.HIGH:
            return "🔴"
        elif risk_level == RiskLevel.MEDIUM:
            return "🟡"
        else:
            return "🟢"
    
    def _create_progress_bar(self, value: float, width: int = 20) -> str:
        """Create a simple text progress bar."""
        filled = int((value / 100.0) * width)
        empty = width - filled
        return "[" + "█" * filled + "░" * empty + "]"
