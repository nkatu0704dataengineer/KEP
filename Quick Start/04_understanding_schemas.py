#!/usr/bin/env python3
"""
04_understanding_schemas.py - KEP Schema Deep Dive

This script provides a comprehensive guide to understanding and working
with KEP schemas - the heart of the extraction system.

Learn about:
- Classification schema structure and purpose
- Extraction schema design principles
- Few-shot vs zero-shot prompting
- Schema validation and best practices
- Real examples from different domains

Usage:
    python "04_understanding_schemas.py"
    python "04_understanding_schemas.py" --interactive    # Interactive examples
    python "04_understanding_schemas.py" --validate      # Validate existing schemas
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import json
import argparse
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)

def print_section(title):
    """Print section header"""
    print(f"\n{title}")
    print("-" * len(title))

def find_kep_root():
    """Find KEP root directory"""
    current_dir = Path.cwd()
    if current_dir.name == "Quick Start":
        return current_dir.parent
    return current_dir

def explain_schema_basics():
    """Explain fundamental schema concepts"""
    print_header("📋 Schema Fundamentals")
    
    print("""
KEP uses JSON-based schemas to define TWO critical operations:

1️⃣ CLASSIFICATION: Determine if text is relevant to your research
2️⃣ EXTRACTION: Pull structured data from relevant text

🎯 Why Two-Stage Process?
   • EFFICIENCY: Only process relevant content (saves time & cost)
   • ACCURACY: Classification filters noise before extraction
   • FLEXIBILITY: Different criteria for relevance vs extraction

📋 Schema Components:
   • PERSONA: Who is the AI assistant?
   • TASK: What exactly should it do?
   • INSTRUCTIONS: Specific rules and guidelines
   • SCHEMAS: Output structure definition
   • EXAMPLE: Training examples (for few-shot learning)
""")

def explain_classification_schemas():
    """Explain classification schema structure"""
    print_header("🏷️ Classification Schemas")
    
    print("""
Classification schemas determine what content is "relevant" vs "irrelevant"
for your specific research domain.

📋 Core Components:
""")
    
    # Example classification schema
    classification_example = {
        "PERSONA": "You are a materials science research assistant specializing in battery technology.",
        "TASK": "Classify paragraphs as containing information about battery materials or not.",
        "INSTRUCTIONS": [
            "Return one valid JSON object",
            "Field 'classification' must be exactly 'battery_related' or 'not_battery_related'",
            "Focus on materials, chemistries, performance metrics, and applications",
            "Include electrodes, electrolytes, separators, and battery systems"
        ],
        "SCHEMAS": {
            "classification": "battery_related or not_battery_related"
        },
        "EXAMPLE": [
            {
                "text": "Lithium iron phosphate (LiFePO4) demonstrates excellent thermal stability and cycling performance in lithium-ion batteries.",
                "classification": "battery_related"
            },
            {
                "text": "The weather forecast shows rain is expected throughout the week.",
                "classification": "not_battery_related"
            }
        ]
    }
    
    print("🔍 Example Classification Schema:")
    print(json.dumps(classification_example, indent=2))
    
    print("""
📋 Key Design Principles:

1️⃣ PERSONA: Establishes domain expertise
   ✅ Good: "Materials science research assistant specializing in..."
   ❌ Poor: "You are a helpful assistant"

2️⃣ TASK: Crystal clear classification goal
   ✅ Good: "Classify as containing battery materials information or not"
   ❌ Poor: "Analyze the text"

3️⃣ INSTRUCTIONS: Specific, actionable rules
   ✅ Good: "Include electrodes, electrolytes, separators"
   ❌ Poor: "Be accurate"

4️⃣ SCHEMAS: Exact output format
   ✅ Good: "battery_related or not_battery_related"
   ❌ Poor: "relevant or irrelevant" (too generic)

5️⃣ EXAMPLES: Diverse, high-quality training data
   ✅ Good: Multiple domains, edge cases, clear decisions
   ❌ Poor: Only obvious cases, no borderline examples
""")

def explain_extraction_schemas():
    """Explain extraction schema structure"""
    print_header("🏗️ Extraction Schemas")
    
    print("""
Extraction schemas define the structured JSON output you want from relevant text.
This is where you get your final research data!

