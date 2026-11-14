figure(1)
clf
ylim([-1 2])
hold on
grid on
L = 21;
s = 20;
cn = 200;
maxT = 8;

savetikz = 0;
a=load(['CodeCyclic' num2str(L)]);

c=dec2bin(a.codes(cn),L);
c= [c=='1'];
c=kron(c,ones(1,s));
c=smooth(c,4,'lowess');

t=c*0+1/length(c)*maxT;
t=cumsum(t);

plot(t,c,'r','LineWidth',3)
plot(t,1-c,'b','LineWidth',3)

%set(gca,'XTickLabel','','YTickLabel','');
t_=t/maxT;
C = -2*(rand(1)*2-1)*t_.^3 +rand(1)*t_.^2+(2*rand(1)-1)*t_+rand(1)*2-1  ;

%%
figure(5)
clf
hold
ylim([-2 2])
grid on

for i=1:length(c)-1
    if c(i)==1 && c(i+1)==1
        h=line([t(i) t(i+1)],C([i,i+1]),'Color',[1 0 0],'LineWidth',4);
    end
    if ~c(i) && ~c(i+1)
        line([t(i) t(i+1)],C([i,i+1]),'Color',[0 0 1]*0.8,'LineWidth',4);
    end
end
t_=t;
C_=C;


%%
figure(2)
clf
hold
ylim([-1 6])
grid on
C=C+c;

plot(t,C,'g','LineWidth',3)
ylim([-1 6])

