"""
HLA-Compass UI Module Template

This template provides a complete starting point for modules with a user interface.
Replace the TODOs with your actual implementation.
"""

from hla_compass import Module
from typing import Dict, Any, List, Optional

# Runtime: the container image executes this Module via the platform's
# `module-runner`, so no separate handler shim is necessary.


class UIModule(Module):
    """
    Module with UI support
    
    This template includes:
    - Input validation
    - Data processing with UI feedback
    - Error handling
    - Result formatting for UI display
    """
    
    def __init__(self):
        """Initialize the module"""
        super().__init__()
        self.logger.info("Module initialized")
        
        # TODO: Initialize your resources here
        # self.model = self.load_model()
        # self.config = self.load_config()
    
    def execute(
        self, 
        input_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main execution function
        
        Args:
            input_data: User input from the UI
            context: Execution context (job_id, user_id, etc.)
            
        Returns:
            Dict with status, results, and UI-friendly data
        """
        try:
            # Step 1: Validate input
            validation_result = self._validate_input(input_data)
            if not validation_result['valid']:
                self.error(validation_result['message'])
            
            # Step 2: Extract parameters
            # TODO: Replace with your actual parameters
            param1 = input_data.get('param1')
            param2 = input_data.get('param2', 'default_value')
            
            self.logger.info(f"Processing with param1={param1}, param2={param2}")
            
            # Step 3: Process data
            # TODO: Implement your core logic here
            results = self._process_data(param1, param2)
            
            # Step 4: Format results for UI
            formatted_results = self._format_for_ui(results)
            
            # Step 5: Generate summary statistics
            summary = self._generate_summary(results)
            
            # Return successful response
            return self.success(
                results=formatted_results,
                summary=summary
            )
            
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            return self.error(f"Processing failed: {str(e)}")
    
    def _validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input
        
        Returns:
            Dict with 'valid' boolean and 'message' if invalid
        """
        # TODO: Implement your validation logic
        if 'param1' not in input_data:
            return {'valid': False, 'message': 'Missing required parameter: param1'}
        
        # Add more validation as needed
        # if not isinstance(input_data['param1'], str):
        #     return {'valid': False, 'message': 'param1 must be a string'}
        
        return {'valid': True}
    
    def _process_data(self, param1: Any, param2: Any) -> List[Dict[str, Any]]:
        """
        Core processing logic
        
        TODO: Replace with your actual processing
        """
        # Example: Query peptides
        # peptides = self.peptides.search(sequence=param1, limit=10)
        
        # Example: Process with model
        # predictions = self.model.predict(peptides)
        
        # Placeholder result
        results = [
            {
                'id': 'result_1',
                'value': f'Processed {param1} with {param2}',
                'score': 0.95,
                'metadata': {'source': 'example'}
            }
        ]
        
        return results
    
    def _format_for_ui(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format results for UI display
        
        Ensures data is in a format that's easy to render in React/TypeScript
        """
        formatted = []
        for item in results:
            formatted.append({
                'id': item.get('id'),
                'displayValue': item.get('value'),
                'score': round(item.get('score', 0), 3),
                'metadata': item.get('metadata', {})
            })
        return formatted
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for UI display
        """
        if not results:
            return {'total': 0, 'average_score': 0}
        
        scores = [r.get('score', 0) for r in results]
        return {
            'total': len(results),
            'average_score': round(sum(scores) / len(scores), 3),
            'max_score': round(max(scores), 3),
            'min_score': round(min(scores), 3)
        }
