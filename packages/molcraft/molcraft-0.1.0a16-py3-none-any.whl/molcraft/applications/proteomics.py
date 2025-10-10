import re
import keras
import numpy as np
import tensorflow as tf
import tensorflow_text as tf_text
import json

from molcraft import featurizers
from molcraft import tensors
from molcraft import layers
from molcraft import models 
from molcraft import chem


# TODO: Add regex pattern for residue (C-term mod + N-term mod)?
# TODO: Add regex pattern for residue (C-term mod + N-term mod + mod)?
residue_pattern: str = "|".join([
    r'(\[[A-Za-z0-9]+\]-[A-Z]\[[A-Za-z0-9]+\])', # residue (N-term mod + mod)
    r'([A-Z]\[[A-Za-z0-9]+\]-\[[A-Za-z0-9]+\])', # residue (C-term mod + mod)
    r'([A-Z]-\[[A-Za-z0-9]+\])', # residue (C-term mod)
    r'(\[[A-Za-z0-9]+\]-[A-Z])', # residue (N-term mod)
    r'([A-Z]\[[A-Za-z0-9]+\])', # residue (mod)
    r'([A-Z])', # residue (no mod)
])

default_residues: dict[str, str] = {
    "A": "N[C@@H](C)C(=O)O",
    "C": "N[C@@H](CS)C(=O)O",
    "D": "N[C@@H](CC(=O)O)C(=O)O",
    "E": "N[C@@H](CCC(=O)O)C(=O)O",
    "F": "N[C@@H](Cc1ccccc1)C(=O)O",
    "G": "NCC(=O)O",
    "H": "N[C@@H](CC1=CN=C-N1)C(=O)O",
    "I": "N[C@@H](C(CC)C)C(=O)O",
    "K": "N[C@@H](CCCCN)C(=O)O",
    "L": "N[C@@H](CC(C)C)C(=O)O",
    "M": "N[C@@H](CCSC)C(=O)O",
    "N": "N[C@@H](CC(=O)N)C(=O)O",
    "P": "N1[C@@H](CCC1)C(=O)O",
    "Q": "N[C@@H](CCC(=O)N)C(=O)O",
    "R": "N[C@@H](CCCNC(=N)N)C(=O)O",
    "S": "N[C@@H](CO)C(=O)O",
    "T": "N[C@@H](C(O)C)C(=O)O",
    "V": "N[C@@H](C(C)C)C(=O)O",
    "W": "N[C@@H](CC(=CN2)C1=C2C=CC=C1)C(=O)O",
    "Y": "N[C@@H](Cc1ccc(O)cc1)C(=O)O",
}


class Peptide(chem.Mol):

    @classmethod
    def from_sequence(cls, sequence: str, **kwargs) -> 'Peptide':
        sequence = [
            match.group(0) for match in re.finditer(residue_pattern, sequence)
        ]
        peptide_smiles = []
        for i, residue in enumerate(sequence):
            if i < len(sequence) - 1:
                residue_smiles = registered_residues[residue + '*']
            else:
                residue_smiles = registered_residues[residue]
            peptide_smiles.append(residue_smiles)
        peptide_smiles = ''.join(peptide_smiles)
        return super().from_encoding(peptide_smiles, **kwargs)


@keras.saving.register_keras_serializable(package='proteomics')
class ResidueEmbedding(keras.layers.Layer):

    def __init__(
        self, 
        featurizer: featurizers.MolGraphFeaturizer,
        embedder: models.GraphModel, 
        **kwargs
    ) -> None:
        residues = kwargs.pop('_residues', None)
        super().__init__(**kwargs)
        if residues is None:
            residues = registered_residues.copy()
        self._residues = residues
        self.embedder = embedder
        self.featurizer = featurizer
        self.ragged_split = SequenceSplitter(pad=False)
        self.split = SequenceSplitter(pad=True)
        self.supports_masking = True
        
    def build(self, input_shape) -> None:
        embedding_dim = self.embedder.output.shape[-1]
        residues = sorted(self._residues.keys())
        smiles = [self._residues[residue] for residue in residues]
        num_residues = len(residues)
        self.oov_index = np.where(np.array(residues) == "G")[0][0]
        self.mapping = tf.lookup.StaticHashTable(
            tf.lookup.KeyValueTensorInitializer(
                keys=residues, 
                values=range(num_residues)
            ),
            default_value=-1,
        )
        self.graph = tf.stack([self.featurizer(s) for s in smiles], axis=0)
        self.cached_embeddings = tf.Variable(
            initial_value=tf.zeros((num_residues, embedding_dim))
        )
        self.use_cached_embeddings = tf.Variable(False)
        super().build(input_shape)

    def call(self, sequences, training=None) -> tensors.GraphTensor:
        if training is False:
            self.use_cached_embeddings.assign(True)
        else:
            self.use_cached_embeddings.assign(False)
        embeddings = tf.cond(
            pred=self.use_cached_embeddings,
            true_fn=lambda: self.cached_embeddings,
            false_fn=lambda: self.embeddings(),
        )
        sequences = self.ragged_split(sequences)
        sequences = keras.ops.concatenate([
            tf.strings.join([sequences[:, :-1], '*']), sequences[:, -1:]
        ], axis=1)
        indices = self.mapping.lookup(sequences)
        indices = keras.ops.where(indices == -1, self.oov_index, indices)
        return tf.gather(embeddings, indices).to_tensor()
    
    def embeddings(self) -> tf.Tensor:
        embeddings = self.embedder(self.graph)
        self.cached_embeddings.assign(embeddings)
        return embeddings
    
    def compute_mask(
        self, 
        inputs: tensors.GraphTensor, 
        mask: bool | None = None
    ) -> tf.Tensor | None:
        sequences = self.split(inputs)
        return keras.ops.not_equal(sequences, '')
                
    def get_config(self) -> dict:
        config = super().get_config()
        config.update({
            '_residues': self._residues,
            'featurizer': keras.saving.serialize_keras_object(self.featurizer),
            'embedder': keras.saving.serialize_keras_object(self.embedder)
        })
        return config
    
    @classmethod
    def from_config(cls, config: dict) -> 'ResidueEmbedding':
        config['featurizer'] = keras.saving.deserialize_keras_object(config['featurizer'])
        config['embedder'] = keras.saving.deserialize_keras_object(config['embedder'])
        return super().from_config(config)
    

