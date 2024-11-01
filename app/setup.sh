#!/bin/bash
# Copyright 2020-2022 Steven Kearnes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -ex

mkdir -p data
time python ../scripture_graph/build_graph.py \
  --input_pattern="../*.epub" \
  --output="data/scripture_graph.graphml" \
  --topics \
  --suggested \
  --tree="data/tree.json"
time python ../scripture_graph/build_connections.py \
  --input="data/scripture_graph.graphml" \
  --output="data/connections.json"