📋 Core Components:
""")
    
    # Example extraction schema
    extraction_example = {
        "PERSONA": "You are a materials science information extraction specialist with expertise in battery technologies.",
        "TASK": "Extract structured information about battery materials, their properties, and performance metrics from scientific text.",
        "INSTRUCTIONS": [
            "Strict schema compliance required",
            "Return valid JSON only",
            "Use empty lists for missing information",
            "Extract specific numerical values with units when available",
            "Include material compositions and chemical formulas"
        ],
        "SCHEMAS": {
            "materials": ["List of material names or chemical formulas"],
            "material_type": "cathode, anode, electrolyte, separator, or other",
            "properties": ["List of material property descriptions"],
            "performance_metrics": {
                "capacity": "mAh/g or similar with units",
                "voltage": "V with units",
                "cycle_life": "number of cycles with retention info",
                "conductivity": "S/cm or similar with units"
            },
            "applications": ["List of application areas or battery types"],
            "synthesis_method": "Preparation or synthesis method if mentioned",
            "temperature_conditions": "Operating or testing temperature if specified"
        },
        "EXAMPLE": [
            {
                "text": "LiFePO4 cathode material synthesized by sol-gel method shows a specific capacity of 160 mAh/g with 3.2V operating voltage and maintains 95% capacity retention after 2000 cycles at room temperature in lithium-ion batteries.",
                "output": {
                    "materials": ["LiFePO4", "lithium iron phosphate"],
                    "material_type": "cathode",
                    "properties": ["high capacity retention", "stable voltage platform"],
                    "performance_metrics": {
                        "capacity": "160 mAh/g",
                        "voltage": "3.2 V",
                        "cycle_life": "2000 cycles with 95% retention",
                        "conductivity": ""
                    },
                    "applications": ["lithium-ion batteries"],
                    "synthesis_method": "sol-gel method",
                    "temperature_conditions": "room temperature"
                }
            }
        ]
    }
    
    print("🔍 Example Extraction Schema:")
    print(json.dumps(extraction_example, indent=2))
    
    print("""
📋 Schema Design Best Practices:

1️⃣ HIERARCHICAL STRUCTURE: Organize related data
   ✅ Good: Group performance metrics together
   ❌ Poor: Flat list of unrelated fields

2️⃣ CLEAR FIELD NAMES: Self-documenting structure
   ✅ Good: "synthesis_method", "performance_metrics"
   ❌ Poor: "method", "data", "info"

3️⃣ TYPE SPECIFICATIONS: Define expected data types
   ✅ Good: ["List of strings"], "Single string", {"key": "value"}
   ❌ Poor: Ambiguous field definitions

4️⃣ UNIT REQUIREMENTS: Specify units for numerical data
   ✅ Good: "mAh/g with units", "V with units"
   ❌ Poor: Just "capacity", "voltage"

5️⃣ FALLBACK HANDLING: Account for missing data
   ✅ Good: "Use empty lists for missing information"
   ❌ Poor: No guidance on missing data
""")

def explain_few_shot_vs_zero_shot():
    """Explain the difference between few-shot and zero-shot modes"""
    print_header("🎯 Few-Shot vs Zero-Shot Learning")
    
    print("""
KEP supports two prompting modes that dramatically affect accuracy:

🎯 ZERO-SHOT MODE:
   • Uses only PERSONA, TASK, INSTRUCTIONS, and SCHEMAS
   • NO examples provided to the LLM
   • Faster execution (fewer tokens)
   • Lower accuracy, especially for complex domains
   • Good for: Simple, well-defined tasks

⭐ FEW-SHOT MODE:
   • Includes EXAMPLE array with training data
   • LLM learns from your specific examples
   • Higher accuracy, especially for nuanced tasks
   • More tokens used (higher cost)
   • REQUIRED for complex domain-specific extraction

📊 Performance Comparison:
""")
    
    comparison_table = """
┌─────────────────┬─────────────┬─────────────┐
│ Aspect          │ Zero-Shot   │ Few-Shot    │
├─────────────────┼─────────────┼─────────────┤
│ Accuracy        │ 60-75%      │ 85-95%      │
│ Speed           │ Fast        │ Moderate    │
│ Cost            │ Low         │ Higher      │
│ Setup Effort    │ Minimal     │ High        │
│ Domain Adapt.   │ Poor        │ Excellent   │
│ Consistency     │ Variable    │ High        │
└─────────────────┴─────────────┴─────────────┘
"""
    print(comparison_table)
    
    print("""
🎯 When to Use Each Mode:

ZERO-SHOT: Use when...
   ✅ Task is simple and well-defined
   ✅ Domain is general (not highly specialized)
   ✅ Speed/cost is more important than accuracy
   ✅ You're prototyping or testing

FEW-SHOT: Use when...
   ⭐ Domain is specialized (materials, medicine, etc.)
   ⭐ High accuracy is critical
   ⭐ You have time to create quality examples
   ⭐ Production/research use

💡 Pro Tip: Start with zero-shot for prototyping, then upgrade to
   few-shot with quality examples for production use.