@keras.saving.register_keras_serializable(package='proteomics')
class SequenceSplitter(keras.layers.Layer):

    def __init__(self, pad: bool, **kwargs):
        super().__init__(**kwargs)
        self.pad = pad 

    def call(self, inputs):
        inputs = tf_text.regex_split(inputs, residue_pattern, residue_pattern)
        if self.pad:
            inputs = inputs.to_tensor()
        return inputs
    

def interpret(model: keras.models.Model, sequence: list[str]) -> tensors.GraphTensor:
    
    if not tf.is_tensor(sequence):
        sequence = keras.ops.convert_to_tensor(sequence)

    # Find embedding layer
    for layer in model.layers:
        if isinstance(layer, ResidueEmbedding):
            break
    
    # Use embedding layer to convert the sequence to a graph
    residues = layer.ragged_split(sequence)
    residues = keras.ops.concatenate([
        tf.strings.join([residues[:, :-1], '*']), residues[:, -1:]
    ], axis=1)
    indices = layer.mapping.lookup(residues)
    graph = tf.concat([
        layer.graph[residue_ids] for residue_ids in indices
    ], axis=0)

    # Define layer which reshapes data into sequences of residue embeddings
    num_residues = indices.row_lengths()
    to_sequence = (
        lambda x: tf.RaggedTensor.from_row_lengths(x, num_residues).to_tensor()
    )
    reshape = keras.layers.Lambda(to_sequence)
    
    # Obtain the embedder part of the original model
    embedder = layer.embedder
    # Obtain the remaining part of the original model
    predictor = keras.models.Model(embedder.output, model.output)
    # Obtain an 'interpretable model', based on the original model
    inputs = layers.Input(graph.spec)
    x = inputs 
    for layer in embedder.layers: # Loop over layers to expose them
        x = layer(x)
    x = reshape(x)
    outputs = predictor(x)
    interpretable_model = models.GraphModel(inputs, outputs)
    
    # Interpret original model through the 'interpretable model'
    graph = models.interpret(interpretable_model, graph)
    del interpretable_model

    # Update 'size' field with new sizes corresponding to peptides for convenience
    # Allows the user to obtain n:th peptide graph using indexing: nth_peptide = graph[n]
    peptide_indices = range(len(num_residues))
    peptide_indicator = keras.ops.repeat(peptide_indices, num_residues)
    residue_sizes = graph.context['size']
    peptide_sizes = keras.ops.segment_sum(residue_sizes, peptide_indicator)
    return graph.update({'context': {'size': peptide_sizes, 'sequence': sequence}})


def register_residues(residues: dict[str, str]) -> None:
    # TODO: Implement functions that check if residue has N- or C-terminal mod
    #       if C-terminal mod, no need to enforce concatenatable perm.
    #       if N-terminal mod, enforce only 'C(=O)O'
    #       if normal mod, enforce concatenateable perm ('N[C@@H]' and 'C(=O)O)).
    for residue, smiles in residues.items():
        if residue.startswith('P'):
            smiles.startswith('N'), f'Incorrect SMILES permutation for {residue}.'
        elif not residue.startswith('['):
            smiles.startswith('N[C@@H]'), f'Incorrect SMILES permutation for {residue}.'
        if len(residue) > 1 and not residue[1] == "-":
            assert smiles.endswith('C(=O)O'), f'Incorrect SMILES permutation for {residue}.'
        registered_residues[residue] = smiles
        registered_residues[residue + '*'] = smiles.strip('O')
    

registered_residues: dict[str, str] = {}
register_residues(default_residues)
