const byId = id => document.getElementById(id);
const keys = new Set();
let pulse = false;
async function boot() {
  const root = document.documentElement.dataset.runtime || "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
  const {loadPyodide} = await import(root + "pyodide.mjs");
  const py = await loadPyodide({indexURL: root});
  const packages = {game:["bird","pipes","levels","engine"], voice:["controller","powers","versus"], ml:["predictor","bluff"]};
  const files = ["main.py"];
  for (const [dir, names] of Object.entries(packages)) {
    py.FS.mkdirTree("/home/pyodide/" + dir);
    for (const name of ["__init__", ...names]) files.push(dir + "/" + name + ".py");
  }
  await Promise.all(files.map(async path => {
    const response = await fetch(path);
    if (!response.ok) throw Error(path + " " + response.status);
    py.FS.writeFile("/home/pyodide/" + path, await response.text());
  }));
  py.runPython("from main import engine, mic, tick, show");
  const engine = py.globals.get("engine"), tick = py.globals.get("tick"), show = py.globals.get("show");
  byId("state").textContent = "Ready · Press Space to start";
  byId("mic").disabled = false;
  let listening = false;
  byId("mic").onclick = async () => {
    byId("mic").disabled = true;
    try {
      await py.runPythonAsync(listening ? "await mic.stop()" : "await mic.start()");
      listening = !listening;
      byId("mic").textContent = listening ? "Disable microphone" : "Enable microphone";
      byId("inputStatus").textContent = listening ? "Microphone active" : "Keyboard mode";
    } catch(e) { byId("inputStatus").textContent = "Check microphone permissions. Arrow keys are available."; }
    finally { byId("mic").disabled = false; }
  };
  function chooseLevel(value) {
    engine.set_level(Number(value)); engine.start(); keys.clear(); pulse = false;
  }
  byId("levelSelect").onchange = e => { chooseLevel(e.target.value); e.target.blur(); };
  byId("pilot").disabled = byId("levelSelect").disabled = false;
  byId("pilot").onclick = () => engine.jump();
  byId("gameCanvas").onpointerdown = () => engine.jump();
  addEventListener("keydown", e => {
    if (e.target.matches("input,select")) return;
    if (e.code==="Space" && e.target.matches("button")) e.target.blur();
    if (["Space","ArrowUp","ArrowDown","KeyX"].includes(e.code)) e.preventDefault();
    keys.add(e.code);
    if (e.repeat) return;
    if (e.code==="Space") engine.jump();
    if (e.code==="KeyX") pulse = true;
    if (/^[1-5]$/.test(e.key)) chooseLevel(e.key);
  });
  addEventListener("keyup",e => keys.delete(e.code));
  addEventListener("blur",()=>{ keys.clear(); pulse=false; });
  let last=performance.now(), acc=0;
  function frame(now) {
    acc += Math.min(100, now-last); last=now;
    while(acc >= 1000/60) {
      tick(Number(keys.has("ArrowDown"))-Number(keys.has("ArrowUp")),pulse,Number(byId("gain").value),byId("role").value);
      pulse=false; acc-=1000/60;
    }
    show(); requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
boot().catch(e=>{ byId("state").textContent="Loading failed · "+e.message; console.error(e); });
