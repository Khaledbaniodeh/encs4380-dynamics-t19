/* Ziegler–Nichols bonus for Homework 2 P4.
   Uses the existing Pyodide instance but its *own* Python module and chart.
   It never calls the main challenge or changes the student's score. */
(() => {
  'use strict';
  const get = (id) => document.getElementById(id);
  const bonus = get('zn-bonus');
  const slider = get('zn-gain-slider');
  const numberInput = get('zn-gain-number');
  const status = get('zn-status');
  const testButton = get('zn-test-p');
  const findButton = get('zn-discover');
  let pythonLoaded = false;
  let busy = false;
  let currentResult = null;
  let currentTuned = null;

  function showStatus(message, isError = false) {
    status.textContent = message;
    status.style.color = isError ? '#a3352b' : '#466474';
  }

  function setBusy(value) {
    busy = value;
    testButton.disabled = value;
    findButton.disabled = value;
    testButton.textContent = value ? 'Working...' : 'Test P-only gain';
    findButton.textContent = value ? 'Calculating...' : 'Find Ku & Calculate PID';
  }

  async function loadBonusPython() {
    if (pythonLoaded) return window.p4Pyodide;
    const py = window.p4Pyodide;
    if (!py) throw new Error('Wait for the main page to say Python ready, then try again.');
    const response = await fetch('python/ziegler_nichols.py', {cache: 'no-store'});
    if (!response.ok) throw new Error('Cannot load python/ziegler_nichols.py. Keep the Python and JS folders together.');
    const source = await response.text();
    // Run source inside an isolated Python module so its names do not overwrite
    // PID Tuning's simulate() or any of the main challenge variables.
    py.globals.set('zn_bonus_source', source);
    py.runPython(`import types
zn_bonus = types.ModuleType('zn_bonus')
exec(zn_bonus_source, zn_bonus.__dict__)
del zn_bonus_source`);
    pythonLoaded = true;
    return py;
  }

  function selectedGain() {
    if (!numberInput.value.trim()) throw new Error('Enter a P-only gain.');
    const value = Number(numberInput.value);
    if (!Number.isFinite(value) || value < 0.5 || value > 12)
      throw new Error('P-only Kp must be between 0.5 and 12.');
    return value;
  }

  function updateInputs(source) {
    if (source === 'slider') numberInput.value = slider.value;
    else {
      const value = Number(numberInput.value);
      if (numberInput.value && Number.isFinite(value) && value >= 0.5 && value <= 12)
        slider.value = String(value);
    }
  }

  function trace(name, x, y, color, dash = 'solid') {
    return {x,y,name,type:'scatter',mode:'lines',line:{color,width:2.8,dash},hovertemplate:'%{x:.2f} s, %{y:.3f}<extra>%{fullData.name}</extra>'};
  }

  function renderChart(pOnly, tuned) {
    const traces = [trace('Setpoint = 1',pOnly.time,pOnly.time.map(()=>1),'#315dda','dash'),
      trace(`P only (Kp=${pOnly.gain.toFixed(2)})`,pOnly.time,pOnly.output,'#b56425')];
    if (tuned) traces.push(trace('ZN PID',tuned.time,tuned.output,'#087f72'));
    if (window.Plotly) {
      window.Plotly.react(get('zn-plot'),traces,{
        autosize:true,paper_bgcolor:'#fff',plot_bgcolor:'#fff',
        margin:{l:52,r:15,t:15,b:70},
        xaxis:{title:'Time (s)',range:[0,28],gridcolor:'#e6edf2',zeroline:false},
        yaxis:{title:'Output y(t)',gridcolor:'#e6edf2',zeroline:false},
        font:{family:'Segoe UI, system-ui, sans-serif',color:'#405568',size:12},
        legend:{orientation:'h',x:0,y:-.22,traceorder:'normal',font:{size:10}},
        hovermode:'x unified',dragmode:'pan',showlegend:true
      },{responsive:true,displaylogo:false,displayModeBar:false});
    } else {
      // Small SVG fallback for offline chart library; the numerical data is real.
      const plot = get('zn-plot');
      const width=600,height=330,left=46,right=15,top=15,bottom=52;
      const allY=traces.flatMap(item=>item.y.filter(Number.isFinite));
      const low=Math.min(0,...allY)-.15,high=Math.max(1,...allY)+.15;
      const xScale=x=>left+(x/28)*(width-left-right);
      const yScale=y=>height-bottom-(y-low)/(high-low)*(height-bottom-top);
      const lines=traces.map(item=>{
        const pts=item.x.map((t,i)=>`${xScale(t).toFixed(1)},${yScale(item.y[i]).toFixed(1)}`).join(' ');
        return `<polyline points="${pts}" fill="none" stroke="${item.line.color}" stroke-width="2.8" ${item.line.dash==='dash'?'stroke-dasharray="6 4"':''}/>`;
      }).join('');
      plot.innerHTML=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="P-only oscillations and tuned PID response" style="width:100%;height:100%"><rect width="100%" height="100%" fill="white"/>${[0,7,14,21,28].map(t=>`<line x1="${xScale(t)}" y1="${top}" x2="${xScale(t)}" y2="${height-bottom}" stroke="#e6edf2"/>`).join('')}${lines}<text x="${width/2}" y="${height-12}" fill="#405568" text-anchor="middle" font-size="13">Time (s)</text></svg>`;
    }
  }

  function fmt(value, digits=3) {return Number(value).toFixed(digits);}
  async function testPOnly() {
    if (busy) return;
    let gain;
    try {gain=selectedGain();} catch(error){showStatus(error.message,true);return;}
    setBusy(true);
    try {
      const py=await loadBonusPython();
      py.globals.set('zn_trial_gain',gain);
      const result=JSON.parse(py.runPython('zn_bonus.test_gain_json(zn_trial_gain)'));
      currentResult=result;currentTuned=null;
      renderChart(result,null);
      get('zn-results').hidden=true;
      const label={decaying:'Peaks shrink: stable, damped oscillations.',sustained:'Peaks stay almost constant: near the ultimate gain.',growing:'Peaks grow: P-only closed loop is unstable.',no_clear_peaks:'Not enough peaks to measure sustained oscillation.'};
      showStatus(`Kp = ${fmt(result.gain,2)} · ${label[result.behavior]||result.behavior}`);
    }catch(error){showStatus(error.message||String(error),true);}
    finally {setBusy(false);}
  }

  async function findUltimateGain() {
    if (busy) return;
    setBusy(true);
    try {
      const py=await loadBonusPython();
      const values=JSON.parse(py.runPython('zn_bonus.calculate_bonus_json()'));
      const d=values.discovery,g=values.gains,r=values.tuned_response;
      currentResult=d.response;currentTuned=r;
      numberInput.value = fmt(d.ultimate_gain,2);
      slider.value = String(d.ultimate_gain);
      renderChart(currentResult,currentTuned);
      get('zn-ku').textContent=fmt(d.ultimate_gain);
      get('zn-pu').textContent=`${fmt(d.ultimate_period)} s`;
      get('zn-kp').textContent=fmt(g.kp);
      get('zn-ki').textContent=fmt(g.ki);
      get('zn-kd').textContent=fmt(g.kd);
      get('zn-performance').textContent=`ZN PID on this plant: overshoot ${fmt(r.overshoot_percent,2)}%, settling time ${r.settling_time==null?'not reached':`${fmt(r.settling_time,2)} s`}, final error ${fmt(r.final_error_percent,3)}%. Ziegler–Nichols is a starting point for tuning, not an optimal solution.`;
      get('zn-results').hidden=false;
      showStatus(`Found Ku numerically with ${d.search_iterations} RK4/bisection steps. Pu is measured from successive peaks.`);
    }catch(error){showStatus(error.message||String(error),true);}
    finally{setBusy(false);}
  }

  slider.addEventListener('input',()=>updateInputs('slider'));
  numberInput.addEventListener('input',()=>updateInputs('number'));
  testButton.addEventListener('click',testPOnly);
  findButton.addEventListener('click',findUltimateGain);
  // Lazy loading: leave P4 playable if the optional bonus file is missing.
  bonus.addEventListener('toggle',()=>{
    if (bonus.open && !currentResult && !busy) {
      if (window.p4Pyodide) testPOnly();
      else showStatus('Wait for Python ready above, then press Test P-only gain.');
    }
    if (bonus.open && window.Plotly && currentResult) {
      requestAnimationFrame(()=>window.Plotly.Plots.resize(get('zn-plot')));
    }
  });
})();