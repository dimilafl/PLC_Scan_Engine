/**
 * PLC MicroScan Engine Web UI
 * Handles all client-side interactions and state rendering.
 */

/**
 * Fetch current state from the server.
 */
async function fetchState() {
  try {
    const res = await fetch('/api/state');
    const data = await res.json();
    renderState(data.state);
  } catch (error) {
    console.error('Error fetching state:', error);
  }
}

/**
 * Render the complete state (bools + timers).
 */
function renderState(state) {
  renderBools(state.bools);
  renderTimers(state.timers);
}

/**
 * Render boolean tags table.
 */
function renderBools(bools) {
  const tbody = document.querySelector('#bools-table tbody');
  tbody.innerHTML = '';

  if (bools.length === 0) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 3;
    td.textContent = 'No boolean tags';
    td.style.textAlign = 'center';
    td.style.color = '#999';
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  bools.forEach(b => {
    const tr = document.createElement('tr');

    // Name column
    const tdName = document.createElement('td');
    tdName.textContent = b.name;

    // Value column
    const tdValue = document.createElement('td');
    tdValue.textContent = b.value ? 'TRUE' : 'FALSE';
    tdValue.className = b.value ? 'bool-true' : 'bool-false';

    // Toggle button column
    const tdToggle = document.createElement('td');
    const btn = document.createElement('button');
    btn.textContent = 'Toggle';
    btn.dataset.tagName = b.name;
    btn.addEventListener('click', onToggleBool);
    tdToggle.appendChild(btn);

    tr.appendChild(tdName);
    tr.appendChild(tdValue);
    tr.appendChild(tdToggle);
    tbody.appendChild(tr);
  });
}

/**
 * Render timer tags table.
 */
function renderTimers(timers) {
  const tbody = document.querySelector('#timers-table tbody');
  tbody.innerHTML = '';

  if (timers.length === 0) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 6;
    td.textContent = 'No timer tags';
    td.style.textAlign = 'center';
    td.style.color = '#999';
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  timers.forEach(t => {
    const tr = document.createElement('tr');

    // Name
    const tdName = document.createElement('td');
    tdName.textContent = t.name;

    // EN flag
    const tdEN = document.createElement('td');
    tdEN.textContent = t.en ? 'TRUE' : 'FALSE';
    tdEN.className = t.en ? 'timer-flag-true' : 'timer-flag-false';

    // DN flag
    const tdDN = document.createElement('td');
    tdDN.textContent = t.dn ? 'TRUE' : 'FALSE';
    tdDN.className = t.dn ? 'timer-flag-true' : 'timer-flag-false';

    // TT flag
    const tdTT = document.createElement('td');
    tdTT.textContent = t.tt ? 'TRUE' : 'FALSE';
    tdTT.className = t.tt ? 'timer-flag-true' : 'timer-flag-false';

    // ACC
    const tdACC = document.createElement('td');
    tdACC.textContent = t.acc_ms;

    // PRE
    const tdPRE = document.createElement('td');
    tdPRE.textContent = t.pre_ms;

    tr.appendChild(tdName);
    tr.appendChild(tdEN);
    tr.appendChild(tdDN);
    tr.appendChild(tdTT);
    tr.appendChild(tdACC);
    tr.appendChild(tdPRE);
    tbody.appendChild(tr);
  });
}

/**
 * Handle toggle bool button click.
 */
async function onToggleBool(event) {
  const name = event.target.dataset.tagName;
  try {
    const res = await fetch('/api/toggle_bool', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    const data = await res.json();
    if (data.state) {
      renderState(data.state);
    }
  } catch (error) {
    console.error('Error toggling bool:', error);
  }
}

/**
 * Handle demo selector change.
 */
async function onSelectDemo(event) {
  const demo = event.target.value;
  try {
    const res = await fetch('/api/select_demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ demo }),
    });
    const data = await res.json();
    if (data.state) {
      renderState(data.state);
    }
  } catch (error) {
    console.error('Error selecting demo:', error);
  }
}

/**
 * Handle step button click.
 */
async function onStep() {
  try {
    const res = await fetch('/api/step', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dt_ms: 100 }),
    });
    const data = await res.json();
    if (data.state) {
      renderState(data.state);
    }
  } catch (error) {
    console.error('Error stepping:', error);
  }
}

/**
 * Handle run button click.
 */
async function onRun() {
  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ steps: 50, dt_ms: 100 }),
    });
    const data = await res.json();
    if (data.state) {
      renderState(data.state);
    }
  } catch (error) {
    console.error('Error running:', error);
  }
}

/**
 * Initialize the UI on page load.
 */
function init() {
  document.getElementById('demo-select').addEventListener('change', onSelectDemo);
  document.getElementById('btn-refresh').addEventListener('click', fetchState);
  document.getElementById('btn-step').addEventListener('click', onStep);
  document.getElementById('btn-run').addEventListener('click', onRun);

  // Initial state fetch
  fetchState();
}

// Run init when DOM is ready
document.addEventListener('DOMContentLoaded', init);
