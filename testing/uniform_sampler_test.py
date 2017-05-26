import tensorflow as tf

import utilities.parse_user_params as parse_user_params
import utilities.misc_csv as misc_csv
from utilities.csv_table import CSVTable
from layer.input_normalisation import HistogramNormalisationLayer as HistNorm
from layer.volume_loader import VolumeLoaderLayer

# sampler
from layer.uniform_sampler import UniformSampler
from layer.input_placeholders import ImagePatch

class SubjectTest(tf.test.TestCase):

    def test_volume_reader(self):

        param = parse_user_params.run()
        csv_dict = {'input_image_file': './testing_data/testing_case_input',
                    'target_image_file': './testing_data/testing_case_target',
                    'weight_map_file': None,
                    'target_note': None}
        # 'target_note': './testing_data/TestComments.csv'}

        csv_loader = CSVTable(csv_dict=csv_dict,
                              modality_names=('FLAIR', 'T1'),
                              allow_missing=True)

        hist_norm = HistNorm(
            models_filename=param.saving_norm_dir,
            multimod_mask_type='or',
            norm_type=param.norm_type,
            cutoff=[x for x in param.norm_cutoff],
            mask_type='otsu_plus')

        volume_loader = VolumeLoaderLayer(csv_loader, hist_norm)
        print('found {} subjects'.format(len(volume_loader.subject_list)))

        # define output element patch
        patch_holder = ImagePatch(image_shape=(32, 32, 32),
                                  label_shape=(32, 32, 32),
                                  weight_map_shape=None,
                                  image_dtype=tf.float32,
                                  label_dtype=tf.int64,
                                  num_image_modality=2,
                                  num_label_modality=1,
                                  num_map=1)

        sampler = UniformSampler(patch=patch_holder,
                                 volume_loader=volume_loader,
                                 name='uniform_sampler')
        for d in sampler():
            assert isinstance(d, ImagePatch)
            data_dict = d.as_dict()
            self.assertAllClose((32, 32, 32, 2), d.image.shape)
            self.assertAllClose((7,), d.info.shape)
            self.assertAllClose((32, 32, 32, 1), d.label.shape)
            print(d.info)

            keys = data_dict.keys()[0]
            output = data_dict.values()[0]
            for (idx, key) in enumerate(keys):
                print(key, output[idx].shape)

if __name__ == "__main__":
    tf.test.main()
