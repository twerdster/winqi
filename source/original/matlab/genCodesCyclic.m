

for n = 3:21;
    endN = n;%1; %n;
    
    dict = zeros(2^(n),1,'uint32');
    codes = []; cnt = 0;
    ind=[]; c_=[]; 
    % create list of codes with cyclic completeness
    tic
    for c=0:(2^n-2)
        if mod(c,100)==0
            fprintf('n=%i : %i/%i : %f%% : %f seconds\n',n, c,2^n-1, c/(2^n-1)*100, toc);
        end
        inDict = false;
        c_ = double(dec2bin(c,n)=='1');
        ind = zeros(n,1);
        V=[];
        for j = 1:endN
            % store the code which has been cycled
            ind(j) = bin2dec(char('0'+(c_))) ;
            
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
            
            c_ = c_([2:end 1]);
        end
        if ~inDict
            cnt = cnt+1;
            codes(cnt) = c;
            for j = 1:endN
                dict(ind(j)+1) = cnt;
                v=V{j};
                for k=1:length(V{j})
                    dict(v(k)+1) = cnt;
                end
            end
            
        end
    end
    
   % save(['CodeCyclic' num2str(n) '.mat'],'codes','dict');
    A{n}.codes=codes;
    
    dec2bin(codes,n)
    size(codes)
end


