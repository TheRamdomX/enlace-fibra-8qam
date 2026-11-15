% Parámetros del enlace 8-QAM sobre 50 km de fibra (se cargan en InitFcn del modelo)
% Si una variable ya existe en el workspace (barrido de run_all.m) se respeta.
def = @(n,v) evalin('base', sprintf('if ~exist(''%s'',''var''), %s = %s; end', n, n, v));
def('M','8');            def('Rs','15e9');        def('sps','8');
def('rolloff','0.25');   def('span','10');        def('txShape','''Square root''');
def('alpha','0.2');      def('L','50');           def('lambda','1550e-9');
def('Dcd','17e-6');      def('useCD','0');        def('P0','1');
def('useAGC','1');       def('delayErr','0');     def('EbNo','10');
def('maxNumErrs','300'); def('logPts','inf'); def('maxNumBits','1e6'); def('frameLen','300');
evalin('base', 'init_derived');
