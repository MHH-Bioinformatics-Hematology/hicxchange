#!/usr/bin/env python
# Test code for hic2cool
# Requires pip installation of cooler to run
# Must be run from the root directory

from __future__ import absolute_import, print_function, unicode_literals
import unittest
import cooler
import os
import h5py
import subprocess
import sys
import math
import hashlib
import shutil
import numpy as np
from hic2cool import (
    hic2cool_convert,
    hic2cool_update,
    hic2cool_extractnorms,
    cool2hic_convert,
    hic2cool_print_stderr,
    hic2cool_force_exit,
    __version__
)
from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


# thanks to Rob Kennedy on S.O. for this bit of code
@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestRunConvertAndExtractNorms(unittest.TestCase):
    """
    Test methods are named "test_#_ ..." because unittest orders methods
    by sorted string name
    """
    infile_name = 'test_data/test_hic.hic'
    infile_no_norms = 'test_data/test_hic_no_norms.hic'
    outfile_name = 'test_data/OUT_test_cool_100000.cool'
    outfile_name2 = 'test_data/OUT_test_cool_2500000.cool'
    outfile_name_all = 'test_data/OUT_test_cool_multi_res.mcool'
    outfile_no_norms = 'test_data/OUT_test_cool_no_norms.mcool'
    copy1_name = 'test_data/OUT_test_cool_no_norms_copy1.mcool'
    binsize = 100000
    binsize2 = 2500000

    def get_norms_content_md5(self, fname, use_resolutions=None, bin_lens={}):
        """
        Return hexidecimal digest of md5 from all res in use_resolutions (list)
        Also return int bin length found in the file
        """
        str_val = ''
        with h5py.File(fname, 'r') as h5:
            if not use_resolutions:
                use_resolutions = [r for r in h5['resolutions']]
            for res in use_resolutions:
                res = str(res)
                if res not in h5['resolutions']:
                    continue
                for norm in ['KR', 'VC', 'VC_SQRT']:
                    if not bin_lens.get(res):
                        bin_lens[res] = len(h5['resolutions'][res]['bins'][norm])
                    str_val += ','.join(repr(item) for item in
                                        h5['resolutions'][res]['bins'][norm][:bin_lens[res]])
        str_val = str_val.encode()
        md5 = hashlib.md5()
        md5.update(str_val)
        return md5.hexdigest(), bin_lens

    @staticmethod
    def stored_bytes(fname):
        """
        Bytes of dataset data stored in the file. hic2cool 1.0.1 asserted the
        file size (6158040), which includes the space h5py leaves unused when
        it rewrites partly filled chunks; the stored data is the same.
        """
        sizes = []
        with h5py.File(fname, 'r') as h5:
            h5.visititems(lambda name, obj: sizes.append(obj.id.get_storage_size())
                          if isinstance(obj, h5py.Dataset) else None)
        return sum(sizes)

    def test_convert(self):
        hic2cool_convert(self.infile_name, self.outfile_name_all)
        assert self.stored_bytes(self.outfile_name_all) == 5558076

    def test_convert_multiprocessing(self):
        hic2cool_convert(self.infile_name, self.outfile_name_all, 0, 2)
        assert self.stored_bytes(self.outfile_name_all) == 5558076

    def test_0_run_with_warnings(self):
        with captured_output() as (out, err):
            hic2cool_convert(self.infile_name, self.outfile_name, self.binsize, 1, True)
        read_err = err.getvalue().strip()
        self.assertTrue('WARNING' in read_err)

    def test_1_run_exclude_missing_100000(self):
        with captured_output() as (out, err):
            hic2cool_convert(self.infile_name, self.outfile_name, self.binsize)
        read_err = err.getvalue().strip()
        self.assertFalse('WARNING' in read_err)
        self.assertTrue(os.path.isfile(self.outfile_name))

    def test_2_run_exclude_missings_2500000(self):
        with captured_output() as (out, err):
            hic2cool_convert(self.infile_name, self.outfile_name2, self.binsize2)
        read_err = err.getvalue().strip()
        self.assertFalse('WARNING' in read_err)
        self.assertTrue(os.path.isfile(self.outfile_name2))

    def test_3_run_exclude_missing_multi_res_no_norms(self):
        # run hic2cool for all resolutions in the hic file
        with captured_output() as (out, err):
            # this should fail, because test file is missing chrMT
            # and excludeMT was not specified
            hic2cool_convert(self.infile_no_norms, self.outfile_no_norms, 0)
        read_err = err.getvalue().strip()
        self.assertTrue('WARNING. No normalization vectors' in read_err)
        self.assertTrue(os.path.isfile(self.outfile_no_norms))

    def test_4_run_exclude_missing_multi_res(self):
        # run hic2cool for all resolutions in the hic file
        with captured_output() as (out, err):
            # this should fail, because test file is missing chrMT
            # and excludeMT was not specified
            hic2cool_convert(self.infile_name, self.outfile_name_all, 0)
        read_err = err.getvalue().strip()
        self.assertFalse('WARNING' in read_err)
        self.assertTrue(os.path.isfile(self.outfile_name_all))

    def test_5_no_norms_in_hic(self):
        with captured_output() as (out, err):
            hic2cool_extractnorms(self.infile_no_norms, self.outfile_no_norms,
                                      exclude_mt=True, show_warnings=True)
        read_out = out.getvalue().strip()
        self.assertTrue('Normalizations:  []' in read_out)
        # no mt in this hic file to begin with
        self.assertTrue('No chromosome found when attempting to exclude MT' in read_out)

    def test_6_add_norms_to_outfile_no_norm(self):
        # infile: [2500000, 1000000, 500000, 250000, 100000, 50000, 25000, 10000, 5000]
        # outfile: [1000000, 16000000, 2000000, 4000000, 500000, 8000000]
        # so, only expected 1000000 and 500000 to be shared
        # copy outfile twice
        shutil.copy(self.outfile_no_norms, self.copy1_name)
        shared = [1000000, 500000]
        not_shared = [2500000, 250000, 100000, 50000, 25000, 10000, 5000]
        with captured_output() as (out, err):
            hic2cool_extractnorms(self.infile_name, self.copy1_name,
                                  exclude_mt=True, show_warnings=True)
        read_out = out.getvalue().strip()
        for share_res in shared:
            self.assertTrue('normalization vector at %s BP' % share_res in read_out)
        for not_share_res in not_shared:
            self.assertTrue('Skip resolution %s' % not_share_res in read_out)
        self.assertTrue('Excluding chromosome chrMT with index 25' in read_out)
        # ensure that running the function again results the same norms
        # run without exclude_mt, which is actually missing anyways
        init_md5, bin_lens = self.get_norms_content_md5(self.copy1_name, shared)
        with captured_output() as (out2, err2):
            hic2cool_extractnorms(self.infile_name, self.copy1_name, show_warnings=True)
        read_err = err2.getvalue().strip()
        self.assertTrue('Normalization vector KR does not exist for chrMT' in read_err)
        fin_md5, _ = self.get_norms_content_md5(self.copy1_name, shared, bin_lens)
        self.assertEqual(init_md5, fin_md5)
        # ensure that norm values match between different runs of extract-norms
        diff_md5, _ = self.get_norms_content_md5(self.outfile_name_all, shared, bin_lens)
        self.assertEqual(init_md5, diff_md5)
        # ensure that extracting norms again doesn't change the mult-res cooler
        # this time use all resolutions
        init2_md5, bin_lens2 = self.get_norms_content_md5(self.outfile_name_all)
        hic2cool_extractnorms(self.infile_name, self.outfile_name_all, silent=True)
        fin2_md5, bin_lens2_2 = self.get_norms_content_md5(self.outfile_name_all)
        self.assertEqual(init2_md5, fin2_md5)
        self.assertEqual(bin_lens2, bin_lens2_2)


