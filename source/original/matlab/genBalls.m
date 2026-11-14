n = 7;
k = 4;
sr = 2 %sample rate. it wont be exactly 2. it might be slightly less or more but we deal with this by randomly adding or removing a bit
N = sr*n;
A = zeros(2^(N+1),1);
C=[];
cnt=0;
for i=0:2^k-1 % create all codewords of rank k
    
    % Create code word
    c = encode(i,n,k,'hamming/decimal');
    
    
    B=[];
   %{ for j=1:n
        % Now pollute it with a single flip (noise on received signal)
        c_ =  bitset(c,j,~bitget(c,j));
        c_b =dec2bin(c_);
        
        % And upsample it
        c_b = c_b(rectpulse(1:length(c_b),sr)');
        c_ = bin2dec(c_b);
      %}  
        % And find all skip variations of this vector
        b = genSkippedBall(c_,N)+1;
        
        B=[B;b];
   % end
    B=unique(B);
    
    if ~sum(A(B))
        A(B)=i+1;
        cnt=cnt+1;
        C(cnt)=i;
    end
end
fprintf('[%i %i-> %i] Efficiency = %f\n',n,2^k, length(C), log2(length(C))/N*100);