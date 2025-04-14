# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Preprocess the HotspotQA dataset to parquet format
"""

import os
import datasets

from verl.utils.hdfs_io import copy, makedirs
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_dir', default='~/data/hotpotqa')
    parser.add_argument('--hdfs_dir', default=None)

    args = parser.parse_args()

    data_source = 'hotpotqa'

    dataset = datasets.load_dataset("RUC-NLPIR/FlashRAG_datasets", "hotpotqa")

    train_dataset = dataset['train']
    test_dataset = dataset['dev']

    system_prompt = (
        r'You FIRST think about the reasoning process as an internal monologue and then provide the final answer. '
        r'During the reasoning process, you always generate search queries between <search>[INSERT QUERY]</search> to gather information.'
        r'The reasoning process MUST BE enclosed within <think> </think> tags. The final answer MUST BE put in \boxed{}.'
    )

    # add a row to each data item that represents a unique id
    def make_map_fn(split):

        def process_fn(example, idx):
            data = {
                "data_source": data_source,
                "prompt": [{
                    "role": "system",
                    "content": system_prompt,
                }, {
                    "role": "user",
                    "content": example["question"]
                }],
                "ability": "math",
                "reward_model": {
                    "style": "rule",
                    "ground_truth": example["golden_answers"][0]
                },
                "extra_info": {
                    'split': split,
                    'index': idx,
                }
            }
            return data

        return process_fn

    train_dataset = train_dataset.map(function=make_map_fn('train'), with_indices=True, num_proc=8)
    test_dataset = test_dataset.map(function=make_map_fn('test'), with_indices=True, num_proc=8)

    local_dir = args.local_dir
    hdfs_dir = args.hdfs_dir

    train_dataset.to_parquet(os.path.join(local_dir, 'train.parquet'))
    test_dataset.to_parquet(os.path.join(local_dir, 'test.parquet'))

    if hdfs_dir is not None:
        makedirs(hdfs_dir)
        copy(src=local_dir, dst=hdfs_dir)
