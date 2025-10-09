from .interface import VLM
from ml import GenerationConfig, SamplerConfig, ChatMessage
import re
import os
import codecs
import argparse

def parse_media_from_input(user_input):
    """Parse quoted media files from user input and return prompt and media paths"""
    # Find all quoted strings (both single and double quotes)
    quoted_pattern = r'["\']([^"\']*)["\']'
    quoted_matches = re.findall(quoted_pattern, user_input)
    
    # Remove quoted strings from the input to get the actual prompt
    prompt = re.sub(quoted_pattern, '', user_input).strip()
    
    # Separate image and audio files based on extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    
    image_paths = []
    audio_paths = []
    
    for quoted_file in quoted_matches:
        if quoted_file:  # Skip empty quotes
            # Expand user path if it starts with ~
            if quoted_file.startswith('~'):
                quoted_file = os.path.expanduser(quoted_file)
            
            # Check if file exists
            if not os.path.exists(quoted_file):
                print(f"Warning: File '{quoted_file}' not found")
                continue
                
            file_ext = os.path.splitext(quoted_file.lower())[1]
            if file_ext in image_extensions:
                image_paths.append(quoted_file)
            elif file_ext in audio_extensions:
                audio_paths.append(quoted_file)
    
    return prompt, image_paths if image_paths else None, audio_paths if audio_paths else None

def parse_arguments():
    """Parse command line arguments for the VLM main function."""
    parser = argparse.ArgumentParser(
        description="Interactive VLM (Vision-Language Model) conversation interface."
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="mlx-community/gemma-3-4b-it-8bit",
        help="The path to the local model directory or Hugging Face repo."
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="",
        help="Specific model name/type (e.g., 'qwen3vl', 'qwen3vl-moe', 'gemma3'). If empty, auto-detect from model_path."
    )
    parser.add_argument(
        "--context_length",
        type=int,
        default=2048,
        help="Context length for the model (default: 2048)."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)."
    )
    parser.add_argument(
        "--top_p",
        type=float,
        default=0.9,
        help="Top-p sampling parameter (default: 0.9)."
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=512,
        help="Maximum tokens to generate (default: 512)."
    )
    return parser.parse_args()

def main():
    """Main function for interactive VLM conversation."""
    args = parse_arguments()
    
    # Auto-detect model name if not provided
    model_name = args.model_name

    # TODO: avoid such hardcoded model name detection
    if not model_name:
        if "qwen3vl-30B" in args.model_path.lower():
            model_name = "qwen3vl-moe"
        elif "qwen3" in args.model_path.lower():
            model_name = "qwen3vl"
        elif "gemma" in args.model_path.lower():
            model_name = "gemma3"
        else:
            model_name = ""
    
    # Load the VLM instance
    vlm = VLM(
        model_name=model_name,
        model_path=args.model_path,
        mmproj_path=None,  # Not needed for this model
        context_length=args.context_length,
        device=None
    )

    # Configure sampler
    sampler_config = SamplerConfig(
        temperature=args.temperature,
        top_p=args.top_p
    )
    vlm.set_sampler(sampler_config)

    # Chat history using ChatMessage objects
    chat = []

    print("VLM Multi-round conversation started. Type 'quit' or 'exit' to end.")
    print("Include images/audios in quotes, e.g.: 'describe \"image1.jpg\" \"image2.png\"'")
    print("You can also use single quotes: 'describe '/path/to/image.jpg''")
    print("=" * 50)

    def on_token(text_chunk):
        """Token callback for streaming"""
        print(text_chunk, end="", flush=True)
        return True

    while True:
        # Get user input
        user_input = input("\nUser: ").strip()

        # Check for exit commands
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Parse media files and prompt from user input
        prompt_text, image_paths, audio_paths = parse_media_from_input(user_input)
        
        # If no text prompt after parsing, use the original input
        if not prompt_text.strip():
            prompt_text = user_input
            image_paths = None
            audio_paths = None

        # Add user message to chat history using ChatMessage
        chat.append(ChatMessage(role="user", content=prompt_text))

        # Calculate number of images and audios for chat template
        num_images = len(image_paths) if image_paths else 0
        num_audios = len(audio_paths) if audio_paths else 0

        # Apply chat template with image/audio token insertion
        try:
            formatted_prompt = vlm.apply_chat_template_with_media(chat, num_images=num_images, num_audios=num_audios)
        except (NotImplementedError, AttributeError):
            # Fallback to manual formatting if chat template is not implemented
            formatted_prompt = ""
            for msg in chat:
                formatted_prompt += f"{msg.role}: {msg.content}\n"
            formatted_prompt += "Assistant: "

        # Generation config with media paths
        generation_config = GenerationConfig(
            max_tokens=args.max_tokens,
            sampler_config=sampler_config,
            image_paths=image_paths,
            audio_paths=audio_paths
        )

        # Generate response
        print("Assistant: ", end="", flush=True)
        
        try:
            # Use streaming generation with callback
            response_text = ""
            
            def token_callback(text_chunk):
                nonlocal response_text
                print(text_chunk, end="", flush=True)
                response_text += text_chunk
                return True
            
            # Use generate_stream method for streaming generation
            response = vlm.generate_stream(
                prompt=formatted_prompt,
                config=generation_config,
                on_token=token_callback
            )
            
            print()  # New line after streaming
            
            # Add assistant response to chat history using ChatMessage
            chat.append(ChatMessage(role="assistant", content=response_text))
            
        except Exception as e:
            print(f"Error generating response: {e}")
            print()

    # Clean up
    vlm.destroy()

