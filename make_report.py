"""Genera Informe_Enlace_Fibra_8QAM.docx a partir de figs/ (ejecutar desde fibra8qam/)."""
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

F = 'figs/'
doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(1.8)
    s.left_margin = s.right_margin = Cm(2.0)
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(4)

def H(t, l=1): doc.add_heading(t, level=l)
def P(t):
    p = doc.add_paragraph(t); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; return p
def B(t): doc.add_paragraph(t, style='List Bullet')
def cap(t):
    p = doc.add_paragraph(t); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
def fig(path, w, c):
    doc.add_picture(F + path, width=Cm(w))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER; cap(c)
def grid(paths, w, c):
    t = doc.add_table(rows=1, cols=len(paths))
    for cell, p in zip(t.rows[0].cells, paths):
        cell.paragraphs[0].add_run().add_picture(F + p, width=Cm(w))
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap(c)
def table(rows, header=True):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = 'Light Grid Accent 1'
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            cell = t.cell(i, j); cell.text = str(v)
            for run in cell.paragraphs[0].runs: run.font.size = Pt(9)
    doc.add_paragraph()

# ---------- Portada breve ----------
t = doc.add_heading('Enlace de fibra óptica 8-QAM de 50 km en Simulink', 0)
P('Integrantes: ____________________   ____________________   ____________________')
P('Asignatura: Redes / Comunicaciones Ópticas — Fecha: ____________')

H('Abstract')
P('Se diseñó, implementó y validó en Simulink (MATLAB R2026b) un enlace de fibra óptica de 50 km que transmite '
  'datos binarios con modulación 8-QAM a 15 Gbaud (45 Gb/s), potencia media de 1 W, filtros de coseno alzado '
  'con roll-off 0,25 y span de 10 símbolos. El canal modela la atenuación de la fibra (α = 0,2 dB/km, 10 dB en '
  'total), el ruido AWGN parametrizado por Eb/N0 y, de forma opcional, la dispersión cromática (D = 17 ps/nm·km) '
  'mediante un filtro FIR. La curva BER vs Eb/N0 simulada coincide con la teórica de 8-QAM en AWGN dentro del '
  'error estadístico (p. ej. 6,9·10⁻⁴ simulada vs 6,5·10⁻⁴ teórica a 10 dB). Se analizaron ocho modificaciones '
  'del enlace: el desajuste de filtros, el roll-off bajo y el span corto introducen interferencia entre símbolos '
  '(ISI) con penalidades de 1 a 3 dB o pisos de error; un error de retardo de un solo bit o la ausencia de control '
  'de ganancia hacen inutilizable el enlace; y la dispersión cromática sin compensar produce un piso de BER ≈ 0,15.')

H('1. Introducción')
P('Los sistemas ópticos modernos (DWDM, redes de transporte ópticas, accesos de alta capacidad) migraron desde '
  'OOK hacia formatos multinivel en cuadratura (QPSK, M-QAM), que transmiten más bits por símbolo y aprovechan '
  'la detección coherente con procesamiento digital para compensar dispersión cromática, dispersión por modo de '
  'polarización y efectos no lineales. 8-QAM transporta 3 bits/símbolo, un punto intermedio entre QPSK (2) y '
  '16-QAM (4) en eficiencia espectral y robustez frente al ruido.')
P('Nota de modelado: el enunciado menciona modulación de intensidad con detección directa, pero un formato QAM '
  'transporta información en la fase, que la detección directa (fotodiodo) no recupera. El modelo implementado es, '
  'por lo tanto, el equivalente en banda base complejo de un enlace con detección coherente: la conversión '
  'eléctrico-óptica y óptico-eléctrica se consideran ideales y el canal se representa por su efecto sobre la '
  'envolvente compleja.')

