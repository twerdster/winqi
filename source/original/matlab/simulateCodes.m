%{
We will create all the code words
 k = 5

The probability of a bit flip is
Pbf = 0.1

These are then our emmission probabilities
i.e. if you are in a 1 state then the probability of
seeing a 1 is 0.9 and 0.1 of seeing a 0
and vice versa


The probability of an insertion and deletion is
Pins = 0.1
Pdel = 0.1

So using these we can define our state transition probabilities
So the probability of staying on the same state is
Pins = 0.1
The probability of moving to the next state is
1-Pdel-Pins = 0.8
And the probability of moving to the state 1 step ahead is
Pdel = 0.1

%}

% Emmission
Pbf = 0.01;
Pb = 1-Pbf;

%State
Pins = 0.01;
Pdel = 0.01;
Pnxt = 1-Pins-Pdel;

%Number of bits
k = 7;

%Codes
codes = [];
cnt = 0;

msb = 2^k;
numCodes = msb;

for c=0:numCodes-1
    inDict = false;
    c_ = double(dec2bin(c+msb)==49);
    c_ = c_(2:end)';
    codes = [codes c_];
end

% State probabilities
v = zeros(k*2^k,1)+0.5; % k bits for each code.
v=v/sum(v);

% Emmission probabilities
c=codes(:);
B = [ [c*Pbf+(1-c)*Pb]  [(1-c)*Pbf+c*Pb] ]; % First col = 0 observation, second col = 1 observation

% Transition probabilities
p = circshift(eye(k),0)*Pdel + ...
    circshift(eye(k),-1)*Pnxt + ...
    circshift(eye(k),-2)*Pins;
P = kron(speye(2^k),p);


% go over a code to visualize probability

o =[codes(:,1); codes(:,2); codes(:,3)]+1;

%p = pr_hmm(o,P,B,v);

tr = P;
e = B;

%symbols = mat2cell([0:numCodes-1]',ones(numCodes,1));

symbols = {'0','1'};

[pStates,pSeq, fs, bs, s] = hmmDecode2(o',tr,e);


clf
imagesc(pStates)




CREATE RANDOM VARIATIONS OF CODE TO START TESTING IT
MAYBE USE FLASHER FILE













