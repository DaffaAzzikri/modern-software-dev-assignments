async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const notes = await fetchJSON('/notes/');
  for (const n of notes) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
}

// Tracks the active filter: 'all' | 'true' | 'false'
let currentFilter = 'all';

function updateBulkButton() {
  const checked = document.querySelectorAll('.action-checkbox:checked');
  document.getElementById('bulk-complete-btn').disabled = checked.length === 0;
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';

  let url = '/action-items/';
  if (currentFilter === 'true') url += '?completed=true';
  else if (currentFilter === 'false') url += '?completed=false';

  const items = await fetchJSON(url);
  for (const a of items) {
    const li = document.createElement('li');
    li.className = 'action-item' + (a.completed ? ' completed' : '');

    // Checkbox (only for incomplete items — completed ones can't be re-selected)
    if (!a.completed) {
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.className = 'action-checkbox';
      checkbox.dataset.id = a.id;
      checkbox.addEventListener('change', updateBulkButton);
      li.appendChild(checkbox);
    }

    const span = document.createElement('span');
    span.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    li.appendChild(span);

    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }

    list.appendChild(li);
  }

  updateBulkButton();
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  // Filter toggle buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      loadActions();
    });
  });

  // Bulk complete
  document.getElementById('bulk-complete-btn').addEventListener('click', async () => {
    const checked = document.querySelectorAll('.action-checkbox:checked');
    const ids = Array.from(checked).map(cb => parseInt(cb.dataset.id, 10));
    if (ids.length === 0) return;
    await fetchJSON('/action-items/bulk-complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids }),
    });
    loadActions();
  });

  loadNotes();
  loadActions();
});
