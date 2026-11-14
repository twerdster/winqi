
mex popcnt.cpp


qry = uint8(0:31)';
arr = randi(255,32,10000000,'uint8');

tic
bitcnts = popcnt(qry,arr);
toc
