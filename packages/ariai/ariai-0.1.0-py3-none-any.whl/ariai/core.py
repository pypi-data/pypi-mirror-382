"""
Core functionality for the AriAI chatbot framework.
Supports both OpenAI and Hugging Face models.
"""

import os
from typing import List, Dict, Optional
import openai
from rich.console import Console
from rich.prompt import Prompt
from rich import print as rprint
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class AriAI:
    """A flexible chatbot that supports multiple AI providers."""
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        hf_model: str = "google/flan-t5-base",
        system_prompt: str = "You are a helpful AI assistant."
    ):
        """
        Initialize the chatbot.
        
        Args:
            provider: AI provider ("openai" or "huggingface")
            api_key: OpenAI API key (required for OpenAI)
            hf_model: Hugging Face model name
            system_prompt: System message defining bot personality
        """
        self.provider = provider.lower()
        self.system_prompt = system_prompt
        self.conversation_history: List[Dict[str, str]] = []
        self.console = Console()
        
        if self.provider == "openai":
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key is required")
            openai.api_key = api_key
        elif self.provider == "huggingface":
            # Use pipeline directly which handles model loading automatically
            self.generator = pipeline(
                "text-generation",
                model="gpt2",  # Using GPT-2 as a default model
                tokenizer=None  # Will be loaded automatically
            )
        else:
            raise ValueError("Provider must be 'openai' or 'huggingface'")
            
    def chat(self, message: str, max_length: int = 200) -> str:
        """
        Send a message to the AI and get a response.
        
        Args:
            message: User's input message
            max_length: Maximum length of the response
            
        Returns:
            The AI's response
        """
        self.conversation_history.append({"role": "user", "content": message})
        
        if self.provider == "openai":
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_length
            )
            reply = response.choices[0].message.content
            
        else:  # huggingface
            # Format conversation history into a single string
            context = self.system_prompt + "\n"
            for msg in self.conversation_history:
                prefix = "User: " if msg["role"] == "user" else "Assistant: "
                context += f"{prefix}{msg['content']}\nAssistant: "
            
            # Generate response
            response = self.generator(
                context,
                max_length=len(context) + max_length,
                num_return_sequences=1
            )
            reply = response[0]["generated_text"][len(context):].strip()
        
        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply
    
    def start_ui(self):
        """Launch the interactive terminal UI."""
        self.console.print("[bold blue]Welcome to AriAI![/bold blue]")
        self.console.print(f"[dim]Using {self.provider} provider[/dim]")
        self.console.print("[dim]Type 'exit' to quit[/dim]\n")
        
        while True:
            try:
                user_input = Prompt.ask("[bold green]You[/bold green]")
                if user_input.lower() == "exit":
                    self.console.print("\n[bold blue]Goodbye![/bold blue]")
                    break
                    
                with self.console.status("[bold yellow]AriAI is thinking...[/bold yellow]"):
                    response = self.chat(user_input)
                
                rprint(f"\n[bold purple]AriAI[/bold purple]: {response}\n")
                
            except KeyboardInterrupt:
                self.console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            except Exception as e:
                self.console.print(f"[bold red]Error: {str(e)}[/bold red]")