#!/usr/bin/env python3
"""
MLOps Data Validation System for DAGnostics
Comprehensive data quality checks and validation pipeline
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import hashlib
import re
from collections import Counter
import numpy as np
from scipy import stats
import warnings

logger = logging.getLogger(__name__)


@dataclass
class DataQualityReport:
    """Data quality assessment report"""
    
    # Basic statistics
    total_samples: int
    unique_samples: int
    duplicate_count: int
    
    # Content analysis
    avg_input_length: float
    avg_output_length: float
    min_input_length: int
    max_input_length: int
    min_output_length: int
    max_output_length: int
    
    # Quality metrics
    empty_inputs: int
    empty_outputs: int
    malformed_samples: int
    encoding_errors: int
    
    # Label distribution
    label_distribution: Dict[str, int]
    class_imbalance_ratio: float
    
    # Advanced metrics
    data_hash: str
    creation_timestamp: str
    
    # Quality score (0-1)
    quality_score: float
    
    # Issues found
    issues: List[str]
    warnings: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DataValidator:
    """
    Comprehensive data validation for training datasets
    Implements data quality checks, schema validation, and drift detection
    """
    
    def __init__(
        self,
        min_samples: int = 50,
        max_input_length: int = 2048,
        max_output_length: int = 512,
        min_input_length: int = 10,
        min_output_length: int = 1,
        max_class_imbalance: float = 10.0  # Max ratio between largest and smallest class
    ):
        self.min_samples = min_samples
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        self.min_input_length = min_input_length
        self.min_output_length = min_output_length
        self.max_class_imbalance = max_class_imbalance
        
        # Reference datasets for drift detection
        self.reference_stats = {}
        
        logger.info("🔍 Data validator initialized")
    
    def validate_dataset(
        self,
        dataset_path: str,
        dataset_type: str = "training"
    ) -> DataQualityReport:
        """
        Comprehensive dataset validation
        Returns detailed quality report
        """
        logger.info(f"🔍 Validating {dataset_type} dataset: {dataset_path}")
        
        if not Path(dataset_path).exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # Load and parse dataset
        samples = self._load_dataset(dataset_path)
        
        # Basic statistics
        basic_stats = self._compute_basic_statistics(samples)
        
        # Content analysis
        content_stats = self._analyze_content(samples)
        
        # Quality checks
        quality_issues = self._check_quality_issues(samples)
        
        # Label analysis
        label_stats = self._analyze_labels(samples)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            basic_stats, content_stats, quality_issues, label_stats
        )
        
        # Generate data hash
        data_hash = self._generate_data_hash(samples)
        
        # Create report
        report = DataQualityReport(
            # Basic statistics
            total_samples=basic_stats['total'],
            unique_samples=basic_stats['unique'],
            duplicate_count=basic_stats['duplicates'],
            
            # Content analysis
            avg_input_length=content_stats['avg_input_length'],
            avg_output_length=content_stats['avg_output_length'],
            min_input_length=content_stats['min_input_length'],
            max_input_length=content_stats['max_input_length'],
            min_output_length=content_stats['min_output_length'],
            max_output_length=content_stats['max_output_length'],
            
            # Quality metrics
            empty_inputs=quality_issues['empty_inputs'],
            empty_outputs=quality_issues['empty_outputs'],
            malformed_samples=quality_issues['malformed'],
            encoding_errors=quality_issues['encoding_errors'],
            
            # Label analysis
            label_distribution=label_stats['distribution'],
            class_imbalance_ratio=label_stats['imbalance_ratio'],
            
            # Metadata
            data_hash=data_hash,
            creation_timestamp=datetime.now().isoformat(),
            quality_score=quality_score,
            issues=quality_issues['issues'],
            warnings=quality_issues['warnings']
        )
        
        # Log results
        self._log_validation_results(report, dataset_type)
        
        # Save report
        self._save_report(report, dataset_path, dataset_type)
        
        return report
    
    def validate_training_pipeline(
        self,
        train_path: str,
        val_path: str,
        test_path: Optional[str] = None
    ) -> Dict[str, DataQualityReport]:
        """Validate complete training pipeline datasets"""
        
        logger.info("🔍 Validating complete training pipeline")
        
        reports = {}
        
        # Validate training set
        reports['train'] = self.validate_dataset(train_path, "training")
        
        # Validate validation set
        if Path(val_path).exists():
            reports['validation'] = self.validate_dataset(val_path, "validation")
        else:
            logger.warning("⚠️  Validation dataset not found")
        
        # Validate test set if provided
        if test_path and Path(test_path).exists():
            reports['test'] = self.validate_dataset(test_path, "test")
        
        # Cross-dataset validation
        cross_validation_issues = self._validate_cross_dataset_consistency(reports)
        
        # Add cross-validation issues to reports
        for dataset_type, issues in cross_validation_issues.items():
            if dataset_type in reports:
                reports[dataset_type].issues.extend(issues)
        
        # Generate pipeline summary
        pipeline_summary = self._generate_pipeline_summary(reports)
        
        logger.info(f"✅ Pipeline validation completed: {pipeline_summary}")
        
        return reports
    
    def detect_data_drift(
        self,
        current_dataset_path: str,
        reference_dataset_path: str,
        threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Detect data drift between current and reference datasets
        Uses statistical tests and distribution comparisons
        """
        logger.info("🔍 Detecting data drift...")
        
        # Load datasets
        current_samples = self._load_dataset(current_dataset_path)
        reference_samples = self._load_dataset(reference_dataset_path)
        
        drift_report = {
            'drift_detected': False,
            'drift_score': 0.0,
            'statistical_tests': {},
            'distribution_shifts': {},
            'recommendations': []
        }
        
        # Statistical tests
        input_lengths_current = [len(s.get('input', '')) for s in current_samples]
        input_lengths_reference = [len(s.get('input', '')) for s in reference_samples]
        
        # KS test for input length distribution
        ks_stat, ks_p_value = stats.ks_2samp(input_lengths_current, input_lengths_reference)
        
        drift_report['statistical_tests']['input_length_ks'] = {
            'statistic': ks_stat,
            'p_value': ks_p_value,
            'drift_detected': ks_p_value < threshold
        }
        
        # Output length distribution
        output_lengths_current = [len(s.get('output', '')) for s in current_samples]
        output_lengths_reference = [len(s.get('output', '')) for s in reference_samples]
        
        ks_stat_out, ks_p_value_out = stats.ks_2samp(output_lengths_current, output_lengths_reference)
        
        drift_report['statistical_tests']['output_length_ks'] = {
            'statistic': ks_stat_out,
            'p_value': ks_p_value_out,
            'drift_detected': ks_p_value_out < threshold
        }
        
        # Vocabulary drift
        vocab_drift = self._detect_vocabulary_drift(current_samples, reference_samples)
        drift_report['distribution_shifts']['vocabulary'] = vocab_drift
        
        # Overall drift detection
        any_drift = any([
            test['drift_detected'] for test in drift_report['statistical_tests'].values()
        ]) or vocab_drift['drift_detected']
        
        drift_report['drift_detected'] = any_drift
        drift_report['drift_score'] = max([
            test['statistic'] for test in drift_report['statistical_tests'].values()
        ])
        
        # Generate recommendations
        if any_drift:
            drift_report['recommendations'] = self._generate_drift_recommendations(drift_report)
        
        logger.info(f"📊 Drift detection completed - Drift detected: {any_drift}")
        
        return drift_report
    
    def _load_dataset(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Load dataset from JSONL file"""
        samples = []
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        sample = json.loads(line.strip())
                        samples.append(sample)
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️  Malformed JSON at line {line_num}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"❌ Failed to load dataset {dataset_path}: {e}")
            raise
        
        return samples
    
    def _compute_basic_statistics(self, samples: List[Dict]) -> Dict[str, Any]:
        """Compute basic dataset statistics"""
        total = len(samples)
        
        # Check for duplicates (by input+output content)
        seen = set()
        unique_count = 0
        
        for sample in samples:
            content_hash = hashlib.md5(
                (str(sample.get('input', '')) + str(sample.get('output', ''))).encode()
            ).hexdigest()
            
            if content_hash not in seen:
                seen.add(content_hash)
                unique_count += 1
        
        return {
            'total': total,
            'unique': unique_count,
            'duplicates': total - unique_count
        }
    
    def _analyze_content(self, samples: List[Dict]) -> Dict[str, Any]:
        """Analyze content length statistics"""
        input_lengths = []
        output_lengths = []
        
        for sample in samples:
            input_text = sample.get('input', '')
            output_text = sample.get('output', '')
            
            input_lengths.append(len(input_text))
            output_lengths.append(len(output_text))
        
        return {
            'avg_input_length': np.mean(input_lengths) if input_lengths else 0,
            'avg_output_length': np.mean(output_lengths) if output_lengths else 0,
            'min_input_length': min(input_lengths) if input_lengths else 0,
            'max_input_length': max(input_lengths) if input_lengths else 0,
            'min_output_length': min(output_lengths) if output_lengths else 0,
            'max_output_length': max(output_lengths) if output_lengths else 0
        }
    
    def _check_quality_issues(self, samples: List[Dict]) -> Dict[str, Any]:
        """Check for data quality issues"""
        issues = []
        warnings = []
        
        empty_inputs = 0
        empty_outputs = 0
        malformed = 0
        encoding_errors = 0
        
        for i, sample in enumerate(samples):
            # Check required fields
            if not isinstance(sample, dict):
                malformed += 1
                continue
            
            # Check for empty inputs
            input_text = sample.get('input', '').strip()
            if not input_text:
                empty_inputs += 1
            
            # Check for empty outputs  
            output_text = sample.get('output', '').strip()
            if not output_text:
                empty_outputs += 1
            
            # Check input length
            if len(input_text) < self.min_input_length:
                warnings.append(f"Sample {i}: Input too short ({len(input_text)} chars)")
            elif len(input_text) > self.max_input_length:
                warnings.append(f"Sample {i}: Input too long ({len(input_text)} chars)")
            
            # Check output length
            if len(output_text) < self.min_output_length:
                warnings.append(f"Sample {i}: Output too short ({len(output_text)} chars)")
            elif len(output_text) > self.max_output_length:
                warnings.append(f"Sample {i}: Output too long ({len(output_text)} chars)")
            
            # Check for encoding issues
            try:
                input_text.encode('utf-8')
                output_text.encode('utf-8')
            except UnicodeEncodeError:
                encoding_errors += 1
        
        # Generate issues
        if len(samples) < self.min_samples:
            issues.append(f"Dataset too small: {len(samples)} < {self.min_samples}")
        
        if empty_inputs > 0:
            issues.append(f"Found {empty_inputs} empty inputs")
        
        if empty_outputs > 0:
            issues.append(f"Found {empty_outputs} empty outputs")
        
        if malformed > 0:
            issues.append(f"Found {malformed} malformed samples")
        
        if encoding_errors > 0:
            issues.append(f"Found {encoding_errors} encoding errors")
        
        return {
            'empty_inputs': empty_inputs,
            'empty_outputs': empty_outputs,
            'malformed': malformed,
            'encoding_errors': encoding_errors,
            'issues': issues,
            'warnings': warnings[:10]  # Limit warnings
        }
    
    def _analyze_labels(self, samples: List[Dict]) -> Dict[str, Any]:
        """Analyze label distribution and class balance"""
        labels = []
        
        for sample in samples:
            # Extract labels/categories from output
            output = sample.get('output', '')
            
            # Try to parse as JSON first (for structured outputs)
            try:
                if output.startswith('{'):
                    output_json = json.loads(output)
                    if 'category' in output_json:
                        labels.append(output_json['category'])
                    else:
                        labels.append('unknown')
                else:
                    # For simple text outputs, use first few words as category
                    words = output.split()[:2]
                    category = '_'.join(words) if words else 'empty'
                    labels.append(category)
            except json.JSONDecodeError:
                # Fallback to text-based categorization
                words = output.split()[:2]
                category = '_'.join(words) if words else 'empty'
                labels.append(category)
        
        # Count distribution
        distribution = dict(Counter(labels))
        
        # Calculate class imbalance
        if distribution:
            max_count = max(distribution.values())
            min_count = min(distribution.values())
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
        else:
            imbalance_ratio = 0.0
        
        return {
            'distribution': distribution,
            'imbalance_ratio': imbalance_ratio
        }
    
    def _calculate_quality_score(
        self,
        basic_stats: Dict,
        content_stats: Dict,
        quality_issues: Dict,
        label_stats: Dict
    ) -> float:
        """Calculate overall data quality score (0-1)"""
        
        score = 1.0
        
        # Penalize for insufficient data
        if basic_stats['total'] < self.min_samples:
            score *= 0.3
        
        # Penalize for duplicates
        duplicate_ratio = basic_stats['duplicates'] / basic_stats['total']
        score *= (1 - duplicate_ratio * 0.5)
        
        # Penalize for empty data
        empty_ratio = (quality_issues['empty_inputs'] + quality_issues['empty_outputs']) / (2 * basic_stats['total'])
        score *= (1 - empty_ratio)
        
        # Penalize for malformed data
        malformed_ratio = quality_issues['malformed'] / basic_stats['total']
        score *= (1 - malformed_ratio)
        
        # Penalize for extreme class imbalance
        if label_stats['imbalance_ratio'] > self.max_class_imbalance:
            score *= 0.7
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _generate_data_hash(self, samples: List[Dict]) -> str:
        """Generate hash for data versioning"""
        content = json.dumps(samples, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _log_validation_results(self, report: DataQualityReport, dataset_type: str):
        """Log validation results"""
        logger.info(f"📊 {dataset_type.title()} Dataset Validation Results:")
        logger.info(f"   📈 Total samples: {report.total_samples}")
        logger.info(f"   🎯 Quality score: {report.quality_score:.2f}")
        logger.info(f"   📝 Issues found: {len(report.issues)}")
        logger.info(f"   ⚠️  Warnings: {len(report.warnings)}")
        
        if report.issues:
            for issue in report.issues[:5]:  # Show first 5 issues
                logger.warning(f"   ❌ {issue}")
    
    def _save_report(self, report: DataQualityReport, dataset_path: str, dataset_type: str):
        """Save validation report"""
        try:
            # Create reports directory
            reports_dir = Path("mlops/data_reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Save report
            report_file = reports_dir / f"{dataset_type}_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report.to_dict(), f, indent=2, default=str)
            
            logger.info(f"💾 Validation report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save report: {e}")
    
    def _validate_cross_dataset_consistency(self, reports: Dict[str, DataQualityReport]) -> Dict[str, List[str]]:
        """Validate consistency across train/validation/test splits"""
        cross_issues = {dataset: [] for dataset in reports.keys()}
        
        if 'train' in reports and 'validation' in reports:
            train_report = reports['train']
            val_report = reports['validation']
            
            # Check size ratio
            size_ratio = val_report.total_samples / train_report.total_samples
            if size_ratio > 0.5:
                cross_issues['validation'].append("Validation set too large compared to training set")
            elif size_ratio < 0.1:
                cross_issues['validation'].append("Validation set too small compared to training set")
            
            # Check length distributions
            if abs(train_report.avg_input_length - val_report.avg_input_length) > train_report.avg_input_length * 0.5:
                cross_issues['validation'].append("Input length distribution differs significantly from training set")
        
        return cross_issues
    
    def _generate_pipeline_summary(self, reports: Dict[str, DataQualityReport]) -> str:
        """Generate pipeline validation summary"""
        total_samples = sum(report.total_samples for report in reports.values())
        avg_quality = np.mean([report.quality_score for report in reports.values()])
        total_issues = sum(len(report.issues) for report in reports.values())
        
        return f"Total samples: {total_samples}, Avg quality: {avg_quality:.2f}, Issues: {total_issues}"
    
    def _detect_vocabulary_drift(self, current_samples: List[Dict], reference_samples: List[Dict]) -> Dict[str, Any]:
        """Detect vocabulary drift between datasets"""
        
        # Extract vocabulary from both datasets
        current_vocab = set()
        reference_vocab = set()
        
        for sample in current_samples:
            text = sample.get('input', '') + ' ' + sample.get('output', '')
            words = re.findall(r'\w+', text.lower())
            current_vocab.update(words)
        
        for sample in reference_samples:
            text = sample.get('input', '') + ' ' + sample.get('output', '')
            words = re.findall(r'\w+', text.lower())
            reference_vocab.update(words)
        
        # Calculate vocabulary overlap
        intersection = current_vocab.intersection(reference_vocab)
        union = current_vocab.union(reference_vocab)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0
        
        # New words in current dataset
        new_words = current_vocab - reference_vocab
        missing_words = reference_vocab - current_vocab
        
        drift_detected = jaccard_similarity < 0.7  # Threshold for significant vocabulary change
        
        return {
            'jaccard_similarity': jaccard_similarity,
            'new_words_count': len(new_words),
            'missing_words_count': len(missing_words),
            'new_words_sample': list(new_words)[:10],
            'missing_words_sample': list(missing_words)[:10],
            'drift_detected': drift_detected
        }
    
    def _generate_drift_recommendations(self, drift_report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on drift detection"""
        recommendations = []
        
        if drift_report['statistical_tests'].get('input_length_ks', {}).get('drift_detected'):
            recommendations.append("Input length distribution has changed - consider retraining or data preprocessing")
        
        if drift_report['statistical_tests'].get('output_length_ks', {}).get('drift_detected'):
            recommendations.append("Output length distribution has changed - review output formatting")
        
        if drift_report['distribution_shifts']['vocabulary']['drift_detected']:
            recommendations.append("Vocabulary drift detected - consider updating training data or retraining model")
        
        return recommendations


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    validator = DataValidator()
    
    # Validate single dataset
    try:
        report = validator.validate_dataset("data/training/train_dataset.jsonl", "training")
        print(f"✅ Validation completed - Quality score: {report.quality_score:.2f}")
        print(f"📊 Issues found: {len(report.issues)}")
        
    except FileNotFoundError:
        print("❌ Dataset file not found - create sample data first")
    
    print("🔍 Data validation system ready!")