function b = genSkippedBall(c,n)
% We will create an output ball of all the variations
% of c which means the code will always be 1 bit longer than 
% input c
c_ = c;
if strcmp(class(c),'char')==0
    c_ = (dec2bin(c));
end
c_ = [repmat('0',1,n-length(c_)) c_];

% create output with "no error"
C = ['0' c_];
C = [C; '1' c_];

% create output with "skipped bit"
for i=1:length(c_)
    c__=c_;
    c__(i)=[];
    C = [C; '00' c__];
    C = [C; '01' c__];
    C = [C; '10' c__];
    C = [C; '11' c__];
end

% create output with "skipped bit"
for i=1:length(c_)
    c__=[c_(1:i) c_(i) c_(i+1:end)];
    C = [C; c__];
end

C= unique(C,'rows');

b = bin2dec(C) ;

