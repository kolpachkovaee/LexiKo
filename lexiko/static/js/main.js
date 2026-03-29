/* LexiKo main.js */

// ── Auto-dismiss messages ───────────────────────────────────────────────────
document.querySelectorAll('.message').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  }, 4000);
});

// ── Import tabs ─────────────────────────────────────────────────────────────
(function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');
  if (!tabBtns.length) return;

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(btn.dataset.tab);
      if (target) target.classList.add('active');
      // Set hidden import_type input
      const typeInput = document.getElementById('import-type-input');
      if (typeInput) typeInput.value = btn.dataset.tab === 'tab-text' ? 'text' : 'csv';
    });
  });
})();

// ── Canvas drawing ──────────────────────────────────────────────────────────
(function initCanvas() {
  const canvas = document.getElementById('draw-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let drawing = false;
  let color = '#3d2b35';
  let lineWidth = 4;

  document.querySelectorAll('.color-dot').forEach(dot => {
    dot.addEventListener('click', () => {
      document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
      dot.classList.add('active');
      color = dot.dataset.color;
    });
  });

  const sizeSlider = document.getElementById('brush-size');
  if (sizeSlider) {
    sizeSlider.addEventListener('input', () => { lineWidth = sizeSlider.value; });
  }

  function getPos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    if (e.touches) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY,
      };
    }
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  }

  function startDraw(e) {
    e.preventDefault();
    drawing = true;
    const pos = getPos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
  }
  function draw(e) {
    if (!drawing) return;
    e.preventDefault();
    const pos = getPos(e);
    ctx.lineTo(pos.x, pos.y);
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();
  }
  function endDraw() { drawing = false; }

  canvas.addEventListener('mousedown', startDraw);
  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', endDraw);
  canvas.addEventListener('mouseleave', endDraw);
  canvas.addEventListener('touchstart', startDraw, { passive: false });
  canvas.addEventListener('touchmove', draw, { passive: false });
  canvas.addEventListener('touchend', endDraw);

  const clearBtn = document.getElementById('canvas-clear');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    });
  }

  const saveBtn = document.getElementById('canvas-save');
  if (saveBtn) {
    saveBtn.addEventListener('click', () => {
      const dataUrl = canvas.toDataURL('image/png');
      const svgData =
        `<svg viewBox="0 0 ${canvas.width} ${canvas.height}" xmlns="http://www.w3.org/2000/svg">` +
        `<image href="${dataUrl}" width="${canvas.width}" height="${canvas.height}"/>` +
        `</svg>`;
      const cardId = saveBtn.dataset.cardId;
      const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
      fetch(`/api/cards/${cardId}/drawing/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ svg_data: svgData }),
      })
        .then(r => r.json())
        .then(data => { if (data.ok) showToast('Рисунок сохранён! 🌸'); })
        .catch(() => showToast('Ошибка сети', 'error'));
    });
  }

  // Restore saved drawing
  const savedSvg = canvas.dataset.savedSvg;
  if (savedSvg && savedSvg.includes('<image')) {
    const match = savedSvg.match(/href="([^"]+)"/);
    if (match) {
      const img = new Image();
      img.onload = () => ctx.drawImage(img, 0, 0);
      img.src = match[1];
    }
  }
})();

// ── Toast ────────────────────────────────────────────────────────────────────
function showToast(msg, type = 'success') {
  const toast = document.createElement('div');
  toast.textContent = msg;
  const bg = type === 'error' ? '#d95858' : '#7bc8a4';
  toast.style.cssText = [
    'position:fixed', 'bottom:1.5rem', 'right:1.5rem', 'z-index:9999',
    'padding:.75rem 1.4rem', 'border-radius:99px', 'font-size:.9rem',
    'font-weight:800', 'color:#fff', `background:${bg}`,
    'box-shadow:0 4px 20px rgba(0,0,0,.15)',
    'font-family:Nunito,sans-serif', 'transition:opacity .4s',
  ].join(';');
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 400); }, 2800);
}
