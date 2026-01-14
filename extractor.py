import os
import json
from typing import Dict, Any, List, Optional
from PIL import Image

class PromptExtractor:
    """Core extraction logic"""
    
    def extract_positive_prompts_comfyui(self, file_path: str) -> Dict[str, Any]:
        """Extract positive prompts using ComfyUI metadata (workflow/prompt)"""
        try:
            with Image.open(file_path) as img:
                if img.format != 'PNG':
                    raise ValueError(f"File is not a PNG: {img.format}")

                metadata = img.info
                result = {
                    'file_info': {
                        'filename': os.path.basename(file_path),
                        'size': img.size,
                        'mode': img.mode
                    },
                    'positive_prompts': [],
                    'extraction_method': 'comfyui'
                }

                processed_nodes = set()

                # Try workflow first
                if 'workflow' in metadata:
                    try:
                        workflow_data = json.loads(metadata['workflow'])
                        prompts = self.extract_positive_from_workflow(workflow_data, processed_nodes)
                        result['positive_prompts'].extend(prompts)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse workflow JSON: {e}")

                # Then prompt data if none found
                if not result['positive_prompts'] and 'prompt' in metadata:
                    try:
                        prompt_data = json.loads(metadata['prompt'])
                        prompts = self.extract_positive_from_prompt_data(prompt_data, processed_nodes)
                        result['positive_prompts'].extend(prompts)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse prompt JSON: {e}")

                return result

        except Exception as e:
            raise Exception(f"Error reading PNG file: {e}")

    def extract_positive_prompts_json(self, file_path: str) -> Dict[str, Any]:
        """Extract positive prompts from a JSON workflow file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            result = {
                'file_info': {
                    'filename': os.path.basename(file_path),
                    'size': 'N/A', 
                    'mode': 'JSON'
                },
                'positive_prompts': [],
                'extraction_method': 'json'
            }

            processed_nodes = set()

            # Try as workflow (has 'nodes' list)
            if isinstance(data, dict) and 'nodes' in data:
                prompts = self.extract_positive_from_workflow(data, processed_nodes)
                result['positive_prompts'].extend(prompts)
            
            # Try as API format (dict of nodes)
            if not result['positive_prompts'] and isinstance(data, dict):
                # Simple heuristic: keys are strings, values are dicts with 'class_type' or 'inputs'
                is_api_format = False
                for k, v in data.items():
                    if isinstance(v, dict) and ('class_type' in v or 'inputs' in v):
                        is_api_format = True
                        break
                
                if is_api_format:
                     prompts = self.extract_positive_from_prompt_data(data, processed_nodes)
                     result['positive_prompts'].extend(prompts)

            return result

        except Exception as e:
            raise Exception(f"Error reading JSON file: {e}")

    def extract_positive_prompts_parameters(self, file_path: str) -> Dict[str, Any]:
        """Extract positive prompt using Parameters metadata and direct PNG properties"""
        try:
            with Image.open(file_path) as img:
                if img.format != 'PNG':
                    raise ValueError(f"File is not a PNG: {img.format}")

                metadata = img.info
                result = {
                    'file_info': {
                        'filename': os.path.basename(file_path),
                        'size': img.size,
                        'mode': img.mode
                    },
                    'positive_prompts': [],
                    'extraction_method': 'parameters'
                }

                # First, try the parameters extraction
                prompt_text = self.extract_positive_from_parameters_strict(metadata)
                if prompt_text:
                    result['positive_prompts'].append({
                        'text': prompt_text,
                        'node_id': 'parameters',
                        'node_type': 'parameters',
                        'title': 'Parameters',
                        'source': 'parameters'
                    })
                else:
                    # If original method fails, try PNG properties as fallback
                    prompt_text = self.extract_positive_from_png_properties(metadata)
                    if prompt_text:
                        result['positive_prompts'].append({
                            'text': prompt_text,
                            'node_id': 'png_properties',
                            'node_type': 'png_properties',
                            'title': 'PNG Properties',
                            'source': 'png_properties'
                        })

                return result

        except Exception as e:
            raise Exception(f"Error reading PNG file: {e}")

    def extract_positive_from_workflow(self, workflow_data: Dict, processed_nodes: set) -> List[Dict]:
        """Extract positive prompts from workflow nodes"""
        positive_prompts = []
        nodes = workflow_data.get('nodes', [])

        for node in nodes:
            node_id = node.get('id')
            node_type = node.get('type', '')
            title = node.get('title', '').lower()

            if node_id in processed_nodes:
                continue

            if (node_type == 'CLIPTextEncode' or
                'cliptext' in node_type.lower() or
                node.get('properties', {}).get('Node name for S&R') == 'CLIPTextEncode'):

                widgets_values = node.get('widgets_values', [])

                if widgets_values and len(widgets_values) > 0:
                    prompt_text = widgets_values[0]

                    is_positive = (
                        'positive' in title or
                        'pos' in title or
                        (title == '' and isinstance(prompt_text, str) and prompt_text.strip() != '' and 'negative' not in prompt_text.lower()[:50]) or
                        (title == 'untitled' and isinstance(prompt_text, str) and prompt_text.strip() != '' and 'negative' not in prompt_text.lower()[:50])
                    )

                    is_negative = (
                        'negative' in title or
                        'neg' in title or
                        (isinstance(prompt_text, str) and (prompt_text.strip() == '' or prompt_text.lower().strip().startswith('negative')))
                    )

                    if isinstance(prompt_text, list):
                        prompt_text = '\n'.join(str(x) for x in prompt_text)

                    if is_positive and not is_negative and isinstance(prompt_text, (str, int, float)):
                        prompt_info = {
                            'text': str(prompt_text),
                            'node_id': node_id,
                            'node_type': node_type,
                            'title': node.get('title', 'Untitled'),
                            'source': 'workflow'
                        }

                        positive_prompts.append(prompt_info)
                        processed_nodes.add(node_id)

        return positive_prompts

    def extract_positive_from_prompt_data(self, prompt_data: Dict, processed_nodes: set) -> List[Dict]:
        """Extract positive prompts from prompt data structure"""
        positive_prompts = []

        for key, value in prompt_data.items():
            if isinstance(value, dict):
                class_type = value.get('class_type', '')

                if key in processed_nodes:
                    continue

                if class_type == 'CLIPTextEncode':
                    inputs = value.get('inputs', {})

                    text_content = None
                    if 'text' in inputs:
                        text_content = inputs['text']
                    elif 'prompt' in inputs:
                        text_content = inputs['prompt']

                    if text_content is None:
                        continue
                    if isinstance(text_content, list):
                        text_content = '\n'.join(str(i) for i in text_content)
                    elif not isinstance(text_content, str):
                        text_content = str(text_content)

                    if text_content.strip():
                        is_negative = (
                            'negative' in text_content.lower()[:50]
                        )

                        if not is_negative:
                            prompt_info = {
                                'text': text_content,
                                'node_id': key,
                                'class_type': class_type,
                                'title': f"Node {key}",
                                'source': 'prompt_data'
                            }

                            positive_prompts.append(prompt_info)
                            processed_nodes.add(key)

        return positive_prompts

    def extract_positive_from_png_properties(self, metadata: Dict) -> Optional[str]:
        """Extract positive prompt directly from PNG properties"""
        try:
            possible_keys = [
                'Positive prompt',
                'positive prompt', 
                'Positive Prompt',
                'positive_prompt'
            ]
            
            for key in possible_keys:
                if key in metadata:
                    value = metadata[key]
                    
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except Exception:
                            value = str(value)
                    elif not isinstance(value, str):
                        value = str(value)
                    
                    if value and value.strip():
                        result = value.strip()
                        if ((result.startswith('"') and result.endswith('"')) or 
                            (result.startswith("'") and result.endswith("'"))):
                            result = result[1:-1]
                        return result
            
            return None
            
        except Exception as e:
            print(f"PNG properties extractor error: {e}")
            return None

    def extract_positive_from_parameters_strict(self, metadata: Dict) -> Optional[str]:
        """Extract from parameters metadata with robust type handling"""
        try:
            if 'parameters' not in metadata:
                return None

            parameters_data = metadata['parameters']

            if isinstance(parameters_data, bytes):
                try:
                    parameters_data = parameters_data.decode('utf-8', errors='ignore')
                except Exception:
                    parameters_data = str(parameters_data)
            elif isinstance(parameters_data, (list, dict)):
                parameters_data = json.dumps(parameters_data, ensure_ascii=False)
            elif not isinstance(parameters_data, str):
                parameters_data = str(parameters_data)

            # Try JSON first
            try:
                parsed_params = json.loads(parameters_data)
                if isinstance(parsed_params, dict):
                    possible_keys = [
                        'Positive prompt',
                        'positive prompt',
                        'Positive Prompt',
                        'positive_prompt',
                        'prompt',
                        'Prompt'
                    ]
                    for key in possible_keys:
                        if key in parsed_params:
                            value = parsed_params[key]
                            if isinstance(value, list):
                                return '\n'.join(str(v) for v in value)
                            return str(value) if value is not None else None
            except json.JSONDecodeError:
                pass

            # Parse text format
            lines = parameters_data.split('\n')
            for i, line in enumerate(lines):
                line_stripped_lower = line.strip().lower()
                if line_stripped_lower.startswith('positive prompt:'):
                    prompt_text = line.split(':', 1)[1].strip() if ':' in line else ''
                    j = i + 1
                    prompt_lines = [prompt_text] if prompt_text else []
                    while j < len(lines):
                        next_line = lines[j]
                        nl = next_line.strip().lower()
                        if ':' in nl and any(param in nl for param in
                                             ['negative prompt', 'steps', 'sampler', 'cfg scale', 'seed', 'size', 'model', 'clip skip']):
                            break
                        prompt_lines.append(next_line.rstrip())
                        j += 1

                    full_prompt = '\n'.join(prompt_lines).rstrip()
                    out_lines = full_prompt.splitlines()
                    k = 0
                    while k < len(out_lines) and out_lines[k].strip() == '':
                        k += 1
                    return '\n'.join(out_lines[k:]) if k < len(out_lines) else None

            return None

        except Exception as e:
            print(f"Parameters extractor error: {e}")
            return None
