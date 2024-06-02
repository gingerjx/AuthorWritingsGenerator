from typing import Dict, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from src.generator.generated_text import GeneratedText

class TextGenerator:
    
    def __init__(self, 
                 models: Dict[str, BaseChatModel],
                 queries_path: str,
                 authors_path: str,
                 response_length: int = 5000):
        self.models = models
        self.authors = open(authors_path, 'r', encoding='utf-8').read().split('\n')[:2]
        self.queries = open(queries_path, 'r', encoding='utf-8').read().split('\n')[:2]
        self.response_length = response_length

    def generate(self) -> List[GeneratedText]:
        generated_texts = []
        for model_name, model in self.models.items():
            for author_name in self.authors:
                for query in self.queries:
                    prompt_template = self._get_prompt_template()
                    generated_text = self._generate_internal(model, 
                                                             prompt_template, 
                                                             query,
                                                             author_name)
                    generated_texts.append(
                        self._transform(generated_text.content,
                                        model_name,
                                        author_name,
                                        query
                        )
                    )
        return generated_texts
    
    def _generate_internal(self, 
                           model: BaseChatModel, 
                           prompt_template: ChatPromptTemplate, 
                           query: str, 
                           author_name: str):
        chain = prompt_template | model
        return chain.invoke(
            {
                "author": author_name,
                "response_length": self.response_length,
                "query": query
            }
        )
    
    def _get_prompt_template(self):
        return ChatPromptTemplate.from_messages([
            ("system", 
            "Come up with the answer in {author}'s writing style. Don't use direct references and citations of {author}. Answer in plain text format. Use {response_length} words."),
            ("human", 
            "{query}"),
        ])
    
    def _transform(self, 
                   generated_text: str, 
                   model_name: str, 
                   author_name: str,
                   query: str) -> GeneratedText:
        return GeneratedText(
            text=generated_text,
            requested_response_length=self.response_length,
            model_name=model_name,
            author_name=author_name,
            prompt_template=self._get_prompt_template(),
            query=query
        )