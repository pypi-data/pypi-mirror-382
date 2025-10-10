# coding=utf-8
# Copyright 2025 The Perch Authors.
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

"""Perch Taxonomy Model class."""

import dataclasses
from typing import Any

from absl import logging
from etils import epath
from ml_collections import config_dict
import numpy as np
from bacpipe.model_specific_utils.perch_v2.perch_hoplite.taxonomy import namespace
from bacpipe.model_specific_utils.perch_v2.perch_hoplite.zoo import hub
from bacpipe.model_specific_utils.perch_v2.perch_hoplite.zoo import zoo_interface
import tensorflow as tf


@dataclasses.dataclass
class TaxonomyModelTF(zoo_interface.EmbeddingModel):
  """Taxonomy SavedModel.

  Attributes:
    model_path: Path to model files.
    window_size_s: Window size for framing audio in seconds. TODO(tomdenton):
      Ideally this should come from a model metadata file.
    hop_size_s: Hop size for inference.
    model: Loaded TF SavedModel.
    class_list: Loaded class_list for the model's output logits.
    batchable: Whether the model supports batched input.
    target_peak: Peak normalization value.
  """

  model_path: str
  window_size_s: float
  hop_size_s: float
  model: Any  # TF SavedModel
  class_list: dict[str, namespace.ClassList]
  batchable: bool
  target_peak: float | None = 0.25
  tfhub_path: str | None = None
  tfhub_version: int | None = None

  @classmethod
  def is_batchable(cls, model: Any) -> bool:
    sig = model.signatures['serving_default']
    return sig.inputs[0].shape[0] is None

  @classmethod
  def load_class_lists(cls, csv_glob):
    class_lists = {}
    for csv_path in csv_glob:
      key = csv_path.name.replace('.csv', '')
      with csv_path.open('r') as f:
        try:
          class_lists[key] = namespace.ClassList.from_csv(f)
        except ValueError as e:
          # Some CSV assets aren't really class lists, so we just skip them.
          logging.warning('Failed to load class list %s: %s', csv_path, e)
          continue
    return class_lists

  @classmethod
  def from_tfhub(
      cls,
      config: config_dict.ConfigDict,
  ) -> 'TaxonomyModelTF':
    if hasattr(config, 'tfhub_path') and config.tfhub_path is not None:
      tfhub_path = config.tfhub_path
    else:
      raise ValueError('tfhub_path is required to load from TFHub.')
    if config.model_path:
      raise ValueError(
          'Exactly one of tfhub_version and model_path should be set.'
      )

    # This model behaves exactly like the usual saved_model.
    model = hub.load(tfhub_path, config.tfhub_version)

    # Check whether the model support polymorphic batch shape.
    batchable = cls.is_batchable(model)

    # Get the labels CSV from TFHub.
    model_path = hub.resolve(tfhub_path, config.tfhub_version)
    class_lists_glob = (epath.Path(model_path) / 'assets').glob('*.csv')
    class_lists = cls.load_class_lists(class_lists_glob)
    mutable_config = config.copy_and_resolve_references()
    del mutable_config.model_path
    return cls(
        model=model,
        class_list=class_lists,
        batchable=batchable,
        model_path=model_path,
        **mutable_config,
    )

  @classmethod
  def load_version(
      cls, tfhub_version: int, hop_size_s: float = 5.0
  ) -> 'TaxonomyModelTF':
    cfg = config_dict.ConfigDict({
        'model_path': '',
        'sample_rate': 32000,
        'window_size_s': 5.0,
        'hop_size_s': hop_size_s,
        'target_peak': 0.25,
        'tfhub_version': tfhub_version,
    })
    return cls.from_tfhub(cfg)

  @classmethod
  def load_surfperch_version(
      cls, tfhub_version: int, hop_size_s: float = 5.0
  ) -> 'TaxonomyModelTF':
    """Load a model from TFHub."""
    cfg = config_dict.ConfigDict({
        'model_path': '',
        'sample_rate': 32000,
        'window_size_s': 5.0,
        'hop_size_s': hop_size_s,
        'target_peak': 0.25,
        'tfhub_version': tfhub_version,
        'tfhub_path': hub.SURFPERCH_SLUG,
    })
    return cls.from_tfhub(cfg)

  @classmethod
  def load_v2_version(
      cls, tfhub_version: int, hop_size_s: float = 5.0
  ) -> 'TaxonomyModelTF':
    """Load a model from TFHub."""
    cfg = config_dict.ConfigDict({
        'model_path': '',
        'sample_rate': 32000,
        'window_size_s': 5.0,
        'hop_size_s': hop_size_s,
        'target_peak': 0.25,
        'tfhub_version': tfhub_version,
        'tfhub_path': hub.PERCH_V2_SLUG,
    })
    return cls.from_tfhub(cfg)

  @classmethod
  def from_config(cls, config: config_dict.ConfigDict) -> 'TaxonomyModelTF':
    logging.info('Loading taxonomy model...')

    if hasattr(config, 'tfhub_version') and config.tfhub_version is not None:
      return cls.from_tfhub(config)

    base_path = epath.Path(config.model_path)
    if (base_path / 'saved_model.pb').exists() and (
        base_path / 'assets'
    ).exists():
      # This looks like a downloaded TFHub model.
      model_path = base_path
      class_lists_glob = (epath.Path(model_path) / 'assets').glob('*.csv')
    else:
      # Probably a savedmodel distributed directly.
      model_path = base_path / 'savedmodel'
      class_lists_glob = epath.Path(base_path).glob('*.csv')

    model = tf.saved_model.load(model_path)
    class_lists = cls.load_class_lists(class_lists_glob)

    # Check whether the model support polymorphic batch shape.
    batchable = cls.is_batchable(model)
    return cls(
        model=model, class_list=class_lists, batchable=batchable, **config
    )

  def get_classifier_head(self, classes: list[str]):
    """Extract a classifier head for the desired subset of classes."""
    base_path = epath.Path(self.model_path)
    if (base_path / 'variables').exists():
      vars_filepath = f'{self.model_path}/variables/variables'
    elif (base_path / 'savedmodel' / 'variables').exists():
      vars_filepath = f'{self.model_path}/savedmodel/variables/variables'
    else:
      raise ValueError(f'No variables found in {self.model_path}')

    def _get_weights_and_bias(num_classes: int):
      weights = None
      bias = None
      for vname, vshape in tf.train.list_variables(vars_filepath):
        if len(vshape) == 1 and vshape[-1] == num_classes:
          if bias is None:
            bias = tf.train.load_variable(vars_filepath, vname)
          else:
            raise ValueError('Multiple possible biases for class list.')
        if len(vshape) == 2 and vshape[-1] == num_classes:
          if weights is None:
            weights = tf.train.load_variable(vars_filepath, vname)
          else:
            raise ValueError('Multiple possible weights for class list.')
      if hasattr(weights, 'numpy'):
        weights = weights.numpy()
      if hasattr(bias, 'numpy'):
        bias = bias.numpy()
      return weights, bias

    class_wts = {}
    for logit_key in self.class_list:
      num_classes = len(self.class_list[logit_key].classes)
      weights, bias = _get_weights_and_bias(num_classes)
      if weights is None or bias is None:
        raise ValueError(
            f'No weights or bias found for {logit_key} {num_classes}'
        )
      for i, k in enumerate(self.class_list[logit_key].classes):
        class_wts[k] = weights[:, i], bias[i]

    wts = []
    biases = []
    found_classes = []
    for target_class in classes:
      if target_class not in class_wts:
        continue
      wts.append(class_wts[target_class][0])
      biases.append(class_wts[target_class][1])
      found_classes.append(target_class)
    print(f'Found classes: {found_classes}')
    return found_classes, np.stack(wts, axis=-1), np.stack(biases, axis=-1)

  def embed(self, audio_array: np.ndarray) -> zoo_interface.InferenceOutputs:
    return zoo_interface.embed_from_batch_embed_fn(
        self.batch_embed, audio_array
    )

  def _nonbatchable_batch_embed(self, audio_batch: np.ndarray):
    """Embed a batch of audio with an old non-batchable model."""
    all_logits = []
    all_embeddings = []
    for audio in audio_batch:
      outputs = self.model.infer_tf(audio[np.newaxis, :])
      if hasattr(outputs, 'keys'):
        embedding = outputs.pop('embedding')
        logits = outputs.pop('label')
      else:
        # Assume the model output is always a (logits, embedding) twople.
        logits, embedding = outputs
      all_logits.append(logits)
      all_embeddings.append(embedding)
    all_logits = np.stack(all_logits, axis=0)
    all_embeddings = np.stack(all_embeddings, axis=0)
    return {
        'embedding': all_embeddings,
        'label': all_logits,
    }

  def batch_embed(
      self, audio_batch: np.ndarray[Any, Any]
  ) -> zoo_interface.InferenceOutputs:
    framed_audio = self.frame_audio(
        audio_batch, self.window_size_s, self.hop_size_s
    )
    framed_audio = self.normalize_audio(framed_audio, self.target_peak)
    rebatched_audio = framed_audio.reshape([-1, framed_audio.shape[-1]])

    if not self.batchable:
      outputs = self._nonbatchable_batch_embed(rebatched_audio)
    elif hasattr(self.model, 'infer_tf'):
      # Older TFJax export.
      outputs = self.model.infer_tf(rebatched_audio)
    else:
      # Perch v2 style.
      outputs = self.model.signatures['serving_default'](inputs=rebatched_audio)

    frontend_output = None
    if hasattr(outputs, 'keys'):
      # Dictionary-type outputs. Arrange appropriately.
      embeddings = outputs.pop('embedding')
      if 'frontend' in outputs:
        frontend_output = outputs.pop('frontend')
      elif 'spectrogram' in outputs:
        frontend_output = outputs.pop('spectrogram')
      if 'spatial_embedding' in outputs:
        outputs.pop('spatial_embedding')
      # Assume remaining outputs are all logits.
      logits = outputs
    elif len(outputs) == 2:
      # Assume logits, embeddings outputs.
      label_logits, embeddings = outputs
      logits = {'label': label_logits}
    else:
      raise ValueError('Unexpected outputs type.')

    for k, v in logits.items():
      logits[k] = np.reshape(v, framed_audio.shape[:2] + (v.shape[-1],))
    # Unbatch and add channel dimension.
    embeddings = np.reshape(
        embeddings,
        framed_audio.shape[:2]
        + (
            1,
            embeddings.shape[-1],
        ),
    )
    # Reshape frontend output to match embeddings.
    if frontend_output is not None:
      frontend_output = np.reshape(
          frontend_output,
          framed_audio.shape[:2] + frontend_output.shape[1:],
      )
    return zoo_interface.InferenceOutputs(
        embeddings=embeddings,
        logits=logits,
        separated_audio=None,
        batched=True,
        frontend=frontend_output,
    )
