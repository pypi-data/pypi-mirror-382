import json
import pandas as pd
from collections import defaultdict
from typing import List
from copy import deepcopy
import ast
from typing import List, Dict
import os
import fitz
from copy import deepcopy
import hashlib
import base64
from google.cloud import storage
from ..models.pipeline_models import (IndexPairPipelineBean, CountResultOutputPipelineBean, SampleAnnotationPipelineBean, SampleResultModel)

def read_pipeline_output_json(pipeline_output_json_fn):
    with open(pipeline_output_json_fn) as fn:
        pipeline_output_json_dict = json.load(fn)
        
    # TODO: Could process into beans here, or just convert into DefaultDict. I prefer a fully processed structure
    return pipeline_output_json_dict

#
# Recursive function for pre-processing pipeline elements into canonical Python types
#
def process_pipeline_element(pipeline_element):
    if type(pipeline_element) is dict:
        if ('left' in pipeline_element.keys()) and ('right' in pipeline_element.keys()): # THIS IS A PAIR
            return (process_pipeline_element(pipeline_element["left"]), process_pipeline_element(pipeline_element["right"])) # RETURN AS TUPLE
        else: # THIS IS A MAP
            new_dict_wrapper = defaultdict()
            for key in pipeline_element.keys():
                pipeline_subelement = pipeline_element[key]
                new_dict_wrapper[key] = process_pipeline_element(pipeline_subelement)
            return new_dict_wrapper # RETURN AS DEFAULTDICT
    elif type(pipeline_element) is list: # THIS IS AN ARRAY
        new_list_wrapper = list()
        for pipeline_subelement in pipeline_element:
            new_list_wrapper.append(process_pipeline_element(pipeline_subelement))
        return new_list_wrapper # RETURN AS ARRAY
    else:
        return pipeline_element

