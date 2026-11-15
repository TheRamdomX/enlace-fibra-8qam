% Magnitudes derivadas (se recalculan cada vez que cambia un parámetro)
k   = log2(M);  Ts = 1/Rs;  fs = sps*Rs;
Ga  = 10^(-alpha*L/10);          % ganancia de potencia de la fibra
K   = sqrt(Ga);                  % ganancia de amplitud (bloque Gain)
Kin = sqrt(P0);                  % amplificador de potencia del Tx (P0 = 1 W por defecto)
Krx = 1/(K*Kin);                 % AGC del receptor
if ~useAGC, Krx = 1; end

% Dispersión cromática: FIR de Ncd taps, retardo fijo de Ncd/2 muestras (= 16 símbolos con sps=8)
c = 3e8;  beta2 = -lambda^2*Dcd/(2*pi*c);  % s^2/m
Ncd = 256;  f = (-Ncd/2:Ncd/2-1)*fs/Ncd;
if useCD
    H   = exp(-1j*2*pi^2*beta2*(L*1e3)*f.^2);
    hCD = fftshift(ifft(ifftshift(H)));
else
    hCD = [zeros(1,Ncd/2) 1 zeros(1,Ncd/2-1)];   % mismo retardo, sin dispersión
end
cdDelaySym = (Ncd/2)/sps;

% Potencia que entra al AWGN: se mide sobre el filtro Tx real
tx  = comm.RaisedCosineTransmitFilter('Shape',txShape,'RolloffFactor',rolloff, ...
      'FilterSpanInSymbols',span,'OutputSamplesPerSymbol',sps);
s   = qammod(randi([0 M-1],4000,1),M,'UnitAveragePower',true);
y   = tx(s);  y = y(span*sps+1:end);
Psig = P0*Ga*mean(abs(y).^2);

% Retardo total en bits para Error Rate Calculation
delaySym  = span + cdDelaySym;           % span/2 (Tx) + span/2 (Rx) + FIR CD
delayBits = k*delaySym + delayErr;
