# Test data

| File | Made by | Content |
|---|---|---|
| `test_hic.hic`, `test_hic_no_norms.hic` | hic2cool upstream | .hic version 8 test files of the original hic2cool |
| `hic2cool_0.4.2_single_res.cool`, `hic2cool_0.7.0_multi_res.mcool` | hic2cool upstream | files written by old hic2cool releases, for `hic2cool update` |
| `GM12878_combined_30.chr21_chr22.v6.hic`, `GM12878_combined_30.chr21_chr22.v7.hic` | re-encoded from GEO GSE63525 `GSE63525_GM12878_insitu_primary+replicate_combined_30.hic` (version 7, Rao et al. 2014) | chromosomes 21 and 22 at 2.5 Mb, 1 Mb, 500 kb and 250 kb; the same pixels as version 6 and version 7 files |
| `SRR1791297_30.juicer_tools_1.22.01.v8.hic` | Juicer tools 1.22.01: `pre -j 1 -r 1000000,250000,50000,10000 contacts.txt out.hic sacCer3.chrom.sizes` | yeast contacts of SRR1791297 (from HiCExplorer's test data), version 8 |
| `SRR1791297_30.juicer_tools_2.20.00.v9.hic` | Juicer tools 2.20.00: `pre -j 1 -k VC,VC_SQRT,KR,SCALE,INTER_SCALE,GW_SCALE -r 1000000,250000,50000,10000 contacts.txt out.hic sacCer3.chrom.sizes` | the same contacts, version 9 |

The last four files come from the test data of hicfilecpp, the .hic library
this fork reads and writes .hic files with.
