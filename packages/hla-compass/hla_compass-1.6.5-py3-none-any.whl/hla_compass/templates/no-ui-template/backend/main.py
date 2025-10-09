"""
HLA-Compass NO-UI Module Template

This template is for backend-only modules without a user interface.
Ideal for data processing, batch operations, API integrations, and automated workflows.
"""

from hla_compass import Module
from typing import Dict, Any, List, Optional
import json

# Runtime: the platform's container runner (`module-runner`) instantiates this
# Module class directly—no additional handler shim is required.


class NoUIModule(Module):
    """
    Backend-only module without UI
    
    This template includes:
    - Input validation
    - Batch processing
    - Data transformation
    - Storage operations
    - API response formatting
    """
    
    def __init__(self):
        """Initialize the module"""
        super().__init__()
        self.logger.info("Backend module initialized")
        
        # TODO: Initialize your resources
        # self.processor = self.initialize_processor()
        # self.validator = self.initialize_validator()
    
    def execute(
        self, 
        input_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main execution function for backend processing
        
        Args:
            input_data: Input parameters (from API, scheduler, or other modules)
            context: Execution context with metadata
            
        Returns:
            Dict with processing results and metadata
        """
        try:
            # Log execution start
            job_id = context.get('job_id', 'unknown')
            self.logger.info(f"Starting job {job_id}")
            
            # Step 1: Validate input
            validation_result = self._validate_input(input_data)
            if not validation_result['valid']:
                self.error(
                    message=validation_result['message'],
                    details=validation_result.get('details', {})
                )
            
            # Step 2: Extract and prepare data
            data_source = input_data.get('data_source')  # file path, S3 key, or data array
            processing_options = input_data.get('options', {})
            
            # Step 3: Load/fetch data
            data = self._load_data(data_source)
            self.logger.info(f"Loaded {len(data)} items for processing")
            
            # Step 4: Process data in batches
            batch_size = processing_options.get('batch_size', 100)
            results = self._process_in_batches(data, batch_size, processing_options)
            
            # Step 5: Store results if needed
            output_location = None
            if processing_options.get('save_results', False):
                output_location = self._save_results(results, job_id)
            
            # Step 6: Generate processing report
            report = self._generate_report(results, data)
            
            # Return successful response
            return self.success(
                results={
                    'processed_count': len(results),
                    'output_location': output_location,
                    'report': report
                },
                summary={'processed': len(results), 'input_count': len(data)}
            )
            
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}", exc_info=True)
            return self.error(
                message="Processing failed",
                details={'error': str(e), 'type': type(e).__name__}
            )
    
    def _validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive input validation
        """
        # Check required fields
        if 'data_source' not in input_data:
            return {
                'valid': False,
                'message': 'Missing required field: data_source',
                'details': {'required_fields': ['data_source']}
            }
        
        # Validate data source format
        data_source = input_data['data_source']
        if not self._is_valid_data_source(data_source):
            return {
                'valid': False,
                'message': 'Invalid data source format',
                'details': {'accepted_formats': ['file_path', 's3_uri', 'array']}
            }
        
        # Validate options if provided
        if 'options' in input_data:
            options = input_data['options']
            if not isinstance(options, dict):
                return {
                    'valid': False,
                    'message': 'Options must be a dictionary'
                }
            
            # Validate specific options
            if 'batch_size' in options:
                if not isinstance(options['batch_size'], int) or options['batch_size'] < 1:
                    return {
                        'valid': False,
                        'message': 'batch_size must be a positive integer'
                    }
        
        return {'valid': True}
    
    def _is_valid_data_source(self, data_source: Any) -> bool:
        """Check if data source is valid"""
        # TODO: Implement your validation logic
        if isinstance(data_source, str):
            # File path or S3 URI
            return True
        elif isinstance(data_source, list):
            # Direct data array
            return True
        return False
    
    def _load_data(self, data_source: Any) -> List[Any]:
        """
        Load data from various sources
        """
        if isinstance(data_source, list):
            # Direct data provided
            return data_source
        
        elif isinstance(data_source, str):
            if data_source.startswith('s3://'):
                # Load from S3
                # data = self.storage.load_from_s3(data_source)
                # return json.loads(data)
                pass
            else:
                # Load from file system
                # with open(data_source, 'r') as f:
                #     return json.load(f)
                pass
        
        # TODO: Replace with actual data loading
        # Example: Load peptides from database
        # return self.peptides.search(limit=1000)
        
        # Placeholder data
        return [
            {'id': i, 'value': f'item_{i}'} 
            for i in range(10)
        ]
    
    def _process_in_batches(
        self, 
        data: List[Any], 
        batch_size: int,
        options: Dict[str, Any]
    ) -> List[Any]:
        """
        Process data in batches for better performance
        """
        results = []
        total_batches = (len(data) + batch_size - 1) // batch_size
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            self.logger.info(f"Processing batch {batch_num}/{total_batches}")
            
            # Process batch
            batch_results = self._process_batch(batch, options)
            results.extend(batch_results)
            
            # Update progress if needed
            # self.update_progress(batch_num / total_batches)
        
        return results
    
    def _process_batch(
        self, 
        batch: List[Any],
        options: Dict[str, Any]
    ) -> List[Any]:
        """
        Process a single batch of data
        
        # TODO: Implement your processing logic
        """
        processed = []
        
        for item in batch:
            # Example processing
            result = {
                'original_id': item.get('id') if isinstance(item, dict) else None,
                'processed_value': str((item.get('value') if isinstance(item, dict) else item) or '').upper(),
                'score': 0.85,  # TODO: Calculate actual score
                'metadata': {
                    'processed_with': options,
                    'timestamp': self.get_timestamp()
                }
            }
            processed.append(result)
        
        return processed
    
    def _save_results(self, results: List[Any], job_id: str) -> str:
        """
        Save results to storage
        """
        # TODO: Implement your storage logic
        output_key = f"results/{job_id}/output.json"
        
        # Example: Save to S3
        # self.storage.save(output_key, json.dumps(results))
        
        # Example: Save to database
        # self.database.insert_results(job_id, results)
        
        self.logger.info(f"Results saved to {output_key}")
        return output_key
    
    def _generate_report(
        self, 
        results: List[Any],
        original_data: List[Any]
    ) -> Dict[str, Any]:
        """
        Generate a processing report with statistics
        """
        if not results:
            return {
                'status': 'no_results',
                'processed': 0,
                'failed': 0
            }
        
        # Calculate statistics
        scores = [r.get('score', 0) for r in results if 'score' in r]
        
        report = {
            'status': 'completed',
            'input_count': len(original_data),
            'output_count': len(results),
            'processing_rate': len(results) / len(original_data) if original_data else 0,
            'statistics': {
                'average_score': sum(scores) / len(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'min_score': min(scores) if scores else 0
            }
        }
        
        return report
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
