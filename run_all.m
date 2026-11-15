function run_all()
% Genera todas las figuras y resultados del informe. Ejecutar: run_all
mdl = 'enlace_fibra_8QAM'; load_system(mdl); set(0,'DefaultFigureVisible','off');
if ~exist('figs','dir'), mkdir figs; end
EbNoVec = 0:2:14;  res = struct();

% ---------- Diagrama de bloques ----------
try, print(['-s' mdl],'-dpng','-r200','figs/00_diagrama_bloques.png'); catch me, disp(me.message), end

% ---------- Caso base: constelaciones y ojos ----------
for e = [4 10 16]
    o = run_vis(mdl, struct('EbNo',e));
    if e==10, plot_const(o.txSym,'Constelación Tx (salida modulador 8-QAM)','figs/01_const_tx.png');
              plot_eye(o.txWave,8,'Ojo Tx (salida filtro RRC Tx)','figs/03_ojo_tx.png'); end
    plot_const(o.rxSym,sprintf('Constelación Rx, Eb/N0 = %d dB',e),sprintf('figs/02_const_rx_%02ddB.png',e));
    plot_eye(o.rxWave,8,sprintf('Ojo Rx (salida filtro RRC Rx), Eb/N0 = %d dB',e),sprintf('figs/04_ojo_rx_%02ddB.png',e));
end
o = run_vis(mdl, struct('EbNo',100));
plot_eye(o.rxWave,8,'Ojo Rx sin ruido (filtro adaptado RRC-RRC)','figs/04_ojo_rx_sin_ruido.png');

% ---------- Curvas BER ----------
cases = {
 'base',      'Base: RRC/RRC, r=0.25, span 10', struct()
 'normalTx',  'M1: Tx Normal + Rx RRC (Fig. 1)', struct('txShape','Normal')
 'r005',      'M2a: roll-off 0.05',              struct('rolloff',0.05)
 'r09',       'M2b: roll-off 0.9',               struct('rolloff',0.9)
 'span2',     'M3: span 2 símbolos',             struct('span',2)
 'delay1',    'M4: retardo erróneo (+1 bit)',    struct('delayErr',1)
 'noAGC',     'M5: sin AGC en Rx',               struct('useAGC',0)
 'sps2',      'M6: 2 muestras/símbolo',          struct('sps',2)
 'P10',       'M7: potencia Tx 10 W',            struct('P0',10)
 'cd',        'M8: con dispersión cromática',    struct('useCD',1)
};
if exist('figs/resultados_ber.mat','file') % borrar el .mat para repetir el barrido BER
    load('figs/resultados_ber.mat');
else
for i = 1:size(cases,1)
    b = zeros(size(EbNoVec));
    for j = 1:numel(EbNoVec)
        cfg = cases{i,3}; cfg.EbNo = EbNoVec(j); cfg.logPts = 10; cfg.maxNumBits = 2e6; cfg.maxNumErrs = 200;
        r = run_cfg(mdl, cfg); b(j) = r(1);
        fprintf('%-10s EbNo=%2d BER=%.3e\n', cases{i,1}, EbNoVec(j), b(j));
    end
    res.(cases{i,1}) = b;
end
theo = berawgn(EbNoVec,'qam',8);
save('figs/resultados_ber.mat','EbNoVec','res','theo','cases');
end
% Variables listas para bertool (pestaña Data Import o Monte Carlo)
assignin('base','BER_base',res.base);

plot_ber(EbNoVec, theo, res, cases, {'base'}, 'BER vs Eb/N0 — 8-QAM, 50 km, 15 Gbaud', 'figs/05_ber_base.png');
plot_ber(EbNoVec, theo, res, cases, {'base','normalTx','r005','r09','span2'}, 'Modificaciones de filtros', 'figs/06_ber_filtros.png');
plot_ber(EbNoVec, theo, res, cases, {'base','delay1','noAGC','sps2','P10'}, 'Modificaciones de retardo, ganancia, muestreo y potencia', 'figs/07_ber_otros.png');
plot_ber(EbNoVec, theo, res, cases, {'base','cd'}, 'Efecto de la dispersión cromática (D = 17 ps/nm·km)', 'figs/08_ber_cd.png');

% ---------- Figuras de las modificaciones ----------
vis = {
 'normalTx', struct('txShape','Normal','EbNo',100)
 'r005',     struct('rolloff',0.05,'EbNo',100)
 'r09',      struct('rolloff',0.9,'EbNo',100)
 'span2',    struct('span',2,'EbNo',100)
 'noAGC',    struct('useAGC',0,'EbNo',14)
 'sps2',     struct('sps',2,'EbNo',100)
 'cd',       struct('useCD',1,'EbNo',100)
};
for i = 1:size(vis,1)
    cfg = vis{i,2}; o = run_vis(mdl, cfg); s = getfield_def(cfg,'sps',8);
    nm = vis{i,1};
    plot_eye(o.rxWave, s, ['Ojo Rx — ' nm], sprintf('figs/m_%s_ojo_rx.png',nm));
    plot_const(o.rxSym, ['Constelación Rx — ' nm], sprintf('figs/m_%s_const_rx.png',nm));
    if strcmp(nm,'normalTx'), plot_eye(o.txWave, 8, 'Ojo Tx — filtro Normal', 'figs/m_normalTx_ojo_tx.png'); end