""")

def analyze_existing_schemas():
    """Analyze schemas in the KEP installation"""
    print_header("🔍 Existing Schema Analysis")
    
    kep_root = find_kep_root()
    schemas_dir = kep_root / "schemas"
    
    if not schemas_dir.exists():
        print("❌ No schemas directory found")
        return
    
    schema_files = list(schemas_dir.glob("*.json"))
    if not schema_files:
        print("❌ No schema files found")
        return
    
    print(f"Found {len(schema_files)} schema files:\n")
    
    for schema_file in schema_files:
        print(f"📋 {schema_file.name}")
        print("─" * (len(schema_file.name) + 2))
        
        try:
            with open(schema_file, 'r') as f:
                schema = json.load(f)
            
            # Analyze schema structure
            components = []
            if 'PERSONA' in schema:
                components.append("PERSONA")
            if 'TASK' in schema:
                components.append("TASK")
            if 'INSTRUCTIONS' in schema:
                components.append(f"INSTRUCTIONS ({len(schema['INSTRUCTIONS'])} items)")
            if 'SCHEMAS' in schema:
                components.append("SCHEMAS")
            
            # Check for examples
            examples = schema.get('EXAMPLE', schema.get('examples', []))
            if examples:
                components.append(f"EXAMPLES ({len(examples)} items)")
                mode = "Few-shot ready ⭐"
            else:
                mode = "Zero-shot only"
            
            print(f"   Components: {', '.join(components)}")
            print(f"   Mode: {mode}")
            
            # Analyze schema type
            if 'classification' in str(schema).lower():
                schema_type = "Classification"
            else:
                schema_type = "Extraction"
            print(f"   Type: {schema_type}")
            
            # Show PERSONA snippet
            if 'PERSONA' in schema:
                persona = schema['PERSONA'][:80] + "..." if len(schema['PERSONA']) > 80 else schema['PERSONA']
                print(f"   Domain: {persona}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error reading schema: {e}")
            print()

def validate_schema_structure(schema_path):
    """Validate a schema file structure"""
    print(f"\n🔍 Validating: {schema_path.name}")
    print("─" * (len(schema_path.name) + 13))
    
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
    except Exception as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    issues = []
    warnings = []
    
    # Required components
    required_fields = ['PERSONA', 'TASK', 'INSTRUCTIONS', 'SCHEMAS']
    for field in required_fields:
        if field not in schema:
            issues.append(f"Missing required field: {field}")
        elif not schema[field]:
            issues.append(f"Empty field: {field}")
    
    # PERSONA validation
    if 'PERSONA' in schema:
        persona = schema['PERSONA']
        if len(persona) < 20:
            warnings.append("PERSONA is very short - consider adding more context")
        if "assistant" not in persona.lower():
            warnings.append("PERSONA should establish the AI as an assistant")
    
    # INSTRUCTIONS validation
    if 'INSTRUCTIONS' in schema:
        instructions = schema['INSTRUCTIONS']
        if not isinstance(instructions, list):
            issues.append("INSTRUCTIONS should be a list")
        elif len(instructions) < 2:
            warnings.append("Consider adding more detailed instructions")
    
    # Examples validation
    examples = schema.get('EXAMPLE', schema.get('examples', []))
    if examples:
        if len(examples) < 2:
            warnings.append("Few-shot works better with 3+ examples")
        
        # Check example structure
        for i, example in enumerate(examples):
            if 'text' not in example:
                issues.append(f"Example {i+1} missing 'text' field")
            if 'classification' not in example and 'output' not in example:
                issues.append(f"Example {i+1} missing output field")
    else:
        warnings.append("No examples found - will run in zero-shot mode")
    
    # Print results
    if not issues and not warnings:
        print("✅ Schema validation passed - excellent structure!")
    else:
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"   • {issue}")
        
        if warnings:
            print("⚠️ Suggestions for improvement:")
            for warning in warnings:
                print(f"   • {warning}")
    
    return len(issues) == 0

def interactive_schema_builder():
    """Interactive schema building guide"""
    print_header("🛠️ Interactive Schema Builder")
    
    print("""
Let's build a schema together! I'll guide you through the process.

