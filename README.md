# Rayls mainnet chain audit

Scripts, data and saved outputs behind the article "Has Rayls Mainnet Ever Gone Down?" (November 2026).

All data comes from the public RPC https://mainnet-rpc.rayls.com (chain ID 72957). No keys, accounts or private data are used.

## What is here

- chain_scan.py: reads every 100th block from block 0 and writes chain_samples.csv (block, timestamp, nonce, miner prefix). It resumes from the CSV if interrupted.
- chain_samples.csv: output of chain_scan.py, 144,037 rows, block 0 to 14,403,600, read on November 13, 2026.
- analyze.py: flags 100-block steps under 30 s or over 400 s, and rounds that go backwards inside an epoch.
- audit.py: for each epoch change, scans the 400 blocks before the boundary for blocks stamped more than 30 s below the latest timestamp already seen.
- epoch_audit_unique.csv: one row per epoch change: epoch, boundary block, boundary time (UTC), late blocks before the boundary, maximum lateness in seconds, transactions in late blocks, late blocks after the boundary.
- late_authors.py: counts the authors of the late blocks in each flagged epoch.
- dups.py: finds blocks that repeat the same nonce and mixHash in a block range.
- hdr2.py: prints epoch, round, mixHash and requestsHash for the block numbers you give it.
- flow.py, regress.py, gaps.py, miners.py, buckets.py: smaller scans used for the windows around May 5 to 6, June 21 and October 26.
- chain_scan_out.txt, analyze_out.txt, audit_out.txt, late_authors_out.txt, flow_3382_out.txt, hdr2_out.txt: saved outputs of the main runs. The smaller scans printed to the terminal only, and their results are quoted in the article.

## Reading a block nonce

The Axyl source (crates/infrastructure/types/src/nonce.rs in github.com/raylsnetwork/axyl) packs the nonce as (epoch << 32) | round. In Python: epoch = nonce >> 32, round = nonce & 0xffffffff.

## Reproduce the main claim

With Foundry installed:

R=https://mainnet-rpc.rayls.com
for n in 3366872 3366873 3366874 3367007 3367008; do
  echo $n $(cast block $n --rpc-url $R --field timestamp) $(cast block $n --rpc-url $R --field nonce) $(cast block $n --rpc-url $R --field mixHash)
done

Blocks 3366873 and 3366874 show the round dropping from 50,388 to 50,116. Blocks 3366872 and 3367007 return the same nonce and mixHash.

## Notes and limits

- Samples are one block in every 100. A stop shorter than about 5 minutes can hide inside a step.
- A "late" block is stamped more than 30 s below the latest timestamp already seen, inside the 400 blocks before an epoch boundary.
- The public RPC prunes old state but still serves old block headers.
- The scripts retry on network errors and can be rerun.
