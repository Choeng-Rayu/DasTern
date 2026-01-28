#!/usr/bin/env python
"""
Simple example script to use the trained Healthcare LNP model
Run this after training the model with: python healthcare_lnp.py
"""

from healthcare_lnp import HealthcarePredictor

def main():
    print("=" * 80)
    print("Healthcare LNP Model - Inference Example")
    print("=" * 80)
    
    # Load the trained model
    try:
        predictor = HealthcarePredictor('healthcare_lnp_model.pth')
        print("✓ Model loaded successfully!\n")
    except FileNotFoundError:
        print("✗ Error: Model file 'healthcare_lnp_model.pth' not found.")
        print("  Please train the model first by running: python healthcare_lnp.py")
        return
    
    # Example medical cases
    test_cases = [
        {
            'id': 1,
            'text': """42 year old male with acute onset chest pain and shortness of breath.
                       History of hypertension and smoking. BP 160/100, HR 115.
                       EKG shows ST elevation. Suspected acute coronary syndrome."""
        },
        {
            'id': 2,
            'text': """28 year old female with high fever (39.5C), productive cough, and body aches.
                       Symptoms started 2 days ago. No significant medical history.
                       Chest exam shows crackles. Suspected pneumonia or bronchitis."""
        },
        {
            'id': 3,
            'text': """56 year old male with persistent abdominal pain and bloating.
                       Associated with constipation. Recent colonoscopy was normal.
                       No fever. Vitals are stable. Possible irritable bowel syndrome."""
        },
        {
            'id': 4,
            'text': """78 year old female with memory loss and confusion for 3 months.
                       Also experiencing mood changes and sleep disturbance.
                       MRI shows mild cerebral atrophy. Risk factors: hypertension, diabetes."""
        },
        {
            'id': 5,
            'text': """35 year old with severe anxiety, insomnia, and persistent sadness.
                       Cannot focus at work. Appetite decreased. Denies suicidal ideation.
                       Family history of depression."""
        }
    ]
    
    # Run predictions
    for case in test_cases:
        print(f"\n{'=' * 80}")
        print(f"Case #{case['id']}")
        print(f"{'=' * 80}")
        print(f"Medical Record:\n{case['text']}\n")
        
        try:
            result = predictor.predict(case['text'])
            
            print("PREDICTION RESULTS:")
            print("-" * 80)
            print(f"🔍 Predicted Disease:     {result['disease_prediction']}")
            print(f"📊 Confidence Level:      {result['disease_confidence']:.2%}")
            print(f"⚠️  Severity Assessment:   {result['severity_assessment']}")
            print(f"⚡ Risk Score:             {result['risk_score']:.2%}")
            print(f"\n💊 Suggested Medications:")
            for i, med in enumerate(result['suggested_medications'], 1):
                print(f"   {i}. {med}")
            
            if result['symptoms_identified']:
                print(f"\n🔬 Identified Symptoms:")
                for symptom in result['symptoms_identified'][:3]:
                    print(f"   • {symptom}")
            
        except Exception as e:
            print(f"❌ Error processing case: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("Inference Complete!")
    print("=" * 80)

def interactive_mode():
    """Allow user to input custom medical text"""
    print("\n" + "=" * 80)
    print("Interactive Mode - Enter Custom Medical Text")
    print("=" * 80)
    print("Enter your medical record (type 'done' on a new line when finished):\n")
    
    try:
        predictor = HealthcarePredictor('healthcare_lnp_model.pth')
    except FileNotFoundError:
        print("✗ Model file not found. Train the model first.")
        return
    
    while True:
        lines = []
        while True:
            line = input()
            if line.lower() == 'done':
                break
            lines.append(line)
        
        if not lines:
            print("Empty input. Please try again.\n")
            continue
        
        medical_text = '\n'.join(lines)
        
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS:")
        print("=" * 80)
        
        result = predictor.predict(medical_text)
        print(f"Disease:       {result['disease_prediction']}")
        print(f"Confidence:    {result['disease_confidence']:.2%}")
        print(f"Severity:      {result['severity_assessment']}")
        print(f"Risk Score:    {result['risk_score']:.2%}")
        print(f"Medications:   {', '.join(result['suggested_medications'])}")
        
        print("\nEnter another record (or 'exit' to quit):")
        cmd = input().strip().lower()
        if cmd == 'exit':
            break
        print("Enter medical record:\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    else:
        main()
        
        # Offer interactive mode
        print("\n💡 Tip: Run 'python example_usage.py --interactive' for interactive mode!")
