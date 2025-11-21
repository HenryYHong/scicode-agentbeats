# SciCode AgentBeats Implementation

This is a complete implementation of a green agent for SciCode following the AgentBeats pattern. The system enables evaluation of white agents (code generators) using the SciCode benchmark through an A2A (Agent-to-Agent) protocol.

## 🏗️ Architecture

### Components

1. **Green Agent** (`green_agent.py`) - The evaluator that:
   - Receives evaluation requests via A2A messages
   - Iterates through SciCode problems
   - Sends problems to white agents
   - Grades responses using SciCode checkers
   - Returns comprehensive metrics

2. **White Agent** (`white_agent.py`) - An example code generator that:
   - Receives problems via A2A messages
   - Generates Python code solutions
   - Returns structured responses

3. **Launcher** (`launcher.py`) - One-command orchestrator that:
   - Starts both green and white agents
   - Sends evaluation requests
   - Collects and displays results
   - Handles cleanup

## 🚀 Quick Start

### Prerequisites

1. **SciCode Setup**:
   ```bash
   # Clone SciCode repository
   git clone https://github.com/scicode-bench/SciCode.git
   cd SciCode
   
   # Install SciCode in editable mode
   pip install -e .
   
   # Download test data (required)
   # Place test_data.h5 in eval/data/test_data.h5
   ```

2. **Python Dependencies**:
   ```bash
   pip install requests openai
   ```

### Running the System

#### Option 1: One-Command Evaluation (Recommended)

```bash
# Run evaluation with 5 problems
python launcher.py --max-problems 5

# Run with background information
python launcher.py --max-problems 5 --with-background

# Run with custom ports
python launcher.py --green-port 3333 --white-port 3334 --max-problems 10
```

#### Option 2: Manual Agent Management

```bash
# Terminal 1: Start Green Agent
python green_agent.py --port 3333 --scicode-root /path/to/SciCode

# Terminal 2: Start White Agent  
python white_agent.py --port 3334 --model gpt-4o-mini

# Terminal 3: Send evaluation request
curl -X POST http://localhost:3333/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "parts": [{"kind": "text", "text": "{\"white_url\": \"http://localhost:3334\", \"max_problems\": 5}"}]
  }'
```

## 📊 Understanding the Results

The system returns comprehensive metrics:

```json
{
  "success": true,
  "total_problems": 5,
  "passed_problems": 3,
  "total_steps": 15,
  "passed_steps": 12,
  "pass_at_1": 0.6,
  "step_accuracy": 0.8,
  "execution_time": 45.2,
  "problem_results": [
    {
      "problem_id": "1",
      "passed": true,
      "total_steps": 3,
      "passed_steps": 3,
      "code": "def add(a, b): return a + b",
      "grade_details": {...}
    }
  ]
}
```

### Key Metrics

- **Pass@1**: Percentage of problems solved completely correctly
- **Step Accuracy**: Percentage of individual steps solved correctly
- **Execution Time**: Total time for evaluation
- **Problem Results**: Detailed results for each problem

## 🔧 Configuration

### Green Agent Configuration

The green agent accepts configuration via A2A messages:

```json
{
  "white_url": "http://localhost:3334",
  "max_problems": 10,
  "with_background": false,
  "timeout_s": 180,
  "sandbox_mode": true
}
```

### White Agent Configuration

The white agent can be configured with different models:

```bash
# Use GPT-4o
python white_agent.py --model gpt-4o

# Use Claude
python white_agent.py --model claude-3-sonnet

# Use mock responses (no API key needed)
python white_agent.py --model mock
```

## 🛠️ Customization

### Creating Your Own White Agent

To create a custom white agent, implement the A2A protocol:

```python
class MyWhiteAgent:
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # Extract problem from message
        prompt = message["parts"][0]["text"]
        
        # Generate your solution
        code = await self.my_code_generator(prompt)
        
        # Return A2A response
        return {
            "role": "agent",
            "parts": [{"kind": "text", "text": code}],
            "context_id": message.get("context_id"),
            "metadata": {"source": "my_white_agent"}
        }
```

### Custom Grading

The green agent supports custom grading strategies:

1. **Sandbox Mode** (default): Safe execution in isolated environment
2. **Checker Mode**: Direct integration with SciCode's checkers
3. **Custom Mode**: Implement your own grading logic

## 🔍 Troubleshooting

### Common Issues

1. **SciCode not found**:
   ```bash
   # Make sure SciCode is installed
   pip install -e /path/to/SciCode
   
   # Check installation
   python -c "import scicode; print('OK')"
   ```

2. **Test data missing**:
   ```bash
   # Download test_data.h5 to SciCode/eval/data/
   # This is required for SciCode evaluation
   ```

3. **Port conflicts**:
   ```bash
   # Use different ports
   python launcher.py --green-port 3335 --white-port 3336
   ```

4. **API key issues**:
   ```bash
   # Set OpenAI API key
   export OPENAI_API_KEY="your-key-here"
   
   # Or use mock mode
   python white_agent.py --model mock
   ```

### Debug Mode

Enable verbose logging:

```bash
python launcher.py --verbose --max-problems 2
```

## 📚 AgentBeats Pattern

This implementation follows the AgentBeats pattern:

- **Green Agent**: Assessment/orchestration agent that manages evaluation
- **White Agent**: System under test that generates code
- **A2A Protocol**: Standardized communication between agents
- **Context Preservation**: Multi-turn conversations with context_id
- **Structured Messages**: JSON-based message format

## 🧪 Testing

### Unit Tests

```bash
# Test individual components
python -c "from green_agent import SciCodeGreenAgent; print('Green agent OK')"
python -c "from white_agent import SciCodeWhiteAgent; print('White agent OK')"
```

### Integration Tests

```bash
# Run small evaluation
python launcher.py --max-problems 1 --verbose

# Test with different models
python launcher.py --max-problems 2 --white-agent-model gpt-4o
```

## 📈 Performance

### Optimization Tips

1. **Parallel Processing**: The system can be extended to evaluate multiple white agents in parallel
2. **Caching**: Problem data can be cached to avoid repeated loading
3. **Streaming**: Large responses can be streamed for better memory usage
4. **Batch Processing**: Multiple problems can be sent in a single request

### Scaling

For production use:

1. **Containerization**: Use Docker for consistent environments
2. **Load Balancing**: Deploy multiple green/white agent instances
3. **Monitoring**: Add metrics collection and alerting
4. **Persistence**: Store results in a database

## 🤝 Contributing

To extend this implementation:

1. **New White Agents**: Implement the A2A protocol
2. **Custom Graders**: Add new grading strategies
3. **Benchmarks**: Integrate additional evaluation datasets
4. **Protocols**: Support additional agent communication protocols

## 📄 License

This implementation follows the same license as the SciCode project.

## 🙏 Acknowledgments

- SciCode team for the excellent benchmark
- AgentBeats framework for the multi-agent pattern
- OpenAI for language model APIs



