"use strict";
const el = id => document.getElementById(id);
const fields = ["K","tau","kp","ki","kd","sensor_tau","setpoint","duration","u_min","u_max"];
const defaults = {K:1,tau:1,kp:2,ki:4,kd:0,sensor_tau:0.05,setpoint:1,duration:30,u_min:-100,u_max:100};
let python = null;
let result = null;
let savedPrediction = null;
let timer = null;
let drawRevision = 0;
const number = x => !Number.isFinite(x) ? "—" : (x!==0 && Math.abs(x)<0.00001) ? x.toExponential(2) : x.toLocaleString("en",{maximumFractionDigits:4});

function readSettings() {
  const values = {};
  for (const key of fields) {
    values[key] = el(key).valueAsNumber;
    if (!Number.isFinite(values[key])) throw new Error("Enter a finite number for " + key + ".");
  }
  return values;
}

function setSettings(values) {
  for (const key of fields) {
    el(key).value = values[key];
    if (el(key+"_range")) el(key+"_range").value = values[key];
  }
}

function showInputError(message) {
  el("input-error").hidden = !message;
  el("input-error").textContent = message || "";
}

function responsePlot() {
  const d = result.response;
  const target = result.settings.setpoint;
  const narrow=el("response-chart").clientWidth<500;
  const traces = [
    {x:[0,result.settings.duration],y:[target,target],name:"Setpoint r",mode:"lines",line:{color:"#718193",dash:"dash",width:1.5}},
    {x:d.time,y:d.true,name:"True output y",mode:"lines",line:{color:"#315dda",width:3}},
    {x:d.time,y:d.measured,name:"Sensor reading ym",mode:"lines",line:{color:"#b96b18",width:2.5}}
  ];
  if (el("show-ideal").checked) traces.push({x:result.ideal.time,y:result.ideal.true,name:"Output with ideal feedback",mode:"lines",line:{color:"#91a2ad",dash:"dot",width:2}});
  return Plotly.react(el("response-chart"),traces,{
    margin:{l:49,r:12,t:22,b:narrow?125:79},autosize:true,hovermode:"x unified",
    xaxis:{title:{text:"Time (s)"},range:[0,result.settings.duration],gridcolor:"#eaf0f4",zeroline:false},
    yaxis:{title:{text:"Output (model units)"},gridcolor:"#eaf0f4",zeroline:false,automargin:true},
    font:{family:"Segoe UI, sans-serif",size:12,color:"#41566a"},paper_bgcolor:"#fff",plot_bgcolor:"#fff",
    legend:{orientation:"h",x:0,y:narrow?-0.38:-0.24,yanchor:"top",font:{size:11}},uirevision:drawRevision
  },{responsive:true,displayModeBar:false,displaylogo:false}).then(inspectTime);
}

function inspectTime() {
  if (!result) return;
  const time = Number(el("inspect-time").value);
  const d = result.response;
  let i=0;
  while (i<d.time.length-1 && d.time[i]<time) i++;
  if (i>0 && time-d.time[i-1]<d.time[i]-time) i--;
  el("inspect-label").textContent = d.time[i].toFixed(2)+" s";
  el("true-now").textContent = number(d.true[i]);
  el("measured-now").textContent = number(d.measured[i]);
  el("gap-now").textContent = number(d.true[i]-d.measured[i]);
  Plotly.relayout(el("response-chart"),{shapes:[{type:"line",x0:d.time[i],x1:d.time[i],yref:"paper",y0:0,y1:1,line:{color:"#9dadb9",width:1,dash:"dot"}}]});
}

