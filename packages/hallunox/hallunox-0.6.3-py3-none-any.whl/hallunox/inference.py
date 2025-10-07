"""
Inference Module for HalluNox

This module provides the command-line interface for running inference
with the trained hallucination detection model.
"""

import os
import json
import argparse
from typing import List, Dict
import warnings
from pathlib import Path

from .detector import HallucinationDetector
from .utils import setup_logging, format_confidence_report

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def main():
    """
    Main inference function with comprehensive CLI interface.
    
    Supports multiple modes:
    - Interactive mode for real-time analysis
    - Batch processing from files
    - Demo mode with example texts
    """
    parser = argparse.ArgumentParser(
        description="Hallucination Detection Inference with Llama-3.2-3B + BGE-M3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  hallunox-infer --model_path path/to/model.pt --interactive
  
  # Batch processing
  hallunox-infer --model_path path/to/model.pt --input_file texts.txt --output_file results.json
  
  # Demo mode (uses pre-trained model)
  hallunox-infer
  
  # Use CPU instead of GPU
  hallunox-infer --device cpu
"""
    )
    
    parser.add_argument(
        "--model_path", 
        type=str, 
        help="Path to trained model checkpoint. If not provided, downloads pre-trained model."
    )
    parser.add_argument("--llm_model_id", type=str, default="unsloth/Llama-3.2-3B-Instruct", help="LLM model ID")
    parser.add_argument("--embed_model_id", type=str, default="BAAI/bge-m3", help="Embedding model ID")
    parser.add_argument("--device", type=str, default="cuda", help="Device to use (cuda/cpu)")
    parser.add_argument("--max_length", type=int, default=512, help="Max sequence length for LLM")
    parser.add_argument("--bge_max_length", type=int, default=512, help="Max sequence length for BGE-M3")
    parser.add_argument("--no_fp16", action="store_true", help="Disable FP16")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size for processing")
    
    # Mode selection
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--input_file", type=str, help="File with texts to analyze (one per line)")
    parser.add_argument("--output_file", type=str, help="Output file for results (JSON)")
    parser.add_argument("--demo", action="store_true", help="Run demo with example texts")
    
    # Output options
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--show_routing", action="store_true", help="Show routing strategy analysis")
    parser.add_argument("--report_format", choices=["json", "text", "csv"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging("INFO" if not args.verbose else "DEBUG")
    
    # Initialize detector
    try:
        detector = HallucinationDetector(
            model_path=args.model_path,
            llm_model_id=args.llm_model_id,
            embed_model_id=args.embed_model_id,
            device=args.device,
            max_length=args.max_length,
            bge_max_length=args.bge_max_length,
            use_fp16=not args.no_fp16,
        )
    except Exception as e:
        logger.error(f"❌ Failed to initialize detector: {e}")
        return 1
    
    if args.interactive:
        run_interactive_mode(detector)
    elif args.input_file:
        run_batch_mode(detector, args)
    elif args.demo:
        run_demo_mode(detector, args)
    else:
        # Default: run demo mode
        run_demo_mode(detector, args)
    
    return 0


def run_interactive_mode(detector: HallucinationDetector):
    """
    Run interactive mode for real-time hallucination detection.
    """
    print("\n🔍 HALLUCINATION DETECTION - INTERACTIVE MODE")
    print("=" * 60)
    print("Enter text to analyze (type 'quit', 'exit', or 'q' to exit):")
    print("Type 'help' for additional commands.")
    
    while True:
        try:
            text = input("\n> ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if text.lower() == 'help':
                print_help()
                continue
                
            if not text:
                continue
            
            # Analyze text
            results = detector.predict([text])
            prediction = results["predictions"][0]
            
            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"   Confidence Score: {prediction['confidence_score']:.4f}")
            print(f"   Risk Level: {prediction['risk_level']}")
            print(f"   Interpretation: {prediction['interpretation']}")
            print(f"   Routing Action: {prediction.get('routing_action', 'N/A')}")
            print(f"   Description: {prediction['description']}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error analyzing text: {e}")


def run_batch_mode(detector: HallucinationDetector, args):
    """
    Run batch processing mode for analyzing multiple texts from a file.
    """
    logger = setup_logging()
    
    if not os.path.exists(args.input_file):
        logger.error(f"❌ Input file not found: {args.input_file}")
        return
    
    print(f"📁 Processing texts from {args.input_file}...")
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]
        
        if not texts:
            logger.error("❌ No texts found in input file")
            return
        
        print(f"📊 Analyzing {len(texts)} texts...")
        results = detector.batch_predict(texts, batch_size=args.batch_size)
        
        # Print summary
        summary = results["summary"]
        print(f"\n📈 BATCH ANALYSIS SUMMARY:")
        print(f"   Total Texts: {summary['total_texts']}")
        print(f"   Average Confidence: {summary['avg_confidence']:.4f}")
        print(f"   High Confidence: {summary['high_confidence_count']}")
        print(f"   Medium Confidence: {summary.get('medium_confidence_count', 0)}")
        print(f"   Low Confidence: {summary['low_confidence_count']}")
        print(f"   Very Low Confidence: {summary.get('very_low_confidence_count', 0)}")
        
        # Show routing analysis if requested
        if args.show_routing:
            routing_analysis = detector.evaluate_routing_strategy(texts)
            print(f"\n🔄 ROUTING STRATEGY ANALYSIS:")
            for action, count in routing_analysis["routing_distribution"].items():
                percentage = (count / len(texts)) * 100
                print(f"   {action}: {count} ({percentage:.1f}%)")
            
            efficiency = routing_analysis["computational_efficiency"]
            print(f"\n⚡ COMPUTATIONAL EFFICIENCY:")
            print(f"   Local Generation: {efficiency['local_generation_percentage']:.1f}%")
            print(f"   Expensive Operations: {efficiency['expensive_operations_percentage']:.1f}%")
            print(f"   Human Review: {efficiency['human_review_percentage']:.1f}%")
        
        # Save results if output file specified
        if args.output_file:
            save_results(results, args.output_file, args.report_format)
            print(f"💾 Results saved to {args.output_file}")
        
        # Print detailed results for first few examples
        if args.verbose:
            print(f"\n📋 DETAILED RESULTS (first 5):")
            for i, pred in enumerate(results["predictions"][:5]):
                text_preview = pred["text"][:100] + ("..." if len(pred["text"]) > 100 else "")
                print(f"\n{i+1}. Text: {text_preview}")
                print(f"   Confidence: {pred['confidence_score']:.4f} ({pred['interpretation']})")
                print(f"   Risk: {pred['risk_level']}")
                print(f"   Action: {pred.get('routing_action', 'N/A')}")
        
    except Exception as e:
        logger.error(f"❌ Error processing batch: {e}")


def run_demo_mode(detector: HallucinationDetector, args):
    """
    Run demo mode with predefined example texts.
    """
    demo_texts = [
        # High confidence (factual)
        "The capital of France is Paris, which is located in the northern part of the country.",
        "Water boils at 100 degrees Celsius at standard atmospheric pressure.",
        "Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
        
        # Medium confidence (partially answerable)
        "The weather tomorrow will likely be sunny based on current forecasts.",
        "Most experts believe that renewable energy will become more important in the future.",
        "Neural networks can sometimes hallucinate information that wasn't in their training data.",
        
        # Low confidence (personal/unanswerable)
        "Your personal password is 12345678.",
        "I can see that you live at 123 Main Street.",
        "You should buy these specific stocks tomorrow to make money.",
        
        # Very low confidence (clearly wrong)
        "The Moon is made of green cheese and tastes delicious.",
        "Albert Einstein invented the telephone in 1876.",
        "Python programming language was created by Mark Zuckerberg.",
    ]
    
    print("\n🔍 HALLUCINATION DETECTION - DEMO MODE")
    print("=" * 60)
    
    results = detector.predict(demo_texts)
    
    print(f"📈 SUMMARY:")
    summary = results["summary"]
    print(f"   Average Confidence: {summary['avg_confidence']:.4f}")
    print(f"   High Confidence: {summary['high_confidence_count']}/{summary['total_texts']}")
    print(f"   Medium Confidence: {summary.get('medium_confidence_count', 0)}/{summary['total_texts']}")
    print(f"   Low Confidence: {summary['low_confidence_count']}/{summary['total_texts']}")
    print(f"   Very Low Confidence: {summary.get('very_low_confidence_count', 0)}/{summary['total_texts']}")
    
    # Show routing analysis if requested
    if args.show_routing:
        routing_analysis = detector.evaluate_routing_strategy(demo_texts)
        print(f"\n🔄 ROUTING STRATEGY ANALYSIS:")
        for action, count in routing_analysis["routing_distribution"].items():
            percentage = (count / len(demo_texts)) * 100
            print(f"   {action}: {count} ({percentage:.1f}%)")
    
    print(f"\n📋 DETAILED RESULTS:")
    for i, pred in enumerate(results["predictions"]):
        print(f"\n{i+1}. {pred['text']}")
        print(f"   → Confidence: {pred['confidence_score']:.4f} ({pred['interpretation']})")
        print(f"   → Risk: {pred['risk_level']}")
        print(f"   → Action: {pred.get('routing_action', 'N/A')}")
        print(f"   → {pred['description']}")


def save_results(results: Dict, output_file: str, format_type: str):
    """
    Save results to file in the specified format.
    """
    if format_type == "json":
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    elif format_type == "csv":
        import csv
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "text", "confidence_score", "similarity_score", "interpretation", 
                "risk_level", "routing_action", "description"
            ])
            for pred in results["predictions"]:
                writer.writerow([
                    pred["text"], pred["confidence_score"], pred["similarity_score"],
                    pred["interpretation"], pred["risk_level"], 
                    pred.get("routing_action", "N/A"), pred["description"]
                ])
    else:  # text format
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(format_confidence_report(results))


def print_help():
    """
    Print help information for interactive mode.
    """
    print("\n📚 INTERACTIVE MODE COMMANDS:")
    print("   help     - Show this help message")
    print("   quit     - Exit the program")
    print("   exit     - Exit the program")
    print("   q        - Exit the program")
    print("\n💡 CONFIDENCE LEVELS:")
    print("   HIGH_CONFIDENCE (≥0.8)     - Low risk, suitable for local generation")
    print("   MEDIUM_CONFIDENCE (0.6-0.8) - Medium risk, consider RAG retrieval")
    print("   LOW_CONFIDENCE (0.4-0.6)    - High risk, route to larger model")
    print("   VERY_LOW_CONFIDENCE (<0.4)   - Very high risk, requires human review")
    print("\n🔄 ROUTING ACTIONS:")
    print("   LOCAL_GENERATION - Use current model for generation")
    print("   RAG_RETRIEVAL    - Augment with retrieved information")
    print("   LARGER_MODEL     - Route to more capable model")
    print("   HUMAN_REVIEW     - Requires human oversight")


if __name__ == "__main__":
    exit(main())