class TestWithCooler(unittest.TestCase):
    outfile_name = 'test_data/OUT_test_cool_100000.cool'
    outfile_name2 = 'test_data/OUT_test_cool_2500000.cool'
    outfile_name_all = 'test_data/OUT_test_cool_multi_res.mcool'
    outfile_no_norms = 'test_data/OUT_test_cool_no_norms.mcool'
    binsize = 100000
    binsize2 = 2500000

    def test_cooler_100000(self):
        with h5py.File(self.outfile_name, 'r') as h5file:
            cool = cooler.Cooler(h5file)
            cool_file = cool.filename.encode('utf-8')
            self.assertEqual(self.outfile_name.encode('utf-8'), cool_file)
            self.assertEqual(len(cool.info), 12)
            self.assertEqual(cool.info['format'], 'HDF5::Cooler')
            self.assertTrue(isinstance(cool.info['format-version'], np.int64))
            self.assertEqual(cool.info['storage-mode'], 'symmetric-upper')
            self.assertTrue(__version__ in cool.info['generated-by'])
            self.assertEqual(cool.info['nchroms'], 25)
            self.assertEqual(len(cool.chromnames), 25) # 'all' excluded
            self.assertEqual(self.binsize, cool.info['bin-size'])
            # check normalization values and balanced/unbalanced counts
            matrix_res = cool.matrix(balance=False).fetch('chr1:25000000-25100000')
            bin_idx = 250 # chr1:25000000-25100000 corresponds to bin 0 at this res
            bin_raw_val = matrix_res[0][0]
            self.assertEqual(matrix_res.shape, (1,1))
            self.assertEqual(bin_raw_val, 2)
            # expect a ValueError -- not balanced and there is no 'weights' column
            with self.assertRaises(ValueError):
                matrix_res = cool.matrix(balance=True).fetch('chr1:25000000-25100000')
            # check a few norms
            bin_info = cool.bins()[bin_idx]
            for norm in ['KR', 'VC', 'VC_SQRT']:
                norm = str(norm) # needed for python 2
                self.assertTrue(norm in bin_info)
                bin_norm_val = bin_info[norm][bin_idx]  # value for weight in this bin
                # cooler now automatically handles HIC vectors with divisive vectors
                # test the inverted (non-handled divisive) matrix balancing as well
                norm_matrix_res = cool.matrix(balance=norm).fetch('chr1:25000000-25100000')
                invert_norm_mat_res = cool.matrix(balance=norm, divisive_weights=False).fetch('chr1:25000000-25100000')
                self.assertEqual(norm_matrix_res.shape, (1,1))
                self.assertEqual(invert_norm_mat_res.shape, (1,1))
                # handle nan
                if math.isnan(bin_norm_val):
                    self.assertTrue(math.isnan(norm_matrix_res[0][0]))
                    self.assertTrue(math.isnan(invert_norm_mat_res[0][0]))
                else:
                    # balanced value is equal to count * weight * weight
                    calc_balanced_val = round(bin_raw_val / bin_norm_val / bin_norm_val, 4)
                    calc_inverted_val = round(bin_raw_val * bin_norm_val * bin_norm_val, 4)
                    found_balanced_val = round(norm_matrix_res[0][0], 4)
                    found_inverted_val = round(invert_norm_mat_res[0][0], 4)
                    self.assertEqual(calc_balanced_val, found_balanced_val)
                    self.assertEqual(calc_inverted_val, found_inverted_val)
        # lastly check cooler dump raw count
        v = subprocess.check_output(['cooler', 'dump', self.outfile_name, '-t',
                                     'pixels', '-r', 'chr1:25000000-25100000'])
        formatted_v = [int(vl) for vl in v.decode().strip().split('\t')]
        # output corresponds to bin1, bin2, count
        self.assertEqual(formatted_v, [bin_idx, bin_idx, bin_raw_val])

    def test_cooler_2500000(self):
        with h5py.File(self.outfile_name2, 'a') as h5file:
            cool = cooler.Cooler(h5file)
            cool_file = cool.filename.encode('utf-8')
            self.assertEqual(self.outfile_name2.encode('utf-8'), cool_file)
            self.assertEqual(len(cool.info), 12)
            self.assertEqual(cool.info['format'], 'HDF5::Cooler')
            self.assertTrue(isinstance(cool.info['format-version'], np.int64))
            self.assertEqual(cool.info['storage-mode'], 'symmetric-upper')
            self.assertTrue(__version__ in cool.info['generated-by'])
            self.assertEqual(len(cool.chromnames), 25)
            self.assertEqual(self.binsize2, cool.info['bin-size'])
            matrix_res = cool.matrix(balance=False).fetch('chr1:0-25000000')
            self.assertEqual(matrix_res.shape, (10,10))
            bin_idx = 9 # chr1:22500000-25000000 corresponds to bin 9 at this res
            bin_raw_val = matrix_res[9][9]
            self.assertEqual(bin_raw_val, 40)
            # expect a ValueError -- not balanced and there is no 'weights' column
            with self.assertRaises(ValueError):
                matrix_res = cool.matrix(balance=True).fetch('chr1:0-25000000')
            # check a few norms
            bin_info = cool.bins()[bin_idx]
            for norm in ['KR', 'VC', 'VC_SQRT']:
                norm = str(norm) # needed for python 2
                self.assertTrue(norm in bin_info)
                bin_norm_val = bin_info[norm][bin_idx]  # value for weight in this bin
                norm_matrix_res = cool.matrix(balance=norm).fetch('chr1:0-25000000')
                self.assertEqual(norm_matrix_res.shape, (10,10))
                # handle nan specially
                if math.isnan(bin_norm_val):
                    self.assertTrue(math.isnan(norm_matrix_res[9][9]))
                else:
                    # balanced value is equal to count / weight / weight
                    # since this is a divisive weight
                    calc_balanced_val = round(bin_raw_val / bin_norm_val / bin_norm_val, 4)
                    found_balanced_val = round(norm_matrix_res[9][9], 4)
                    self.assertEqual(calc_balanced_val, found_balanced_val)
        # lastly check cooler dump raw count
        v = subprocess.check_output(['cooler', 'dump', self.outfile_name2, '-t',
                                     'pixels', '-r', 'chr1:22500000-25000000'])
        formatted_v = [int(vl) for vl in v.decode().strip().split('\t')]
        # output corresponds to bin1, bin2, count
        self.assertEqual(formatted_v, [bin_idx, bin_idx, bin_raw_val])

    def test_cooler_multi_res(self):
        with h5py.File(self.outfile_name_all, 'r') as h5file:
            # there should be some mcool attributes on the base collection
            self.assertEqual(h5file.attrs['format'], 'HDF5::MCOOL')
            self.assertTrue(isinstance(h5file.attrs['format-version'], np.int64))
            # since this is multi-res, hdf5 structure is different
            # expect the following 9 resultions to be present:
            # [2500000, 1000000, 500000, 250000, 100000, 50000, 25000, 10000, 5000]
            self.assertEqual(len(h5file['resolutions'].keys()), 9)
            # take a resolution and check the metadata
            res250kb = h5file['resolutions']['250000']
            cool = cooler.Cooler(res250kb)
            cool_file = cool.filename.encode('utf-8')
            self.assertEqual(self.outfile_name_all.encode('utf-8'), cool_file)
            # cooler info has 8 entries
            self.assertEqual(len(cool.info), 12)
            self.assertEqual(cool.info['format'], 'HDF5::Cooler')
            self.assertTrue(isinstance(cool.info['format-version'], np.int64))
            self.assertEqual(cool.info['storage-mode'], 'symmetric-upper')
            self.assertTrue(__version__ in cool.info['generated-by'])
            self.assertEqual(len(cool.chromnames), 25)
            self.assertEqual(250000, cool.info['bin-size'])
            matrix_res = cool.matrix(balance=False).fetch('chr1:25000000-25250000')
            self.assertEqual(matrix_res.shape, (1,1))
            self.assertEqual(matrix_res[0][0], 4)
            # make sure the updated cooler multi-res syntax is working
            cool = cooler.Cooler(self.outfile_name_all + '::resolutions/100000')
            cool_file = cool.filename.encode('utf-8')
            self.assertEqual(self.outfile_name_all.encode('utf-8'), cool_file)
            cool_res = int(cool.info['bin-size'])
            self.assertEqual(100000, cool_res)

    def test_check_norms(self):
        NORMS = ["VC", "VC_SQRT", "KR"]
        with h5py.File(self.outfile_name, 'r') as h5file:
            bins = h5file['bins']
            for norm in NORMS:
                self.assertTrue(norm in bins.keys())

    def test_no_norms(self):
        """
        Added support for missing norm vectors in the hic file
        outfile_no_norms is a mcool
        """
        NORMS = ["VC", "VC_SQRT", "KR"]
        with h5py.File(self.outfile_no_norms, 'r') as h5file:
            # resolutions are ['1000000', '16000000', '2000000', '4000000', '500000', '8000000']
            self.assertEqual(len(h5file['resolutions'].keys()), 6)
            res500kb_bins = h5file['resolutions']['500000']['bins']
            for norm in NORMS:
                self.assertTrue(norm not in res500kb_bins.keys())

