%{
Here we will generate a k bit code

And then encode it, add noise and decode it.

We want to try for all the different tranmission lengths n
And we want to see what happens for all the different noise variations

So we will send a signal with Clean, Clean, Noisy, Clean, Clean Noisy, etc
For each and every code

We will try the following methods
1)
%}


n = 21;

dict = zeros(2^(n+1),1,'uint32');
codes = []; cnt = 0;

% create list of codes with cyclic completeness

for c=0:(2^n-1)
    inDict = false;
    c_ = double(dec2bin(c,n)==49);
    c_ = c_(2:end);
    ind = zeros(n,1);
    for j = 1:n
        c_ = c_([2:end 1]);
        % store the code which has been cycled
        ind(j) = bin2dec(char(48+(c_))) ;
        
        % Get all noisy versions
        [f,s,d,v] = genNoise(c_);
        V{j}=v;
        %check if this code and its noised versions are already
        %in the dictionary. if yes then
        % the mother code is already there and we dont add it again
        if dict(ind(j)+1)
            inDict = true;
        end
        for k=1:size(v,2)
            if dict(v(k)+1)
                inDict = true;
                break;
            end
        end
        if inDict
            continue;
        end
    end
    if ~inDict
        cnt = cnt+1;
        codes(cnt) = c;
        for j = 1:n
            dict(ind(j)+1) = c+1;
            v=V{j};
            for k=1:length(V{j})
                dict(v(k)+1) = c+1;
            end
        end
        
    end
end

save(['CODE' num2str(n) '.mat'],'codes','dict');

dec2bin(codes,n)
size(codes)
%
% % Go over all codes and find distance (using cyclic equivalence)
% for i=2:length(codes)-1 % we ignore the all-0 and all-1 codes
%     ind = zeros(n,1);
%     c=codes(i);
%     c_ = double(dec2bin(c+msb)==49);
%     c_ = c_(2:end);
%     for j = 1:n
%         c_ = c_([2:end 1]);
%         ind(j) = bin2dec(char(48+(dec2bin(c_)'==49))) ;
%     end
%     % Get all the cyclically equivalent codewords for c
%     H{i-1} = (unique(ind));
%     h=H{i-1};
%     m=[];
%
%     % Go over all the code words for c and find the smallest
%     % intra-code distance.
%     for k=2:length(h)
%         m(k-1) = disthamming(uint16(h(1)),uint16(h(k)));
%     end
%     % store
%     Mintra(i-1) = min(m);
% end
%
% % Now find all the inter-code distances
% for i=1:length(H)
%     h = H{i};
%     hi=h(1);
%     for j=1:length(H)
%         hj = H{j};
%         m=[];
%         for k=1:length(hj)
%             m(k) = disthamming(uint16(hi),uint16(hj(k)));
%         end
%         Minter(i,j) = min(m);
%     end
% end

code11=[
00000000000
00000000111
00000110011
00001010101
00001111111
00101001111
01101110111
11111111111];

code13=[
0000000000000
0000000000111
0000000110011
0000001010101
0000001111111
0000100001001
0000101001111
0000111010011
0001011101101
0001101111011
0010010110111
0011110011111
0101011111111
1111111111111];

code15=[
000000000000000
000000000000111
000000000110011
000000001010101
000000001111111
000000100001001
000000101001111
000000111010011
000001011100101
000001110111111
000010010110111
000010110000111
000011000101111
000011011011001
000011111010111
000100010100011
000100011110101
000101010101101
000101100111011
000110011111111
001001001001101
001010101111111
001101101001111
001111110111111
010101110110111
011110111101111
111111111111111];