H('2. Desarrollo')
H('2.1 Parámetros y cálculos previos', 2)
table([
 ['Parámetro', 'Valor', 'Comentario'],
 ['Modulación', '8-QAM rectangular (4×2), Gray', 'k = log₂8 = 3 bits/símbolo'],
 ['Tasa de símbolo / bits', '15 Gbaud / 45 Gb/s', 'Ts = 66,7 ps'],
 ['Potencia media Tx', '1 W (30 dBm) sobre 1 Ω', 'normalización "Average Power"'],
 ['Filtros', 'Coseno alzado raíz (RRC), r = 0,25, span 10', '8 muestras/símbolo, fs = 120 GHz'],
 ['Atenuación', 'αL = 0,2·50 = 10 dB', 'Ga = 10^(−αL/10) = 0,1'],
 ['Ganancia bloque K', '√Ga = 0,3162', 'el bloque Gain actúa sobre amplitud'],
 ['Potencia tras la fibra', '0,1 W (20 dBm)', '0,0125 W por muestra a la entrada del AWGN'],
 ['β₂ = −λ²D/(2πc)', '−21,7 ps²/km', 'β₂L = −1084 ps² en 50 km'],
 ['Long. de dispersión L_D = Ts²/|β₂|', '≈ 205 km', 'ensanchamiento ≈ 127 ps ≈ 1,9 símbolos'],
 ['Retardo extremo a extremo', '10 símb. (filtros) + 16 símb. (FIR)', '= 78 bits en Error Rate Calculation'],
])
H('2.2 Diagrama de bloques', 2)
fig('00_diagrama_bloques.png', 17, 'Figura 1. Modelo Simulink enlace_fibra_8QAM.slx.')
P('Transmisor: Random Integer Generator (M = 8, una muestra cada Ts, tramas de 300 símbolos) → Rectangular QAM '
  'Modulator (M = 8, potencia media 1 W) → Raised Cosine Transmit Filter (RRC). El bloque "Amplificador P0" '
  'permite escalar la potencia de transmisión (vale 1 en el caso base). Canal: Gain K = 0,3162 (atenuación) → '
  'Discrete FIR Filter con la respuesta H_CD(f) = exp(−j2π²β₂Lf²) (256 coeficientes complejos obtenidos por IFFT; '
  'cuando la dispersión está desactivada se reemplaza por un retardo puro de 128 muestras para mantener la '
  'alineación) → AWGN Channel en modo Eb/N0, 3 bits/símbolo, 8 muestras/símbolo y potencia de entrada 0,0125 W. '
  'Receptor: AGC (ganancia 1/K, equivalente al amplificador/preamplificador óptico del receptor) → Raised Cosine '
  'Receive Filter (RRC, diezmado ×8) → Rectangular QAM Demodulator → Integer to Bit Converter. El bloque Error '
  'Rate Calculation compara los bits transmitidos con los recibidos con un retardo de 78 bits, guarda el vector '
  '[BER, errores, bits] en la variable BER y detiene la simulación al alcanzar maxNumErrs errores o maxNumBits '
  'bits, lo que lo hace compatible con la pestaña Monte Carlo de bertool. Se incluyen los instrumentos '
  'Constellation Diagram (salida del modulador y entrada del demodulador) y Eye Diagram (salida de los filtros Tx y Rx).')
P('Validación del modelo: sin ruido (Eb/N0 = 100 dB) la BER fue exactamente 0 en 3·10⁵ bits; la potencia medida '
  'a la entrada del AWGN (0,01251 W) coincide con la calculada (0,01251 W), y la correlación cruzada entre símbolos '
  'transmitidos y recibidos confirmó el retardo de 26 símbolos.')

H('3. Resultados')
H('3.1 Diagrama de constelación', 2)
P('El diagrama de constelación representa cada símbolo en el plano complejo: componente en fase (I) en abscisas y '
  'en cuadratura (Q) en ordenadas, muestreado una vez por símbolo. En el transmisor muestra los 8 puntos ideales '
  '(4 niveles en I × 2 en Q, ±0,41 y ±1,22 en I, ±0,41 en Q para potencia media unitaria). En el receptor permite '
  'medir de forma visual y cuantitativa (EVM, MER) el ruido (dispersión de las nubes), la ISI (deformación de las '
  'nubes), errores de ganancia (constelación escalada), de fase o frecuencia (rotación) y de sincronismo.')
grid(['01_const_tx.png', '02_const_rx_04dB.png', '02_const_rx_10dB.png', '02_const_rx_16dB.png'], 4.1,
     'Figura 2. Constelación a la salida del modulador y a la entrada del demodulador para Eb/N0 = 4, 10 y 16 dB.')
