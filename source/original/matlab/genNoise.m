function [f,s,d,V] = genNoise(code)
% Take in a code and produce all its noisy variations

n = size(code,2);

ind = 1:n;

bitvec = 2.^(n:-1:0);
V=[];

for i=1:n
    
    % Bit flips
    f(:,:,i) = code;
    f(:,i,i) = ~f(:,i,i); 
     
    % Bit slip
    ind_s = ind;
    ind_s(i)=[];
    s(:,:,2*i-1) = code(:,[ind_s 1]);
    s(:,:,2*i) = code(:,[n ind_s]);
    
    % Bit insertion
    d_ = [code(:,1:i) 1 code(:,i+1:end)];
    d(:,:,2*i-1) = d_(2:end) ;
    d_ = [code(:,1:i) 0 code(:,i+1:end)];
    d(:,:,2*i) = d_(2:end);
    
end


V=[bitvec(2:end)*squeeze(s) bitvec(2:end)*squeeze(f) bitvec(2:end)*squeeze(d)];  
V=unique(V);

%{
function [f,s,d,V] = genNoise(code)
% Take in a code and produce all its noisy variations

n = size(code,2);

ind = 1:n;

bitvec = 2.^(n:-1:0);
V=[];

for i=1:n
    % Bit flips
    f(:,:,i) = code;
    f(:,i,i) = ~f(:,i,i); 
     
    % Bit slip
    ind_s = ind;
    ind_s(i)=[];
    s(:,:,i) = code(:,ind_s);
    
    % Bit duplicate
    ind_d= [ind(1:i) ind(i:end)];
    d(:,:,i) = code(:,ind_d);
end


V=[bitvec(3:end)*squeeze(s) bitvec(2:end)*squeeze(f) bitvec*squeeze(d)];  
V=unique(V);
%}