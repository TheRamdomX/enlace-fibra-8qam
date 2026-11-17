% Construye enlace_fibra_8QAM.slx (enlace 8-QAM, 50 km, 15 Gbaud)
mdl = 'enlace_fibra_8QAM';
if bdIsLoaded(mdl), close_system(mdl,0); end
if exist([mdl '.slx'],'file'), delete([mdl '.slx']); end
new_system(mdl); open_system(mdl);
libs = {'commrandsrc3','commdigbbndam3','commfilt2','commchan3','commsink2','commutil2','simulink'};
for i=1:numel(libs), load_system(libs{i}); end
nl = @(s) sprintf(strrep(s,'|','\n'));
add = @(src,name,pos,varargin) add_block(nl(src),[mdl '/' name],'Position',pos,varargin{:});

y = 100; h = 50; w = 90; x = @(i) 30 + (i-1)*130; P = @(i,yy) [x(i) yy x(i)+w yy+h];
add('commrandsrc3/Random Integer|Generator','Random Integer',P(1,y), ...
    'SetSize','M','SampleTime','Ts','SamplesPerFrame','frameLen');
add('commdigbbndam3/Rectangular QAM|Modulator|Baseband','8-QAM Mod',P(2,y), ...
    'M','M','PowType','Average Power','AvgPow','1');
add('commfilt2/Raised Cosine|Transmit Filter','RC Tx',P(3,y), ...
    'filtType','Square root','R','rolloff','filtSpan','span','N','sps');
add('simulink/Math|Operations/Gain','Amplificador P0',P(4,y),'Gain','Kin');
add('simulink/Math|Operations/Gain','K (atenuacion)',P(5,y),'Gain','K');
add('simulink/Discrete/Discrete FIR Filter','Dispersion cromatica',P(6,y),'Coefficients','hCD','InputProcessing','Columns as channels (frame based)');
add('commchan3/AWGN|Channel','AWGN',P(7,y),'NoiseMethod','Signal to noise ratio  (Eb/No)','noiseMode','Signal to noise ratio  (Eb/No)', ...
    'EbNo','EbNo','BitsPerSymbol','k','SignalPower','Psig','SamplesPerSymbol','sps');
add('simulink/Math|Operations/Gain','AGC Rx',P(8,y),'Gain','Krx');
add('simulink/Discrete/Discrete FIR Filter','Compensacion CD',P(9,y),'Coefficients','hCDcomp','InputProcessing','Columns as channels (frame based)');
add('commfilt2/Raised Cosine|Receive Filter','RC Rx',P(10,y), ...
    'filtType','Square root','R','rolloff','filtSpan','span','N','sps','downFactor','sps');
add('commdigbbndam3/Rectangular QAM|Demodulator|Baseband','8-QAM Demod',P(11,y), ...
    'M','M','PowType','Average Power','AvgPow','1');
add('commutil2/Integer to Bit|Converter','Int2Bit Rx',P(12,y),'nbits','k');
add('commutil2/Integer to Bit|Converter','Int2Bit Tx',P(2,y+150),'nbits','k');
add('commsink2/Error Rate|Calculation','Error Rate Calculation',[x(13) y+60 x(13)+w y+60+80], ...
    'N','delayBits','PMode','Workspace','WsName','BER','stop','on', ...
    'numErr','maxNumErrs','maxBits','maxNumBits');

% Instrumentos pedidos (puntos 3 y 5)
add('commsink2/Constellation Diagram','Constelacion Tx',P(3,y-90));
add('commsink2/Constellation Diagram','Constelacion Rx',P(11,y-90));
add('commsink2/Eye Diagram','Ojo Tx',P(4,y-90),'SamplesPerSymbol','sps');
add('commfilt2/Raised Cosine|Receive Filter','RC Rx (sin decimar)',P(10,y+80), ...
    'filtType','Square root','R','rolloff','filtSpan','span','N','sps','downFactor','1');
add('commsink2/Eye Diagram','Ojo Rx',P(11,y+80),'SamplesPerSymbol','sps');

% Registro a workspace para generar las figuras del informe
tw = @(name,var,pos) add('simulink/Sinks/To Workspace',name,pos,'VariableName',var, ...
    'SaveFormat','Array','MaxDataPoints','logPts');
tw('log txSym','txSym',P(3,y+240)); tw('log txWave','txWave',P(4,y+240));
tw('log rxSym','rxSym',P(11,y+240)); tw('log rxWave','rxWave',P(12,y+80));
tw('log Pin','awgnIn',P(7,y+240));

c = @(a,b) add_line(mdl,a,b,'autorouting','smart');
c('Random Integer/1','8-QAM Mod/1');  c('8-QAM Mod/1','RC Tx/1');
c('RC Tx/1','Amplificador P0/1');     c('Amplificador P0/1','K (atenuacion)/1');
c('K (atenuacion)/1','Dispersion cromatica/1'); c('Dispersion cromatica/1','AWGN/1');
c('AWGN/1','AGC Rx/1'); c('AGC Rx/1','Compensacion CD/1'); c('Compensacion CD/1','RC Rx/1'); c('RC Rx/1','8-QAM Demod/1');
c('8-QAM Demod/1','Int2Bit Rx/1');    c('Int2Bit Rx/1','Error Rate Calculation/2');
c('Random Integer/1','Int2Bit Tx/1'); c('Int2Bit Tx/1','Error Rate Calculation/1');
c('8-QAM Mod/1','Constelacion Tx/1'); c('RC Rx/1','Constelacion Rx/1');
c('RC Tx/1','Ojo Tx/1'); c('Compensacion CD/1','RC Rx (sin decimar)/1'); c('RC Rx (sin decimar)/1','Ojo Rx/1');
c('8-QAM Mod/1','log txSym/1'); c('RC Tx/1','log txWave/1'); c('RC Rx/1','log rxSym/1');
c('RC Rx (sin decimar)/1','log rxWave/1'); c('Dispersion cromatica/1','log Pin/1');

set_param(mdl,'InitFcn','init_params','StopTime','inf','SolverType','Fixed-step', ...
    'Solver','FixedStepDiscrete');
save_system(mdl);