function controlPlot() {
  if (!result || !el("control-details").open) return;
  const end=result.metrics.end_time;
  Plotly.react(el("control-chart"),[
    {x:result.response.time,y:result.response.control,name:"Control u",mode:"lines",line:{color:"#087f72",width:2}},
    {x:[0,end],y:[result.settings.u_min,result.settings.u_min],name:"Lower limit",mode:"lines",line:{color:"#a4acb5",dash:"dot",width:1}},
    {x:[0,end],y:[result.settings.u_max,result.settings.u_max],name:"Upper limit",mode:"lines",line:{color:"#a4acb5",dash:"dot",width:1}}
  ],{
    margin:{l:48,r:12,t:12,b:48},xaxis:{title:{text:"Time (s)"},gridcolor:"#edf1f4"},
    yaxis:{title:{text:"Control u"},gridcolor:"#edf1f4",automargin:true},paper_bgcolor:"#fff",plot_bgcolor:"#fff",
    font:{family:"Segoe UI, sans-serif",size:12,color:"#41566a"},showlegend:false
  },{responsive:true,displayModeBar:false});
}

function sameExceptSensor(a,b) {
  return fields.filter(key=>key!=="sensor_tau").every(key=>a[key]===b[key]);
}

function updatePrediction() {
  if (!savedPrediction || !result) {el("check-prediction").disabled=true;return;}
  const same = sameExceptSensor(savedPrediction.settings,result.settings);
  el("check-prediction").disabled = !same || result.settings.sensor_tau<=savedPrediction.settings.sensor_tau;
  if (!same) el("prediction-feedback").textContent="The plant, PID gains, command limits, target or time window changed. Restore them or start a new prediction.";
}

function runSimulation() {
  if (!python) return;
  try {
    const values=readSettings();
    python.globals.set("p2_values",JSON.stringify(values));
    const next=JSON.parse(python.runPython("simulate_json(p2_values)"));
    result=next;
    showInputError("");drawRevision++;
    el("status").textContent="Python ready · Compare the true output with the measured response.";
    el("status").classList.remove("error");
    el("motion").textContent=result.metrics.motion;
    el("motion").classList.toggle("warning",result.metrics.motion!=="Steady response");
    el("overshoot").textContent=result.metrics.overshoot===null?"N/A":number(result.metrics.overshoot)+"%";
    el("last-error").textContent="True tracking error at "+number(result.metrics.end_time)+" s: "+number(result.metrics.last_error);
    el("saturation-note").textContent="Command limits: "+number(result.settings.u_min)+" to "+number(result.settings.u_max)+" · "+(result.response.saturated?"Saturation occurred":"No saturation")+" · Anti-windup enabled.";
    el("solver-note").textContent="RK4 internal step: "+result.response.step.toPrecision(3)+" s · "+result.response.steps.toLocaleString("en")+" steps. This is not the digital PID sampling time Ts from P3.";
    el("inspect-time").max=result.metrics.end_time;
    if (Number(el("inspect-time").value)>result.metrics.end_time) el("inspect-time").value=result.metrics.end_time;
    if (result.response.stopped) showInputError("The response exceeded the simulation’s numeric limit. The displayed trace ends at "+number(result.metrics.end_time)+" s; reduce the gains or sensor lag.");
    responsePlot();controlPlot();updatePrediction();
  } catch (error) {
    console.error(error);
    const message=error.message || String(error);
    const validationMessage=message.match(/ValueError: ([^\n]+)/);
    showInputError((validationMessage ? validationMessage[1] : message) + (result ? " The chart still shows the last valid settings." : ""));
    el("check-prediction").disabled=true;
  }
}

function requestSimulation() {
  el("check-prediction").disabled=true;
  document.querySelectorAll("[data-preset]").forEach(button=>button.setAttribute("aria-pressed","false"));
  clearTimeout(timer);
  timer=setTimeout(runSimulation,180);
}

function clearPrediction() {
  savedPrediction=null;
  el("prediction-choice").value="";
  el("prediction-feedback").textContent="Choose a prediction, save it, then increase only the sensor time constant.";
  el("prediction-feedback").dataset.state="";
  el("check-prediction").disabled=true;
}

