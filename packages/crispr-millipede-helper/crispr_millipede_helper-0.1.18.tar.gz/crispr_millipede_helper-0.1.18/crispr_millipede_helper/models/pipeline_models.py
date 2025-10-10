from dataclasses import dataclass
from typing import Optional, List
import pandas as pd

@dataclass
class IndexPairPipelineBean:
    index2: str
    index1: str
    read1_fn: str
    read2_fn: Optional[str]
        
@dataclass
class CountResultOutputPipelineBean:
    screen_id: str
    count_result_fn: str
    protospacer_editing_efficiency: float
    surrogate_editing_efficiency: Optional[float]
    barcode_editing_efficiency: Optional[float]
        
    match_set_whitelist_reporter_observed_sequence_counter_series_results_fn: str
    mutations_results_fn: str
    linked_mutation_counters_fn: str
    protospacer_total_mutation_histogram_pdf_fn: str
    surrogate_total_mutation_histogram_pdf_fn: Optional[str]
    barcode_total_mutation_histogram_pdf_fn: Optional[str]
    surrogate_trinucleotide_mutational_signature_fn: Optional[str]
    surrogate_trinucleotide_positional_signature_fn: Optional[str]
    whitelist_guide_reporter_df_fn: str
    count_series_result_fn: str

@dataclass
class SampleAnnotationPipelineBean:
    sample_annotations_series: pd.Series
        
@dataclass
class SampleResultModel:
    sample_id: str
    index_pair_pipeline_bean: IndexPairPipelineBean
    sample_annotation_pipeline_bean: SampleAnnotationPipelineBean
    count_result_output_pipeline_bean: Optional[CountResultOutputPipelineBean] = None