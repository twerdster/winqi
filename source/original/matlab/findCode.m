function pos = findCode(codeFile, subCodeFile)
codeFileDat=codeFile;
codeFileMat = strrep(codeFile,'dat','mat');
b=load(subCodeFile);
nb = log2(length(b.dict))-1;
num = str2num(regexprep(codeFile,'[\D]',''));

cnt=1;
for sc = b.codes
    sc_ = double(dec2bin(sc,nb)==49);
    % Get all noisy versions
    [sf,ss,sd] = genNoise(sc_);
    sf=char(squeeze(sf)'+'0');
    ss=char(squeeze(ss)'+'0');
    sd=char(squeeze(sd)'+'0');
    
    S = {char(squeeze(sc_)+'0')};
    S = [S; mat2cell(sf,1+0*(1:size(sf,1)),size(sf,2))];
    S = [S; mat2cell(ss,1+0*(1:size(ss,1)),size(ss,2))];
    S = [S; mat2cell(sd,1+0*(1:size(sd,1)),size(sd,2))];
    S=unique(S,'rows');
    
    pos{cnt}=[];
    % Go over all codes in the subcode
    for i=1:size(S,1)
        generateCodeFiles(codeFileMat,S(i,:));
        system(['grep -o -n ''' S{i,:} ''' ' codeFileDat ' | cut -d : -f 1 | uniq -c >out.txt']);
        res = load('out.txt');
        res(:,1)=res(:,1)-(num*3+1);
        lines = find(res(:,1)==0);
        if i==1
            pos{cnt}=lines;
        else
            pos{cnt}=intersect(pos{cnt},lines);
        end
    end
    %pos{cnt} = length;
    cnt=cnt+1
end


