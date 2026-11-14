function codeout = genUpsample(codein, r)

codeout = kron(codein,ones(1,r));