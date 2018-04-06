function [out] = tempfun(tradeoff)
%temp function to test if output varies with changing tradeoff
x = 3; %Sii
y = 5;  %Sji
g = tradeoff;

a = tradeoff*x + (tradeoff-1)*y;
b = tradeoff*y + (tradeoff-1)*x;
% out = exp(a)/(exp(a) + exp(b));

fe = exp(1); %fake exp 
out = fe.^(a)/(fe.^(a) + fe.^(b));


%Check different version of formula

xt = exp(x);
yt = exp(y);

z = (xt*yt)^tradeoff;
out2 = (z/yt)/(z/yt + z/xt);


a = (exp(g*x) * exp(g*y))/exp(y);
b = (exp(g*x) * exp(g*y))/exp(x);

out3 = a/(a+b);

a = exp(g*x + g*y - y);
b = exp(g*y + g*x - x);
out4 = a/(a+b);

exp(-y)/(exp(-y)+exp(-x))