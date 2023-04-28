

compression => only lz4 and zstd
page size => ​​​[64 KB, 128 KB, 256 KB,​ 512 KB, 1 MB, 2 MB, 4 MB, MB, 16 MB]
cluster size => [10 MB, 20 MB, 30 MB, 40 MB, 50 MB, 75 MB, 100 MB, 150 MB]
cluster bunch => [1, 2, 3]

memory usage =>  (szReadPayload / nClusterLoaded) * cluster bunch

/usr/bin/time 

0.50user 0.39system 0:00.62elapsed 144%CPU (0avgtext+0avgdata 370632maxresident)k
0inputs+0outputs (0major+270643minor)pagefaults 0swaps

take maxresident