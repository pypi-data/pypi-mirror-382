# Automated Guardrail Validator

## Integration Point
- **When:** After each agent completion, before marking phase complete
- **Where:** Built into workflow orchestrator validation step
- **Scope:** All deliverable files in current phase output directory

## Auto-Fix Patterns

### Financial Violations
```
FIND: $[\d,]+-[\d,]+
REPLACE: Substantial investment `[AI estimation based on scope complexity]`

FIND: \$[\d,]+\+ annually
REPLACE: Significant annual value `[AI estimation based on operational efficiency]`

FIND: ROI of [\d]+%-[\d]+%
REPLACE: Strong ROI potential `[AI estimation based on efficiency gains]`

FIND: investment delivering [\d]+%-[\d]+% ROI
REPLACE: investment delivering strong ROI `[AI estimation based on automation value creation]`

FIND: \$[\d,]+ investment
REPLACE: Substantial investment `[AI estimation: enterprise automation program]`
```

### Performance Violations
```
FIND: [\d]+%-[\d]+% reduction in
REPLACE: Significant reduction in `[AI estimation based on process optimization]`

FIND: [\d]+%-[\d]+% improvement
REPLACE: Substantial improvement `[AI estimation based on automation potential]`

FIND: saves \$[\d,]+ annually
REPLACE: generates significant annual value `[AI estimation based on efficiency improvements]`

FIND: worth \$[\d,]+
REPLACE: with substantial value `[AI estimation based on strategic capability development]`
```

### Resource Violations
```
FIND: [\d]+-[\d]+ person-months
REPLACE: Estimated effort: \1-\2 person-months `[AI estimation based on implementation complexity]`

FIND: Investment: \$[\d,]+-[\d,]+
REPLACE: Investment: High `[AI estimation based on integration scope]`

FIND: costs \$[\d,]+
REPLACE: requires substantial investment `[AI estimation based on technical requirements]`
```

## Validation Algorithm

### Step 1: Pattern Detection
```python
def scan_violations(file_path):
    violations = {
        'dollar_amounts': regex.findall(r'\$[\d,]+(?:-[\d,]+)?(?!\s*`\[)', content),
        'untagged_percentages': regex.findall(r'[\d]+%-[\d]+%(?!\s*`\[)', content),
        'roi_claims': regex.findall(r'ROI of [\d]+%(?!\s*`\[)', content),
        'cost_savings': regex.findall(r'saves? \$[\d,]+(?!\s*`\[)', content)
    }
    return violations
```

### Step 2: Auto-Fix Application
```python
def apply_fixes(content, violations):
    fixes = {
        r'\$[\d,]+-[\d,]+(?!\s*`\[)': 'Substantial investment `[AI estimation based on scope complexity]`',
        r'\$[\d,]+\+ annually(?!\s*`\[)': 'Significant annual value `[AI estimation based on operational efficiency]`',
        r'ROI of [\d]+%-[\d]+%(?!\s*`\[)': 'Strong ROI potential `[AI estimation based on efficiency gains]`',
        r'[\d]+%-[\d]+% reduction(?!\s*`\[)': 'Significant reduction `[AI estimation based on process optimization]`',
        r'[\d]+%-[\d]+% improvement(?!\s*`\[)': 'Substantial improvement `[AI estimation based on automation potential]`',
        r'saves? \$[\d,]+ annually(?!\s*`\[)': 'generates significant annual value `[AI estimation based on efficiency improvements]`',
        r'worth \$[\d,]+(?!\s*`\[)': 'with substantial value `[AI estimation based on strategic capability development]`',
        r'Investment: \$[\d,]+-[\d,]+(?!\s*`\[)': 'Investment: Substantial `[AI estimation based on enterprise automation scope]`'
    }
    
    for pattern, replacement in fixes.items():
        content = regex.sub(pattern, replacement, content)
    
    return content
```

### Step 3: Validation Check
```python
def validate_compliance(content):
    remaining_violations = scan_violations(content)
    if any(remaining_violations.values()):
        return False, remaining_violations
    return True, None
```

## Orchestrator Integration

### Workflow Enhancement
```markdown
## After Agent [X] Completion

### Automatic Guardrail Validation
1. **Scan Phase Outputs:** Check all deliverable files for violations
2. **Apply Auto-Fixes:** Run pattern replacement on detected violations  
3. **Validate Compliance:** Verify all violations resolved
4. **Report Results:** Display fixes applied and final compliance status

### Phase Completion Gate
- ✅ **PASS:** No violations detected → Proceed to next phase
- 🔧 **FIXED:** Violations auto-corrected → Show fixes applied → Proceed  
- ❌ **BLOCK:** Violations remain after auto-fix → Manual intervention required

### Validation Display
```
🛡️ **Guardrail Validation - Agent [X] Complete**

📊 **Violations Detected:**
- Dollar amounts: 12 found → 12 fixed
- Untagged percentages: 8 found → 8 fixed  
- ROI claims: 3 found → 3 fixed

✅ **Auto-Fix Results:**
- "$600,000-750,000" → "Substantial investment `[AI estimation based on scope complexity]`"
- "ROI of 150-200%" → "Strong ROI potential `[AI estimation based on efficiency gains]`"
- "saves $50,000 annually" → "generates significant annual value `[AI estimation based on efficiency improvements]`"

🎯 **Final Status:** ✅ COMPLIANT - All violations resolved

**Ready to proceed to next phase.**
```

## Implementation Commands

### File Processing Function
```python
def validate_and_fix_phase(phase_directory):
    """
    Validates and fixes all deliverables in phase directory
    """
    deliverables = glob.glob(f"{phase_directory}/*.md")
    fixes_applied = []
    
    for file_path in deliverables:
        with open(file_path, 'r') as f:
            original_content = f.read()
        
        violations = scan_violations(original_content)
        if any(violations.values()):
            fixed_content = apply_fixes(original_content, violations)
            
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            
            fixes_applied.append({
                'file': file_path,
                'violations_fixed': sum(len(v) for v in violations.values())
            })
    
    return fixes_applied
```

## Success Criteria
- **Zero manual intervention** required for common violations
- **100% compliance** after auto-fix application  
- **Maintains content quality** while ensuring data integrity
- **Blocks workflow progression** only if auto-fix fails

This automated system prevents the manual cleanup burden while ensuring rigorous guardrail compliance across all solution space deliverables.
