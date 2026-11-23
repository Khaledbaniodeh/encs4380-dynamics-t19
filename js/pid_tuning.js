/* P4 PID Tuning Challenge — browser UI. Simulation and challenge generation live in
   python/pid_tuning.py, running inside Pyodide (no server-side Python). */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const params = ['kp', 'ki', 'kd'];
  const defaults = {kp: 1.5, ki: 1, kd: 0.2};
  const state = {py: null, ready: false, busy: false, locked: false, challenge: null,
    tried: false, attempts: 0, roundBest: 0, rounds: 0, total: 0,
    lastResponse: null, previousOutput: null, zoomed: false, fullView: false};

  const format = (v, decimals=2) => v == null ? '—' : Number(v).toFixed(decimals);
  function showError(text) {
    $('input-error').textContent = text;
    $('input-error').hidden = !text;
  }
  function setStatus(text, style) {
    const element = $('python-status');
    element.className = `pill ${style}`;
    element.innerHTML = `<span class="dot"></span>${text}`;
  }
  function refreshSession() {
    $('total-points').textContent = format(state.total);
    $('average-score').textContent = state.rounds ? format(state.total/state.rounds) : '—';
    $('rounds-count').textContent = String(state.rounds);
  }
  function setBusy(busy) {
    state.busy = busy;
    const enabled = state.ready && !busy;
    $('new-challenge').disabled = !enabled;
    $('reset-session').disabled = !enabled;
    $('gain-fields').disabled = !enabled || state.locked;
    $('prediction-fields').disabled = !enabled || state.locked;
    $('check-tuning').disabled = !enabled || state.locked;
    $('reset-gains').disabled = !enabled || state.locked;
    $('show-hint').disabled = !enabled || state.locked;
    $('response-zoom').disabled = !enabled || !state.challenge;
    $('response-full').disabled = !enabled || !state.challenge;
    $('response-expand').disabled = !enabled || !state.challenge;
    $('reveal-plant').disabled = !enabled || state.locked;
    $('check-tuning').textContent = busy ? 'Simulating...' : (state.locked ? 'Round finished' : 'Check Tuning →');
  }
  function gainValues() {
    const out = {};
    for (const name of params) {
      const el = $(`${name}-number`);
      if (!el.value.trim()) throw new Error(`${name.toUpperCase()} is required.`);
      const v = Number(el.value);
      const min = Number(el.min), max = Number(el.max);
      if (!Number.isFinite(v) || v < min || v > max)
        throw new Error(`${name.toUpperCase()} must be between ${min} and ${max}.`);
      out[name] = v;
    }
    return out;
  }
  function syncInputs() {
    for (const name of params) {
      const range = $(`${name}-range`), number = $(`${name}-number`);
      range.addEventListener('input', () => {number.value = range.value; showError('');});
      number.addEventListener('input', () => {
        const v = Number(number.value);
        if (number.value && Number.isFinite(v) && v >= Number(number.min) && v <= Number(number.max)) range.value = String(v);
        showError('');
      });
    }
    $('reset-gains').addEventListener('click', () => resetGains());
    $('response-zoom').addEventListener('click', toggleResponseZoom);
    $('response-full').addEventListener('click', toggleFullView);
    $('response-expand').addEventListener('click', toggleExpandChart);
    window.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && $('response-card').classList.contains('is-expanded')) toggleExpandChart();
    });
    $('show-hint').addEventListener('click', () => {
      const willOpen = $('hint-content').hidden;
      $('hint-content').hidden = !willOpen;
      $('show-hint').textContent = willOpen ? 'Hide Hint' : 'Get Hint';
      $('show-hint').setAttribute('aria-expanded', String(willOpen));
    });
  }
  function resetGains() {
    for (const name of params) {
      $(`${name}-range`).value = String(defaults[name]);
      $(`${name}-number`).value = String(defaults[name]);
    }
    document.querySelectorAll('input[name="prediction"]').forEach(el => { el.checked = false; });
    showError('');
  }
  function resetChallengeUi() {
    state.locked = false; state.tried = false; state.attempts = 0; state.roundBest = 0;
    state.lastResponse = null; state.previousOutput = null; state.zoomed = false; state.fullView = false;
    setChartExpanded(false);
    updateZoomButton();
    resetGains();
    $('result-panel').hidden = true;
    $('chart-checks').hidden = true;
    $('chart-checks').replaceChildren();
    $('revealed-plant').hidden = true;
    $('revealed-plant').textContent = '';
    $('reveal-plant').hidden = false;
    $('hint-content').hidden = true;
    $('show-hint').textContent = 'Get Hint';
    $('show-hint').setAttribute('aria-expanded', 'false');
    $('attempt-badge').textContent = 'Loading original plant';
    $('response-placeholder').hidden = false;
    $('response-chart').hidden = true;
    $('control-placeholder').hidden = false;
    $('control-chart').hidden = true;
    if (window.Plotly) {
      // Purge old plots when a round changes; prevents stale plots and memory leak.
      for (const id of ['response-chart','control-chart']) {
        try { window.Plotly.purge($(id)); } catch (_) { /* not yet plotted */ }
      }
    }
  }
  function newChallenge() {
    if (!state.ready || state.busy) return;
    setBusy(true);
    try {
      const result = JSON.parse(state.py.runPython('new_challenge_json()'));
      state.challenge = result;
      resetChallengeUi();
      $('challenge-number').textContent = `#${result.challenge_number}`;
      $('plant-type').textContent = result.plant_type === 'first_order' ? 'First-Order Plant' : 'Second-Order Plant';
      $('spec-os').textContent = `≤ ${format(result.specs.overshoot_max_percent,0)}%`;
      $('spec-ts').textContent = `≤ ${format(result.specs.settling_max_seconds,1)} s`;
      $('spec-ess').textContent = `≤ ${format(result.specs.steady_error_max_percent,1)}%`;
      drawInitialResponse(result.baseline);
      updateZoomButton();
    } catch (err) {
      showError(`Could not create challenge: ${err.message || err}`);
    } finally {setBusy(false);}
  }
  function plotLayout(title, yTitle, short=false) {
    // Let Plotly fill the CSS-sized chart; a fixed layout height previously
    // made the plot smaller than its available card, especially on desktop.
    return {margin:{l:65,r:24,t:22,b:82},autosize:true,
      paper_bgcolor:'#ffffff',plot_bgcolor:'#ffffff',font:{color:'#405568',size:13,family:'Segoe UI, system-ui, sans-serif'},
      xaxis:{title:{text:'Time (s)',font:{size:13},standoff:12},tickfont:{size:12},nticks:9,
        gridcolor:'#e6edf2',linecolor:'#b7c6d1',showline:true,zeroline:false,automargin:true},
      yaxis:{title:{text:yTitle,font:{size:13},standoff:10},tickfont:{size:12},nticks:8,
        gridcolor:'#e6edf2',linecolor:'#b7c6d1',showline:true,zeroline:false,automargin:true},
      showlegend:true,legend:{orientation:'h',x:0,y:-0.20,xanchor:'left',font:{size:12},traceorder:'normal'},
      hovermode:'x unified',dragmode:'pan',
      title:title?{text:title,font:{size:14}}:undefined};
  }
  // Display only the first 8 seconds by default; retain the complete 16-second
  // simulation for settling calculations, scoring, and full-view inspection.
  // Changing the view NEVER reruns the solver or changes the challenge.
  function zoomEnd(times) {
    const full = times[times.length - 1];
    const spec = Number(state.challenge?.specs?.settling_max_seconds) || 3;
    return Math.min(full, Math.max(3.5, Math.min(8, spec * 1.6)));
  }
  function visibleEnd(times) {
    const full = times[times.length - 1];
    if (state.fullView) return full;
    if (state.zoomed) return zoomEnd(times);
    return Math.min(8, full);
  }
  function updateZoomButton() {
    const zoom = $('response-zoom');
    zoom.textContent = state.zoomed ? 'Back to 8 s' : 'Zoom to transient';
    zoom.setAttribute('aria-pressed', String(state.zoomed));
    const fullButton = $('response-full');
    fullButton.textContent = state.fullView ? 'Back to 8 s' : 'Show all 16 s';
    fullButton.setAttribute('aria-pressed', String(state.fullView));
    const times = state.challenge?.baseline?.time;
    $('response-view-window').textContent = times?.length
      ? (state.fullView ? `Full view · 0–${format(times.at(-1),0)} s`
         : state.zoomed ? `Detail view · 0–${format(visibleEnd(times),1)} s`
         : `Default view · 0–${format(visibleEnd(times),0)} s`)
      : 'Default view · 0–8 s';
  }
  function redrawCurrentCharts() {
    if (state.lastResponse) drawPlots(state.lastResponse);
    else drawInitialResponse(state.challenge.baseline);
  }
  function toggleResponseZoom() {
    if (!state.ready || state.busy || !state.challenge) return;
    state.zoomed = !state.zoomed;
    state.fullView = false;
    updateZoomButton();
    redrawCurrentCharts();
  }
  function toggleFullView() {
    if (!state.ready || state.busy || !state.challenge) return;
    state.fullView = !state.fullView;
    state.zoomed = false;
    updateZoomButton();
    redrawCurrentCharts();
  }
  function setChartExpanded(expanded) {
    $('response-card').classList.toggle('is-expanded', expanded);
    document.body.classList.toggle('chart-expanded', expanded);
    const button=$('response-expand');
    button.textContent=expanded ? 'Exit expanded view' : 'Expand chart';
    button.setAttribute('aria-pressed', String(expanded));
    // Plotly has a responsive layout, but explicitly resize when switching
    // from the column to a fullscreen-sized chart to prevent stale dimensions.
    if (window.Plotly && window.Plotly.Plots?.resize && !$('response-chart').hidden) {
      window.requestAnimationFrame(() => {
        try { window.Plotly.Plots.resize($('response-chart')); } catch (_) { /* fallback SVG needs no resize */ }
      });
    }
  }
  function toggleExpandChart() {
    if (!state.ready || state.busy || !state.challenge) return;
    setChartExpanded(!$('response-card').classList.contains('is-expanded'));
  }
  function focusedLayout(yTitle, times, traces, short=false) {
    const layout = plotLayout('', yTitle, short);
    if (!times?.length || state.fullView) return layout;
    const end = visibleEnd(times);
    layout.xaxis.range = [0, end];
    const values = [];
    for (const trace of traces) {
      for (let i = 0; i < trace.y.length; i++) {
        if (trace.x[i] <= end + 1e-8 && Number.isFinite(trace.y[i])) values.push(trace.y[i]);
      }
    }
    if (values.length) {
      const low = Math.min(0, ...values);
      const high = Math.max(1, ...values);
      const padding = Math.max(.06, (high - low) * .10);
      layout.yaxis.range = [low - padding, high + padding];
    }
    return layout;
  }
  function clippedFallback(times, lines) {
    if (!times.length || state.fullView) return {times, lines};
    const end = visibleEnd(times);
    const firstBeyond = times.findIndex(t => t > end);
    if (firstBeyond < 0) return {times, lines};
    // Keep the right edge at EXACTLY 8 s (or the requested detail end), even
    // if the solver/smoke-test sample points skip over that timestamp.
    const before = firstBeyond - 1;
    if (before < 0) return {times: times.slice(0,1), lines: lines.map(line=>({...line,y:line.y.slice(0,1)}))};
    if (Math.abs(times[before] - end) < 1e-10)
      return {times: times.slice(0,firstBeyond), lines: lines.map(line=>({...line,y:line.y.slice(0,firstBeyond)}))};
    const fraction = (end - times[before]) / (times[firstBeyond] - times[before]);
    return {
      times: [...times.slice(0,firstBeyond),end],
      lines: lines.map(line=>({...line,y:[...line.y.slice(0,firstBeyond),
        line.y[before] + fraction * (line.y[firstBeyond] - line.y[before])]}))
    };
  }
  function drawInitialResponse(baseline) {
    // The student sees this genuine RK4 plant response BEFORE any PID tuning.
    // It is an open-loop unit ACTUATOR step u=1, not a PID simulation.
    if (!baseline || !Array.isArray(baseline.time) || !Array.isArray(baseline.output)
        || !baseline.time.length || baseline.time.length !== baseline.output.length)
      throw new Error('The initial plant response is missing or incomplete.');
    $('response-placeholder').hidden = true;
    $('response-chart').hidden = false;
    $('attempt-badge').textContent = 'Original plant · before PID';
    const setpoint = baseline.time.map(() => 1);
    if (!window.Plotly) {
      drawFallback($('response-chart'), baseline.time, [
        {y:setpoint, color:'#315dda',dash:'5,4',label:'Setpoint r=1'},
        {y:baseline.output,color:'#8799aa',dash:'3,4',label:'Open-loop u=1'}
      ], 'Open-loop plant output');
      return;
    }
    const sample = {x:baseline.time,mode:'lines',type:'scatter',hovertemplate:'%{y:.3f}<extra></extra>'};
    const traces = [
      {...sample,y:setpoint,name:'Setpoint r=1',line:{color:'#315dda',dash:'dash',width:2}},
      {...sample,y:baseline.output,name:'Original plant (u=1)',line:{color:'#8799aa',dash:'dot',width:3.2}}
    ];
    const config={responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','autoScale2d'],scrollZoom:false};
    window.Plotly.react('response-chart',traces,focusedLayout('Output y(t)',baseline.time,traces),config);
  }
  function drawPlots(result) {
    $('response-placeholder').hidden = true;
    $('response-chart').hidden = false;
    $('control-placeholder').hidden = true;
    $('control-chart').hidden = false;
    const original = state.challenge.baseline;
    if (!window.Plotly) {
      // The supplied offline plot renderer is used when the CDN is unavailable.
      drawFallback($('response-chart'), result.time, [
        {y:result.time.map(()=>1),color:'#315dda',dash:'5,4',label:'Setpoint'},
        {y:original.output,color:'#8799aa',dash:'3,4',label:'Original plant'},
        ...(state.previousOutput?[{y:state.previousOutput,color:'#b56425',dash:'6,4',label:'Previous PID'}]:[]),
        {y:result.output,color:'#087f72',label:'Current PID'}], 'Output');
      drawFallback($('control-chart'), result.time, [
        {y:result.time.map(()=>10),color:'#b56425',dash:'5,4',label:'Limit +10'},
        {y:result.time.map(()=>-10),color:'#b56425',dash:'5,4',label:'Limit -10'},
        {y:result.control,color:'#315dda',label:'u(t)'}], 'Control');
      return;
    }
    const sample = {x:result.time,mode:'lines',type:'scatter',hovertemplate:'%{y:.3f}<extra></extra>'};
    const response = [
      {...sample,y:result.time.map(()=>1),name:'Setpoint',line:{color:'#315dda',dash:'dash',width:2}},
      {...sample,y:original.output,name:'Original plant (u=1)',line:{color:'#8799aa',dash:'dot',width:3.2}},
      ...(state.previousOutput?[{...sample,y:state.previousOutput,name:'Previous PID attempt',line:{color:'#b56425',dash:'dash',width:2}}]:[]),
      {...sample,y:result.output,name:'Current PID',line:{color:'#087f72',width:3.6}},
    ];
    const command = [
      {...sample,y:result.time.map(()=>10),name:'Max +10',line:{color:'#b56425',width:1,dash:'dash'}},
      {...sample,y:result.time.map(()=>-10),name:'Min -10',line:{color:'#b56425',width:1,dash:'dash'}},
      {...sample,y:result.control,name:'Control u(t)',line:{color:'#315dda',width:2.3}},
    ];
    const config = {responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d','autoScale2d'],scrollZoom:false};
    window.Plotly.react('response-chart',response,focusedLayout('Output y(t)',result.time,response),config);
    window.Plotly.react('control-chart',command,focusedLayout('Control u(t)',result.time,command,true),config);
  }
  function drawFallback(el, t, lines, title) {
    // Scalable SVG fallback (no Plotly connection): includes readable tick
    // labels, grid and a legend, and fills the larger CSS chart height.
    ({times:t, lines} = clippedFallback(t,lines));
    const compact=el.classList.contains('small');
    const w=Math.max(320, Math.round(el.clientWidth || 800));
    const h=Math.max(compact?240:320, Math.round(el.clientHeight || (compact?315:520)));
    const l=w<420?40:64,r=w<420?12:20,top=24,bot=112;
    const allY=lines.flatMap(x=>x.y.filter(Number.isFinite));
    const rawMin=Math.min(0,...allY),rawMax=Math.max(1,...allY);
    const pad=Math.max(.12,(rawMax-rawMin)*.10);const ymin=rawMin-pad,ymax=rawMax+pad;
    const total=t[t.length-1]-t[0] || 1;
    const X=(v)=>l+(v-t[0])/total*(w-l-r);
    const Y=(v)=>h-bot-(v-ymin)/(ymax-ymin)*(h-top-bot);
    const yticks=Array.from({length:6},(_,i)=>ymin+(ymax-ymin)*i/5);
    const gridY=yticks.map(y=>`<line x1="${l}" y1="${Y(y)}" x2="${w-r}" y2="${Y(y)}" stroke="#e5ecef"/><text x="${l-12}" y="${Y(y)+5}" font-size="12" text-anchor="end" fill="#536879">${y.toFixed(1)}</text>`).join('');
    const tickCount=w<460?5:9;
    const xticks=Array.from({length:tickCount},(_,i)=>t[0]+total*i/(tickCount-1));
    const gridX=xticks.map(x=>`<line x1="${X(x)}" y1="${top}" x2="${X(x)}" y2="${h-bot}" stroke="#edf1f5"/><text x="${X(x)}" y="${h-bot+26}" text-anchor="middle" font-size="12" fill="#536879">${Number(x.toFixed(1))}</text>`).join('');
    const paths=lines.map(line=>{
      const skip=Math.max(1,Math.ceil(t.length/1000));
      const points=t.map((v,k)=>({v,k})).filter((_,k)=>k%skip===0||k===t.length-1).map(({v,k})=>`${X(v).toFixed(1)},${Y(line.y[k]).toFixed(1)}`).join(' ');
      return `<polyline points="${points}" fill="none" stroke="${line.color}" stroke-width="${line.dash?2.4:3.5}" ${line.dash?`stroke-dasharray="${line.dash}"`:''}/>`;
    }).join('');
    const legendCols=w<460?2:3;
    const legendFont=w<460?10:12;
    const legend=lines.map((s,i)=>{
      const x=l+(i%legendCols)*((w-l-r)/legendCols), y=h-35+Math.floor(i/legendCols)*20;
      return `<line x1="${x}" y1="${y-4}" x2="${x+18}" y2="${y-4}" stroke="${s.color}" stroke-width="2.5" ${s.dash?`stroke-dasharray="${s.dash}"`:''}/><text x="${x+22}" y="${y}" font-size="${legendFont}" fill="#405568">${s.label}</text>`;
    }).join('');
    el.innerHTML=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${title} vs time" preserveAspectRatio="xMidYMid meet" style="width:100%;height:100%;display:block;overflow:hidden;font-family:Segoe UI,system-ui,sans-serif">${gridY}${gridX}<line x1="${l}" y1="${h-bot}" x2="${w-r}" y2="${h-bot}" stroke="#a4b6c1"/>${paths}<text x="${w/2}" y="${h-bot+54}" text-anchor="middle" font-size="12" fill="#536879">Time (s)</text>${legend}</svg>`;
  }
  const statusTag = (pass) => `<span class="${pass?'pass':'fail'}">${pass?'PASS':'FAIL'}</span>`;
  function resultRow(name, actual, max, ok) {
    const row=document.createElement('div'); row.className='check';
    // Only numerical values from our solver are inserted as text to avoid HTML injection.
    const text=document.createElement('div');const strong=document.createElement('strong');strong.textContent=name;
    const small=document.createElement('small');small.textContent=`Measured: ${actual} · Required: ${max}`;
    text.append(strong,small);row.append(text);
    const span=document.createElement('span');span.className=ok?'pass':'fail';span.textContent=ok?'PASS':'FAIL';row.append(span);
    return row;
  }
  function showChartChecks(result) {
    const m = result.metrics, passed = result.passes;
    const items = [
      ['Overshoot', m.overshoot_percent == null ? 'Unstable' : `${format(m.overshoot_percent,2)}%`, passed.overshoot],
      ['Settling time', m.settling_time == null ? 'Not settled' : `${format(m.settling_time,2)} s`, passed.settling],
      ['Steady-state error', m.steady_error_percent == null ? 'Unstable' : `${format(m.steady_error_percent,2)}%`, passed.steady_error]
    ];
    const container = $('chart-checks');
    container.replaceChildren();
    for (const [name, value, good] of items) {
      const card = document.createElement('div');
      card.className = `chart-check ${good ? 'is-pass' : 'is-fail'}`;
      const title = document.createElement('span');
      title.textContent = name;
      const number = document.createElement('strong');
      number.textContent = value;
      const status = document.createElement('span');
      status.textContent = good ? 'PASS' : 'FAIL';
      status.className = good ? 'pass' : 'fail';
      card.append(title,number,status);
      container.append(card);
    }
    container.hidden = false;
  }
  function showResults(result, predicted) {
    $('result-panel').hidden=false;
    const m=result.metrics,p=result.passes,s=state.challenge.specs;
    showChartChecks(result);
    $('result-overall').textContent=result.all_pass?'ALL SPECS PASSED':'KEEP TUNING';
    $('result-overall').className=`result-badge${result.all_pass?'':' fail'}`;
    $('result-score').textContent=`${format(result.score)} / 100`;
    const rows=$('result-checks');rows.replaceChildren();
    rows.append(
      resultRow('Overshoot',m.overshoot_percent==null?'Unstable':`${format(m.overshoot_percent)}%`,`≤ ${format(s.overshoot_max_percent,0)}%`,p.overshoot),
      resultRow('Settling time',m.settling_time==null?'Not settled':`${format(m.settling_time,2)} s`,`≤ ${format(s.settling_max_seconds,1)} s`,p.settling),
      resultRow('Steady-state error',m.steady_error_percent==null?'Unstable':`${format(m.steady_error_percent,2)}%`,`≤ ${format(s.steady_error_max_percent,1)}% + stable tail`,p.steady_error)
    );
    const correct=(predicted==='pass')===result.all_pass;
    $('prediction-feedback').textContent=correct?'✓ Your prediction matched this result.':'↻ Your prediction did not match — use the plot to learn why.';
    $('prediction-feedback').style.color=correct?'#167554':'#a36020';
    $('best-score-note').textContent=`Best score this round: ${format(state.roundBest)} / 100 · ${state.attempts} attempt${state.attempts===1?'':'s'}`;
  }
  function checkTuning() {
    if(!state.ready||state.busy||state.locked)return;
    let gains;
    try {gains=gainValues();}catch(err){showError(err.message);return;}
    const pred=document.querySelector('input[name="prediction"]:checked')?.value;
    if (!pred) {showError('Make a prediction (PASS or FAIL) before checking your tuning.');return;}
    showError('');setBusy(true);
    try {
      state.py.globals.set('p4_gains_json',JSON.stringify(gains));
      const result=JSON.parse(state.py.runPython('check_tuning_json(p4_gains_json)'));
      const previous=state.lastResponse ? state.lastResponse.output : null;
      state.attempts++;
      if (!state.tried) { state.tried=true;state.rounds++; }
      if(result.score>state.roundBest){state.total+=result.score-state.roundBest;state.roundBest=result.score;}
      refreshSession();
      state.previousOutput=previous;
      state.lastResponse=result;
      drawPlots(result);
      showResults(result,pred);
      $('attempt-badge').textContent=`Attempt ${state.attempts}`;
      document.querySelectorAll('input[name="prediction"]').forEach(radio=>radio.checked=false);
      $('result-panel').scrollIntoView({behavior:'smooth',block:'nearest'});
    }catch(err){showError(`Simulation failed: ${err.message||err}`);}
    finally {setBusy(false);}
  }
  function revealPlant() {
    if (!state.tried||state.locked||state.busy) return;
    try {
      const p=JSON.parse(state.py.runPython('reveal_plant_json()'));
      state.locked=true;
      const description=p.type==='first_order'
        ?`First-order: K = ${format(p.K,3)}, τ = ${format(p.tau,3)} s.  G(s) = K/(τs+1).`
        :`Second-order: K = ${format(p.K,3)}, ζ = ${format(p.zeta,3)}, ωn = ${format(p.omega_n,3)} rad/s.  G(s) = Kωn²/(s²+2ζωn s+ωn²).`;
      $('revealed-plant').textContent=`Hidden plant revealed: ${description}  Round closed; click New Challenge to continue.`;
      $('revealed-plant').hidden=false;
      $('reveal-plant').hidden=true;
      $('attempt-badge').textContent='Round finished';
      setBusy(false);
    } catch(err) {showError(`Could not reveal plant: ${err.message||err}`);}
  }
  function resetSession() {
    if(!state.ready||state.busy)return;
    // This does not silently discard an in-progress challenge.
    if (!window.confirm('Clear the session total and round count? Your current plant will remain.'))return;
    state.total = 0;
    state.rounds = 0;
    // Start a fresh round too: a reset now truly clears the entire session.
    newChallenge();
    refreshSession();
  }
  async function initialize() {
    setStatus('Loading Python...', 'waiting');
    $('loading-error').hidden=true;showError('');
    setBusy(true);
    try {
      if(typeof window.loadPyodide!=='function')throw new Error('Pyodide script unavailable (CDN connection).');
      const py=await window.loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/'});
      const response=await fetch('python/pid_tuning.py',{cache:'no-store'});
      if (!response.ok)throw new Error(`Cannot load python/pid_tuning.py (${response.status}). Start the HTTP server in the extracted project folder.`);
      const source=await response.text();
      py.runPython(source);
      state.py=py;state.ready=true;
      window.p4Pyodide=py;
      window.dispatchEvent(new Event('p4-python-ready'));
      setStatus('Python ready · RK4 solver loaded','ready');
      setBusy(false);
      newChallenge();
    }catch(err){state.ready=false;setStatus('Python load failed','error');$('loading-error').hidden=false;
      const div=$('loading-error');div.firstChild.textContent=`Could not start: ${err.message||err}. Check internet and use the local HTTP server. `;
      setBusy(false);
    }
  }
  syncInputs();refreshSession();
  $('check-tuning').addEventListener('click',checkTuning);
  $('new-challenge').addEventListener('click',newChallenge);
  $('reset-session').addEventListener('click',resetSession);
  $('reveal-plant').addEventListener('click',revealPlant);
  $('retry-python').addEventListener('click',initialize);
  window.addEventListener('load', initialize);
})();