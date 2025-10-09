from rich import print

class GetPromptTemplate:
    def __init__(self):
        pass

    # ---------------------------
    # Static prompt template
    # ---------------------------
    def static_prompt_template(self):
        print("[bold green]--- Static Prompt Template ---[/bold green]")
        print("[magenta]Purpose:[/magenta] Simple, fixed queries with no dynamic content. Use for testing or quick one-liners.")
        template = 'query = "Explain machine learning in simple words"\nllm.invoke(query).content'
        print(f"[yellow]{template}[/yellow]\n")

    # ---------------------------
    # Dynamic prompt template
    # ---------------------------
    def dynamic_prompt_template(self):
        print("[bold green]--- Dynamic Prompt Template ---[/bold green]")
        print("[magenta]Purpose:[/magenta] Queries with placeholders that can change at runtime. Useful for flexible prompts with variables.")
        template = '''template = "Explain {topic} in {words} words"
final_prompt = PromptTemplate.from_template(template).format(topic="AI", words=50)
llm.invoke(final_prompt).content'''
        print(f"[yellow]{template}[/yellow]\n")

    # ---------------------------
    # Chat prompt template
    # ---------------------------
    def chat_prompt_template(self):
        print("[bold green]--- Chat Prompt Template ---[/bold green]")
        print("[magenta]Purpose:[/magenta] Multi-turn chat style prompts with system & human messages. Use for conversational agents or assistants.")
        template = '''prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "Explain {topic} in {words} words")
])
final_prompt = prompt.format(topic="AI", words=50).to_messages()
llm.invoke(final_prompt).content'''
        print(f"[yellow]{template}[/yellow]\n")

    # ---------------------------
    # Few-shot prompt template
    # ---------------------------
    def few_shot_prompt_template(self):
        print("[bold green]--- Few-Shot Prompt Template ---[/bold green]")
        print("[magenta]Purpose:[/magenta] Include example Q&A pairs to guide LLM. Useful for teaching model patterns or style of response.")
        template = '''examples = [
    {"input": "What is Python?", "output": "A programming language."},
    {"input": "What is Java?", "output": "Also a programming language."}
]
example_prompt = PromptTemplate(template="Q: {input}\\nA: {output}", input_variables=["input","output"])
few_shot = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Q: {input}\\nA:",
    input_variables=["input"]
)
final_prompt = few_shot.format(input="What is C++?")
llm.invoke(final_prompt).content'''
        print(f"[yellow]{template}[/yellow]\n")

    # ---------------------------
    # Zero-shot prompt template
    # ---------------------------
    def zero_shot_prompt_template(self):
        print("[bold green]--- Zero-Shot Prompt Template ---[/bold green]")
        print("[magenta]Purpose:[/magenta] Direct prompt without examples. Use when you want model to generate response from instructions only.")
        template = '''template = "Explain {topic} clearly without giving examples"
final_prompt = PromptTemplate.from_template(template).format(topic="Reinforcement Learning")
llm.invoke(final_prompt).content'''
        print(f"[yellow]{template}[/yellow]\n")

    # ---------------------------
    # Instruction-based template
    # ---------------------------
    def instruction_prompt_template(self):
        print("[bold green]--- Instruction-Based Prompt Template ---[/bold green]")
        print("[magenta]Purpose:[/magenta] Give explicit instructions for model behavior. Useful for summarization, step-by-step, or style control.")
        template = '''template = "Instruction: {instruction}\\nOutput:"
final_prompt = PromptTemplate.from_template(template).format(instruction="Summarize latest AI news")
llm.invoke(final_prompt).content'''
        print(f"[yellow]{template}[/yellow]\n")

    # ---------------------------
    # Multi-turn conversation template
    # ---------------------------
    def multi_turn_prompt_template(self):
        print("[bold green]--- Multi-Turn Conversation Template ---[/bold green]")
        print("[magenta]Purpose:[/magenta] Handles user & AI conversation context. Use for chatbots that need memory of previous exchanges.")
        template = '''prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{user_input}"),
    ("ai", "{ai_response}")
])
final_prompt = prompt.format(user_input="Explain AI", ai_response="Sure! AI is ...").to_messages()
llm.invoke(final_prompt).content'''
        print(f"[yellow]{template}[/yellow]\n")

    # ---------------------------
    # List all templates
    # ---------------------------
    def list_all_templates(self):
        print("[bold green]--- Available Prompt Templates ---[/bold green]")
        methods = [func for func in dir(self) 
                   if callable(getattr(self, func)) 
                   and not func.startswith("__") 
                   and func.endswith("_template")]
        for i, method in enumerate(methods, 1):
            print(f"[yellow]{i}.[/yellow] [cyan]{method}[/cyan]")
