#!/usr/bin/env python3
"""
TalkBridge Ollama - Prompt Engineer
===================================

Module engine

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- requests
======================================================================
Functions:
- __init__: Initialize prompt engineer.
- _load_default_templates: Load default prompt templates.
- add_template: Add a prompt template.
- get_template: Get a prompt template by name.
- list_templates: List prompt templates.
- render_template: Render a prompt template with variables.
- test_prompt: Test a prompt with a model.
- _calculate_similarity: Calculate similarity between response and expected response.
- optimize_prompt: Optimize a prompt to get closer to target response.
- batch_test_templates: Test multiple templates with test cases.
======================================================================
"""

import json
import time
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from .ollama_client import OllamaClient


@dataclass
class PromptTemplate:
    """Prompt template data class."""
    name: str
    description: str
    template: str
    variables: List[str]
    category: str
    tags: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PromptResult:
    """Prompt result data class."""
    prompt: str
    response: str
    model: str
    timestamp: float
    performance_metrics: Optional[Dict[str, Any]] = None


class PromptEngineer:
    """
    Manages and optimizes prompts for Ollama models.
    """
    
    def __init__(self, client: Optional[OllamaClient] = None):
        """
        Initialize prompt engineer.
        
        Args:
            client: Ollama client instance
        """
        self.client = client or OllamaClient()
        self.templates: Dict[str, PromptTemplate] = {}
        self.results: List[PromptResult] = []
        self.default_model = "llama2"
        
        # Load default templates
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default prompt templates."""
        default_templates = [
            PromptTemplate(
                name="code_assistant",
                description="Assistant for coding tasks",
                template="You are a helpful coding assistant. Please help me with the following task:\n\n{task}\n\nProvide clear, well-documented code with explanations.",
                variables=["task"],
                category="coding",
                tags=["programming", "code", "development"]
            ),
            PromptTemplate(
                name="text_summarizer",
                description="Summarize text content",
                template="Please summarize the following text in a concise manner:\n\n{text}\n\nSummary:",
                variables=["text"],
                category="text_processing",
                tags=["summarization", "text", "content"]
            ),
            PromptTemplate(
                name="question_answerer",
                description="Answer questions based on context",
                template="Based on the following context, please answer the question:\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
                variables=["context", "question"],
                category="qa",
                tags=["question", "answer", "context"]
            ),
            PromptTemplate(
                name="creative_writer",
                description="Creative writing assistant",
                template="You are a creative writing assistant. Please help me write about:\n\n{topic}\n\nStyle: {style}\n\nWrite a creative piece:",
                variables=["topic", "style"],
                category="writing",
                tags=["creative", "writing", "story"]
            ),
            PromptTemplate(
                name="data_analyzer",
                description="Analyze data and provide insights",
                template="Please analyze the following data and provide insights:\n\n{data}\n\nAnalysis:",
                variables=["data"],
                category="analysis",
                tags=["data", "analysis", "insights"]
            )
        ]
        
        for template in default_templates:
            self.add_template(template)
    
    def add_template(self, template: PromptTemplate) -> bool:
        """
        Add a prompt template.
        
        Args:
            template: Prompt template to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.templates[template.name] = template
            return True
        except Exception as e:
            print(f"Error adding template: {e}")
            return False
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a prompt template by name.
        
        Args:
            name: Template name
            
        Returns:
            Prompt template or None if not found
        """
        return self.templates.get(name)
    
    def list_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """
        List prompt templates.
        
        Args:
            category: Filter by category (optional)
            
        Returns:
            List of prompt templates
        """
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    def render_template(self, template_name: str, variables: Dict[str, str]) -> Optional[str]:
        """
        Render a prompt template with variables.
        
        Args:
            template_name: Name of the template
            variables: Variables to substitute
            
        Returns:
            Rendered prompt or None if error
        """
        template = self.get_template(template_name)
        if not template:
            return None
        
        try:
            rendered = template.template
            
            # Replace variables in template
            for var_name, value in variables.items():
                placeholder = f"{{{var_name}}}"
                rendered = rendered.replace(placeholder, str(value))
            
            return rendered
        except Exception as e:
            print(f"Error rendering template: {e}")
            return None
    
    def test_prompt(self, prompt: str, model: Optional[str] = None,
                   expected_response: Optional[str] = None) -> PromptResult:
        """
        Test a prompt with a model.
        
        Args:
            prompt: Prompt to test
            model: Model to use (optional)
            expected_response: Expected response for evaluation (optional)
            
        Returns:
            Prompt result
        """
        model = model or self.default_model
        start_time = time.time()
        
        try:
            response = self.client.generate(model, prompt)
            end_time = time.time()
            
            # Calculate performance metrics
            performance_metrics = {
                'response_time': end_time - start_time,
                'response_length': len(response) if response else 0,
                'prompt_length': len(prompt)
            }
            
            if expected_response and response:
                # Simple similarity metric
                similarity = self._calculate_similarity(response, expected_response)
                performance_metrics['similarity'] = similarity
            
            result = PromptResult(
                prompt=prompt,
                response=response or "",
                model=model,
                timestamp=start_time,
                performance_metrics=performance_metrics
            )
            
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"Error testing prompt: {e}")
            return PromptResult(
                prompt=prompt,
                response="",
                model=model,
                timestamp=start_time,
                performance_metrics={'error': str(e)}
            )
    
    def _calculate_similarity(self, response: str, expected: str) -> float:
        """
        Calculate similarity between response and expected response.
        
        Args:
            response: Actual response
            expected: Expected response
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Simple word overlap similarity
        response_words = set(response.lower().split())
        expected_words = set(expected.lower().split())
        
        if not expected_words:
            return 0.0
        
        intersection = response_words.intersection(expected_words)
        union = response_words.union(expected_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def optimize_prompt(self, base_prompt: str, target_response: str,
                       model: Optional[str] = None, iterations: int = 5) -> str:
        """
        Optimize a prompt to get closer to target response.
        
        Args:
            base_prompt: Base prompt to optimize
            target_response: Target response
            model: Model to use (optional)
            iterations: Number of optimization iterations
            
        Returns:
            Optimized prompt
        """
        model = model or self.default_model
        current_prompt = base_prompt
        best_similarity = 0.0
        best_prompt = base_prompt
        
        for i in range(iterations):
            # Test current prompt
            result = self.test_prompt(current_prompt, model)
            
            if result.response:
                similarity = self._calculate_similarity(result.response, target_response)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_prompt = current_prompt
                
                print(f"Iteration {i+1}: Similarity = {similarity:.3f}")
                
                # Simple optimization: add more context if similarity is low
                if similarity < 0.3:
                    current_prompt = f"{base_prompt}\n\nPlease be more specific and detailed in your response."
                elif similarity < 0.6:
                    current_prompt = f"{base_prompt}\n\nFocus on the key points and provide a structured response."
        
        return best_prompt
    
    def batch_test_templates(self, template_names: List[str], 
                           test_cases: List[Dict[str, str]],
                           model: Optional[str] = None) -> Dict[str, List[PromptResult]]:
        """
        Test multiple templates with test cases.
        
        Args:
            template_names: List of template names to test
            test_cases: List of test cases with variables
            model: Model to use (optional)
            
        Returns:
            Dictionary of results for each template
        """
        results = {}
        model = model or self.default_model
        
        for template_name in template_names:
            template = self.get_template(template_name)
            if not template:
                continue
            
            template_results = []
            
            for test_case in test_cases:
                # Render template
                prompt = self.render_template(template_name, test_case)
                if prompt:
                    # Test the prompt
                    result = self.test_prompt(prompt, model)
                    template_results.append(result)
            
            results[template_name] = template_results
        
        return results
    
    def analyze_prompt_performance(self, template_name: str) -> Dict[str, Any]:
        """
        Analyze performance of a prompt template.
        
        Args:
            template_name: Name of the template to analyze
            
        Returns:
            Performance analysis dictionary
        """
        template = self.get_template(template_name)
        if not template:
            return {}
        
        # Get results for this template
        template_results = [r for r in self.results if template_name in r.prompt]
        
        if not template_results:
            return {'error': 'No results found for template'}
        
        # Calculate metrics
        response_times = [r.performance_metrics.get('response_time', 0) for r in template_results]
        response_lengths = [r.performance_metrics.get('response_length', 0) for r in template_results]
        
        return {
            'template_name': template_name,
            'total_tests': len(template_results),
            'average_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'average_response_length': sum(response_lengths) / len(response_lengths) if response_lengths else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'success_rate': len([r for r in template_results if r.response]) / len(template_results)
        }
    
    def export_templates(self, filename: str) -> bool:
        """
        Export templates to JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            templates_data = []
            for template in self.templates.values():
                templates_data.append(asdict(template))
            
            with open(filename, 'w') as f:
                json.dump(templates_data, f, indent=2)
            
            print(f"Exported templates to: {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting templates: {e}")
            return False
    
    def import_templates(self, filename: str) -> bool:
        """
        Import templates from JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'r') as f:
                templates_data = json.load(f)
            
            for template_data in templates_data:
                template = PromptTemplate(**template_data)
                self.add_template(template)
            
            print(f"Imported {len(templates_data)} templates from: {filename}")
            return True
            
        except Exception as e:
            print(f"Error importing templates: {e}")
            return False
    
    def search_templates(self, query: str) -> List[PromptTemplate]:
        """
        Search templates by name, description, or tags.
        
        Args:
            query: Search query
            
        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        matching_templates = []
        
        for template in self.templates.values():
            # Search in name
            if query_lower in template.name.lower():
                matching_templates.append(template)
                continue
            
            # Search in description
            if query_lower in template.description.lower():
                matching_templates.append(template)
                continue
            
            # Search in tags
            for tag in template.tags:
                if query_lower in tag.lower():
                    matching_templates.append(template)
                    break
        
        return matching_templates
    
    def get_template_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all templates.
        
        Returns:
            Statistics dictionary
        """
        templates = list(self.templates.values())
        
        # Group by category
        category_counts = {}
        for template in templates:
            category = template.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count total variables
        total_variables = sum(len(template.variables) for template in templates)
        
        # Get most common tags
        all_tags = []
        for template in templates:
            all_tags.extend(template.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            'total_templates': len(templates),
            'categories': category_counts,
            'total_variables': total_variables,
            'average_variables_per_template': total_variables / len(templates) if templates else 0,
            'most_common_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }


if __name__ == "__main__":
    # Test the prompt engineer
    engineer = PromptEngineer()
    
    # List templates
    templates = engineer.list_templates()
    print(f"Available templates: {[t.name for t in templates]}")
    
    # Test a template
    if templates:
        template = templates[0]
        variables = {"task": "Write a Python function to calculate fibonacci numbers"}
        prompt = engineer.render_template(template.name, variables)
        
        if prompt:
            result = engineer.test_prompt(prompt)
            print(f"Test result: {result.response[:100]}...")
    
    # Get stats
    stats = engineer.get_template_stats()
    print(f"Template stats: {stats}") 