P('A la salida del modulador los símbolos coinciden con los 8 puntos ideales. A la entrada del demodulador cada '
  'punto se convierte en una nube circular, lo que indica ruido aditivo gaussiano sin ISI ni distorsión de fase '
  '(gracias al filtro adaptado RRC–RRC y al AGC). A 4 dB las nubes se superponen y aparecen errores de decisión '
  '(BER ≈ 4,7·10⁻²); a 10 dB están separadas salvo colas ocasionales (BER ≈ 7·10⁻⁴) y a 16 dB son compactas. Las '
  'nubes conservan su posición, lo que confirma que la atenuación de 10 dB quedó correctamente compensada.')

H('3.2 Diagrama de ojo', 2)
P('El diagrama de ojo superpone segmentos de la forma de onda de duración dos símbolos sincronizados con el reloj '
  'de símbolo. La apertura vertical indica el margen frente al ruido, la apertura horizontal la tolerancia al '
  'jitter o error de sincronismo, el punto de máxima apertura el instante óptimo de muestreo, y el cierre del ojo '
  'evidencia ISI. En 8-QAM la rama I tiene 4 niveles (3 ojos) y la rama Q 2 niveles (1 ojo).')
grid(['03_ojo_tx.png', '04_ojo_rx_sin_ruido.png'], 8.2,
     'Figura 3. Ojo a la salida del filtro Tx (izq.) y a la salida del filtro Rx sin ruido (der.).')
grid(['04_ojo_rx_10dB.png', '04_ojo_rx_16dB.png'], 8.2,
     'Figura 4. Ojo a la salida del filtro Rx con Eb/N0 = 10 dB y 16 dB.')
P('A la salida del filtro Tx el ojo aparece parcialmente cerrado: un único filtro raíz de coseno alzado no cumple '
  'el criterio de Nyquist, por lo que en el instante de muestreo existe ISI. Tras el filtro Rx, la cascada RRC·RRC '
  'equivale a un coseno alzado completo y el ojo se abre con trayectorias que convergen en un punto en el instante '
  'óptimo (t = 0,5 en la figura): ISI nula. Con ruido el ojo se cierra verticalmente; a 10 dB los cruces se '
  'ensanchan pero el ojo sigue abierto, coherente con una BER baja. La rama Q (2 niveles) presenta mayor apertura '
  'relativa que la I (4 niveles), por lo que la mayoría de los errores ocurren entre niveles de la rama I.')

H('3.3 BER vs Eb/N0 (bertool)', 2)
fig('05_ber_base.png', 11, 'Figura 5. BER vs Eb/N0 simulada (barrido 0:2:14 dB, hasta 200 errores o 2·10⁶ bits por punto) y teórica (bertool).')
table([
 ['Eb/N0 [dB]', '0', '2', '4', '6', '8', '10', '12', '14'],
 ['Teórica', '1,3e-1', '8,7e-2', '4,7e-2', '1,9e-2', '5,0e-3', '6,5e-4', '2,9e-5', '2,3e-7'],
 ['Simulada', '1,4e-1', '8,2e-2', '4,7e-2', '1,9e-2', '5,5e-3', '6,9e-4', '3,0e-5', '5,0e-7'],
])
P('La curva simulada se superpone a la teórica de 8-QAM en AWGN. La única diferencia apreciable está a 14 dB, '
  'donde con 2·10⁶ bits solo se observó un error, de modo que el estimador no es confiable (se requerirían ~10⁸ '
  'bits). Para alcanzar BER = 10⁻³ (umbral típico antes de FEC) el enlace requiere Eb/N0 ≈ 9,6 dB. Como Eb/N0 es '
  'una magnitud relativa, el resultado no depende de la potencia absoluta; la atenuación de la fibra afecta la '
  'BER solo a través de la SNR que llega al receptor frente a su ruido propio.')

H('4. Modificaciones y análisis')
P('Se mantuvo la modulación 8-QAM y la longitud de 50 km, y se realizaron ocho modificaciones (incluida la '
  'dispersión cromática opcional). En la Tabla 3 se resume su efecto.')