class TestRunUpdate(unittest.TestCase):
    infile_name = 'test_data/hic2cool_0.4.2_single_res.cool'
    outfile_name = 'test_data/OUT_new_version_single_res.cool'
    infile_mcool_name = 'test_data/hic2cool_0.7.0_multi_res.mcool'
    outfile_mcool_name = 'test_data/OUT_new_version_multi_res.cool'

    def norm_convert(self, val):
        if val != 0.0:
            return 1 / val
        else:
            return np.nan

    def test_run_update_cooler(self):
        """
        Test to ensure the update functionality works and changes generated
        by tags.

        Specifically test updates for re-inverting normalization vectors and
        adding format-version and storage-mode attributes.
        """
        # first check some stuff on the input file, which is single-res
        original_kr_data = []  # first 10 values in KR normalization
        final_kr_data = []
        original_creation_date = ''
        update_date = ''
        with h5py.File(self.infile_name, 'r') as h5file:
            self.assertEqual(h5file.attrs.get('generated-by'), 'hic2cool-0.4.2')
            self.assertEqual(h5file.attrs.get('update-date'), None)
            self.assertEqual(h5file.attrs.get('format-version'), None)
            self.assertEqual(h5file.attrs.get('storage-mode'), None)
            original_creation_date = h5file.attrs.get('creation-date')
            original_kr_data = h5file['bins/KR'][:100]
        hic2cool_update(self.infile_name, self.outfile_name, silent=True)
        self.assertTrue(os.path.isfile(self.outfile_name))
        # ensure that the new file has a new version and update-date
        expected_version = 'hic2cool-' + __version__
        with h5py.File(self.outfile_name, 'r') as h5file:
            self.assertEqual(h5file.attrs.get('generated-by'), expected_version)
            self.assertEqual(h5file.attrs.get('creation-date'), original_creation_date)
            self.assertTrue(h5file.attrs.get('update-date') is not None)
            self.assertTrue(isinstance(h5file.attrs.get('format-version'), np.int64))
            self.assertEqual(h5file.attrs.get('storage-mode'), 'symmetric-upper')
            update_date = h5file.attrs.get('update-date')
            final_kr_data = h5file['bins/KR'][:100]
        # make sure the norms got updated correctly
        for comp in zip(original_kr_data, final_kr_data):
            if math.isnan(comp[0]):  # special case
                self.assertTrue(math.isnan(comp[1]))
                self.assertTrue(math.isnan(self.norm_convert(comp[1])))
            else:
                self.assertEqual(comp[0], self.norm_convert(comp[1]))
        # make sure running it again does nothing (update-date unchanged)
        hic2cool_update(self.outfile_name, silent=True)
        with h5py.File(self.outfile_name, 'r') as h5file:
            self.assertEqual(h5file.attrs.get('generated-by'), expected_version)
            self.assertEqual(h5file.attrs.get('update-date'), update_date)

    def test_run_update_mcool(self):
        """
        Test updates run exclusively on multi-res files
        """
        with h5py.File(self.infile_mcool_name, 'r') as h5file:
            self.assertTrue('format' not in h5file.attrs)
            self.assertTrue('format-version' not in h5file.attrs)
        hic2cool_update(self.infile_mcool_name, self.outfile_mcool_name, silent=True)
        with h5py.File(self.outfile_mcool_name, 'r') as h5file:
            self.assertEqual(h5file.attrs['format'], 'HDF5::MCOOL')
            self.assertTrue(isinstance(h5file.attrs['format-version'], np.int64))


