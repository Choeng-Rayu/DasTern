"""
Chat Assistant
Responsibility: Conversational AI for medical information queries
Two modes: General medical info + Prescription Q&A
"""

# TODO: from core.generation import generate

def chat(message: str, conversation_history: list, context: dict = None):
    """
    Process chat message with conversation context
    
    Args:
        message: User message
        conversation_history: Previous messages
        context: Optional context (e.g., user's prescriptions)
        
    Returns:
        Assistant response
    """
    # TODO: Build conversation prompt
    # prompt = build_chat_prompt(message, conversation_history, context)
    
    # TODO: Generate response
    # response = generate(prompt, max_tokens=512)
    
    # TODO: Validate safety
    # TODO: Return response
    pass


def build_chat_prompt(message: str, history: list, context: dict = None):
    """
    Build complete chat prompt with history and context
    
    Args:
        message: Current user message
        history: Conversation history
        context: Additional context
        
    Returns:
        Complete prompt for LLM
    """
    # TODO: Format conversation history
    # TODO: Add system instructions
    # TODO: Include relevant context
    # TODO: Add safety guardrails
    # TODO: Return formatted prompt
    pass


def answer_prescription_question(question: str, prescription_data: dict):
    """
    Answer questions about a specific prescription
    
    Args:
        question: User's question
        prescription_data: Prescription context
        
    Returns:
        Answer based on prescription data
    """
    # TODO: Build prescription-specific prompt
    # TODO: Include prescription data as context
    # TODO: Generate answer
    # TODO: Validate no medical advice given
    # TODO: Return answer
    pass