end
disp('Listo.');
end

% ================= funciones =================
function r = run_cfg(mdl, cfg)
    evalin('base','clearvars');
    f = fieldnames(cfg);
    for n = 1:numel(f), assignin('base', f{n}, cfg.(f{n})); end
    shape = getfield_def(cfg,'txShape','Square root');
    set_param([mdl '/RC Tx'],'filtType',shape);
    assignin('base','txShape',shape);
    sim(mdl);  r = evalin('base','BER');
    set_param([mdl '/RC Tx'],'filtType','Square root');
end
function o = run_vis(mdl, cfg)
    cfg.maxNumBits = 3*6000; cfg.maxNumErrs = 1e9; cfg.logPts = inf;
    evalin('base','clearvars');
    f = fieldnames(cfg);
    for n = 1:numel(f), assignin('base', f{n}, cfg.(f{n})); end
    shape = getfield_def(cfg,'txShape','Square root');
    set_param([mdl '/RC Tx'],'filtType',shape); assignin('base','txShape',shape);
    out = sim(mdl);
    set_param([mdl '/RC Tx'],'filtType','Square root');
    sk = 60;  % descarta transitorio inicial (símbolos)
    s = getfield_def(cfg,'sps',8);
    o.txSym  = squeeze_v(out.get('txSym'));  o.txSym = o.txSym(sk:end);
    o.rxSym  = squeeze_v(out.get('rxSym'));  o.rxSym = o.rxSym(sk:end);
    o.txWave = squeeze_v(out.get('txWave')); o.txWave = o.txWave(sk*s+1:end);
    o.rxWave = squeeze_v(out.get('rxWave')); o.rxWave = o.rxWave(sk*s+1:end);
end
function v = squeeze_v(x), v = x(:); end
function v = getfield_def(s,f,d), if isfield(s,f), v = s.(f); else, v = d; end, end
function plot_const(x, ttl, fn)
    fig = figure('Position',[0 0 520 520]); theme(fig,'light');
    ref = qammod(0:7,8,'UnitAveragePower',true);
    plot(real(x),imag(x),'.','MarkerSize',4,'Color',[0.2 0.45 0.8]); hold on
    plot(real(ref),imag(ref),'r+','MarkerSize',14,'LineWidth',2);
    axis equal; grid on; lim = max(1.6, 1.1*max(abs([real(x);imag(x)])));
    xlim([-lim lim]); ylim([-lim lim]); xlabel('En fase (I)'); ylabel('Cuadratura (Q)');
    title(ttl); legend('Recibido','Ideal','Location','southoutside','Orientation','horizontal');
    exportgraphics(fig, fn, 'Resolution', 150); close(fig);
end
function plot_eye(x, sps, ttl, fn)
    n = 2*sps; x = x(1:floor(numel(x)/n)*n); x = circshift(x, -sps/2);
    t = (0:n)/sps; fig = figure('Position',[0 0 900 420]); theme(fig,'light');
    parts = {real(x),'Fase (I)'; imag(x),'Cuadratura (Q)'};
    for p = 1:2
        subplot(1,2,p); v = parts{p,1}; m = reshape(v(1:end-n), n, []);
        m = [m; v(n+1:n:end).']; m = m(:, 1:min(end,600));
        plot(t, m, 'Color', [0.1 0.4 0.75 0.15]); grid on; xlim([0 2]);
        xlabel('Tiempo [símbolos]'); ylabel('Amplitud'); title(parts{p,2});
    end
    sgtitle(ttl); exportgraphics(fig, fn, 'Resolution', 150); close(fig);
end
function plot_ber(E, theo, res, cases, keys, ttl, fn)
    fig = figure('Position',[0 0 760 520]); theme(fig,'light');
    semilogy(E, theo, 'k--', 'LineWidth', 1.8, 'DisplayName', 'Teórica 8-QAM (AWGN)'); hold on
    mk = 'osd^v><ph*';
    for i = 1:numel(keys)
        idx = find(strcmp(cases(:,1), keys{i})); b = res.(keys{i}); b(b==0) = NaN;
        semilogy(E, b, ['-' mk(i)], 'LineWidth', 1.4, 'DisplayName', cases{idx,2});
    end
    grid on; ylim([1e-6 1]); xlabel('E_b/N_0 [dB]'); ylabel('BER'); title(ttl);
    legend('Location','southwest'); exportgraphics(fig, fn, 'Resolution', 150); close(fig);
end