class TestUtilities(unittest.TestCase):
    infile_name = 'test_data/test_hic.hic'

    def test_print_stderr(self):
        with captured_output() as (out, err):
            hic2cool_print_stderr('error message!')
        read_err = err.getvalue().strip()
        self.assertTrue('error message!' in read_err)

    def test_force_exit(self):
        """
        Open a dummy file and make sure it is closed
        """
        req = open(self.infile_name, 'rb')
        with captured_output() as (out, err):
            with self.assertRaises(SystemExit) as exc:
                hic2cool_force_exit('fatal error!', req)
            self.assertEqual(exc.exception.code, 1)
        read_err = err.getvalue().strip()
        self.assertTrue('fatal error!' in read_err)
        self.assertTrue(req.closed)  # file closed by force_exit


def datasets_of(fname):
    """Every dataset of a cool or mcool file as a numpy array, by path."""
    out = {}
    with h5py.File(fname, 'r') as h5:
        h5.visititems(lambda name, obj: out.__setitem__(name, obj[:])
                      if isinstance(obj, h5py.Dataset) else None)
    return out


def assert_same_arrays(test, a, b, names=None):
    names = sorted(a) if names is None else names
    test.assertEqual(sorted(k for k in a if k in names), sorted(k for k in b if k in names))
    for name in names:
        if a[name].dtype.kind == 'f':
            test.assertTrue(np.array_equal(a[name], b[name], equal_nan=True), name)
        else:
            test.assertTrue(np.array_equal(a[name], b[name]), name)


