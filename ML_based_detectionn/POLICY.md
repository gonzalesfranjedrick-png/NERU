# Detection Policy and False Positive Trade-offs

## Overview
This document outlines the detection policies and acceptable false-positive trade-offs for the polymorphic malware detection system.

## Detection Sensitivity Levels

### High Sensitivity (Default)
- Detection Threshold: 0.65
- False Positive Rate: < 0.5%
- False Negative Rate: < 0.1%
- Use Case: High-security environments where missing malware is critical
- Trade-off: May flag some benign but unusual files

### Medium Sensitivity
- Detection Threshold: 0.75
- False Positive Rate: < 0.1%
- False Negative Rate: < 1%
- Use Case: General purpose scanning
- Trade-off: Balanced between detection and false positives

### Low Sensitivity
- Detection Threshold: 0.85
- False Positive Rate: < 0.01%
- False Negative Rate: < 5%
- Use Case: Environments where false positives are very costly
- Trade-off: May miss some sophisticated malware

## Feature Weights and Importance

### Critical Features (High Weight)
1. Entropy Analysis
   - Section entropy variations
   - Sliding window entropy
   - Compression ratios
   
2. Code Characteristics
   - Executable sections
   - Permission anomalies
   - Import patterns

3. Dynamic Indicators
   - API call patterns
   - Memory operations
   - System interactions

### Supporting Features (Medium Weight)
1. Resource Analysis
   - Resource entropy
   - Resource size distributions
   
2. Structural Analysis
   - Section alignment
   - Header characteristics
   
3. Statistical Patterns
   - Byte frequency
   - N-gram patterns

### Contextual Features (Low Weight)
1. File Metadata
   - Timestamps
   - Size relationships
   
2. Environmental Context
   - File location
   - System type

## False Positive Mitigation

### Whitelisting
1. Known Good Files
   - Signed system files
   - Common applications
   - Standard libraries

2. Patterns
   - Development tools
   - Compression utilities
   - Encrypted containers

### Exception Handling
1. High-entropy Benign Files
   - Media files
   - Compressed archives
   - Encrypted storage

2. Custom Applications
   - Internal tools
   - Custom packers
   - Security software

## Performance Targets

### Speed vs Accuracy
- Default: Balanced mode
- Fast mode: 2x speed, 95% accuracy
- Thorough mode: 0.5x speed, 99.9% accuracy

### Resource Usage
- CPU: < 30% single core
- Memory: < 200MB per scan
- Disk: < 100MB temp storage

## Monitoring and Maintenance

### Performance Metrics
- Track false positive/negative rates
- Monitor detection speed
- Resource usage patterns

### Model Updates
- Weekly validation
- Monthly retraining
- Quarterly feature updates

## Incident Response

### False Positive Handling
1. Immediate triage
2. Root cause analysis
3. Model adjustment
4. Pattern updates

### Detection Gaps
1. Sample collection
2. Feature extraction
3. Model retraining
4. Validation testing

## Compliance and Reporting

### Logging Requirements
- Detection events
- System performance
- Error conditions

### Audit Trail
- Model versions
- Configuration changes
- Detection patterns

## Version Control

### Document History
- v1.0: Initial policy
- v1.1: Added performance targets
- v1.2: Updated false positive handling

Last Updated: October 17, 2025