T= t(5:s:length(C));
A = interp1(t(1:length(C)),C',T);
A2 = interp1(t(1:length(C)),C_',T);
h=plot(T,A,'k.','MarkerSize',20);
%matlab2tikz('plot1.tex');

W = [ T.^2 T.^1 T.^0];

a = W\A;
y=W*a;
indup = A>y;
inddn = A<y;

aup = W(indup,:)\A(indup);
adn = W(inddn,:)\A(inddn);
yup=W*aup;
ydn=W*adn;


plot(T,y,'c-');
plot(T(indup),yup(indup),'ro','MarkerSize',10);
plot(T,yup,'r','MarkerSize',10);

plot(T(inddn),ydn(inddn),'bo','MarkerSize',10);
plot(T,ydn,'b','MarkerSize',10);
set(gca,'XTickLabel','','YTickLabel','')
%%
figure(3)
clf
hold on
ylim([-1 6]);
grid on
set(gca,'XTickLabel','','YTickLabel','')

plot(t,C,'g','LineWidth',3);
h=plot(T,A,'k.','MarkerSize',20);

dA = diff(A);
[~,j]=max(abs(dA));
if dA(j)<0
    plot(T(j),A(j),'r.','MarkerSize',40);
    plot(T(j+1),A(j+1),'b.','MarkerSize',40);
else
    plot(T(j),A(j),'b.','MarkerSize',40);
    plot(T(j+1),A(j+1),'r.','MarkerSize',40);
end
%%
figure(4)
clf
hold on
ylim([-2 2]);
grid on
set(gca,'XTickLabel','','YTickLabel','')

plot(t,C,'k','LineWidth',1);
h=plot(T,A,'k.','MarkerSize',20);

dA = diff(A);
[mda,j]=max(abs(dA));

J=j;
if dA(j)<0
    plot(T(j),A(j),'r.','MarkerSize',40);
    plot(T(j+1),A(j+1),'b.','MarkerSize',40);
    j=j;
else
    plot(T(j),A(j),'b.','MarkerSize',40);
    plot(T(j+1),A(j+1),'r.','MarkerSize',40);
    j=j+1;
end

alpha = 0.85;
val = 1;
current = A(j);
for i=[(j-1):-1:1 1:length(A)]
    next = A(i);
    if next<current-0.5*(alpha*mda)
        val = 0;
    elseif next>current+0.5*(alpha*mda)
        val = 1;
    else
        % no change in val;
    end
    if val
        plot(T(i),A(i),'r.','MarkerSize',25);
    else
        plot(T(i),A(i),'b.','MarkerSize',25);
    end
    val_(i)=val;
    current = A(i);
end

%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Make tikz figure
ofs = 2;

inred = 0;
redcnt=1;
bluecnt=1;
redl={[]};
bluel={[]};


T_=T;
A_=A+ofs;
A2_=A2+ofs;

for i=1:length(c)
    if inred
        if c(i)
            redl{redcnt} = [redl{redcnt} [t_(i); C_(i)+ofs] ];
        else
            inred = 0;
            redcnt = redcnt+1;
            redl{redcnt}=[];
        end
    else
        if ~c(i)
            bluel{bluecnt} = [bluel{bluecnt} [t_(i); C_(i)+ofs] ];
        else
            inred = 1;
            bluecnt = bluecnt+1;
            bluel{bluecnt}=[];
        end
    end
    
end

for i=1:length(redl)
    ff = redl{i};
    if length(ff)==0
        continue;
    end
    fprintf('\\draw[line width=3pt,red,fill=red!76] ');
    fprintf('(%.3f,%.3f) --',ff(:));
    fprintf('(%.3f,%.3f)',ff(end-1:end));
    fprintf(';\n');
end

for i=1:length(bluel)
    ff = bluel{i};
    if length(ff)==0
        continue;
    end
    fprintf('\\draw[line width=3pt,blue,fill=blue!76] ');
    fprintf('(%.3f,%.3f) --',ff(:));
    fprintf('(%.3f,%.3f)',ff(end-1:end));
    fprintf(';\n');
end

for i=1:length(A_)
    if val_(i)
        fprintf('\\draw[black,fill=white] (%.3f,%.3f) circle (0.5ex);\n',T_(i),A2_(i));
    else
        fprintf('\\draw[black,fill=black!85] (%.3f,%.3f) circle (0.5ex);\n',T_(i),A2_(i));
    end
end

ff=[t C+ofs]';
fprintf('\\draw[line width=1pt] ');
fprintf('(%.3f,%.3f) --',ff(:));
fprintf('(%.3f,%.3f)',ff(end-1:end));
fprintf(';\n\n');

for i=1:length(A_)
    if val_(i)
        fprintf('\\draw[black,fill=white] (%.3f,%.3f) circle (0.5ex);\n',T_(i),A_(i));
    else
        fprintf('\\draw[black,fill=black!85] (%.3f,%.3f) circle (0.5ex);\n',T_(i),A_(i));
    end
end
if dA(J)<0
    fprintf('\\draw[black,fill=white] (%.3f,%.3f) circle (1ex);\n',T_(J),A_(J));
    fprintf('\\draw[black,fill=black!85] (%.3f,%.3f) circle (1ex);\n',T_(J+1),A_(J+1));
else
    fprintf('\\draw[black,fill=white] (%.3f,%.3f) circle (1ex);\n',T_(J+1),A_(J+1));
    fprintf('\\draw[black,fill=black!85] (%.3f,%.3f) circle (1ex);\n',T_(J),A_(J));
end

%%
clc
for bitlen=3:21
    a=load(['CodeCyclic' num2str(bitlen)]);
    a.codes=a.codes(2:end);
    len = length(a.codes);
    numRows = 94;
    numCols = ceil(len/numRows);
    fprintf(['', ...
        '\\begin{table*}[]\n', ...
        '\\centering\n', ...
        '\\caption{%i-bit codes. Total : %i}\n', ...
        '\\label{tab:code%i}\n', ...
        '\\noindent\\makebox[\\textwidth]{%%\n\\tiny\n', ...
        '\\begin{tabular}{@{}%s@{}}\n'],bitlen,len,bitlen,char([kron(ones(1,numCols-1),'ll|') 'll']));
    
    for i=1:numRows
        for j=1:numCols
            ind = (j-1)*numRows +(i-1) + 1;
            if ind>len
                fprintf(' &');
            else
                dec = a.codes(ind);
                bin = dec2bin(dec,bitlen);
                fprintf('%i & %s',dec,bin);
            end
            if j<numCols
                fprintf(' & ');
            end
        end
        fprintf('\\\\\n');
        
    end
    fprintf(['\\end{tabular}\n}\n',...
        '\\end{table*}\n\n\n']);
    
end

%%
p = [0 0 2 2 2 3 3 5 4 5 8 9 14 17 27 37 53 85 140 232 377]';
p2 = [0 0 0 0 0 0 2 4 3 5 6 8 12 15 25 35 52 83 138 231 376]';
c = [2, 3, 4, 6, 8, 14, 20, 36, 60, 108, 188, 352, 632, 1182, 2192, 4116, 7712, 14602, 27596, 52488, 99880]';
t = [1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21]';


ff=[t log2(c)]';
fprintf('\\draw[line width=1pt] ');
fprintf('(%.3f,%.3f) --',ff(:));
fprintf('(%.3f,%.3f)',ff(end-1:end));
fprintf(';\n\n');