def test_vlm_generate_stream(model_path, model_name):
    # Specify the checkpoint
    context_length = 2048

    # Load the corresponding model and VLM instance
    vlm = VLM(
        model_name=model_name,
        model_path=model_path,
        mmproj_path=None,  # Not needed for this model
        context_length=context_length,
        device=None
    )

    # Configure sampler
    sampler_config = SamplerConfig(
        temperature=0.7,
        top_p=0.9
    )
    vlm.set_sampler(sampler_config)

    # Chat history using ChatMessage objects (following ml.py API)
    chat = []

    print("Multi-round VLM conversation started. Type 'quit' or 'exit' to end.")
    print("Include images/audios in quotes, e.g.: 'describe \"image1.jpg\" \"image2.png\"'")
    print("You can also use single quotes: 'describe '/path/to/image.jpg''")
    print("=" * 50)

    def on_token(text_chunk, user_data):
        """Token callback for streaming"""
        print(text_chunk, end="", flush=True)
        if user_data is not None:
            user_data["response"] += text_chunk
        return True

    while True:
        # Get user input
        user_input = input("\nUser: ").strip()

        # Check for exit commands
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Parse media files and prompt from user input
        prompt_text, image_paths, audio_paths = parse_media_from_input(user_input)
        
        # If no text prompt after parsing, use the original input
        if not prompt_text.strip():
            prompt_text = user_input
            image_paths = None
            audio_paths = None

        # Add user message to chat history using ChatMessage (following ml.py API)
        chat.append(ChatMessage(role="user", content=prompt_text))

        # Calculate number of images and audios for chat template
        num_images = len(image_paths) if image_paths else 0
        num_audios = len(audio_paths) if audio_paths else 0

        # Apply chat template with image/audio token insertion
        try:
            formatted_prompt = vlm.apply_chat_template_with_media(chat, num_images=num_images, num_audios=num_audios)
        except (NotImplementedError, AttributeError):
            # Fallback to manual formatting if chat template is not implemented
            formatted_prompt = ""
            for msg in chat:
                formatted_prompt += f"{msg.role}: {msg.content}\n"
            formatted_prompt += "Assistant: "

        # Generation config with media paths
        generation_config = GenerationConfig(
            max_tokens=512,
            sampler_config=sampler_config,
            image_paths=image_paths,
            audio_paths=audio_paths
        )

        # Generate response
        print("Assistant: ", end="", flush=True)
        
        try:
            # Use streaming generation with callback - single method handles all cases
            user_data = {"response": ""}
            
            # Always use the unified generate_stream method
            response = vlm.generate_stream(
                prompt=formatted_prompt,
                config=generation_config,
                on_token=on_token,
                user_data=user_data
            )
            
            print()  # New line after streaming
            
            # Add assistant response to chat history using ChatMessage
            chat.append(ChatMessage(role="assistant", content=user_data["response"]))
            
        except Exception as e:
            print(f"Error generating response: {e}")
            print()

    # Clean up
    vlm.destroy()

if __name__ == "__main__":
    main()