First, what type of schema do you want to create?
""")
    
    schema_type = input("Enter 'c' for Classification or 'e' for Extraction: ").lower()
    
    if schema_type not in ['c', 'e']:
        print("Invalid choice. Please run again and enter 'c' or 'e'.")
        return
    
    print(f"\n{'Classification' if schema_type == 'c' else 'Extraction'} Schema Builder")
    print("=" * 50)
    
    # Collect basic information
    domain = input("\nWhat research domain? (e.g., 'battery materials', 'drug discovery'): ")
    
    if schema_type == 'c':
        relevant_criteria = input("What makes text relevant to your research? ")
        categories = input("What are your classification categories? (e.g., 'relevant, irrelevant'): ")
    else:
        data_types = input("What data do you want to extract? (e.g., 'materials, properties, performance'): ")
    
    # Generate schema template
    if schema_type == 'c':
        schema_template = {
            "PERSONA": f"You are a research assistant specializing in {domain}.",
            "TASK": f"Classify paragraphs as containing information about {relevant_criteria} or not.",
            "INSTRUCTIONS": [
                "Return one valid JSON object",
                f"Field 'classification' must be exactly one of: {categories}",
                "Be consistent and accurate in your classifications",
                "Consider the research context when making decisions"
            ],
            "SCHEMAS": {
                "classification": categories
            },
            "EXAMPLE": [
                {
                    "text": "[Add example relevant text here]",
                    "classification": "[First category]"
                },
                {
                    "text": "[Add example irrelevant text here]",
                    "classification": "[Second category]"
                }
            ]
        }
    else:
        schema_template = {
            "PERSONA": f"You are an information extraction specialist with expertise in {domain}.",
            "TASK": f"Extract structured information about {data_types} from scientific text.",
            "INSTRUCTIONS": [
                "Strict schema compliance required",
                "Return valid JSON only",
                "Use empty lists for missing information",
                "Extract specific values with units when available"
            ],
            "SCHEMAS": {
                # This would be customized based on data_types
                "extracted_data": f"Structure for {data_types}"
            },
            "EXAMPLE": [
                {
                    "text": "[Add example text here]",
                    "output": {
                        "extracted_data": "[Example extracted data]"
                    }
                }
            ]
        }
    
    print(f"\n📋 Generated Schema Template:")
    print(json.dumps(schema_template, indent=2))
    
    save_choice = input(f"\nSave this template? (y/n): ").lower()
    if save_choice == 'y':
        filename = input("Enter filename (without .json): ")
        kep_root = find_kep_root()
        schemas_dir = kep_root / "schemas"
        schemas_dir.mkdir(exist_ok=True)
        
        output_path = schemas_dir / f"{filename}.json"
        with open(output_path, 'w') as f:
            json.dump(schema_template, f, indent=2)
        
        print(f"✅ Schema saved to: {output_path}")
        print(f"💡 Edit the file to add real examples and refine the structure")

def main():
    """Main schema education function"""
    parser = argparse.ArgumentParser(description='KEP Schema Understanding')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive schema builder')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='Validate existing schemas')
    
    args = parser.parse_args()
    
    print("📋 KEP Schema Deep Dive")
    print("Understanding the heart of the extraction system...")
    
    if args.interactive:
        interactive_schema_builder()
        return
    
    if args.validate:
        print_header("✅ Schema Validation")
        kep_root = find_kep_root()
        schemas_dir = kep_root / "schemas"
        
        if schemas_dir.exists():
            schema_files = list(schemas_dir.glob("*.json"))
            if schema_files:
                all_valid = True
                for schema_file in schema_files:
                    is_valid = validate_schema_structure(schema_file)
                    if not is_valid:
                        all_valid = False
                
                if all_valid:
                    print(f"\n🎉 All {len(schema_files)} schemas are valid!")
                else:
                    print(f"\n⚠️ Some schemas need improvement")
            else:
                print("No schema files found to validate")
        else:
            print("No schemas directory found")
        return
    
    # Default: educational content
    explain_schema_basics()
    explain_classification_schemas()
    explain_extraction_schemas()
    explain_few_shot_vs_zero_shot()
    analyze_existing_schemas()
    
    print_header("🎯 Key Takeaways")
    print("""
🎯 Schema Success Formula:

1️⃣ DOMAIN EXPERTISE: Establish clear domain knowledge in PERSONA
2️⃣ CRYSTAL CLEAR TASK: Specify exactly what you want
3️⃣ DETAILED INSTRUCTIONS: Leave no ambiguity
4️⃣ STRUCTURED OUTPUT: Design schemas that match your research needs
5️⃣ QUALITY EXAMPLES: Invest time in diverse, high-quality training data

💡 Remember: Schemas are the foundation of extraction quality.
   Spend time getting them right - everything else builds on this!

🚀 Next Steps:
   • Examine existing schemas in detail
   • Try the interactive builder: --interactive
   • Validate your schemas: --validate
   • Create domain-specific schemas for your research
   
📋 Coming Next: python "05_pipeline_demo.py"
""")

if __name__ == "__main__":
    main()