table([
 ['#', 'Modificación', 'BER @10 dB', 'Efecto'],
 ['—', 'Base (RRC/RRC, r=0,25, span 10)', '6,9e-4', 'Coincide con la teoría'],
 ['M1', 'Tx Normal + Rx RRC (config. Fig. 1 del enunciado)', '2,1e-3', '≈1,2 dB de penalidad a 10⁻³; ISI residual'],
 ['M2a', 'Roll-off 0,05', '3,8e-3', '≈2,5 dB de penalidad; ojo muy estrecho'],
 ['M2b', 'Roll-off 0,9', '7,6e-4', 'Sin penalidad; ancho de banda 28,5 GHz vs 18,75 GHz'],
 ['M3', 'Span 2 símbolos', '4,7e-2', 'Piso de error ≈ 4·10⁻²: filtros truncados'],
 ['M4', 'Retardo erróneo (+1 bit)', '0,52', 'BER ≈ 0,5: bits comparados desalineados'],
 ['M5', 'Sin AGC en el receptor', '0,18', 'Piso ≈ 0,15: constelación escalada por 0,32'],
 ['M6', '2 muestras/símbolo', '7,0e-4', 'Sin cambio en BER; ojo pobremente muestreado'],
 ['M7', 'Potencia Tx 10 W', '6,2e-4', 'Sin cambio: Eb/N0 es relativo a la señal'],
 ['M8', 'Dispersión cromática D = 17 ps/nm·km', '0,14', 'Piso ≈ 0,15: ISI de ~2 símbolos sin ecualizar'],
])
fig('06_ber_filtros.png', 11.5, 'Figura 6. BER para las modificaciones de los filtros (M1–M3).')
grid(['m_normalTx_ojo_rx.png', 'm_r005_ojo_rx.png'], 8.2, 'Figura 7. Ojo Rx sin ruido con Tx Normal (M1) y con roll-off 0,05 (M2a).')
grid(['m_r09_ojo_rx.png', 'm_span2_ojo_rx.png'], 8.2, 'Figura 8. Ojo Rx sin ruido con roll-off 0,9 (M2b) y span de 2 símbolos (M3).')
P('M1 – Filtro Normal en Tx y raíz en Rx: la respuesta total es un coseno alzado multiplicado por un raíz, que no '
  'es de Nyquist; el ojo Rx muestra trayectorias que no convergen a un punto (ISI) y el filtro Rx deja de ser '
  'adaptado, perdiendo SNR. La penalidad crece con Eb/N0 (≈1,2 dB a 10⁻³ y ≈2,5 dB a 10⁻⁴), porque la ISI es '
  'determinística y domina cuando el ruido es pequeño. Por ello se adoptó RRC–RRC como caso base.')
P('M2 – Roll-off: con r = 0,05 el ancho de banda ocupado baja a 15,75 GHz, pero el pulso decae muy lentamente y el '
  'span de 10 símbolos lo trunca, generando ISI y un ojo con apertura horizontal casi nula (sensibilidad máxima al '
  'jitter): ≈2,5 dB de penalidad. Con r = 0,9 el ojo es muy abierto y la BER es la teórica, a costa de ocupar '
  '28,5 GHz (+52 % respecto del base), lo que reduce la cantidad de canales en un sistema DWDM. r = 0,25 es un buen '
  'compromiso.')
P('M3 – Span de 2 símbolos: los filtros quedan con solo 17 coeficientes y dejan de ser de Nyquist y adaptados. '
  'Incluso sin ruido, en el instante de muestreo (desplazado a t = 1 en la Fig. 8 por el menor retardo) la rama I '
  'converge a 7 niveles en lugar de 4 y la Q a 3 en lugar de 2: la ISI fusiona niveles vecinos. La BER se estanca '
  'en ≈4·10⁻², un piso de error que no se corrige aumentando la potencia.')
fig('07_ber_otros.png', 11.5, 'Figura 9. BER para las modificaciones de retardo, ganancia, muestreo y potencia (M4–M7).')
grid(['m_noAGC_const_rx.png', 'm_sps2_ojo_rx.png'], 7.5, 'Figura 10. Constelación Rx sin AGC (M5) y ojo Rx con 2 muestras/símbolo (M6).')
P('M4 – Retardo: desplazar el retardo de Error Rate Calculation en un solo bit hace que se comparen bits no '
  'correspondientes y la BER es ≈0,5 para cualquier Eb/N0 (comparación de secuencias independientes). La '
  'sincronización de trama/símbolo es tan crítica como la SNR.')
