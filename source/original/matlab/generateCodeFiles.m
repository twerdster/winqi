function generateCodeFiles(codeFile,comma)

a=load(codeFile);
na = log2(length(a.dict))-1;

tic
cnt=1;
fid = fopen(strrep(codeFile,'mat','dat'),'wt');
len=length(a.codes);
for c = a.codes
    c_ = double(dec2bin(c,na)=='1');
    % Get all noisy versions
    [f,s,d] = genNoise(c_);
    f=char(squeeze(f)'+'0');
    s=char(squeeze(s)'+'0');
    d=char(squeeze(d)'+'0');

    S0 = {char(squeeze(c_)+'0')};
    
    if ~exist('comma')
        comma = S0;
    end
    
    S = [S0; mat2cell(f,1+0*(1:size(f,1)),size(f,2))];
    S = [S; mat2cell(s,1+0*(1:size(s,1)),size(s,2))];
    S = [S; mat2cell(d,1+0*(1:size(d,1)),size(d,2))];
    %S=unique(S,'rows');
    S1=cell(2*length(S),1);
    S1(1:2:end)=S;
    S1(2:2:end)=comma;
    fprintf(fid,'%s',S1{:});
    fprintf(fid,'\n');
    cnt=cnt+1;
    if mod(cnt,100)==0
        fprintf('%i / %i -> %f seconds\n',cnt,len,toc);
    end
end
fclose(fid);