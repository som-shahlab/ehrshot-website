(function () {
  'use strict';

  const STATE = {
    data: null,
    metric: 'auroc',
    search: '',
    selectedModels: new Set(),
    sortCol: null,
    sortDir: 'desc',
    showFewShot: false,
  };

  const MODEL_COLORS = {
    'CLMBR-T-base': '#8b1a1a',
    'MOTOR-T-base': '#c0392b',
    'GBM': '#2980b9',
    'Logistic Regression': '#27ae60',
    'Random Forest': '#8e44ad',
  };

  const K_VALUES = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 128];

  // ── Bootstrap ──────────────────────────────────────────────

  async function init() {
    try {
      const base = document.querySelector('meta[name="lb-base"]');
      const baseURL = base ? base.content.replace(/\/$/, '') : '';
      const resp = await fetch(baseURL + '/data/leaderboard.json');
      STATE.data = await resp.json();
    } catch (e) {
      document.getElementById('leaderboard-app').innerHTML =
        '<p class="text-danger">Failed to load leaderboard data.</p>';
      return;
    }

    const versionEl = document.getElementById('lb-dataset-version');
    if (versionEl && STATE.data.datasetVersion) {
      versionEl.textContent = 'Dataset ' + STATE.data.datasetVersion;
    }

    STATE.selectedModels = new Set(STATE.data.models);
    buildControls();
    render();
    bindEvents();
  }

  // ── Controls ───────────────────────────────────────────────

  function buildControls() {
    buildMetricToggle();
    buildFewShotToggle();
    buildModelToggles();
    buildSearchBox();
  }

  function buildMetricToggle() {
    const el = document.getElementById('metric-toggle');
    el.innerHTML = ['auroc', 'auprc'].map(m =>
      `<button class="lb-btn ${m === STATE.metric ? 'lb-btn--active' : ''}" data-metric="${m}">${m.toUpperCase()}</button>`
    ).join('');
  }

  function buildFewShotToggle() {
    const el = document.getElementById('fewshot-toggle');
    el.innerHTML = `<button class="lb-btn ${STATE.showFewShot ? 'lb-btn--active' : ''}" id="fewshot-btn">
      ${STATE.showFewShot ? 'Hide' : 'Show'} Few-Shot Results
    </button>`;
  }

  function buildModelToggles() {
    const el = document.getElementById('model-toggles');
    el.innerHTML = STATE.data.models.map(m => {
      const checked = STATE.selectedModels.has(m) ? 'checked' : '';
      const color = MODEL_COLORS[m] || '#666';
      return `<label class="lb-model-toggle">
        <input type="checkbox" value="${m}" ${checked}>
        <span class="lb-model-swatch" style="background:${color}"></span>
        ${m}
      </label>`;
    }).join('');
  }

  function buildSearchBox() {
    const el = document.getElementById('task-search');
    el.value = STATE.search;
  }

  // ── Event binding ──────────────────────────────────────────

  function bindEvents() {
    document.getElementById('metric-toggle').addEventListener('click', e => {
      const btn = e.target.closest('[data-metric]');
      if (!btn) return;
      STATE.metric = btn.dataset.metric;
      buildMetricToggle();
      render();
    });

    document.getElementById('fewshot-toggle').addEventListener('click', e => {
      const btn = e.target.closest('button');
      if (!btn) return;
      STATE.showFewShot = !STATE.showFewShot;
      STATE.sortCol = null;
      STATE.sortDir = 'desc';
      buildFewShotToggle();
      render();
    });

    document.getElementById('model-toggles').addEventListener('change', e => {
      const cb = e.target;
      if (cb.checked) STATE.selectedModels.add(cb.value);
      else STATE.selectedModels.delete(cb.value);
      render();
    });

    document.getElementById('task-search').addEventListener('input', e => {
      STATE.search = e.target.value.toLowerCase();
      render();
    });
  }

  // ── Main render ────────────────────────────────────────────

  function render() {
    const container = document.getElementById('leaderboard-tables');
    container.innerHTML = '';

    const models = STATE.data.models.filter(m => STATE.selectedModels.has(m));
    if (models.length === 0) return;

    if (STATE.showFewShot) {
      renderFewShot(container, models);
    } else {
      renderSummary(container, models);
      renderPerTask(container, models);
    }
  }

  // ── Summary table: models=rows, task groups=columns ────────

  function renderSummary(container, models) {
    const groupedData = STATE.data.grouped[STATE.metric];
    if (!groupedData) return;

    const groups = Object.keys(STATE.data.taskGroups);

    const rows = models.map(m => {
      const row = { model: m, groups: {} };
      for (const g of groups) {
        if (groupedData[g] && groupedData[g][m]) {
          const d = groupedData[g][m];
          row.groups[g] = { all: parseFloat(d.all), ci: d.ci || '' };
        }
      }
      return row;
    });

    const bestPerGroup = {};
    for (const g of groups) {
      const vals = rows.map(r => r.groups[g] ? r.groups[g].all : -Infinity);
      bestPerGroup[g] = Math.max(...vals);
    }

    sortSummaryRows(rows, groups);

    const section = document.createElement('div');
    section.className = 'lb-table-section';
    section.innerHTML = '<h3 class="lb-section-title">Summary by Task Group</h3>';

    const wrapper = document.createElement('div');
    wrapper.className = 'lb-table-wrap';

    let html = `<table class="lb-table">
      <thead><tr>
        <th class="lb-th--model lb-sortable" data-sort="model">Model ${sortArrow('model')}</th>`;
    for (const g of groups) {
      html += `<th class="lb-sortable" data-sort="group_${g}">${g} ${sortArrow('group_' + g)}</th>`;
    }
    html += `<th>Run Date</th>`;
    html += '</tr></thead><tbody>';

    const meta = STATE.data.modelMeta || {};
    for (const row of rows) {
      const color = MODEL_COLORS[row.model] || '#666';
      const runDate = (meta[row.model] && meta[row.model].runDate) || '\u2014';
      html += `<tr>
        <td class="lb-td--model"><span class="lb-model-dot" style="background:${color}"></span>${row.model}</td>`;
      for (const g of groups) {
        const d = row.groups[g];
        if (!d) {
          html += '<td class="lb-na">\u2014</td>';
        } else {
          const best = d.all === bestPerGroup[g] ? 'lb-best' : '';
          html += `<td class="${best}">${d.all.toFixed(3)}${d.ci ? ' <span class="lb-ci">(' + d.ci + ')</span>' : ''}</td>`;
        }
      }
      html += `<td class="lb-date">${runDate}</td>`;
      html += '</tr>';
    }

    html += '</tbody></table>';
    wrapper.innerHTML = html;
    attachSortListeners(wrapper);
    section.appendChild(wrapper);
    container.appendChild(section);
  }

  function sortSummaryRows(rows, groups) {
    const col = STATE.sortCol;
    const dir = STATE.sortDir === 'desc' ? -1 : 1;
    if (!col) return;

    rows.sort((a, b) => {
      if (col === 'model') return dir * a.model.localeCompare(b.model);
      if (col.startsWith('group_')) {
        const g = col.slice(6);
        const va = a.groups[g] ? a.groups[g].all : -Infinity;
        const vb = b.groups[g] ? b.groups[g].all : -Infinity;
        return dir * (va - vb);
      }
      return 0;
    });
  }

  // ── Per-task tables: models=rows, just "All" column ────────

  function renderPerTask(container, models) {
    const individualData = STATE.data.individual[STATE.metric];
    if (!individualData) return;

    const groups = Object.keys(STATE.data.taskGroups);

    for (const group of groups) {
      const tasks = STATE.data.taskGroups[group];
      const filtered = tasks.filter(t =>
        !STATE.search || t.toLowerCase().includes(STATE.search) || group.toLowerCase().includes(STATE.search)
      );
      if (filtered.length === 0) continue;

      const groupDiv = document.createElement('div');
      groupDiv.className = 'lb-group-section';
      groupDiv.innerHTML = `<h3 class="lb-group-title">${group}</h3>`;

      const wrapper = document.createElement('div');
      wrapper.className = 'lb-table-wrap';

      const taskCols = [];
      for (const task of filtered) {
        if (individualData[task]) taskCols.push(task);
      }
      if (taskCols.length === 0) continue;

      const rows = models.map(m => {
        const row = { model: m, tasks: {} };
        for (const t of taskCols) {
          const d = individualData[t][m];
          if (d) {
            row.tasks[t] = { all: d.all, allStd: d.allStd };
          }
        }
        return row;
      });

      const bestPerTask = {};
      for (const t of taskCols) {
        const vals = rows.map(r => r.tasks[t] ? r.tasks[t].all : -Infinity);
        bestPerTask[t] = Math.max(...vals);
      }

      sortPerTaskRows(rows, taskCols);

      let html = `<table class="lb-table">
        <thead><tr>
          <th class="lb-th--model lb-sortable" data-sort="model">Model ${sortArrow('model')}</th>`;
      for (const t of taskCols) {
        html += `<th class="lb-sortable" data-sort="task_${t}">${t} ${sortArrow('task_' + t)}</th>`;
      }
      html += '</tr></thead><tbody>';

      for (const row of rows) {
        const color = MODEL_COLORS[row.model] || '#666';
        html += `<tr>
          <td class="lb-td--model"><span class="lb-model-dot" style="background:${color}"></span>${row.model}</td>`;
        for (const t of taskCols) {
          const d = row.tasks[t];
          if (!d) {
            html += '<td class="lb-na">\u2014</td>';
          } else {
            const best = d.all === bestPerTask[t] ? 'lb-best' : '';
            const std = d.allStd ? ` <span class="lb-std">\u00B1 ${d.allStd.toFixed(3)}</span>` : '';
            html += `<td class="${best}">${d.all.toFixed(3)}${std}</td>`;
          }
        }
        html += '</tr>';
      }

      html += '</tbody></table>';
      wrapper.innerHTML = html;
      attachSortListeners(wrapper);
      groupDiv.appendChild(wrapper);
      container.appendChild(groupDiv);
    }
  }

  function sortPerTaskRows(rows, taskCols) {
    const col = STATE.sortCol;
    const dir = STATE.sortDir === 'desc' ? -1 : 1;
    if (!col) return;

    rows.sort((a, b) => {
      if (col === 'model') return dir * a.model.localeCompare(b.model);
      if (col.startsWith('task_')) {
        const t = col.slice(5);
        const va = a.tasks[t] ? a.tasks[t].all : -Infinity;
        const vb = b.tasks[t] ? b.tasks[t].all : -Infinity;
        return dir * (va - vb);
      }
      return 0;
    });
  }

  // ── Few-shot view: one table per task group, then per task ─

  function renderFewShot(container, models) {
    const groupedData = STATE.data.grouped[STATE.metric];
    const individualData = STATE.data.individual[STATE.metric];
    const groups = Object.keys(STATE.data.taskGroups);

    for (const group of groups) {
      const groupDiv = document.createElement('div');
      groupDiv.className = 'lb-group-section';
      groupDiv.innerHTML = `<h3 class="lb-group-title">${group}</h3>`;

      if (groupedData && groupedData[group]) {
        const sec = document.createElement('div');
        sec.className = 'lb-table-section';
        sec.innerHTML = '<h4 class="lb-table-title">Aggregate</h4>';
        sec.appendChild(buildFewShotTable(groupedData[group], models, 'grouped'));
        groupDiv.appendChild(sec);
      }

      const tasks = STATE.data.taskGroups[group];
      const filtered = tasks.filter(t =>
        !STATE.search || t.toLowerCase().includes(STATE.search) || group.toLowerCase().includes(STATE.search)
      );

      for (const task of filtered) {
        if (!individualData || !individualData[task]) continue;
        const sec = document.createElement('div');
        sec.className = 'lb-table-section';
        sec.innerHTML = `<h4 class="lb-table-title">${task}</h4>`;
        sec.appendChild(buildFewShotTable(individualData[task], models, 'individual'));
        groupDiv.appendChild(sec);
      }

      container.appendChild(groupDiv);
    }
  }

  function buildFewShotTable(data, models, type) {
    const visibleModels = models.filter(m => data[m]);

    const rows = visibleModels.map(m => {
      const d = data[m];
      if (type === 'grouped') {
        return {
          model: m,
          all: parseFloat(d.all),
          ci: d.ci || '',
          allStd: null,
          k: K_VALUES.map(k => d.k[String(k)] != null ? d.k[String(k)] : null),
        };
      } else {
        return {
          model: m,
          all: d.all,
          allStd: d.allStd,
          ci: '',
          k: K_VALUES.map(k => d.k[String(k)] || null),
        };
      }
    });

    sortFewShotRows(rows);

    const bestAll = Math.max(...rows.map(r => r.all).filter(v => !isNaN(v)));
    const bestK = K_VALUES.map((_, i) => {
      const vals = rows.map(r => {
        const kv = r.k[i];
        if (kv == null) return -Infinity;
        return typeof kv === 'object' ? kv.mean : kv;
      });
      return Math.max(...vals);
    });

    const wrapper = document.createElement('div');
    wrapper.className = 'lb-table-wrap';

    let html = `<table class="lb-table">
      <thead><tr>
        <th class="lb-th--model lb-sortable" data-sort="model">Model ${sortArrow('model')}</th>
        <th class="lb-th--all lb-sortable" data-sort="all">All ${sortArrow('all')}</th>`;
    for (let i = 0; i < K_VALUES.length; i++) {
      html += `<th class="lb-th--k lb-sortable" data-sort="k${i}">k=${K_VALUES[i]} ${sortArrow('k' + i)}</th>`;
    }
    html += '</tr></thead><tbody>';

    for (const row of rows) {
      const color = MODEL_COLORS[row.model] || '#666';
      const ciStr = row.ci ? ` <span class="lb-ci">(${row.ci})</span>` : '';
      const stdStr = row.allStd ? ` <span class="lb-std">\u00B1 ${row.allStd.toFixed(3)}</span>` : '';

      html += `<tr>
        <td class="lb-td--model"><span class="lb-model-dot" style="background:${color}"></span>${row.model}</td>
        <td class="lb-td--all ${row.all === bestAll ? 'lb-best' : ''}">${row.all.toFixed(3)}${ciStr}${stdStr}</td>`;

      for (let i = 0; i < K_VALUES.length; i++) {
        const kv = row.k[i];
        if (kv == null) {
          html += '<td class="lb-na">\u2014</td>';
        } else if (typeof kv === 'object') {
          const best = kv.mean === bestK[i] ? 'lb-best' : '';
          html += `<td class="${best}">${kv.mean.toFixed(3)} <span class="lb-std">\u00B1 ${kv.std.toFixed(3)}</span></td>`;
        } else {
          const best = kv === bestK[i] ? 'lb-best' : '';
          html += `<td class="${best}">${kv.toFixed(3)}</td>`;
        }
      }
      html += '</tr>';
    }

    html += '</tbody></table>';
    wrapper.innerHTML = html;
    attachSortListeners(wrapper);
    return wrapper;
  }

  function sortFewShotRows(rows) {
    const col = STATE.sortCol;
    const dir = STATE.sortDir === 'desc' ? -1 : 1;
    if (!col) return;

    rows.sort((a, b) => {
      if (col === 'model') return dir * a.model.localeCompare(b.model);
      if (col === 'all') return dir * (a.all - b.all);
      if (col.startsWith('k')) {
        const idx = parseInt(col.slice(1));
        const aK = a.k[idx];
        const bK = b.k[idx];
        const va = aK != null ? (typeof aK === 'object' ? aK.mean : aK) : -Infinity;
        const vb = bK != null ? (typeof bK === 'object' ? bK.mean : bK) : -Infinity;
        return dir * (va - vb);
      }
      return 0;
    });
  }

  // ── Shared helpers ─────────────────────────────────────────

  function attachSortListeners(wrapper) {
    wrapper.querySelectorAll('.lb-sortable').forEach(th => {
      th.addEventListener('click', () => {
        const col = th.dataset.sort;
        if (STATE.sortCol === col) {
          STATE.sortDir = STATE.sortDir === 'desc' ? 'asc' : 'desc';
        } else {
          STATE.sortCol = col;
          STATE.sortDir = 'desc';
        }
        render();
      });
    });
  }

  function sortArrow(col) {
    if (STATE.sortCol !== col) return '<span class="lb-sort-icon">\u21C5</span>';
    return STATE.sortDir === 'desc'
      ? '<span class="lb-sort-icon lb-sort-icon--active">\u2193</span>'
      : '<span class="lb-sort-icon lb-sort-icon--active">\u2191</span>';
  }

  // ── Init ───────────────────────────────────────────────────

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
