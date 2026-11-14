function c = decodeEditDistance(stream, codes, n, dict)

% Returns 
inDict = false;
m = length(stream);
c_ = double(stream=='1');

c= - ones(3,m);

if m<n-1
    fprintf('Stream needs to be at least %i bits long\n',n);
    return
end

for indEnd = (n-1):m
    % Insertion
    indStart=indEnd-n + 0;
    if indStart>0
        c(1,indEnd)=dict(bin2dec(char('0'+(c_(indStart:indEnd))))+1);
    end
    % No Slip
    indStart=indEnd-n + 1;
    if indStart>0
        c(2,indEnd)=dict(bin2dec(char('0'+(c_(indStart:indEnd))))+1);
    end
    % Deletion
    indStart=indEnd-n + 2;
    if indStart>0
        c(3,indEnd)=dict(bin2dec(char('0'+(c_(indStart:indEnd))))+1);
    end
end



