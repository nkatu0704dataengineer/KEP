#!/usr/bin/env python3
"""
06_results_explorer.py - KEP Results Analysis & Exploration

This script helps you understand and analyze KEP pipeline outputs,
providing insights into the extraction process and results quality.

Features:
- Interactive results browser
- Statistical analysis of extractions
- Quality assessment and validation
- Export capabilities for further analysis
- Visualization of processing workflow

Usage:
    python "06_results_explorer.py"                    # Interactive explorer
    python "06_results_explorer.py" --run demo         # Explore specific run
    python "06_results_explorer.py" --stats            # Statistical summary
    python "06_results_explorer.py" --export csv       # Export results
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import json
import csv
from pathlib import Path
import argparse
from collections import Counter, defaultdict
from datetime import datetime

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

def discover_pipeline_runs():
    """Discover available pipeline runs"""
    kep_root = find_kep_root()
    runs_dir = kep_root / "runs"
    
    if not runs_dir.exists():
        return []
    
    runs = []
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir():
            # Check directly in run dir AND in extraction/classification subdirs
            essential_files = [
                run_dir / 'structured.json',
                run_dir / 'classified_relevant.json',
                run_dir / 'extraction' / 'structured.json',
                run_dir / 'classification' / 'classified_relevant.json',
            ]
            if any(f.exists() for f in essential_files):
                mtime = run_dir.stat().st_mtime
                runs.append({
                    'name': run_dir.name,
                    'path': run_dir,
                    'mtime': mtime,
                    'date': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                })
    
    # Sort by modification time (newest first)
    runs.sort(key=lambda x: x['mtime'], reverse=True)
    return runs

def select_run_interactively():
    """Let user select a pipeline run interactively"""
    runs = discover_pipeline_runs()
    
    if not runs:
        print("❌ No pipeline runs found")
        print("💡 Run the pipeline first: python \"05_pipeline_demo.py\"")
        return None
    
    print("📁 Available Pipeline Runs:")
    print()
    for i, run in enumerate(runs):
        print(f"   {i+1}. {run['name']} ({run['date']})")
    
    while True:
        try:
            choice = input(f"\nSelect run (1-{len(runs)}): ").strip()
            if not choice:
                return runs[0]['path']  # Default to most recent
            
            idx = int(choice) - 1
            if 0 <= idx < len(runs):
                return runs[idx]['path']
            else:
                print(f"Invalid choice. Enter 1-{len(runs)}")
        except ValueError:
            print("Invalid input. Enter a number.")
        except KeyboardInterrupt:
            return None

def load_run_data(run_path):
    """Load all data from a pipeline run"""
    data = {}
    
    def resolve(candidates):
        """Return first existing path from a list of candidates."""
        for p in candidates:
            if (run_path / p).exists():
                return run_path / p
        return None

    # Define files to load, checking both flat and subdirectory layouts
    files_to_load = {
        'all_paragraphs':      resolve(['ingest/all_paragraphs.json', 'all_paragraphs.json']),
        'classified_full':     resolve(['classification/classified_full.json', 'classified_full.json']),
        'classified_relevant': resolve(['classification/classified_relevant.json', 'classified_relevant.json']),
        'structured':          resolve(['extraction/structured.json', 'structured.json']),
        'general_metadata':    resolve(['general_metadata.json']),
        'llm_metadata':        resolve(['llm_metadata.json']),
    }
    
    for key, full_path in files_to_load.items():
        if full_path and full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data[key] = json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load {full_path.name}: {e}")
                data[key] = None
        else:
            data[key] = None
    
    return data

def analyze_run_overview(run_path, data):
    """Provide high-level overview of the run"""
    print_header(f"📊 Run Overview: {run_path.name}")
    
    # Basic statistics
    all_paragraphs = data.get('all_paragraphs', []) or []
    classified_full = data.get('classified_full', []) or []
    classified_relevant = data.get('classified_relevant', []) or []
    structured = data.get('structured', []) or []
    
    print("📈 Processing Statistics:")
    print(f"   • Total paragraphs extracted: {len(all_paragraphs)}")
    print(f"   • Paragraphs classified: {len(classified_full)}")
    print(f"   • Relevant paragraphs: {len(classified_relevant)}")
    print(f"   • Structured extractions: {len(structured)}")
    
    # Calculate ratios
    if len(classified_full) > 0:
        relevance_ratio = len(classified_relevant) / len(classified_full) * 100
        print(f"   • Relevance ratio: {relevance_ratio:.1f}%")
    
    if len(classified_relevant) > 0:
        extraction_ratio = len(structured) / len(classified_relevant) * 100
        print(f"   • Extraction success ratio: {extraction_ratio:.1f}%")
    
    # Metadata information
    general_meta = data.get('general_metadata', {}) or {}
    llm_meta = data.get('llm_metadata', {}) or {}
    
    if llm_meta:
        print(f"\n🤖 Model Information:")
        print(f"   • Provider: {llm_meta.get('provider', 'Unknown')}")
        print(f"   • Model: {llm_meta.get('model', 'Unknown')}")
        print(f"   • Prompt mode: {llm_meta.get('prompt_mode', 'Unknown')}")
        
        cls_examples = llm_meta.get('cls_example_count', 0)
        ext_examples = llm_meta.get('ext_example_count', 0)
        print(f"   • Classification examples: {cls_examples}")
        print(f"   • Extraction examples: {ext_examples}")
    
    # Timeline information
    if general_meta:
        print(f"\n⏱️ Processing Timeline:")
        for key, value in general_meta.items():
            if 'time' in key.lower() or 'duration' in key.lower():
                print(f"   • {key}: {value}")

def analyze_classification_results(data):
    """Analyze classification step results"""
    print_header("🏷️ Classification Analysis")
    
    classified_full = data.get('classified_full', []) or []
    
    if not classified_full:
        print("❌ No classification data found")
        return
    
    # Count classifications
    classifications = [item.get('classification', 'unknown') for item in classified_full]
    class_counts = Counter(classifications)
    
    print("📊 Classification Distribution:")
    total = len(classifications)
    for classification, count in class_counts.most_common():
        percentage = count / total * 100
        print(f"   • {classification}: {count} ({percentage:.1f}%)")
    
    # Analyze classification confidence (if available)
    confidences = []
    for item in classified_full:
        if 'confidence' in item:
            confidences.append(item['confidence'])
    
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        print(f"\n🎯 Average classification confidence: {avg_confidence:.2f}")
    
    # Show examples of each classification
    print(f"\n📝 Classification Examples:")
    for classification in class_counts.keys():
        examples = [item for item in classified_full 
                   if item.get('classification') == classification]
        if examples:
            example = examples[0]
            text = example.get('text', '')[:100] + "..."
            print(f"\n   {classification.upper()}:")
            print(f"   \"{text}\"")

def analyze_extraction_results(data):
    """Analyze extraction step results"""
    print_header("🏗️ Extraction Analysis")
    
    structured = data.get('structured', []) or []
    
    if not structured:
        print("❌ No extraction data found")
        return
    
    print(f"📊 Extraction Statistics:")
    print(f"   • Total extractions: {len(structured)}")
    
    # Analyze extracted fields
    if structured and isinstance(structured[0], dict):
        all_fields = set()
        field_usage = defaultdict(int)
        field_types = defaultdict(set)
        
        for item in structured:
            if isinstance(item, dict):
                for key, value in item.items():
                    all_fields.add(key)
                    if value:  # Non-empty value
                        field_usage[key] += 1
                        field_types[key].add(type(value).__name__)
        
        print(f"\n📋 Extracted Fields:")
        for field in sorted(all_fields):
            usage_count = field_usage[field]
            usage_percent = usage_count / len(structured) * 100
            types = ', '.join(field_types[field])
            print(f"   • {field}: {usage_count}/{len(structured)} ({usage_percent:.1f}%) - {types}")
        
        # Show example extraction
        print(f"\n📝 Example Extraction:")
        example = structured[0]
        print(json.dumps(example, indent=4))
    
    # Analyze extraction quality
    empty_extractions = 0
    for item in structured:
        if isinstance(item, dict):
            # Check if extraction has meaningful content
            has_content = any(value for value in item.values() 
                             if value and value != [] and value != "")
            if not has_content:
                empty_extractions += 1
    
    if empty_extractions > 0:
        empty_percent = empty_extractions / len(structured) * 100
        print(f"\n⚠️ Quality Concerns:")
        print(f"   • Empty extractions: {empty_extractions} ({empty_percent:.1f}%)")

def explore_individual_extractions(data):
    """Allow interactive exploration of individual extractions"""
    print_header("🔍 Individual Extraction Explorer")
    
    classified_relevant = data.get('classified_relevant', []) or []
    structured = data.get('structured', []) or []
    
    if not classified_relevant or not structured:
        print("❌ No data available for exploration")
        return
    
    print(f"Found {len(structured)} extractions to explore")
    
    while True:
        try:
            choice = input(f"\nEnter extraction number (1-{len(structured)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                break
            
            idx = int(choice) - 1
            if 0 <= idx < len(structured):
                print(f"\n🔍 Extraction #{idx + 1}")
                print("=" * 30)
                
                # Show source text (if available)
                if idx < len(classified_relevant):
                    source_text = classified_relevant[idx].get('text', 'No source text')
                    print(f"📄 Source Text:")
                    print(f'   "{source_text}"')
                
                # Show extracted data
                extracted = structured[idx]
                print(f"\n🏗️ Extracted Data:")
                print(json.dumps(extracted, indent=4))
                
                input("\nPress Enter to continue...")
            else:
                print(f"Invalid number. Enter 1-{len(structured)}")
                
        except ValueError:
            print("Invalid input. Enter a number or 'q'")
        except KeyboardInterrupt:
            break

def export_results(run_path, data, format='csv'):
    """Export results in various formats"""
    print_header(f"📤 Export Results ({format.upper()})")
    
    structured = data.get('structured', []) or []
    
    if not structured:
        print("❌ No structured data to export")
        return
    
    # Generate export filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"kep_export_{run_path.name}_{timestamp}.{format}"
    export_path = run_path / filename
    
    try:
        if format.lower() == 'csv':
            # Flatten structured data for CSV
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                if structured:
                    # Get all possible field names
                    all_fields = set()
                    for item in structured:
                        if isinstance(item, dict):
                            all_fields.update(item.keys())
                    
                    fieldnames = sorted(all_fields)
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for item in structured:
                        if isinstance(item, dict):
                            # Flatten nested structures
                            flattened = {}
                            for key, value in item.items():
                                if isinstance(value, (list, dict)):
                                    flattened[key] = json.dumps(value)
                                else:
                                    flattened[key] = str(value) if value is not None else ""
                            writer.writerow(flattened)
        
        elif format.lower() == 'json':
            # Export as formatted JSON
            with open(export_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(structured, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✅ Results exported to: {export_path}")
        print(f"📊 Exported {len(structured)} records")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

def generate_quality_report(data):
    """Generate a quality assessment report"""
    print_header("📊 Quality Assessment Report")
    
    all_paragraphs = data.get('all_paragraphs', []) or []
    classified_full = data.get('classified_full', []) or []
    classified_relevant = data.get('classified_relevant', []) or []
    structured = data.get('structured', []) or []
    
    quality_scores = []
    
    # Data completeness
    completeness_score = 0
    if all_paragraphs and classified_full:
        completeness_score = min(len(classified_full) / len(all_paragraphs), 1.0) * 100
    quality_scores.append(("Data Completeness", completeness_score))
    
    # Classification ratio (moderate is good)
    classification_score = 0
    if classified_full:
        relevance_ratio = len(classified_relevant) / len(classified_full)
        # Optimal range is 10-50% relevant
        if 0.1 <= relevance_ratio <= 0.5:
            classification_score = 100
        elif relevance_ratio < 0.1:
            classification_score = relevance_ratio * 1000  # Scale up low ratios
        else:
            classification_score = 100 - (relevance_ratio - 0.5) * 100
        classification_score = max(0, min(100, classification_score))
    quality_scores.append(("Classification Quality", classification_score))
    
    # Extraction success rate
    extraction_score = 0
    if classified_relevant and structured:
        extraction_score = min(len(structured) / len(classified_relevant), 1.0) * 100
    quality_scores.append(("Extraction Success", extraction_score))
    
    # Data richness (non-empty extractions)
    richness_score = 0
    if structured:
        non_empty = 0
        for item in structured:
            if isinstance(item, dict):
                has_content = any(value for value in item.values() 
                                 if value and value != [] and value != "")
                if has_content:
                    non_empty += 1
        richness_score = (non_empty / len(structured)) * 100
    quality_scores.append(("Data Richness", richness_score))
    
    # Display quality scores
    print("🎯 Quality Metrics:")
    overall_score = 0
    for metric, score in quality_scores:
        status = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        print(f"   {status} {metric}: {score:.1f}%")
        overall_score += score
    
    overall_score /= len(quality_scores)
    print(f"\n📊 Overall Quality Score: {overall_score:.1f}%")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if overall_score >= 85:
        print("   🎉 Excellent results! Your pipeline is working very well.")
    elif overall_score >= 70:
        print("   ✅ Good results with room for improvement.")
    else:
        print("   ⚠️ Results need attention. Consider:")
    
    if completeness_score < 80:
        print("   • Check for errors in classification step")
    if classification_score < 60:
        print("   • Review classification schema and examples")
        print("   • Consider adjusting relevance criteria")
    if extraction_score < 80:
        print("   • Review extraction schema complexity")
        print("   • Add more examples for few-shot learning")
    if richness_score < 70:
        print("   • Improve extraction schema specificity")
        print("   • Add better examples with rich content")

def main():
    """Main results exploration function"""
    parser = argparse.ArgumentParser(description='KEP Results Explorer')
    parser.add_argument('--run', help='Specific run to analyze')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistical summary only')
    parser.add_argument('--export', choices=['csv', 'json'],
                       help='Export results in specified format')
    
    args = parser.parse_args()
    
    print("🔍 KEP Results Explorer")
    print("Analyze and understand your pipeline outputs...")
    
    # Discover or select run
    if args.run:
        kep_root = find_kep_root()
        run_path = kep_root / "runs" / args.run
        if not run_path.exists():
            print(f"❌ Run '{args.run}' not found")
            return False
    else:
        run_path = select_run_interactively()
        if not run_path:
            return False
    
    print(f"\n📁 Analyzing run: {run_path.name}")
    
    # Load data
    data = load_run_data(run_path)
    
    # Provide overview
    analyze_run_overview(run_path, data)
    
    if args.stats:
        # Stats only mode
        analyze_classification_results(data)
        analyze_extraction_results(data)
        generate_quality_report(data)
        return True
    
    if args.export:
        # Export mode
        export_results(run_path, data, args.export)
        return True
    
    # Interactive mode
    while True:
        print(f"\n🔍 Exploration Options:")
        print("   1. Classification analysis")
        print("   2. Extraction analysis")
        print("   3. Individual extraction explorer")
        print("   4. Quality assessment report")
        print("   5. Export results (CSV)")
        print("   6. Export results (JSON)")
        print("   q. Quit")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == '1':
            analyze_classification_results(data)
        elif choice == '2':
            analyze_extraction_results(data)
        elif choice == '3':
            explore_individual_extractions(data)
        elif choice == '4':
            generate_quality_report(data)
        elif choice == '5':
            export_results(run_path, data, 'csv')
        elif choice == '6':
            export_results(run_path, data, 'json')
        else:
            print("Invalid option. Please try again.")
    
    print(f"\n📊 Analysis complete!")
    print(f"Results available in: {run_path}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)