"""
    IMPORTANT TODO:
    - Handle optional arguments (i.e. surrogate, barcode, read2 arguments). Maybe convert dict to default dict with None as default value
    - Need to ensure that the corresponding sample is the same between different indices of the output types: output_screen_countResults_map, output_screen_editingEfficiencies_map, output_screen_supplementaryFiles_map
        - Can do some assertions, or better yet, build a helper function that converts Maps/Pairs into Dict/
"""
def retrieve_demultiplex_sample_result_model_list(samples_json_selected_local: List[Dict],
    index2_attribute_name="index2",
    index2_attribute_name_backup="barcode_index",
    index1_attribute_name="index1",
    index1_attribute_name_backup="i5_index",
    read1_fn_attribute_name="read1_fn",
    read2_fn_attribute_name="read2_fn",
    output_count_result_attribute_name="output_count_result",
    output_editing_efficiency_dict_attribute_name="output_editing_efficiency_dict",
    output_supplementary_files_dict_attribute_name="output_supplementary_files_dict",
    screen_id_attribute_name="SAMPLE_METADATA_screen",
    screen_id_attribute_name_backup="SAMPLE_METADATA_SCREEN",
    protospacer_editing_efficiency_attribute_name="protospacer_editing_efficiency",
    surrogate_editing_efficiency_attribute_name="surrogate_editing_efficiency",
    barcode_editing_efficiency_attribute_name="barcode_editing_efficiency",
    match_set_whitelist_reporter_observed_sequence_counter_series_results_attribute_name="match_set_whitelist_reporter_observed_sequence_counter_series_results",
    mutations_results_attribute_name="mutations_results",
    linked_mutation_counters_attribute_name="linked_mutation_counters",
    protospacer_total_mutation_histogram_pdf_attribute_name="protospacer_total_mutation_histogram_pdf",
    surrogate_total_mutation_histogram_pdf_attribute_name="surrogate_total_mutation_histogram_pdf",
    barcode_total_mutation_histogram_pdf_attribute_name="barcode_total_mutation_histogram_pdf",
    surrogate_trinucleotide_mutational_signature_attribute_name="surrogate_trinucleotide_mutational_signature",
    surrogate_trinucleotide_positional_signature_attribute_name="surrogate_trinucleotide_positional_signature",
    whitelist_guide_reporter_df_attribute_name="whitelist_guide_reporter_df",
    count_series_result_attribute_name="count_series_result"
) -> List[SampleResultModel]:
    sample_result_model_list = []
    for samples_json_selected_local_item in samples_json_selected_local:
        # TODO: Need to store associated sample and participant entity information (i.e. their IDs)
        try:
            index1 = samples_json_selected_local_item["attributes"][index1_attribute_name]
        except KeyError as e:
            index1 = samples_json_selected_local_item["attributes"][index1_attribute_name_backup]

        try:
            index2 = samples_json_selected_local_item["attributes"][index2_attribute_name]
        except KeyError as e:
            index2 = samples_json_selected_local_item["attributes"][index2_attribute_name_backup]
            
        index_pair_pipeline_bean = IndexPairPipelineBean(
                index2 = index2,
                index1 = index1,
                read1_fn = samples_json_selected_local_item["attributes"][read1_fn_attribute_name],
                read2_fn = samples_json_selected_local_item["attributes"][read2_fn_attribute_name]
            )

        sample_annotations_tuple_list = [(attribute_name,samples_json_selected_local_item["attributes"][attribute_name]) for attribute_name in samples_json_selected_local_item["attributes"].keys() if ("SAMPLE" in attribute_name) or ("REPLICATE" in attribute_name)]
        sample_annotations_indices, sample_annotations_values = zip(*sample_annotations_tuple_list)
        
        sample_annotation_pipeline_bean = SampleAnnotationPipelineBean(
            sample_annotations_series = pd.Series(sample_annotations_values, index=sample_annotations_indices)
        )

        count_result_output_pipeline_bean = None
        output_screen_countResults = samples_json_selected_local_item["attributes"].get(output_count_result_attribute_name, None)
        output_screen_editingEfficiencies = samples_json_selected_local_item["attributes"].get(output_editing_efficiency_dict_attribute_name, None)
        output_screen_supplementaryFiles = samples_json_selected_local_item["attributes"].get(output_supplementary_files_dict_attribute_name, None)
        if (output_screen_countResults is not None) and (output_screen_editingEfficiencies is not None) and (output_screen_supplementaryFiles is not None):
            try:
                screen_id = samples_json_selected_local_item["attributes"][screen_id_attribute_name]
            except KeyError as e:
                screen_id = samples_json_selected_local_item["attributes"][screen_id_attribute_name_backup]

            count_result_output_pipeline_bean = CountResultOutputPipelineBean(
                count_result_fn =  output_screen_countResults,
                screen_id = screen_id,
                protospacer_editing_efficiency = output_screen_editingEfficiencies[protospacer_editing_efficiency_attribute_name],
                surrogate_editing_efficiency = output_screen_editingEfficiencies[surrogate_editing_efficiency_attribute_name],
                barcode_editing_efficiency = output_screen_editingEfficiencies[barcode_editing_efficiency_attribute_name],

                match_set_whitelist_reporter_observed_sequence_counter_series_results_fn = output_screen_supplementaryFiles[match_set_whitelist_reporter_observed_sequence_counter_series_results_attribute_name],
                mutations_results_fn = output_screen_supplementaryFiles[mutations_results_attribute_name],
                linked_mutation_counters_fn = output_screen_supplementaryFiles[linked_mutation_counters_attribute_name],
                protospacer_total_mutation_histogram_pdf_fn = output_screen_supplementaryFiles[protospacer_total_mutation_histogram_pdf_attribute_name],
                surrogate_total_mutation_histogram_pdf_fn = output_screen_supplementaryFiles[surrogate_total_mutation_histogram_pdf_attribute_name],
                barcode_total_mutation_histogram_pdf_fn = output_screen_supplementaryFiles[barcode_total_mutation_histogram_pdf_attribute_name],
                surrogate_trinucleotide_mutational_signature_fn = output_screen_supplementaryFiles[surrogate_trinucleotide_mutational_signature_attribute_name],
                surrogate_trinucleotide_positional_signature_fn = output_screen_supplementaryFiles[surrogate_trinucleotide_positional_signature_attribute_name],
                whitelist_guide_reporter_df_fn = output_screen_supplementaryFiles[whitelist_guide_reporter_df_attribute_name],
                count_series_result_fn = output_screen_supplementaryFiles[count_series_result_attribute_name],
            )

        sample_result_model = SampleResultModel(
            sample_id = samples_json_selected_local_item["name"],
            index_pair_pipeline_bean = index_pair_pipeline_bean,
            count_result_output_pipeline_bean = count_result_output_pipeline_bean,
            sample_annotation_pipeline_bean = sample_annotation_pipeline_bean
        )

        sample_result_model_list.append(sample_result_model)
    return sample_result_model_list
    

def sample_result_model_list_to_dataframe(sample_result_model_list: List[SampleResultModel]) -> pd.DataFrame:
    sample_result_series_list: List[pd.Series] = []
    for sample_result_model in sample_result_model_list:
        indices = []
        values = []
        indices.append("sample_id")
        values.append(sample_result_model.sample_id)

        indices.extend(sample_result_model.index_pair_pipeline_bean.__dict__.keys())
        values.extend(sample_result_model.index_pair_pipeline_bean.__dict__.values())
        
        if sample_result_model.count_result_output_pipeline_bean is not None:
            indices.extend(sample_result_model.count_result_output_pipeline_bean.__dict__.keys())
            values.extend(sample_result_model.count_result_output_pipeline_bean.__dict__.values())
        
        indices.extend(sample_result_model.sample_annotation_pipeline_bean.sample_annotations_series.index.values)
        values.extend(sample_result_model.sample_annotation_pipeline_bean.sample_annotations_series.values)
        
        sample_result_series_list.append(pd.Series(values, index=indices))
    return pd.DataFrame(sample_result_series_list)
    

