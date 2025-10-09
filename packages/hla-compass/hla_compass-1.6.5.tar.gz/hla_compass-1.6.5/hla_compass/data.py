"""
Data access utilities for HLA-Compass modules
"""

import logging
from typing import Any, Optional, List, Dict


logger = logging.getLogger(__name__)


class DataAccessError(Exception):
    """Error accessing HLA-Compass data"""

    pass


class BaseData:
    """Base class for data access"""

    def __init__(self, api_client=None, db_client=None):
        """
        Initialize data access with API client and optional database client.

        Args:
            api_client: API client from execution context
            db_client: Optional ScientificQuery database client for direct access
        """
        self.api = api_client
        self.db = db_client  # Direct database access when available
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _handle_api_error(self, error: Exception, operation: str):
        """Handle API errors consistently"""
        self.logger.error(f"API error during {operation}: {error}")
        raise DataAccessError(f"Failed to {operation}: {str(error)}")


class PeptideData(BaseData):
    """Access and query peptide data"""

    def search(
        self,
        sequence: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        mass: Optional[float] = None,
        mass_tolerance: Optional[float] = None,
        modifications: Optional[List[str]] = None,
        limit: int = 1000,
        offset: int = 0,
        similarity_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search peptides with various filters.

        Args:
            sequence: Peptide sequence (supports wildcards: % for any characters, _ for single)
            min_length: Minimum peptide length
            max_length: Maximum peptide length
            mass: Target mass for mass-based search
            mass_tolerance: Mass tolerance (Da or ppm)
            modifications: List of modifications to filter by
            limit: Maximum number of results
            offset: Pagination offset
            similarity_threshold: For similarity search when db client is available (0.0-1.0)

        Returns:
            List of peptide dictionaries
        """
        try:
            # Use direct database access if available
            if self.db and (sequence or (min_length and max_length)):
                self.logger.debug("Using direct database access for peptide search")

                if (
                    sequence and
                    similarity_threshold is not None and
                    similarity_threshold < 1.0
                ):
                    # Similarity search
                    return self.db.execute_function(
                        "search_peptides_by_similarity",
                        {
                            "target_sequence": sequence.replace("%", "").replace(
                                "_", ""
                            ),
                            "similarity_threshold": similarity_threshold,
                            "max_results": limit,
                        },
                    )
                elif sequence:
                    # Pattern search
                    return self.db.execute_function(
                        "search_peptides_by_sequence",
                        {"pattern": sequence, "max_results": limit},
                    )
                elif min_length is not None and max_length is not None:
                    # Length range search
                    return self.db.execute_function(
                        "search_peptides_by_length",
                        {
                            "min_length": min_length,
                            "max_length": max_length,
                            "max_results": limit,
                        },
                    )

            # Fall back to API access
            if not self.api:
                raise DataAccessError("No API client available for peptide search")

            filters = {}

            if sequence:
                filters["sequence"] = sequence
            if min_length is not None:
                filters["min_length"] = min_length
            if max_length is not None:
                filters["max_length"] = max_length
            if mass is not None:
                filters["mass"] = mass
                filters["mass_tolerance"] = mass_tolerance or 0.01
            if modifications:
                filters["modifications"] = modifications

            self.logger.debug(f"Searching peptides with filters: {filters}")

            result = self.api.get_peptides(filters=filters, limit=limit, offset=offset)

            self.logger.info(f"Found {len(result)} peptides")
            return result

        except Exception as e:
            self._handle_api_error(e, "search peptides")

    def get_by_id(self, peptide_id: str) -> Dict[str, Any]:
        """
        Get peptide by ID.

        Args:
            peptide_id: Peptide identifier

        Returns:
            Peptide dictionary
        """
        try:
            return self.api.get_peptide(peptide_id)
        except Exception as e:
            self._handle_api_error(e, f"get peptide {peptide_id}")

    def get_samples(self, peptide_id: str) -> List[Dict[str, Any]]:
        """
        Get all samples where a peptide was found.

        Args:
            peptide_id: Peptide identifier

        Returns:
            List of sample associations with abundance data
        """
        try:
            return self.api.get_peptide_samples(peptide_id)
        except Exception as e:
            self._handle_api_error(e, f"get samples for peptide {peptide_id}")

    def get_proteins(self, peptide_id: str) -> List[Dict[str, Any]]:
        """
        Get proteins containing a peptide.

        Args:
            peptide_id: Peptide identifier

        Returns:
            List of protein associations
        """
        try:
            return self.api.get_peptide_proteins(peptide_id)
        except Exception as e:
            self._handle_api_error(e, f"get proteins for peptide {peptide_id}")

    def search_by_hla(
        self, allele: str, binding_score_min: float = 0.0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search peptides associated with an HLA allele.

        Args:
            allele: HLA allele name (e.g., 'HLA-A*02:01')
            binding_score_min: Minimum binding score/intensity
            limit: Maximum number of results

        Returns:
            List of peptides with binding information
        """
        try:
            # Use direct database access if available
            if self.db:
                self.logger.debug(
                    f"Using direct database access for HLA search: {allele}"
                )
                return self.db.execute_function(
                    "search_peptides_by_hla",
                    {
                        "allele_name": allele,
                        "min_intensity": binding_score_min,
                        "max_results": limit,
                    },
                )

            # Fall back to API if available
            if self.api:
                # Prefer an explicit API method if provided
                if hasattr(self.api, "search_peptides_by_hla"):
                    return self.api.search_peptides_by_hla(
                        allele=allele, min_score=binding_score_min, limit=limit
                    )
                # Generic fallback using get_peptides with mapped filters
                return self.api.get_peptides(
                    filters={"hla_allele": allele, "min_intensity": binding_score_min},
                    limit=limit,
                    offset=0,
                )

            # If neither is available, raise error
            raise DataAccessError(f"HLA search not available for allele {allele}")

        except Exception as e:
            self._handle_api_error(e, f"search peptides by HLA {allele}")

    def query(
        self, filters: Dict[str, Any], limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query peptides with complex filters.

        This method supports both simple filters (via search) and
        complex queries when direct database access is available.

        Args:
            filters: Dictionary of filter criteria
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of matching peptides
        """
        # Check if we can use a specialized query
        if self.db:
            # Disease-based search
            if "disease" in filters:
                return self.db.execute_function(
                    "search_peptides_by_disease",
                    {
                        "disease_name": filters["disease"],
                        "min_intensity": filters.get("min_intensity", 0.0),
                        "max_results": limit,
                    },
                )

            # HLA allele search
            if "alleles" in filters and isinstance(filters["alleles"], list):
                # For multiple alleles, combine results
                all_results = []
                for allele in filters["alleles"][:5]:  # Limit to 5 alleles
                    results = self.search_by_hla(
                        allele=allele,
                        binding_score_min=filters.get("min_binding_score", 0.0),
                        limit=limit // len(filters["alleles"]),
                    )
                    all_results.extend(results)
                return all_results[:limit]

        # Fall back to basic search
        return self.search(
            sequence=filters.get("sequence"),
            min_length=filters.get("length", {}).get("gte"),
            max_length=filters.get("length", {}).get("lte"),
            mass=filters.get("mass"),
            mass_tolerance=filters.get("mass_tolerance"),
            limit=limit,
            offset=offset,
        )

    def to_dataframe(self, peptides: List[Dict[str, Any]]) -> Any:
        """
        Convert peptide list to pandas DataFrame.

        Args:
            peptides: List of peptide dictionaries

        Returns:
            DataFrame with peptide data
        """
        # Import pandas lazily to avoid hard dependency for non-data users
        try:
            import pandas as pd  # type: ignore
        except Exception as e:  # pragma: no cover
            raise DataAccessError(
                "pandas is required for DataFrame utilities. Install with: \n"
                "  pip install 'hla-compass[data]'\n"
                f"(original error: {e})"
            )

        if not peptides:
            return pd.DataFrame()

        df = pd.DataFrame(peptides)

        # Ensure standard columns exist
        standard_cols = ["id", "sequence", "length", "mass", "charge"]
        for col in standard_cols:
            if col not in df.columns:
                df[col] = None

        return df


class ProteinData(BaseData):
    """Access and query protein data"""

    def search(
        self,
        accession: Optional[str] = None,
        gene_name: Optional[str] = None,
        organism: Optional[str] = None,
        description: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Search proteins with various filters.

        Args:
            accession: UniProt accession number
            gene_name: Gene name (supports wildcards)
            organism: Organism name or taxonomy ID
            description: Text search in protein description
            min_length: Minimum protein length
            max_length: Maximum protein length
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of protein dictionaries
        """
        try:
            filters = {}

            if accession:
                filters["accession"] = accession
            if gene_name:
                filters["gene_name"] = gene_name
            if organism:
                filters["organism"] = organism
            if description:
                filters["description"] = description
            if min_length is not None:
                filters["min_length"] = min_length
            if max_length is not None:
                filters["max_length"] = max_length

            self.logger.debug(f"Searching proteins with filters: {filters}")

            result = self.api.get_proteins(filters=filters, limit=limit, offset=offset)

            self.logger.info(f"Found {len(result)} proteins")
            return result

        except Exception as e:
            self._handle_api_error(e, "search proteins")

    def get_by_id(self, protein_id: str) -> Dict[str, Any]:
        """
        Get protein by ID.

        Args:
            protein_id: Protein identifier

        Returns:
            Protein dictionary with full sequence
        """
        try:
            return self.api.get_protein(protein_id)
        except Exception as e:
            self._handle_api_error(e, f"get protein {protein_id}")

    def get_peptides(
        self, protein_id: str, unique_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all peptides from a protein.

        Args:
            protein_id: Protein identifier
            unique_only: Return only peptides unique to this protein

        Returns:
            List of peptide dictionaries
        """
        try:
            result = self.api.get_protein_peptides(protein_id)

            if unique_only:
                # Filter for unique peptides
                result = [p for p in result if p.get("is_unique", False)]

            return result
        except Exception as e:
            self._handle_api_error(e, f"get peptides for protein {protein_id}")

    def get_coverage(self, protein_id: str) -> Dict[str, Any]:
        """
        Get sequence coverage information for a protein.

        Args:
            protein_id: Protein identifier

        Returns:
            Coverage statistics and covered regions
        """
        try:
            return self.api.get_protein_coverage(protein_id)
        except Exception as e:
            self._handle_api_error(e, f"get coverage for protein {protein_id}")


class SampleData(BaseData):
    """Access and query sample data"""

    def search(
        self,
        sample_type: Optional[str] = None,
        tissue: Optional[str] = None,
        disease: Optional[str] = None,
        cell_line: Optional[str] = None,
        treatment: Optional[str] = None,
        experiment_type: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Search samples with various filters.

        Args:
            sample_type: Type of sample (e.g., 'tissue', 'cell_line', 'fluid')
            tissue: Tissue type
            disease: Disease association
            cell_line: Cell line name
            treatment: Treatment condition
            experiment_type: Type of experiment
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of sample dictionaries
        """
        try:
            filters = {}

            if sample_type:
                filters["sample_type"] = sample_type
            if tissue:
                filters["tissue"] = tissue
            if disease:
                filters["disease"] = disease
            if cell_line:
                filters["cell_line"] = cell_line
            if treatment:
                filters["treatment"] = treatment
            if experiment_type:
                filters["experiment_type"] = experiment_type

            self.logger.debug(f"Searching samples with filters: {filters}")

            result = self.api.get_samples(filters=filters, limit=limit, offset=offset)

            self.logger.info(f"Found {len(result)} samples")
            return result

        except Exception as e:
            self._handle_api_error(e, "search samples")

    def get_by_id(self, sample_id: str) -> Dict[str, Any]:
        """
        Get sample by ID.

        Args:
            sample_id: Sample identifier

        Returns:
            Sample dictionary with full metadata
        """
        try:
            return self.api.get_sample(sample_id)
        except Exception as e:
            self._handle_api_error(e, f"get sample {sample_id}")

    def get_peptides(
        self, sample_id: str, min_abundance: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all peptides found in a sample.

        Args:
            sample_id: Sample identifier
            min_abundance: Minimum abundance threshold

        Returns:
            List of peptides with abundance data
        """
        try:
            result = self.api.get_sample_peptides(sample_id)

            if min_abundance is not None:
                result = [p for p in result if p.get("abundance", 0) >= min_abundance]

            return result
        except Exception as e:
            self._handle_api_error(e, f"get peptides for sample {sample_id}")

class HLAData(BaseData):
    """Access HLA-related data"""

    def get_alleles(
        self, locus: Optional[str] = None, resolution: str = "2-digit"
    ) -> List[str]:
        """
        Get list of HLA alleles.

        Args:
            locus: HLA locus (e.g., 'A', 'B', 'C', 'DRB1')
            resolution: Allele resolution ('2-digit' or '4-digit')

        Returns:
            List of HLA allele names
        """
        try:
            return self.api.get_hla_alleles(locus=locus, resolution=resolution)
        except Exception as e:
            self._handle_api_error(e, "get HLA alleles")

    def get_frequencies(self, population: Optional[str] = None) -> Dict[str, float]:
        """
        Get HLA allele frequencies.

        Args:
            population: Population name (e.g., 'European', 'African', 'Asian')

        Returns:
            Dictionary of allele: frequency pairs
        """
        try:
            return self.api.get_hla_frequencies(population=population)
        except Exception as e:
            self._handle_api_error(e, "get HLA frequencies")

    def predict_binding(
        self, peptides: List[str], alleles: List[str], method: str = "netmhcpan"
    ) -> List[Dict[str, Any]]:
        """
        Predict HLA-peptide binding.

        Args:
            peptides: List of peptide sequences
            alleles: List of HLA alleles
            method: Prediction method

        Returns:
            List of predictions with scores
        """
        try:
            return self.api.predict_hla_binding(
                peptides=peptides, alleles=alleles, method=method
            )
        except Exception as e:
            self._handle_api_error(e, "predict HLA binding")
