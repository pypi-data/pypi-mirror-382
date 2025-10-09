import json
import uuid
from dataclasses import dataclass
from typing import Literal, List, get_origin, get_args
    

@dataclass
class Field:
    name: str
    content: str
    desc: str = None # This description is for optimizing the context when trainable is True
    title: str = None

    def render(self) -> str:
        if self.title is not None:
            context = (
                "{title}:\n"
                "{content}"
            ).format(title=self.title, content=self.content)
        else:
            context = self.content
        return context


@dataclass
class ModelContext:
        id: str = None
        input_template: str = None
        system_prompt_template: str = None
        system_prompt: List[Field] = None

        def to_json(self, path):
            data = {
                "input_template": self.input_template,
                "system_prompt_template": self.system_prompt_template,
                "system_prompt": [context.__dict__ for context in self.system_prompt] if self.system_prompt is not None else None,
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        
        @classmethod
        def from_json(cls, path):
            with open(path, "r") as f:
                data = json.load(f)
            return ModelContext(
                input_template=data.get("input_template", None),
                system_prompt_template=data.get("system_prompt_template", None),
                system_prompt=[Field(**context) for context in data.get("system_prompt", [])] if data.get("system_prompt", None) is not None else None,
            )

        def __post_init__(self):
            self.id = uuid.uuid4()
            if isinstance(self.system_prompt, str):
                self.system_prompt = [Field(name="system_prompt", content=self.system_prompt)]
            elif isinstance(self.system_prompt, list):
                self.system_prompt = self.system_prompt
            elif self.system_prompt is None:
                self.system_prompt = None
            else:
                raise ValueError("system_prompt must be either a string, a list of Context objects, or a SystemPrompt object")
            
        def update_system_prompt(self, name, content):
            for field in self.system_prompt:
                if field.name == name:
                    field.content = content

        def get_field_content(self, name):
            for field in self.system_prompt:
                if field.name == name:
                    return field.content
            return None

        def render_system_prompt(self, output_structure = None) -> str:
            if self.system_prompt is None:
                system_prompt = None

            if self.system_prompt_template is None:
                if self.system_prompt is None:
                    return None
                system_prompt = "\n\n".join(field.render() for field in self.system_prompt)
            else:
                system_prompt = self.system_prompt_template.format(**{field.name: field.render() for field in self.system_prompt})

            if (isinstance(output_structure, list) and isinstance(output_structure[0], dict)) or isinstance(output_structure, dict):
                is_list = isinstance(output_structure, list)
                if is_list:
                    output_structure = output_structure[0]

                schema = json.dumps({k: str(v).replace("typing.", "").replace("<class '", "").replace("'>", "") for k, v in output_structure.items()})
                items = []
                for item in schema[1:-1].split("\", \""):
                    if not item.startswith('"'):
                        item = '"' + item
                    if not item.endswith('"'):
                        item = item + '"'
                    key, value = item.split(": ")
                    value = value[1:-1]
                    item = f"{key}: {value}"
                    items.append(item)
                schema = "{" + ", ".join(items) + "}"
                system_prompt = system_prompt + "\n\n" if system_prompt is not None else ""
                if is_list:
                    system_prompt += (
                        "The final output must be a JSON array of objects that exactly match the following schema:\n"
                        "```json\n"
                        "[{output_structure}]\n"
                        "```"
                    ).format(output_structure=schema)
                else:
                    system_prompt += (
                        "The final output must be a single JSON that exactly matches the following schema:\n"
                        "```json\n"
                        "{output_structure}\n"
                        "```"
                    ).format(output_structure=schema)
            elif get_origin(output_structure) == Literal:
                keywords = "\n".join(list(get_args(output_structure)))
                system_prompt = system_prompt + "\n\n" if system_prompt is not None else ""
                system_prompt += (
                    "The final output must be a one of the following keyword:\n"
                    "{keywords}"
                ).format(keywords=keywords)
            return system_prompt
            
        def render_input(self, input_instance) -> str:
            input_instance = input_instance.to_dict()
            if self.input_template is None:
                return "\n\n".join([f"{key.capitalize()}: {value}" for key, value in input_instance.items()])
            else:
                kwargs = {key: value for key, value in input_instance.items()}
                # Remove keys that are not in the template
                for key in list(kwargs.keys()):
                    if f"{{{key}}}" not in self.input_template:
                        kwargs.pop(key)
                return self.input_template.format(**kwargs)


if __name__ == "__main__":
    model_context = ModelContext(
        system_prompt=[
            Field(name="task_definition", content="Given a topic, generate a list of people related to the topic.", title="Task Definition"),
            Field(name="method", content="Think step by step before answering.", title="Methodology"),
        ],
    )
    print(model_context.render_system_prompt())