for (const key of fields) {
  const slider=el(key+"_range");
  if(slider) slider.addEventListener("input",()=>{el(key).value=slider.value;requestSimulation();});
  el(key).addEventListener("input",()=>{if(slider&&Number.isFinite(el(key).valueAsNumber))slider.value=el(key).value;requestSimulation();});
}
document.querySelectorAll("[data-preset]").forEach(button=>button.addEventListener("click",()=>{
  const lag={fast:0.05,slow:1,oscillating:3}[button.dataset.preset];
  setSettings({...defaults,sensor_tau:lag});clearPrediction();runSimulation();
  document.querySelectorAll("[data-preset]").forEach(b=>b.setAttribute("aria-pressed",String(b===button)));
}));
el("reset").addEventListener("click",()=>{setSettings(defaults);clearPrediction();runSimulation();document.querySelectorAll("[data-preset]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.preset==="fast")));});
el("inspect-time").addEventListener("input",inspectTime);
el("show-ideal").addEventListener("change",responsePlot);
el("control-details").addEventListener("toggle",controlPlot);
el("save-prediction").addEventListener("click",()=>{
  runSimulation();
  if (!result || !el("input-error").hidden) return;
  const choice=el("prediction-choice").value;
  if (!choice) {el("prediction-feedback").textContent="Choose increase, decrease or stay similar first.";return;}
  if (result.metrics.overshoot===null) {el("prediction-feedback").textContent="Choose a nonzero setpoint for a percentage-overshoot prediction.";return;}
  savedPrediction={settings:{...result.settings},overshoot:result.metrics.overshoot,choice};
  el("prediction-feedback").textContent="Saved at τs = "+number(result.settings.sensor_tau)+" s and overshoot "+number(result.metrics.overshoot)+"%. Now increase τs without changing the other settings.";
  updatePrediction();
});
el("new-prediction").addEventListener("click",clearPrediction);
el("check-prediction").addEventListener("click",()=>{
  runSimulation();
  if (!savedPrediction || !result || el("check-prediction").disabled) return;
  const difference=result.metrics.overshoot-savedPrediction.overshoot;
  const actual=Math.abs(difference)<=0.5?"similar":difference>0?"increase":"decrease";
  const correct=actual===savedPrediction.choice;
  el("prediction-feedback").dataset.state=correct?"correct":"retry";
  el("prediction-feedback").textContent=(correct?"Correct. ":"Compare your prediction. ")+"Overshoot changed from "+number(savedPrediction.overshoot)+"% to "+number(result.metrics.overshoot)+"% in the same time window. Changes within 0.5 percentage points count as similar.";
});
el("retry").addEventListener("click",()=>location.reload());
window.addEventListener("resize",()=>{if(result){Plotly.Plots.resize(el("response-chart"));if(el("control-details").open)Plotly.Plots.resize(el("control-chart"));}});

async function initialize() {
  try {
    if(typeof loadPyodide!=="function" || typeof Plotly==="undefined") throw new Error("The Python or plotting library did not load. Check internet access.");
    python=await loadPyodide({indexURL:"https://cdn.jsdelivr.net/pyodide/v314.0.7/full/"});
    const response=await fetch("python/slow_sensor.py",{cache:"no-cache"});
    if(!response.ok)throw new Error("Could not load the P2 Python model.");
    python.runPython(await response.text());
    const rows=JSON.parse(python.runPython("validation_json()"));
    el("validation").replaceChildren();
    rows.forEach(row=>{
      const tr=document.createElement("tr");
      [row.name,number(row.expected)+" "+row.unit,number(row.computed)+" "+row.unit,number(row.tolerance)+" "+row.unit,row.passed?"Pass":"Fail"].forEach((value,i)=>{const td=document.createElement("td");td.textContent=value;if(i===4&&row.passed)td.className="pass";tr.append(td);});
      el("validation").append(tr);
    });
    el("parameters").disabled=false;
    ["inspect-time","show-ideal","prediction-choice","save-prediction","new-prediction"].forEach(id=>el(id).disabled=false);
    runSimulation();
  } catch(error) {
    console.error(error);
    el("status").textContent="Could not start the experiment: "+(error.message||error);
    el("status").classList.add("error");el("retry").hidden=false;
  }
}
initialize();