class TestFork(unittest.TestCase):
    """
    What the C++ fork adds: .hic versions 6 to 9, output independent of the
    number of threads, and cool2hic.
    """
    v6 = 'test_data/GM12878_combined_30.chr21_chr22.v6.hic'
    v7 = 'test_data/GM12878_combined_30.chr21_chr22.v7.hic'
    v8 = 'test_data/SRR1791297_30.juicer_tools_1.22.01.v8.hic'
    v9 = 'test_data/SRR1791297_30.juicer_tools_2.20.00.v9.hic'

    def test_versions_6_and_7(self):
        a = datasets_of(hic2cool_convert(self.v6, 'test_data/OUT_fork_v6.mcool', silent=True))
        b = datasets_of(hic2cool_convert(self.v7, 'test_data/OUT_fork_v7.mcool', silent=True))
        assert_same_arrays(self, a, b)
        self.assertEqual(len(a['resolutions/250000/pixels/count']), 39771)

    def test_version_9(self):
        a = datasets_of(hic2cool_convert(self.v8, 'test_data/OUT_fork_v8.mcool', silent=True))
        b = datasets_of(hic2cool_convert(self.v9, 'test_data/OUT_fork_v9.mcool', silent=True))
        # Juicer tools 1.22.01 and 2.20.00 wrote the same contacts; their
        # normalization vectors differ in rounding (and SCALE at 10 kb).
        names = [n for n in a if '/bins/' not in n or n.split('/')[-1] in ('chrom', 'start', 'end')]
        assert_same_arrays(self, a, b, names)
        self.assertEqual(len(b['resolutions/10000/pixels/count']), 701342)
        for norm in ('VC', 'VC_SQRT', 'KR'):
            x, y = a['resolutions/50000/bins/' + norm], b['resolutions/50000/bins/' + norm]
            self.assertTrue(np.allclose(x, y, rtol=1e-6, equal_nan=True))

    def test_threads_do_not_change_the_output(self):
        a = datasets_of(hic2cool_convert(self.v8, 'test_data/OUT_fork_p1.mcool', nproc=1, silent=True))
        b = datasets_of(hic2cool_convert(self.v8, 'test_data/OUT_fork_p8.mcool', nproc=8, silent=True))
        assert_same_arrays(self, a, b)

    def test_cool2hic_round_trip(self):
        for version in (8, 9):
            source = self.v8 if version == 8 else self.v9
            first = hic2cool_convert(source, 'test_data/OUT_fork_rt%d.mcool' % version, silent=True)
            hic = cool2hic_convert(first, 'test_data/OUT_fork_rt%d.hic' % version, hic_version=version, silent=True)
            back = hic2cool_convert(hic, 'test_data/OUT_fork_rt%d_back.mcool' % version, silent=True)
            # pixels and normalization vectors come back bit for bit
            assert_same_arrays(self, datasets_of(first), datasets_of(back))
            with h5py.File(back, 'r') as h5:
                self.assertEqual(h5['resolutions/10000'].attrs['software'],
                                 'cool2hic (hic2cool %s)' % __version__)

    def test_cool2hic_single_resolution_added_resolutions_computed_norms(self):
        single = hic2cool_convert(self.v8, 'test_data/OUT_fork_10kb.cool', 10000, silent=True)
        hic = cool2hic_convert(single, 'test_data/OUT_fork_10kb.hic', add_resolutions=[50000, 250000],
                               normalizations=['VC', 'KR'], silent=True)
        back = datasets_of(hic2cool_convert(hic, 'test_data/OUT_fork_10kb_back.mcool', silent=True))
        full = datasets_of(hic2cool_convert(self.v8, 'test_data/OUT_fork_v8_all.mcool', silent=True))
        for res in ('10000', '50000', '250000'):
            names = ['resolutions/%s/%s' % (res, n) for n in
                     ('pixels/bin1_id', 'pixels/bin2_id', 'pixels/count', 'bins/start', 'indexes/bin1_offset')]
            assert_same_arrays(self, full, back, names)
        self.assertEqual(sorted(k.split('/')[-1] for k in back if k.startswith('resolutions/10000/bins/')),
                         ['KR', 'VC', 'chrom', 'end', 'start'])
        # computed as Juicer tools 1.22.01 computes them
        self.assertTrue(np.allclose(full['resolutions/50000/bins/KR'], back['resolutions/50000/bins/KR'],
                                    rtol=1e-3, equal_nan=True))

    def test_cool2hic_errors(self):
        single = hic2cool_convert(self.v8, 'test_data/OUT_fork_10kb.cool', 10000, silent=True)
        with captured_output() as (out, err):
            with self.assertRaises(SystemExit) as exc:
                cool2hic_convert(single, 'test_data/OUT_fork_bad.hic', resolution=5000, silent=True)
        self.assertEqual(exc.exception.code, 1)
        self.assertTrue('not a resolution of this file' in err.getvalue())
        with captured_output() as (out, err):
            with self.assertRaises(SystemExit):
                cool2hic_convert(single, 'test_data/OUT_fork_bad.hic', add_resolutions=[15000], silent=True)
        self.assertTrue('not a multiple' in err.getvalue())

    def test_unreadable_input(self):
        with captured_output() as (out, err):
            with self.assertRaises(SystemExit):
                hic2cool_convert('test_data/hic2cool_0.4.2_single_res.cool', 'test_data/OUT_fork_x.cool', silent=True)
        self.assertTrue('magic string is incorrect' in err.getvalue())


if __name__ == '__main__':
    unittest.main()