def download_if_changed(gcs_uri: str, local_path: str, client: storage.Client = None, deep_check: bool = False) -> None:
     '''Download the object at gcs_uri to local_path.
     If deep_check is True, compare remote MD5 to local MD5 and only download if they differ.
     If deep_check is False, only download if local file is missing.'''
     if client is None:
         client = storage.Client()
     if not gcs_uri.startswith('gs://'):
         raise ValueError(f'Invalid GCS URI: {gcs_uri}')
     _, rest = gcs_uri.split('://', 1)
     bucket_name, blob_name = rest.split('/', 1)
     bucket = client.bucket(bucket_name)
     blob = bucket.blob(blob_name)

     if deep_check:
         blob.reload()
         remote_md5 = blob.md5_hash
         if os.path.exists(local_path):
             with open(local_path, 'rb') as f:
                 local_md5 = base64.b64encode(hashlib.md5(f.read()).digest()).decode('utf-8')
             need_download = (local_md5 != remote_md5)
         else:
             need_download = True
     else:
         need_download = not os.path.exists(local_path)

     if need_download:
         os.makedirs(os.path.dirname(local_path), exist_ok=True)
         blob.download_to_filename(local_path)
         print(f'Downloaded: {local_path}')
     else:
         print(f'Up-to-date: {local_path}')

def localize_sample_files(samples_json_selected: list, localized_dir: str = '', deep_check: bool = False) -> list:
     '''Take FISS sample list structure and localize all files from GCP,
     re-downloading only if the remote object has changed (deep_check=True) or
     only if not already present (deep_check=False).'''
     os.makedirs(localized_dir, exist_ok=True)
     client = storage.Client()
     samples_local = []

     for item in samples_json_selected:
         local_item = deepcopy(item)
         sample_id = item.get('name')

         out_count = item['attributes'].get('output_count_result')
         if out_count:
             local_count = os.path.join(localized_dir,
                                        f'{sample_id}_{os.path.basename(out_count)}')
             download_if_changed(out_count, local_count, client, deep_check)
             local_item['attributes']['output_count_result'] = local_count

         out_eff = item['attributes'].get('output_editing_efficiency_dict')
         if isinstance(out_eff, str):
             out_eff = ast.literal_eval(out_eff)
         local_item['attributes']['output_editing_efficiency_dict'] = out_eff

         supp_dict = item['attributes'].get('output_supplementary_files_dict')
         if isinstance(supp_dict, str):
             supp_dict = ast.literal_eval(supp_dict)
         local_supp = {}
         if supp_dict:
             for fid, uri in supp_dict.items():
                 local_supp_path = os.path.join(localized_dir,
                                                f'{sample_id}_{os.path.basename(uri)}')
                 download_if_changed(uri, local_supp_path, client, deep_check)

                 root, ext = os.path.splitext(local_supp_path)
                 if ext.lower() == '.pdf':
                     png_path = root + '.png'
                     if not os.path.exists(png_path):
                         doc = fitz.open(local_supp_path)
                         pix = doc[0].get_pixmap()
                         pix.save(png_path)
                         print(f'Converted PDF to PNG: {png_path}')
                     local_supp[fid] = png_path
                 else:
                     local_supp[fid] = local_supp_path

         local_item['attributes']['output_supplementary_files_dict'] = local_supp

         if out_count:
             samples_local.append(local_item)

     return samples_local


def retrieve_demultiplex_particpant_sample_result_model_list(input_i5ToBarcodeToSampleInfoVarsMap,input_sampleInfoVarnames, output_screenIdToSampleMap, screen_id) -> List[SampleResultModel]:
    
    input_i5ToBarcodeToSampleInfoVarsMap_processed = process_pipeline_element(input_i5ToBarcodeToSampleInfoVarsMap)
    input_sampleInfoVarnames_processed = process_pipeline_element(input_sampleInfoVarnames)
    output_screenIdToSampleMap_processed = process_pipeline_element(output_screenIdToSampleMap)
    
    total_count_result: int = len(output_screenIdToSampleMap_processed[screen_id])
    
    sample_result_model_list: List[SampleResultModel] = []
    for index in range(0, total_count_result):
        index_pair_pipeline_bean = IndexPairPipelineBean(
                index1 =  output_screenIdToSampleMap_processed[screen_id][index][0]["index1"],
                index2 =  output_screenIdToSampleMap_processed[screen_id][index][0]["index2"],
                read1_fn =  output_screenIdToSampleMap_processed[screen_id][index][0]["read1"],
                read2_fn =  output_screenIdToSampleMap_processed[screen_id][index][0]["read2"]
            )

        sample_annotation_pipeline_bean = SampleAnnotationPipelineBean(
            sample_annotations_series = pd.Series(input_i5ToBarcodeToSampleInfoVarsMap_processed[index_pair_pipeline_bean.index1][index_pair_pipeline_bean.index2], index=input_sampleInfoVarnames_processed)
        )

        sample_result_model = SampleResultModel(
            index_pair_pipeline_bean = index_pair_pipeline_bean,
            sample_annotation_pipeline_bean = sample_annotation_pipeline_bean
        )
        
        sample_result_model_list.append(sample_result_model)
        
    return sample_result_model_list   
