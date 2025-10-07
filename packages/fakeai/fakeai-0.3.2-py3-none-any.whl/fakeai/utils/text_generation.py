"""
Simulated text generation for various prompt types.

This module provides the SimulatedGenerator class which generates realistic
responses for different types of prompts including greetings, questions, and
coding requests.
"""

#  SPDX-License-Identifier: Apache-2.0

import random
import re

from faker import Faker

from fakeai.utils.tokens import calculate_token_count


class SimulatedGenerator:
    """Generator for simulated responses."""

    def __init__(self):
        """Initialize the simulated generator."""
        self.fake = Faker()

        # Common AI responses for different types of prompts
        self.responses = {
            "greeting": [
                "Hello! How can I assist you today?",
                "Hi there! I'm here to help you with any questions you might have.",
                "Greetings! How may I be of service?",
                "Hello! I'm your AI assistant. What can I help you with?",
            ],
            "question": [
                "That's an interesting question. Let me think about it...\n\n{}",
                "I'd be happy to answer that for you.\n\n{}",
                "Great question! Here's what I know:\n\n{}",
            ],
            "coding": [
                "Here's a code example that might help:\n\n```{}\n{}\n```\n\nLet me explain how this works...",
                "I can help you with that coding challenge. Consider this approach:\n\n```{}\n{}\n```\n\nThe key concept here is...",
            ],
            "default": [
                "I understand you're asking about {}. Let me provide some information...\n\n{}",
                "When it comes to {}, there are several important aspects to consider:\n\n{}",
                "I'd be happy to share what I know about {}.\n\n{}",
            ],
        }

    def generate_response(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 100,
        delay: float = 0,
    ) -> str:
        """Generate a simulated response based on the prompt."""
        # Identify the type of prompt
        prompt_type = self._identify_prompt_type(prompt.lower())

        # Generate a response based on the prompt type
        if prompt_type == "greeting":
            response = random.choice(self.responses["greeting"])
        elif prompt_type == "question":
            base = random.choice(self.responses["question"])
            # Generate paragraphs based on keywords in the prompt
            content = self._generate_content_from_keywords(prompt, max_tokens)
            response = base.format(content)
        elif prompt_type == "coding":
            base = random.choice(self.responses["coding"])
            language = self._identify_coding_language(prompt)
            code = self._generate_simulated_code(language, prompt)
            response = base.format(language, code)
        else:
            base = random.choice(self.responses["default"])
            topic = self._extract_topic(prompt)
            content = self._generate_content_from_keywords(prompt, max_tokens)
            response = base.format(topic, content)

        # Trim to max tokens using actual token counting
        # Check actual token count
        current_tokens = calculate_token_count(response)

        # If over limit, trim by sentences
        if current_tokens > max_tokens:
            sentences = response.split(". ")
            trimmed = ""
            for sentence in sentences:
                test_text = trimmed + sentence + ". "
                if calculate_token_count(test_text) <= max_tokens:
                    trimmed = test_text
                else:
                    break

            # If we got at least something, use it
            if trimmed:
                return trimmed.strip()

            # Otherwise, hard trim by characters (fallback)
            max_chars = max_tokens * 4
            return response[:max_chars]

        return response

    def _identify_prompt_type(self, prompt: str) -> str:
        """Identify the type of prompt."""
        greeting_patterns = [
            r"\bhello\b",
            r"\bhi\b",
            r"\bhey\b",
            r"\bgreetings\b",
            r"\bgood (morning|afternoon|evening)\b",
        ]

        question_patterns = [
            r"\bwhat\b",
            r"\bwho\b",
            r"\bwhen\b",
            r"\bwhere\b",
            r"\bwhy\b",
            r"\bhow\b",
            r"\bcan you\b",
            r"\bcould you\b",
        ]

        coding_patterns = [
            r"\bcode\b",
            r"\bfunction\b",
            r"\bclass\b",
            r"\bpython\b",
            r"\bjavascript\b",
            r"\btypescript\b",
            r"\bjava\b",
            r"\bc\+\+\b",
            r"\bruby\b",
            r"\brust\b",
            r"\bgo\b",
            r"\bprogram\b",
            r"\balgorithm\b",
        ]

        for pattern in greeting_patterns:
            if re.search(pattern, prompt):
                return "greeting"

        for pattern in coding_patterns:
            if re.search(pattern, prompt):
                return "coding"

        for pattern in question_patterns:
            if re.search(pattern, prompt):
                return "question"

        return "default"

    def _extract_topic(self, prompt: str) -> str:
        """Extract a topic from the prompt."""
        # Simple topic extraction based on keywords
        topic_phrases = re.findall(
            r"(?:about|regarding|on) (\w+(?:\s+\w+){0,3})", prompt
        )
        if topic_phrases:
            return topic_phrases[0]

        # Look for nouns following question words
        noun_phrases = re.findall(
            r"(?:what|who|when|where|why|how) (?:is|are|was|were) (\w+(?:\s+\w+){0,3})",
            prompt,
        )
        if noun_phrases:
            return noun_phrases[0]

        # Default to the first few words
        words = prompt.strip().split()
        if len(words) <= 3:
            return prompt.strip()
        else:
            return " ".join(words[:3]) + "..."

    def _generate_content_from_keywords(self, prompt: str, max_tokens: int) -> str:
        """Generate content based on keywords in the prompt."""
        # Extract keywords from the prompt
        words = re.findall(r"\b\w{4,}\b", prompt.lower())
        relevant_words = [word for word in words if word not in self.fake.words()]

        if not relevant_words:
            relevant_words = ["topic"]

        # Generate paragraphs
        num_paragraphs = min(3, max(1, max_tokens // 100))
        paragraphs = []

        for _ in range(num_paragraphs):
            paragraph = self.fake.paragraph(
                nb_sentences=min(10, max(3, max_tokens // 50))
            )
            for word in relevant_words[:3]:  # Use up to 3 keywords
                # Insert the keyword in a relevant context
                replacement = random.choice(
                    [
                        f"the {word}",
                        f"this {word}",
                        f"a {word}",
                        f"{word} concept",
                        f"{word} process",
                    ]
                )
                paragraph = paragraph.replace(
                    random.choice(
                        paragraph.split()[:5]
                    ),  # Replace a word near the beginning
                    replacement,
                    1,
                )
            paragraphs.append(paragraph)

        return "\n\n".join(paragraphs)

    def _identify_coding_language(self, prompt: str) -> str:
        """Identify the coding language from the prompt."""
        languages = {
            "python": r"\bpython\b",
            "javascript": r"\b(?:javascript|js)\b",
            "typescript": r"\b(?:typescript|ts)\b",
            "java": r"\bjava\b",
            "c++": r"\b(?:c\+\+|cpp)\b",
            "rust": r"\brust\b",
            "go": r"\b(?:golang|go)\b",
            "ruby": r"\bruby\b",
            "php": r"\bphp\b",
            "c#": r"\b(?:c#|csharp)\b",
            "swift": r"\bswift\b",
            "kotlin": r"\bkotlin\b",
        }

        for lang, pattern in languages.items():
            if re.search(pattern, prompt.lower()):
                return lang

        # Default to Python if no language is specified
        return "python"

    def _generate_simulated_code(self, language: str, prompt: str) -> str:
        """Generate simulated code in the specified language."""
        # Extract relevant code concepts from the prompt
        concepts = set(
            re.findall(
                r"\b(function|class|object|array|list|dictionary|map|sort|search|algorithm|api|http|request|response|json|xml|database|sql|query|insert|update|delete|select|from|where|join|group by|order by|file|read|write|input|output|print|log|debug|error|exception|try|catch|if|else|for|while|loop|recursion|callback|promise|async|await|thread|process|parallel)\b",
                prompt.lower(),
            )
        )

        if language == "python":
            return self._generate_python_code(concepts, prompt)
        elif language in ["javascript", "js"]:
            return self._generate_javascript_code(concepts, prompt)
        elif language in ["typescript", "ts"]:
            return self._generate_typescript_code(concepts, prompt)
        elif language == "java":
            return self._generate_java_code(concepts, prompt)
        elif language in ["c++", "cpp"]:
            return self._generate_cpp_code(concepts, prompt)
        else:
            # For other languages, generate a generic code sample
            return self._generate_generic_code(language, concepts, prompt)

    def _generate_python_code(self, concepts: set, prompt: str) -> str:
        """Generate Python code based on concepts."""
        if "class" in concepts:
            class_name = "".join(
                w.capitalize()
                for w in random.choice(
                    ["data", "user", "processing", "service"]
                ).split()
            )
            code = f"class {class_name}:\n"
            code += "    def __init__(self, name, value=None):\n"
            code += "        self.name = name\n"
            code += "        self.value = value or 0\n\n"
            code += "    def process(self):\n"
            code += "        return self.value * 2\n\n"
            code += f"# Create an instance\nobj = {class_name}('example', 42)\n"
            code += "result = obj.process()\n"
            code += "print(f'Processed {obj.name}: {result}')"
            return code
        elif "function" in concepts:
            func_name = random.choice(
                [
                    "process_data",
                    "calculate_result",
                    "transform_input",
                    "handle_request",
                ]
            )
            code = f"def {func_name}(data, option=None):\n"
            code += '    """\n'
            code += "    Process the input data and return a result.\n"
            code += "    \n"
            code += "    Args:\n"
            code += "        data: The input data to process\n"
            code += "        option: Optional processing parameter\n"
            code += "    \n"
            code += "    Returns:\n"
            code += "        The processed result\n"
            code += '    """\n'
            code += "    result = {}\n"
            code += "    if isinstance(data, list):\n"
            code += "        result['type'] = 'list'\n"
            code += "        result['length'] = len(data)\n"
            code += "        result['sum'] = sum(data) if all(isinstance(x, (int, float)) for x in data) else None\n"
            code += "    elif isinstance(data, dict):\n"
            code += "        result['type'] = 'dict'\n"
            code += "        result['keys'] = list(data.keys())\n"
            code += "    else:\n"
            code += "        result['type'] = str(type(data).__name__)\n"
            code += "        result['string'] = str(data)\n"
            code += "    \n"
            code += "    if option:\n"
            code += "        result['option'] = option\n"
            code += "    \n"
            code += "    return result\n\n"
            code += "# Example usage\n"
            code += "sample_data = [1, 2, 3, 4, 5]\n"
            code += f"output = {func_name}(sample_data, 'sum')\n"
            code += "print(output)"
            return code
        else:
            # General Python snippet
            code = "# Example Python code\n"
            code += "import json\n"
            code += "from datetime import datetime\n\n"
            code += "def analyze_data(data):\n"
            code += "    results = {\n"
            code += "        'timestamp': datetime.now().isoformat(),\n"
            code += "        'count': len(data),\n"
            code += "        'types': {}\n"
            code += "    }\n"
            code += "    \n"
            code += "    for item in data:\n"
            code += "        item_type = type(item).__name__\n"
            code += "        if item_type not in results['types']:\n"
            code += "            results['types'][item_type] = 0\n"
            code += "        results['types'][item_type] += 1\n"
            code += "    \n"
            code += "    return results\n\n"
            code += "# Sample data\n"
            code += "sample = [1, 'text', 3.14, {'key': 'value'}, [1, 2, 3]]\n"
            code += "result = analyze_data(sample)\n"
            code += "print(json.dumps(result, indent=2))"
            return code

    def _generate_javascript_code(self, concepts: set, prompt: str) -> str:
        """Generate JavaScript code based on concepts."""
        if "class" in concepts:
            class_name = "".join(
                w.capitalize()
                for w in random.choice(
                    ["data", "user", "processing", "service"]
                ).split()
            )
            code = f"class {class_name} {{\n"
            code += "  constructor(name, value = 0) {\n"
            code += "    this.name = name;\n"
            code += "    this.value = value;\n"
            code += "    this.created = new Date();\n"
            code += "  }\n\n"
            code += "  process() {\n"
            code += "    return this.value * 2;\n"
            code += "  }\n\n"
            code += "  getInfo() {\n"
            code += "    return {\n"
            code += "      name: this.name,\n"
            code += "      value: this.value,\n"
            code += "      processed: this.process(),\n"
            code += "      created: this.created\n"
            code += "    };\n"
            code += "  }\n"
            code += "}\n\n"
            code += (
                f"// Create an instance\nconst obj = new {class_name}('example', 42);\n"
            )
            code += "console.log(obj.getInfo());"
            return code
        elif "async" in concepts or "await" in concepts or "promise" in concepts:
            func_name = random.choice(
                ["fetchData", "processAsync", "loadResources", "getApiResponse"]
            )
            code = f"async function {func_name}(url, options = {{}}) {{\n"
            code += "  console.log(`Fetching data from ${url}...`);\n\n"
            code += "  try {\n"
            code += "    const response = await fetch(url, {\n"
            code += "      method: options.method || 'GET',\n"
            code += "      headers: options.headers || { 'Content-Type': 'application/json' },\n"
            code += (
                "      body: options.body ? JSON.stringify(options.body) : undefined\n"
            )
            code += "    });\n\n"
            code += "    if (!response.ok) {\n"
            code += "      throw new Error(`HTTP error: ${response.status}`);\n"
            code += "    }\n\n"
            code += "    const data = await response.json();\n"
            code += "    return {\n"
            code += "      success: true,\n"
            code += "      data,\n"
            code += "      timestamp: new Date()\n"
            code += "    };\n"
            code += "  } catch (error) {\n"
            code += "    console.error(`Error in ${func_name}:`, error);\n"
            code += "    return {\n"
            code += "      success: false,\n"
            code += "      error: error.message,\n"
            code += "      timestamp: new Date()\n"
            code += "    };\n"
            code += "  }\n"
            code += "}\n\n"
            code += "// Example usage\n"
            code += f"{func_name}('https://api.example.com/data')\n"
            code += "  .then(result => console.log(result))\n"
            code += "  .catch(error => console.error(error));"
            return code
        else:
            # General JavaScript snippet
            code = "// Example JavaScript utility functions\n\n"
            code += "const utils = {\n"
            code += "  formatDate(date) {\n"
            code += "    const d = new Date(date);\n"
            code += "    const year = d.getFullYear();\n"
            code += "    const month = String(d.getMonth() + 1).padStart(2, '0');\n"
            code += "    const day = String(d.getDate()).padStart(2, '0');\n"
            code += "    return `${year}-${month}-${day}`;\n"
            code += "  },\n\n"
            code += "  generateId(prefix = 'id') {\n"
            code += (
                "    return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;\n"
            )
            code += "  },\n\n"
            code += "  debounce(func, wait) {\n"
            code += "    let timeout;\n"
            code += "    return function executedFunction(...args) {\n"
            code += "      const later = () => {\n"
            code += "        clearTimeout(timeout);\n"
            code += "        func(...args);\n"
            code += "      };\n"
            code += "      clearTimeout(timeout);\n"
            code += "      timeout = setTimeout(later, wait);\n"
            code += "    };\n"
            code += "  }\n"
            code += "};\n\n"
            code += "// Example usage\n"
            code += "console.log(utils.formatDate(new Date()));\n"
            code += "console.log(utils.generateId('user'));\n\n"
            code += "const handleInput = utils.debounce(() => {\n"
            code += "  console.log('Input handled!');\n"
            code += "}, 300);\n\n"
            code += "// Call handleInput multiple times - it will only execute once after 300ms\n"
            code += "handleInput();\n"
            code += "handleInput();\n"
            code += "handleInput();"
            return code

    def _generate_typescript_code(self, concepts: set, prompt: str) -> str:
        """Generate TypeScript code based on concepts."""
        if "interface" in concepts or "type" in concepts or "class" in concepts:
            # Generate TypeScript with interfaces and classes
            interface_name = "".join(
                w.capitalize()
                for w in random.choice(["data", "user", "item", "config"]).split()
            )
            class_name = interface_name + "Service"

            code = f"interface {interface_name} {{\n"
            code += "  id: string;\n"
            code += "  name: string;\n"
            code += "  value: number;\n"
            code += "  createdAt: Date;\n"
            code += "  metadata?: Record<string, any>;\n"
            code += "}\n\n"

            code += (
                f"type {interface_name}Status = 'active' | 'inactive' | 'pending';\n\n"
            )

            code += f"class {class_name} {{\n"
            code += "  private items: Map<string, " + interface_name + ">;\n"
            code += "  private status: Map<string, " + interface_name + "Status>;\n\n"

            code += "  constructor() {\n"
            code += "    this.items = new Map();\n"
            code += "    this.status = new Map();\n"
            code += "  }\n\n"

            code += f"  create(name: string, value: number, metadata?: Record<string, any>): {interface_name} {{\n"
            code += "    const id = this.generateId();\n"
            code += "    const now = new Date();\n"
            code += "    const item = { id, name, value, createdAt: now, metadata };\n"
            code += "    this.items.set(id, item);\n"
            code += "    this.status.set(id, 'active');\n"
            code += "    return item;\n"
            code += "  }\n\n"

            code += f"  get(id: string): {interface_name} | undefined {{\n"
            code += "    return this.items.get(id);\n"
            code += "  }\n\n"

            code += f"  getStatus(id: string): {interface_name}Status | undefined {{\n"
            code += "    return this.status.get(id);\n"
            code += "  }\n\n"

            code += (
                "  update(id: string, updates: Partial<"
                + interface_name
                + ">): boolean {\n"
            )
            code += "    const item = this.items.get(id);\n"
            code += "    if (!item) return false;\n\n"
            code += "    this.items.set(id, { ...item, ...updates });\n"
            code += "    return true;\n"
            code += "  }\n\n"

            code += "  private generateId(): string {\n"
            code += "    return Math.random().toString(36).substr(2, 9);\n"
            code += "  }\n"
            code += "}\n\n"

            code += "// Example usage\n"
            code += f"const service = new {class_name}();\n"
            code += "const item = service.create('Example', 42, { tags: ['test'] });\n"
            code += "console.log(item);\n"
            code += "console.log(`Status: ${service.getStatus(item.id)}`);\n\n"
            code += "// Update the item\n"
            code += "service.update(item.id, { value: 100 });\n"
            code += "console.log(service.get(item.id));"

            return code
        else:
            # Default to JS-style with TypeScript types
            return (
                self._generate_javascript_code(concepts, prompt)
                .replace("function", "function")
                .replace(
                    "const utils = {",
                    "interface Utils {\n  formatDate(date: Date | string): string;\n  generateId(prefix?: string): string;\n  debounce<T extends (...args: any[]) => any>(func: T, wait: number): (...args: Parameters<T>) => void;\n}\n\nconst utils: Utils = {",
                )
                .replace(".padStart(2, '0')", ".padStart(2, '0' as string)")
            )

    def _generate_java_code(self, concepts: set, prompt: str) -> str:
        """Generate Java code based on concepts."""
        class_name = "".join(
            w.capitalize()
            for w in random.choice(["data", "user", "processing", "service"]).split()
        )

        code = f"import java.util.HashMap;\nimport java.util.Map;\nimport java.time.LocalDateTime;\nimport java.time.format.DateTimeFormatter;\n\npublic class {class_name} {{\n"

        # Add class fields
        code += "    private String name;\n"
        code += "    private int value;\n"
        code += "    private LocalDateTime createdAt;\n"
        code += "    private Map<String, Object> properties;\n\n"

        # Constructor
        code += f"    public {class_name}(String name, int value) {{\n"
        code += "        this.name = name;\n"
        code += "        this.value = value;\n"
        code += "        this.createdAt = LocalDateTime.now();\n"
        code += "        this.properties = new HashMap<>();\n"
        code += "    }\n\n"

        # Methods
        code += "    public int processValue() {\n"
        code += "        return this.value * 2;\n"
        code += "    }\n\n"

        code += "    public void addProperty(String key, Object value) {\n"
        code += "        this.properties.put(key, value);\n"
        code += "    }\n\n"

        code += "    public Object getProperty(String key) {\n"
        code += "        return this.properties.get(key);\n"
        code += "    }\n\n"

        code += "    @Override\n"
        code += "    public String toString() {\n"
        code += "        DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;\n"
        code += "        return String.format(\"%s(name='%s', value=%d, createdAt='%s', properties=%s)\",\n"
        code += f"                {class_name}.class.getSimpleName(),\n"
        code += "                this.name,\n"
        code += "                this.value,\n"
        code += "                this.createdAt.format(formatter),\n"
        code += "                this.properties);\n"
        code += "    }\n\n"

        # Main method
        code += "    public static void main(String[] args) {\n"
        code += f'        {class_name} instance = new {class_name}("example", 42);\n'
        code += '        instance.addProperty("category", "test");\n'
        code += '        instance.addProperty("active", true);\n\n'
        code += "        System.out.println(instance);\n"
        code += '        System.out.println("Processed value: " + instance.processValue());\n'
        code += "    }\n"

        code += "}"
        return code

    def _generate_cpp_code(self, concepts: set, prompt: str) -> str:
        """Generate C++ code based on concepts."""
        class_name = "".join(
            w.capitalize()
            for w in random.choice(["data", "user", "processor", "calculator"]).split()
        )

        code = "#include <iostream>\n"
        code += "#include <string>\n"
        code += "#include <unordered_map>\n"
        code += "#include <vector>\n"
        code += "#include <ctime>\n\n"

        code += f"class {class_name} {{\nprivate:\n"
        code += "    std::string name;\n"
        code += "    int value;\n"
        code += "    time_t createdAt;\n"
        code += "    std::unordered_map<std::string, std::string> properties;\n\n"

        code += "public:\n"
        code += f"    {class_name}(const std::string& name, int value) : name(name), value(value) {{\n"
        code += "        createdAt = time(nullptr);\n"
        code += "    }}\n\n"

        code += "    int processValue() const {\n"
        code += "        return value * 2;\n"
        code += "    }\n\n"

        code += (
            "    void addProperty(const std::string& key, const std::string& value) {\n"
        )
        code += "        properties[key] = value;\n"
        code += "    }\n\n"

        code += "    std::string getProperty(const std::string& key) const {\n"
        code += "        auto it = properties.find(key);\n"
        code += "        if (it != properties.end()) {\n"
        code += "            return it->second;\n"
        code += "        }\n"
        code += '        return "";\n'
        code += "    }\n\n"

        code += (
            "    friend std::ostream& operator<<(std::ostream& os, const "
            + class_name
            + "& obj) {\n"
        )
        code += (
            '        os << "'
            + class_name
            + '(name=\'" << obj.name << "\', value=" << obj.value << ", ";\n'
        )
        code += '        os << "createdAt=\'" << std::ctime(&obj.createdAt) << "\', properties={";\n'
        code += "        \n"
        code += "        bool first = true;\n"
        code += "        for (const auto& pair : obj.properties) {\n"
        code += '            if (!first) os << ", ";\n'
        code += '            os << pair.first << ": \'" << pair.second << "\'";\n'
        code += "            first = false;\n"
        code += "        }\n"
        code += '        os << "})";\n'
        code += "        return os;\n"
        code += "    }\n"
        code += "};\n\n"

        code += "int main() {\n"
        code += f'    {class_name} instance("example", 42);\n'
        code += '    instance.addProperty("category", "test");\n'
        code += '    instance.addProperty("status", "active");\n\n'
        code += "    std::cout << instance << std::endl;\n"
        code += '    std::cout << "Processed value: " << instance.processValue() << std::endl;\n'
        code += "    \n"
        code += "    return 0;\n"
        code += "}"

        return code

    def _generate_generic_code(self, language: str, concepts: set, prompt: str) -> str:
        """Generate generic code for other languages."""
        func_name = random.choice(
            ["processData", "calculateValue", "transformInput", "handleRequest"]
        )

        # Create a simple generic function
        code = f"// Example {language} function\n"
        code += f"function {func_name}(data) {{\n"
        code += "  // Initialize result object/map\n"
        code += "  let result = {};\n\n"
        code += "  // Check data type\n"
        code += "  if (Array.isArray(data)) {{\n"
        code += "    result.type = 'array';\n"
        code += "    result.length = data.length;\n"
        code += "  }} else if (typeof data === 'object') {{\n"
        code += "    result.type = 'object';\n"
        code += "    result.keys = Object.keys(data);\n"
        code += "  }} else {{\n"
        code += "    result.type = typeof data;\n"
        code += "    result.value = String(data);\n"
        code += "  }}\n\n"
        code += "  // Add timestamp\n"
        code += "  result.timestamp = new Date().toISOString();\n\n"
        code += "  return result;\n"
        code += "}}\n\n"
        code += "// Example usage\n"
        code += f"const output = {func_name}([1, 2, 3, 'test']);\n"
        code += "console.log(output);\n"

        return code
