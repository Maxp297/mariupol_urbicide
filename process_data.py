from anthropic import Anthropic
import os
import hashlib
from datetime import datetime
import json

class ForensicClaudeAPI:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        self.timestamp = datetime.now().isoformat()
        
    def analyze_data(self, data, task_description, source_file=None):
        """
        Analyze data using Claude while maintaining forensic requirements
        """
        interaction_id = hashlib.sha256(f"{self.timestamp}{task_description}".encode()).hexdigest()[:12]
        
        try:
            response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",  # Updated to Sonnet
                messages=[{
                    "role": "user", 
                    "content": f"{task_description}\n\nData: {json.dumps(data)}"
                }],
                max_tokens=500,  # Reduced for cost efficiency
                temperature=0.1  # More deterministic for forensic analysis
            )
            
            # Log for evidence chain
            log_entry = {
                "timestamp": self.timestamp,
                "interaction_id": interaction_id,
                "source_file": source_file,
                "input_hash": hashlib.sha256(str(data).encode()).hexdigest(),
                "response_hash": hashlib.sha256(str(response.content).encode()).hexdigest(),
                "model": "claude-3-sonnet-20240229",
                "token_usage": {
                    "prompt_tokens": len(str(data)) // 4,  # Approximate
                    "completion_tokens": len(str(response.content)) // 4
                }
            }
            
            return response.content, log_entry
            
        except Exception as e:
            print(f"Error in Claude analysis: {e}")
            return None, None
        
    def prepare_chat_prompt(self, data, task_description, source_file=None):
        """
        Prepares a formatted prompt for chat.claude.ai and copies to clipboard
        """
        import pyperclip  # Add to imports at top of file
        
        interaction_id = hashlib.sha256(f"{self.timestamp}{task_description}".encode()).hexdigest()[:12]
        
        prompt = f"""# Forensic Analysis Request
Task: {task_description}

## Metadata
- Source: {source_file}
- ID: {interaction_id}
- Timestamp: {self.timestamp}

## Data
```json
{json.dumps(data, indent=2, ensure_ascii=False)}
```

Please analyze this data following forensic requirements:
1. Maintain evidence chain integrity
2. Note temporal patterns
3. Document all observations
4. Flag any anomalies
"""
        # Copy to clipboard for easy pasting
        pyperclip.copy(prompt)
        return interaction_id

if __name__ == "__main__":
    # Initialize the API wrapper
    claude_api = ForensicClaudeAPI()
    
    # Test with Morskoy 46 metadata
    try:
        with open(os.path.join(os.path.dirname(__file__), "data/processed/Morskoy46/morskoy46_image_metadata_aggregated.csv"), 'r') as f:
            test_data = f.read()
        
        # Generate and copy prompt
        interaction_id = claude_api.prepare_chat_prompt(
            data=test_data,
            task_description="Analyze this metadata for patterns in property documentation.",
            source_file="morskoy46_image_metadata_aggregated.csv"
        )
        
        print("✓ Prompt copied to clipboard!")
        print("1. Open chat.claude.ai in your browser")
        print("2. Paste the prompt (Cmd+V)")
        print(f"3. Save Claude's response in: data/processed/analysis_logs/claude_chat_{interaction_id}.txt")
    except Exception as e:
        print(f"Error in main execution: {e}")