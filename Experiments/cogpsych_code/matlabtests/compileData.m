%Script to compile data

%Nosofsky1986
assignCat1 = load('n86cat1.dat');
assignCat2 = load('n86cat2.dat');
p_observed = assignCat1/(assignCat1 + assignCat2);