P('M5 – Sin AGC: la señal llega con amplitud √0,1 = 0,32 veces la esperada; el demodulador usa umbrales para '
  'potencia 1 W y decide todos los símbolos como de las columnas interiores (Fig. 10). La BER queda en ≈0,15–0,2. '
  'En QAM la amplitud porta información, a diferencia de QPSK, por lo que el control de ganancia del receptor '
  '(o un amplificador óptico) es indispensable.')
P('M6 – 2 muestras/símbolo: la BER no cambia porque las decisiones solo dependen de la muestra óptima y el bloque '
  'AWGN referencia correctamente la potencia por símbolo; sin embargo los diagramas de ojo pierden resolución y '
  'la simulación es menos representativa de la forma de onda analógica.')
P('M7 – Potencia de 10 W: la BER es idéntica, porque el bloque AWGN ajusta el ruido para mantener el Eb/N0 '
  'pedido. En un enlace real el aumento de potencia sí mejora la SNR (ruido del receptor fijo), hasta que aparecen '
  'efectos no lineales de la fibra (Kerr), no modelados aquí.')
fig('08_ber_cd.png', 10, 'Figura 11. BER con y sin dispersión cromática (M8, punto opcional 7).')
grid(['m_cd_const_rx.png', 'm_cd_ojo_rx.png'], 7.5, 'Figura 12. Constelación y ojo Rx sin ruido con dispersión cromática.')
P('M8 – Dispersión cromática: el FIR de 256 coeficientes implementa la fase cuadrática −2π²β₂Lf². Aunque 50 km '
  'es menor que L_D ≈ 205 km, el ensanchamiento estimado (≈127 ps ≈ 1,9 símbolos) basta para mezclar cada símbolo '
  'con sus vecinos: la constelación sin ruido se convierte en nubes deformadas y rotadas, el ojo se cierra y la BER '
  'se estanca en ≈0,15 independientemente de Eb/N0. Esto justifica el uso de detección coherente con '
  'compensación digital: aplicar en el receptor el filtro inverso H_CD*(f) = exp(+j2π²β₂Lf²) eliminaría el efecto '
  'por ser un sistema de fase pura (unitario). En un sistema IM/DD, en cambio, la dispersión produciría además '
  'desvanecimiento selectivo en frecuencia, que no es compensable linealmente.')

H('5. Conclusiones')
B('El modelo implementado reproduce la BER teórica de 8-QAM en AWGN (BER = 10⁻³ a Eb/N0 ≈ 9,6 dB), lo que valida '
  'la atenuación (Ga = 0,1), la calibración de potencia del canal AWGN (0,0125 W/muestra) y el retardo de 78 bits.')
B('La atenuación de 10 dB de la fibra es transparente para la BER siempre que el receptor recupere la escala de '
  'amplitud; sin control de ganancia la detección 8-QAM falla (BER ≈ 0,15) porque la amplitud porta información.')
B('Los filtros de coseno alzado deben formar un par adaptado RRC–RRC con span suficiente: la configuración Normal–raíz '
  'cuesta 1–2,5 dB y spans cortos o roll-off muy bajos generan ISI y pisos de error. El roll-off fija el '
  'compromiso entre ancho de banda (15·(1+r) GHz) y robustez a ISI y jitter.')
B('Los diagramas de constelación y de ojo permiten diagnosticar el tipo de degradación: ruido (nubes circulares, '
  'ojo cerrado verticalmente), ISI (nubes deformadas, cruces no convergentes) o error de ganancia (constelación '
  'escalada), complementando la curva BER.')
B('La dispersión cromática a 1550 nm (D = 17 ps/nm·km) produce en 50 km a 15 Gbaud una ISI de ~2 símbolos que '
  'vuelve inutilizable el enlace sin compensación; en sistemas reales se corrige por DSP en receptores coherentes '
  'o con fibra compensadora.')
P('Archivos entregados: enlace_fibra_8QAM.slx (modelo), init_params.m / init_derived.m (parámetros, cargados en '
  'InitFcn), build_model.m (construcción del modelo) y run_all.m (barridos y figuras).')

doc.save('Informe_Enlace_Fibra_8QAM.docx')
print('ok')
